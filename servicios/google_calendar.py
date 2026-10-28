from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, time as datetime_time, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen

from cryptography.fernet import Fernet, InvalidToken
from flask import after_this_request, current_app, has_request_context, request, url_for

from database.db import consultar, ejecutar, transaccion

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API_BASE = "https://www.googleapis.com/calendar/v3"
SCOPES = "openid email https://www.googleapis.com/auth/calendar.events"
MAX_SYNC_ATTEMPTS = 12


class GoogleCalendarError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status
        self.retryable = status is None or status == 429 or status >= 500


def configuracion_lista() -> bool:
    return apps_script_configurada() or configuracion_oauth_lista()


def configuracion_oauth_lista() -> bool:
    origen = current_app.config.get("APP_ORIGIN", "").strip()
    try:
        parsed_origin = urlsplit(origen)
    except ValueError:
        return False
    return bool(
        current_app.config.get("GOOGLE_OAUTH_CLIENT_ID")
        and current_app.config.get("GOOGLE_OAUTH_CLIENT_SECRET")
        and parsed_origin.scheme == "https"
        and parsed_origin.hostname
        and not parsed_origin.username
        and not parsed_origin.password
    )


def apps_script_configurada() -> bool:
    url = (current_app.config.get("GOOGLE_APPS_SCRIPT_URL") or "").strip()
    secret = current_app.config.get("GOOGLE_APPS_SCRIPT_SECRET") or ""
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.hostname == "script.google.com"
        and parsed.path.startswith("/macros/s/")
        and parsed.path.endswith("/exec")
        and len(secret) >= 32
    )


def probar_apps_script() -> None:
    respuesta = _solicitud_apps_script({"action": "test"})
    if not respuesta.get("ok"):
        raise GoogleCalendarError("El puente no pudo acceder al calendario institucional.")
    if respuesta.get("protocol") != "payload-json-v2":
        raise GoogleCalendarError(
            "Actualiza y vuelve a implementar EDUTURNOSCalendar.gs en Apps Script para corregir la verificación de firma."
        )


def _canonical_json(value: dict) -> str:
    # ASCII escapes make the signed bytes identical across Python, Apps Script,
    # and Google Apps Script's UTF-16 string runtime, including unusual place names.
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _solicitud_apps_script(payload: dict) -> dict:
    if not apps_script_configurada():
        raise GoogleCalendarError("El puente institucional de Google Calendar no está configurado.", 400)
    timestamp = str(int(time.time()))
    nonce = uuid.uuid4().hex
    payload_json = _canonical_json(payload)
    message = f"{timestamp}\n{nonce}\n{payload_json}".encode("utf-8")
    digest = hmac.new(
        current_app.config["GOOGLE_APPS_SCRIPT_SECRET"].encode("utf-8"),
        message,
        hashlib.sha256,
    ).digest()
    signature = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    envelope = {
        "timestamp": timestamp,
        "nonce": nonce,
        "payload": payload,
        "payload_json": payload_json,
        "signature": signature,
    }
    request = Request(
        current_app.config["GOOGLE_APPS_SCRIPT_URL"].strip(),
        data=json.dumps(envelope, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 401:
            raise GoogleCalendarError(
                "Google Apps Script requiere acceso anónimo. En la implementación web selecciona Ejecutar como: yo y Acceso: Cualquier persona, y vuelve a implementar.",
                exc.code,
            ) from exc
        raise GoogleCalendarError(f"El puente respondió HTTP {exc.code}.", exc.code) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise GoogleCalendarError("No se pudo contactar el puente de Google Calendar.") from exc
    if not isinstance(result, dict):
        raise GoogleCalendarError("El puente devolvió una respuesta no válida.")
    if not result.get("ok"):
        raise GoogleCalendarError(
            str(result.get("error") or "El puente rechazó la operación.")[:180],
            int(result.get("status") or 503),
        )
    return result


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


def _solicitud_json(
    url: str,
    data: dict,
    access_token: str | None = None,
    method: str = "POST",
) -> dict:
    headers = {"Content-Type": "application/json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    request = Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=12) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise GoogleCalendarError(f"Google respondió HTTP {exc.code}.", exc.code) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise GoogleCalendarError("No se pudo completar la solicitud con Google.") from exc


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
        raise GoogleCalendarError("Google no pudo completar la autorización.") from exc
    if not token.get("access_token") or not token.get("refresh_token"):
        raise GoogleCalendarError(
            "Google no entregó credenciales renovables; vuelve a autorizar y acepta el acceso solicitado."
        )
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
        email = (data.get("email") or "").strip()[:180]
        if not email:
            raise GoogleCalendarError("Google no devolvió el correo autorizado.")
        return email
    except HTTPError as exc:
        raise GoogleCalendarError(
            f"No se pudo verificar la cuenta Google (HTTP {exc.code}).",
            exc.code,
        ) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise GoogleCalendarError("No se pudo verificar la cuenta Google.") from exc


def calendar_id_objetivo(scope_key: str) -> str:
    calendar_id = (
        (current_app.config.get("GOOGLE_CALENDAR_ID") or "primary").strip()
        if scope_key == "institucional"
        else "primary"
    )
    if not calendar_id or len(calendar_id) > 255:
        raise ValueError("El identificador del calendario de Google no es válido.")
    return calendar_id


def probar_conexion_calendario(access_token: str, calendar_id: str) -> None:
    url = (
        f"{API_BASE}/calendars/{quote(calendar_id, safe='')}/events"
        "?maxResults=1"
    )
    request = Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    try:
        with urlopen(request, timeout=12) as response:
            response.read()
    except HTTPError as exc:
        raise GoogleCalendarError(
            f"Google rechazó el acceso al calendario (HTTP {exc.code}).",
            exc.code,
        ) from exc
    except (URLError, TimeoutError) as exc:
        raise GoogleCalendarError("No se pudo comprobar el acceso al calendario de Google.") from exc


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
        raise GoogleCalendarError(
            "No se pudieron descifrar las credenciales de Google; vuelve a conectar la cuenta."
        ) from exc


def guardar_conexion(scope_key: str, tipo: str, user_id: int | None, email: str, token: dict) -> None:
    calendar_id = calendar_id_objetivo(scope_key)
    ejecutar(
        "INSERT INTO integraciones_google(scope_key,tipo,id_usuario,correo_google,calendar_id,token_cifrado,fecha_prueba) "
        "VALUES(%s,%s,%s,%s,%s,%s,NOW()) ON DUPLICATE KEY UPDATE tipo=VALUES(tipo),"
        "id_usuario=VALUES(id_usuario),correo_google=VALUES(correo_google),calendar_id=VALUES(calendar_id),"
        "token_cifrado=VALUES(token_cifrado),fecha_prueba=NOW(),fecha_actualizacion=NOW()",
        (scope_key, tipo, user_id, email or None, calendar_id, cifrar_token(token)),
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
    except HTTPError as exc:
        raise GoogleCalendarError(
            f"Google respondió HTTP {exc.code} al renovar la autorización.",
            exc.code,
        ) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise GoogleCalendarError("No se pudo renovar la autorización de Google.") from exc
    token["access_token"] = refresh["access_token"]
    token["expires_at"] = time.time() + int(refresh.get("expires_in", 3600))
    if refresh.get("refresh_token"):
        token["refresh_token"] = refresh["refresh_token"]
    ejecutar("UPDATE integraciones_google SET token_cifrado=%s WHERE scope_key=%s", (cifrar_token(token), connection["scope_key"]))
    return token


def _conexiones_para_cita(cita_id: int, creador_id: int) -> list[dict]:
    conexiones = consultar(
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
    if apps_script_configurada():
        # El puente representa una única agenda institucional, sin guardar tokens OAuth.
        if not configuracion_oauth_lista():
            conexiones = []
        else:
            conexiones = [item for item in conexiones if item.get("scope_key") != "institucional"]
        conexiones.append({
            "scope_key": "institucional",
            "calendar_id": calendar_id_objetivo("institucional"),
            "apps_script": True,
        })
    return conexiones


def _normalizar_hora_cita(hora):
    if isinstance(hora, datetime_time):
        return hora
    if isinstance(hora, timedelta):
        total = int(hora.total_seconds())
        return datetime_time((total // 3600) % 24, (total % 3600) // 60, total % 60)
    raise TypeError("La hora de la cita no tiene un formato compatible.")


def _event_id(cita_id: int, scope_key: str) -> str:
    digest = hashlib.sha256(f"{scope_key}:{cita_id}".encode()).hexdigest()
    return "eduturnos" + digest


def _programar_sincronizacion_inmediata() -> None:
    if not apps_script_configurada() or not has_request_context():
        return
    if request.environ.get("eduturnos_google_sync_scheduled"):
        return
    request.environ["eduturnos_google_sync_scheduled"] = True
    app = current_app._get_current_object()

    @after_this_request
    def iniciar_worker(response):
        try:
            with app.app_context():
                resultado = procesar_cola_google(limite=20)
            app.logger.info(
                "Sincronización inmediata de Google Calendar: %s procesadas, %s correctas, %s fallidas.",
                resultado["procesadas"],
                resultado["sincronizadas"],
                resultado["fallidas"],
            )
        except Exception:
            app.logger.exception("No se pudo completar la sincronización inmediata con Google Calendar")
        return response


def _encolar_scope_cursor(cursor, cita_id: int, scope_key: str, operacion: str) -> None:
    cursor.execute(
        "SELECT google_event_id FROM eventos_google WHERE id_cita=%s AND scope_key=%s",
        (cita_id, scope_key),
    )
    previo = cursor.fetchone()
    event_id = (
        previo["google_event_id"]
        if previo and previo.get("google_event_id")
        else _event_id(cita_id, scope_key)
    )
    cursor.execute(
        "INSERT INTO google_calendar_sync_queue "
        "(id_cita,scope_key,google_event_id,operacion,estado,intentos,proximo_intento) "
        "VALUES(%s,%s,%s,%s,'Pendiente',0,NOW()) "
        "ON DUPLICATE KEY UPDATE google_event_id=VALUES(google_event_id),"
        "operacion=VALUES(operacion),estado='Pendiente',intentos=0,"
        "ultimo_intento=NULL,proximo_intento=NOW(),ultimo_error=NULL,"
        "claim_token=NULL,lease_until=NULL",
        (cita_id, scope_key, event_id, operacion),
    )


def encolar_cita_cursor(cursor, cita_id: int, creador_id: int, operacion: str = "upsert") -> int:
    if operacion not in {"upsert", "delete"}:
        raise ValueError("La operación de sincronización no es válida.")
    cursor.execute(
        "SELECT DISTINCT i.scope_key FROM integraciones_google i "
        "LEFT JOIN citas c ON c.id=%s "
        "LEFT JOIN estudiantes e ON e.id_estudiante=c.id_estudiante "
        "LEFT JOIN acudientes a ON a.id_acudiente=c.id_acudiente "
        "LEFT JOIN docentes d ON d.id_docente=c.id_docente "
        "LEFT JOIN usuarios u ON u.id_usuario=i.id_usuario "
        "LEFT JOIN roles r ON r.id=u.id_rol "
        "WHERE i.scope_key='institucional' OR (u.estado=1 AND (i.id_usuario=%s "
        "OR i.id_usuario IN (c.creado_por,e.id_usuario,a.id_usuario,d.id_usuario) "
        "OR r.nombre IN ('Super Admin','Rector','Administrador / Coordinador')))",
        (cita_id, creador_id),
    )
    scopes = cursor.fetchall()
    if apps_script_configurada():
        if configuracion_oauth_lista():
            scopes = [row for row in scopes if row["scope_key"] != "institucional"]
        else:
            scopes = []
    if apps_script_configurada() and not any(row["scope_key"] == "institucional" for row in scopes):
        scopes.append({"scope_key": "institucional"})
    for row in scopes:
        _encolar_scope_cursor(cursor, cita_id, row["scope_key"], operacion)
    if scopes:
        _programar_sincronizacion_inmediata()
    return len(scopes)


def encolar_cita(cita_id: int, creador_id: int, operacion: str = "upsert") -> int:
    if operacion not in {"upsert", "delete"}:
        raise ValueError("La operación de sincronización no es válida.")
    conexiones = _conexiones_para_cita(cita_id, creador_id)
    cantidad = 0
    for conexion in conexiones:
        previo = consultar(
            "SELECT google_event_id FROM eventos_google WHERE id_cita=%s AND scope_key=%s",
            (cita_id, conexion["scope_key"]),
            uno=True,
        )
        ejecutar(
            "INSERT INTO google_calendar_sync_queue "
            "(id_cita,scope_key,google_event_id,operacion,estado,intentos,proximo_intento) "
            "VALUES(%s,%s,%s,%s,'Pendiente',0,NOW()) "
            "ON DUPLICATE KEY UPDATE google_event_id=VALUES(google_event_id),"
            "operacion=VALUES(operacion),estado='Pendiente',intentos=0,"
            "ultimo_intento=NULL,proximo_intento=NOW(),ultimo_error=NULL,"
            "claim_token=NULL,lease_until=NULL",
            (
                cita_id,
                conexion["scope_key"],
                (
                    previo["google_event_id"]
                    if previo and previo.get("google_event_id")
                    else _event_id(cita_id, conexion["scope_key"])
                ),
                operacion,
            ),
        )
        cantidad += 1
    if cantidad:
        _programar_sincronizacion_inmediata()
    return cantidad


def encolar_citas_futuras(scope_key: str, user_id: int | None = None) -> dict:
    filtros = [
        "TIMESTAMP(c.fecha,c.hora)>=NOW()",
        "ec.nombre IN ('Pendiente','Confirmada','Reprogramada')",
    ]
    parametros = []
    if scope_key != "institucional":
        if user_id is None:
            return {"citas": 0, "encoladas": 0}
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
        "JOIN estados_cita ec ON ec.id=c.id_estado WHERE " + " AND ".join(filtros)
        + " ORDER BY c.fecha,c.hora",
        tuple(parametros),
    )
    encoladas = 0
    for cita in citas:
        encoladas += encolar_cita(cita["id"], cita["creado_por"])
    return {"citas": len(citas), "encoladas": encoladas}


def sincronizar_cita(
    cita_id: int,
    creador_id: int,
    scope_key: str | None = None,
) -> list[dict]:
    if not configuracion_lista():
        return []
    cita = consultar(
        "SELECT c.id,c.fecha,c.hora,c.lugar,c.creado_por,s.direccion sede "
        "FROM citas c JOIN estudiantes e ON e.id_estudiante=c.id_estudiante "
        "LEFT JOIN sedes s ON s.id=e.id_sede WHERE c.id=%s",
        (cita_id,), uno=True,
    )
    if not cita:
        return []
    conexiones = _conexiones_para_cita(cita_id, creador_id)
    if scope_key is not None:
        conexiones = [item for item in conexiones if item["scope_key"] == scope_key]
    if not conexiones:
        return []
    inicio = datetime.combine(cita["fecha"], _normalizar_hora_cita(cita["hora"]), tzinfo=timezone(timedelta(hours=-5)))
    fin = inicio + timedelta(minutes=30)
    resultado = []
    for conexion in conexiones:
        scope = conexion["scope_key"]
        event_id = _event_id(cita_id, scope)
        try:
            previo = consultar(
                "SELECT google_event_id,estado FROM eventos_google WHERE id_cita=%s AND scope_key=%s",
                (cita_id, scope),
                uno=True,
            )
            if previo and previo.get("google_event_id"):
                event_id = previo["google_event_id"]
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
            events_url = f"{API_BASE}/calendars/{quote(conexion['calendar_id'], safe='')}/events"
            event_url = f"{events_url}/{quote(event_id, safe='')}?sendUpdates=none"
            if previo and previo.get("estado") != "Cancelado":
                try:
                    _actualizar_evento_google(event_url, event, token["access_token"])
                except RuntimeError as exc:
                    if "HTTP 404" not in str(exc):
                        raise
                    _solicitud_json(f"{events_url}?sendUpdates=none", event, token["access_token"])
            else:
                try:
                    _solicitud_json(f"{events_url}?sendUpdates=none", event, token["access_token"])
                except RuntimeError as exc:
                    if "HTTP 409" not in str(exc):
                        raise
                    _actualizar_evento_google(event_url, event, token["access_token"])
            ejecutar(
                "INSERT INTO eventos_google(id_cita,scope_key,google_event_id,estado,ultimo_error) "
                "VALUES(%s,%s,%s,'Sincronizado',NULL) ON DUPLICATE KEY UPDATE google_event_id=VALUES(google_event_id),estado='Sincronizado',ultimo_error=NULL",
                (cita_id, scope, event_id),
            )
            resultado.append({"scope": scope, "estado": "Sincronizado"})
        except Exception as exc:
            error = error_google_seguro(exc)
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


def _tomar_tarea_google():
    with transaccion() as cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM google_calendar_sync_queue "
                "WHERE (estado IN ('Pendiente','Reintentar') "
                "AND (proximo_intento IS NULL OR proximo_intento<=NOW())) "
                "OR (estado='Procesando' AND lease_until<=NOW()) "
                "ORDER BY COALESCE(proximo_intento,fecha_creacion),id LIMIT 1 FOR UPDATE"
            )
            tarea = cursor.fetchone()
            if not tarea:
                return None
            claim_token = str(uuid.uuid4())
            cursor.execute(
                "UPDATE google_calendar_sync_queue SET estado='Procesando',"
                "intentos=intentos+1,ultimo_intento=NOW(),claim_token=%s,"
                "lease_until=DATE_ADD(NOW(),INTERVAL 5 MINUTE) WHERE id=%s",
                (claim_token, tarea["id"]),
            )
            tarea["claim_token"] = claim_token
            tarea["intentos"] = int(tarea["intentos"]) + 1
            return tarea
        finally:
            cursor.close()


def _eliminar_evento_google(calendar_id: str, event_id: str, access_token: str) -> None:
    url = (
        f"{API_BASE}/calendars/{quote(calendar_id, safe='')}/events/"
        f"{quote(event_id, safe='')}?sendUpdates=none"
    )
    request = Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        method="DELETE",
    )
    try:
        with urlopen(request, timeout=12) as response:
            response.read()
    except HTTPError as exc:
        if exc.code == 404:
            return
        raise GoogleCalendarError(
            f"Google respondió HTTP {exc.code} al cancelar el evento.",
            exc.code,
        ) from exc
    except (URLError, TimeoutError) as exc:
        raise GoogleCalendarError("No se pudo completar la cancelación en Google.") from exc


def _procesar_tarea_apps_script(tarea: dict) -> None:
    cita = consultar(
        "SELECT c.id,c.fecha,c.hora,c.lugar,c.creado_por,ec.nombre estado,s.direccion sede "
        "FROM citas c JOIN estados_cita ec ON ec.id=c.id_estado "
        "LEFT JOIN estudiantes e ON e.id_estudiante=c.id_estudiante "
        "LEFT JOIN sedes s ON s.id=e.id_sede WHERE c.id=%s",
        (tarea["id_cita"],),
        uno=True,
    )
    operacion = tarea["operacion"]
    if not cita or cita.get("estado") == "Cancelada":
        operacion = "delete"
    event_id = tarea.get("google_event_id") or _event_id(tarea["id_cita"], tarea["scope_key"])
    payload = {
        "action": operacion,
        "external_id": _event_id(tarea["id_cita"], tarea["scope_key"]),
        "google_event_id": event_id,
    }
    if cita:
        inicio = datetime.combine(
            cita["fecha"],
            _normalizar_hora_cita(cita["hora"]),
            tzinfo=timezone(timedelta(hours=-5)),
        )
        payload.update({
            "start": inicio.isoformat(),
        })
    if operacion == "upsert":
        payload.update({
            "title": "Citación escolar",
            "description": "Consulta los detalles de la cita en EDUTURNOS.",
            "location": cita.get("lugar") or cita.get("sede") or "Ibagué, Tolima",
            "end": (inicio + timedelta(minutes=30)).isoformat(),
        })
    respuesta = _solicitud_apps_script(payload)
    if operacion == "delete":
        ejecutar(
            "INSERT INTO eventos_google(id_cita,scope_key,google_event_id,estado,ultimo_error) "
            "VALUES(%s,%s,%s,'Cancelado',NULL) ON DUPLICATE KEY UPDATE "
            "google_event_id=VALUES(google_event_id),estado='Cancelado',ultimo_error=NULL",
            (tarea["id_cita"], tarea["scope_key"], event_id),
        )
        return
    actual_id = str(respuesta.get("eventId") or event_id)[:100]
    ejecutar(
        "INSERT INTO eventos_google(id_cita,scope_key,google_event_id,estado,ultimo_error) "
        "VALUES(%s,%s,%s,'Sincronizado',NULL) ON DUPLICATE KEY UPDATE "
        "google_event_id=VALUES(google_event_id),estado='Sincronizado',ultimo_error=NULL",
        (tarea["id_cita"], tarea["scope_key"], actual_id),
    )


def _procesar_tarea_google(tarea: dict) -> None:
    if tarea["scope_key"] == "institucional" and apps_script_configurada():
        _procesar_tarea_apps_script(tarea)
        return
    conexion = consultar(
        "SELECT * FROM integraciones_google WHERE scope_key=%s",
        (tarea["scope_key"],),
        uno=True,
    )
    if not conexion:
        raise GoogleCalendarError(
            "La cuenta autorizada ya no está conectada; un administrador debe reconectarla.",
            403,
        )
    cita = consultar(
        "SELECT c.id,c.fecha,c.hora,c.lugar,c.creado_por,ec.nombre estado,s.direccion sede "
        "FROM citas c JOIN estados_cita ec ON ec.id=c.id_estado "
        "LEFT JOIN estudiantes e ON e.id_estudiante=c.id_estudiante "
        "LEFT JOIN sedes s ON s.id=e.id_sede WHERE c.id=%s",
        (tarea["id_cita"],),
        uno=True,
    )
    operacion = tarea["operacion"]
    if not cita or cita.get("estado") == "Cancelada":
        operacion = "delete"
    token = _renovar_token(conexion, descifrar_token(conexion["token_cifrado"]))
    event_id = tarea.get("google_event_id") or _event_id(tarea["id_cita"], tarea["scope_key"])
    if operacion == "delete":
        _eliminar_evento_google(
            conexion["calendar_id"],
            event_id,
            token["access_token"],
        )
        ejecutar(
            "UPDATE eventos_google SET estado='Cancelado',ultimo_error=NULL "
            "WHERE id_cita=%s AND scope_key=%s",
            (tarea["id_cita"], tarea["scope_key"]),
        )
        return
    if not cita:
        return
    resultados = sincronizar_cita(
        tarea["id_cita"],
        cita["creado_por"],
        scope_key=tarea["scope_key"],
    )
    if not any(
        resultado["estado"] == "Sincronizado"
        for resultado in resultados
    ):
        raise GoogleCalendarError("No se pudo sincronizar el evento con el calendario autorizado.")


def error_google_seguro(error: Exception) -> str:
    if isinstance(error, GoogleCalendarError):
        mensaje = str(error).strip()
    else:
        mensaje = f"Error interno de tipo {type(error).__name__}."
    if not mensaje:
        mensaje = "Error de sincronización."
    return mensaje[:180]


def _es_reintentable(error: Exception) -> bool:
    if isinstance(error, GoogleCalendarError):
        return error.retryable
    for status in (400, 401, 403, 404):
        if f"HTTP {status}" in str(error):
            return False
    return True


def procesar_cola_google(limite: int = 20) -> dict:
    procesadas = sincronizadas = fallidas = 0
    for _ in range(max(1, min(int(limite), 100))):
        tarea = _tomar_tarea_google()
        if not tarea:
            break
        procesadas += 1
        try:
            _procesar_tarea_google(tarea)
            ejecutar(
                "UPDATE google_calendar_sync_queue SET estado='Sincronizado',"
                "ultimo_error=NULL,proximo_intento=NULL,claim_token=NULL,lease_until=NULL "
                "WHERE id=%s AND claim_token=%s",
                (tarea["id"], tarea["claim_token"]),
            )
            sincronizadas += 1
        except Exception as exc:
            error = error_google_seguro(exc)
            retry = _es_reintentable(exc) and tarea["intentos"] < MAX_SYNC_ATTEMPTS
            demora = min(2 ** min(tarea["intentos"], 10), 1440)
            if retry:
                estado = "Reintentar"
                proximo_intento = f"DATE_ADD(NOW(),INTERVAL {demora} MINUTE)"
            else:
                estado = "Fallido"
                proximo_intento = "NULL"
            ejecutar(
                "UPDATE google_calendar_sync_queue SET estado=%s,ultimo_error=%s,"
                f"proximo_intento={proximo_intento},claim_token=NULL,lease_until=NULL "
                "WHERE id=%s AND claim_token=%s",
                (estado, error, tarea["id"], tarea["claim_token"]),
            )
            current_app.logger.warning(
                "Falló la sincronización de Google Calendar para la cita %s (%s): %s",
                tarea["id_cita"],
                tarea["scope_key"],
                error,
            )
            fallidas += 1
    return {
        "procesadas": procesadas,
        "sincronizadas": sincronizadas,
        "fallidas": fallidas,
    }


def estado_cola_google(scope_key: str) -> dict:
    resumen = consultar(
        "SELECT "
        "SUM(estado IN ('Pendiente','Procesando','Reintentar')) pendientes,"
        "SUM(estado='Fallido') fallidas,"
        "MAX(CASE WHEN estado='Sincronizado' THEN fecha_actualizacion END) ultima_correcta,"
        "(SELECT q2.ultimo_error FROM google_calendar_sync_queue q2 "
        "WHERE q2.scope_key=%s AND q2.estado='Fallido' "
        "ORDER BY q2.fecha_actualizacion DESC,q2.id DESC LIMIT 1) ultimo_error "
        "FROM google_calendar_sync_queue WHERE scope_key=%s",
        (scope_key, scope_key),
        uno=True,
    )
    return resumen or {
        "pendientes": 0,
        "fallidas": 0,
        "ultima_correcta": None,
        "ultimo_error": None,
    }


def reintentar_fallidas_google(scope_key: str) -> int:
    """Devuelve a la cola las tareas fallidas de un calendario conectado."""
    cantidad = consultar(
        "SELECT COUNT(*) cantidad FROM google_calendar_sync_queue "
        "WHERE scope_key=%s AND estado='Fallido'",
        (scope_key,),
        uno=True,
    )
    total = int((cantidad or {}).get("cantidad") or 0)
    if not total:
        return 0
    ejecutar(
        "UPDATE google_calendar_sync_queue SET estado='Pendiente',intentos=0,"
        "ultimo_intento=NULL,proximo_intento=NOW(),ultimo_error=NULL,"
        "claim_token=NULL,lease_until=NULL "
        "WHERE scope_key=%s AND estado='Fallido'",
        (scope_key,),
    )
    return total


def _actualizar_evento_google(url: str, event: dict, access_token: str) -> None:
    payload = {key: value for key, value in event.items() if key != "id"}
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        method="PATCH",
    )
    try:
        with urlopen(request, timeout=12) as response:
            response.read()
    except HTTPError as exc:
        raise GoogleCalendarError(
            f"Google respondió HTTP {exc.code} al actualizar el evento.",
            exc.code,
        ) from exc
    except (URLError, TimeoutError) as exc:
        raise GoogleCalendarError("No se pudo actualizar el evento en Google Calendar.") from exc
