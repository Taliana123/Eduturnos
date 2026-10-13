from __future__ import annotations

import base64
import hashlib
import json
import time
from datetime import datetime, time as datetime_time, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app, url_for

from database.db import consultar, ejecutar

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API_BASE = "https://www.googleapis.com/calendar/v3"
SCOPES = "openid email https://www.googleapis.com/auth/calendar.events"


def configuracion_lista() -> bool:
    origen = current_app.config.get("APP_ORIGIN", "").strip()
    return bool(
        current_app.config.get("GOOGLE_OAUTH_CLIENT_ID")
        and current_app.config.get("GOOGLE_OAUTH_CLIENT_SECRET")
        and origen.startswith("https://")
    )


def uri_callback() -> str:
    origen = current_app.config["APP_ORIGIN"].strip().rstrip("/")
    return origen + url_for("integraciones_google.callback")


def url_autorizacion(state: str) -> str:
    return AUTH_URL + "?" + urlencode({
        "client_id": current_app.config["GOOGLE_OAUTH_CLIENT_ID"],
        "redirect_uri": uri_callback(),
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    })


def _solicitud_json(url: str, data: dict, access_token: str | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    request = Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urlopen(request, timeout=12) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"Google respondió HTTP {exc.code}.") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("No se pudo completar la solicitud con Google.") from exc


def intercambiar_codigo(code: str) -> dict:
    body = urlencode({
        "code": code,
        "client_id": current_app.config["GOOGLE_OAUTH_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
        "redirect_uri": uri_callback(),
        "grant_type": "authorization_code",
    }).encode("utf-8")
    request = Request(TOKEN_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urlopen(request, timeout=12) as response:
            token = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("Google no pudo completar la autorización.") from exc
    if not token.get("access_token") or not token.get("refresh_token"):
        raise RuntimeError("Google no entregó credenciales renovables; vuelve a autorizar y acepta el acceso solicitado.")
    token["expires_at"] = time.time() + int(token.get("expires_in", 3600))
    return token


def correo_google(access_token: str) -> str:
    request = Request(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    try:
        with urlopen(request, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
        return (data.get("email") or "").strip()[:180]
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return ""


def _fernet() -> Fernet:
    material = (current_app.config["SECRET_KEY"] + "|eduturnos-google-calendar-v1").encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(material).digest())
    return Fernet(key)


def cifrar_token(token: dict) -> str:
    return _fernet().encrypt(json.dumps(token).encode("utf-8")).decode("ascii")


def descifrar_token(value: str) -> dict:
    try:
        return json.loads(_fernet().decrypt(value.encode("ascii")).decode("utf-8"))
    except (InvalidToken, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("No se pudieron descifrar las credenciales de Google; vuelve a conectar la cuenta.") from exc


def guardar_conexion(scope_key: str, tipo: str, user_id: int | None, email: str, token: dict) -> None:
    ejecutar(
        "INSERT INTO integraciones_google(scope_key,tipo,id_usuario,correo_google,calendar_id,token_cifrado) "
        "VALUES(%s,%s,%s,%s,'primary',%s) ON DUPLICATE KEY UPDATE tipo=VALUES(tipo),"
        "id_usuario=VALUES(id_usuario),correo_google=VALUES(correo_google),calendar_id='primary',"
        "token_cifrado=VALUES(token_cifrado),fecha_actualizacion=NOW()",
        (scope_key, tipo, user_id, email or None, cifrar_token(token)),
    )


def _renovar_token(connection: dict, token: dict) -> dict:
    if float(token.get("expires_at", 0)) > time.time() + 60:
        return token
    body = urlencode({
        "client_id": current_app.config["GOOGLE_OAUTH_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
        "refresh_token": token["refresh_token"],
        "grant_type": "refresh_token",
    }).encode("utf-8")
    request = Request(TOKEN_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urlopen(request, timeout=12) as response:
            refresh = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("No se pudo renovar la autorización de Google.") from exc
    token["access_token"] = refresh["access_token"]
    token["expires_at"] = time.time() + int(refresh.get("expires_in", 3600))
    if refresh.get("refresh_token"):
        token["refresh_token"] = refresh["refresh_token"]
    ejecutar("UPDATE integraciones_google SET token_cifrado=%s WHERE scope_key=%s", (cifrar_token(token), connection["scope_key"]))
    return token


def _conexiones_para_cita(cita_id: int, creador_id: int) -> list[dict]:
    return consultar(
        "SELECT DISTINCT i.* FROM integraciones_google i "
        "LEFT JOIN citas c ON c.id=%s "
        "LEFT JOIN estudiantes e ON e.id_estudiante=c.id_estudiante "
        "LEFT JOIN acudientes a ON a.id_acudiente=c.id_acudiente "
        "LEFT JOIN docentes d ON d.id_docente=c.id_docente "
        "LEFT JOIN usuarios u ON u.id_usuario=i.id_usuario "
        "LEFT JOIN roles r ON r.id=u.id_rol "
        "WHERE i.scope_key='institucional' OR (u.estado=1 AND (i.id_usuario=%s "
        "OR i.id_usuario IN (c.creado_por,e.id_usuario,a.id_usuario,d.id_usuario) "
        "OR r.nombre IN ('Super Admin','Rector','Administrador / Coordinador'))) ",
        (cita_id, creador_id),
    )


def _normalizar_hora_cita(hora):
    if isinstance(hora, datetime_time):
        return hora
    if isinstance(hora, timedelta):
        total = int(hora.total_seconds())
        return datetime_time((total // 3600) % 24, (total % 3600) // 60, total % 60)
    raise TypeError("La hora de la cita no tiene un formato compatible.")


def sincronizar_cita(cita_id: int, creador_id: int) -> list[dict]:
    if not configuracion_lista():
        return []
    cita = consultar(
        "SELECT c.id,c.fecha,c.hora,c.lugar,c.creado_por,m.nombre motivo,s.direccion sede "
        "FROM citas c JOIN motivos m ON m.id=c.id_motivo "
        "JOIN estudiantes e ON e.id_estudiante=c.id_estudiante "
        "LEFT JOIN sedes s ON s.id=e.id_sede WHERE c.id=%s",
        (cita_id,), uno=True,
    )
    if not cita:
        return []
    conexiones = _conexiones_para_cita(cita_id, creador_id)
    if not conexiones:
        return []
    inicio = datetime.combine(cita["fecha"], _normalizar_hora_cita(cita["hora"]), tzinfo=timezone(timedelta(hours=-5)))
    fin = inicio + timedelta(minutes=30)
    resultado = []
    for conexion in conexiones:
        scope = conexion["scope_key"]
        event_id = "eduturnos" + hashlib.sha256(f"{scope}:{cita_id}".encode()).hexdigest()
        try:
            previo = consultar("SELECT estado FROM eventos_google WHERE id_cita=%s AND scope_key=%s", (cita_id, scope), uno=True)
            if previo and previo["estado"] == "Sincronizado":
                resultado.append({"scope": scope, "estado": "Sincronizado"})
                continue
            token = _renovar_token(conexion, descifrar_token(conexion["token_cifrado"]))
            event = {
                "id": event_id,
                "summary": "Citación escolar",
                "description": "Consulta los detalles de la cita en EDUTURNOS.",
                "location": cita.get("lugar") or cita.get("sede") or "Ibagué, Tolima",
                "start": {"dateTime": inicio.isoformat(), "timeZone": "America/Bogota"},
                "end": {"dateTime": fin.isoformat(), "timeZone": "America/Bogota"},
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 1440},
                        {"method": "popup", "minutes": 120},
                    ],
                },
            }
            url = f"{API_BASE}/calendars/{quote(conexion['calendar_id'], safe='')}/events?sendUpdates=none"
            try:
                _solicitud_json(url, event, token["access_token"])
            except RuntimeError as exc:
                if "HTTP 409" not in str(exc):
                    raise
                patch_url = f"{url.rsplit('/events?', 1)[0]}/events/{event_id}?sendUpdates=none"
                _actualizar_evento_google(patch_url, event, token["access_token"])
            ejecutar(
                "INSERT INTO eventos_google(id_cita,scope_key,google_event_id,estado,ultimo_error) "
                "VALUES(%s,%s,%s,'Sincronizado',NULL) ON DUPLICATE KEY UPDATE google_event_id=VALUES(google_event_id),estado='Sincronizado',ultimo_error=NULL",
                (cita_id, scope, event_id),
            )
            resultado.append({"scope": scope, "estado": "Sincronizado"})
        except Exception as exc:
            error = type(exc).__name__[:180]
            try:
                ejecutar(
                    "INSERT INTO eventos_google(id_cita,scope_key,google_event_id,estado,ultimo_error) "
                    "VALUES(%s,%s,%s,'Fallido',%s) ON DUPLICATE KEY UPDATE estado='Fallido',ultimo_error=VALUES(ultimo_error)",
                    (cita_id, scope, event_id, error),
                )
            except Exception:
                current_app.logger.exception("No se pudo registrar el fallo de Google Calendar para la cita %s", cita_id)
            current_app.logger.exception("No se pudo sincronizar la cita %s con Google Calendar", cita_id)
            resultado.append({"scope": scope, "estado": "Fallido"})
    return resultado


def sincronizar_citas_futuras(scope_key: str, user_id: int | None = None) -> dict:
    filtros = [
        "TIMESTAMP(c.fecha,c.hora)>=NOW()",
        "ec.nombre IN ('Pendiente','Confirmada','Reprogramada')",
    ]
    parametros = []
    if scope_key != "institucional":
        if user_id is None:
            return {"citas": 0, "fallidas": 0}
        filtros.append(
            "(c.creado_por=%s OR e.id_usuario=%s OR a.id_usuario=%s OR d.id_usuario=%s "
            "OR EXISTS (SELECT 1 FROM usuarios u JOIN roles r ON r.id=u.id_rol "
            "WHERE u.id_usuario=%s AND u.estado=1 "
            "AND r.nombre IN ('Super Admin','Rector','Administrador / Coordinador')))"
        )
        parametros.extend([user_id] * 5)
    citas = consultar(
        "SELECT DISTINCT c.id,c.creado_por FROM citas c "
        "JOIN estudiantes e ON e.id_estudiante=c.id_estudiante "
        "LEFT JOIN acudientes a ON a.id_acudiente=c.id_acudiente "
        "LEFT JOIN docentes d ON d.id_docente=c.id_docente "
        "JOIN estados_cita ec ON ec.id=c.id_estado WHERE " + " AND ".join(filtros) + " ORDER BY c.fecha,c.hora",
        tuple(parametros),
    )
    resumen = {"citas": len(citas), "fallidas": 0}
    for cita in citas:
        resultados = sincronizar_cita(cita["id"], cita["creado_por"])
        if any(resultado["estado"] == "Fallido" for resultado in resultados):
            resumen["fallidas"] += 1
    return resumen


def _actualizar_evento_google(url: str, event: dict, access_token: str) -> None:
    request = Request(
        url,
        data=json.dumps(event).encode("utf-8"),
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        method="PATCH",
    )
    try:
        with urlopen(request, timeout=12) as response:
            response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError("No se pudo actualizar el evento duplicado en Google Calendar.") from exc