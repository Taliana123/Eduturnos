from __future__ import annotations

from datetime import date, datetime, time, timedelta
from email.message import EmailMessage
from pathlib import Path
import os
import smtplib
import sys

import mysql.connector
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")
from servicios.reuniones import formatear_hora

LOCK_FILE = BASE_DIR / "tools" / "recordatorios.lock"
LOG_FILE = BASE_DIR / "tools" / "recordatorios.log"


def _env(name, default=""):
    value = os.getenv(name)
    return default if value is None else value.strip()


def _env_int(name, default):
    try:
        return int(_env(name, str(default)))
    except (TypeError, ValueError):
        return default


DB_CONFIG = {
    "host": _env("MYSQL_HOST", _env("MYSQLHOST", "127.0.0.1")),
    "port": _env_int("MYSQL_PORT", _env_int("MYSQLPORT", 3306)),
    "user": _env("MYSQL_USER", _env("MYSQLUSER", "root")),
    "password": _env("MYSQL_PASSWORD", _env("MYSQLPASSWORD", "")),
    "database": _env("MYSQL_DATABASE", _env("MYSQLDATABASE", "eduturnos")),
    "connection_timeout": 10,
}

REMINDER_WINDOW_MINUTES = max(1, _env_int("REMINDER_WINDOW_MINUTES", 10))

MAIL_HOST = _env("MAIL_HOST", _env("SMTP_HOST", ""))
MAIL_PORT = _env_int("MAIL_PORT", _env_int("SMTP_PORT", 587))
MAIL_USERNAME = _env("MAIL_USERNAME", _env("SMTP_USER", ""))
MAIL_PASSWORD = _env("MAIL_PASSWORD", _env("SMTP_PASSWORD", ""))
MAIL_FROM = _env("MAIL_FROM", MAIL_USERNAME)
MAIL_USE_TLS = _env("MAIL_USE_TLS", _env("SMTP_TLS", "1")) == "1"
MAIL_USE_SSL = _env("MAIL_USE_SSL", "1" if MAIL_PORT == 465 else "0") == "1"
_LOCK_HANDLE = None


def escribir_log(mensaje):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as archivo:
            archivo.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {mensaje}\n")
    except Exception:
        pass


def obtener_bloqueo():
    global _LOCK_HANDLE
    handle = None
    try:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        handle = open(LOCK_FILE, "a+", encoding="utf-8")
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(" ")
            handle.flush()
        handle.seek(0)

        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        handle.seek(0)
        handle.truncate()
        handle.write(str(os.getpid()))
        handle.flush()
        _LOCK_HANDLE = handle
        return True
    except Exception as exc:
        if handle:
            handle.close()
        escribir_log(f"No se pudo crear bloqueo: {exc}")
        return False


def liberar_bloqueo():
    global _LOCK_HANDLE
    handle = _LOCK_HANDLE
    _LOCK_HANDLE = None
    if not handle:
        return
    try:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except Exception as exc:
        escribir_log(f"No se pudo liberar bloqueo: {exc}")
    finally:
        handle.close()


def conexion():
    return mysql.connector.connect(**DB_CONFIG)


def consultar(sql, params=()):
    cnx = conexion()
    cur = cnx.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        cnx.close()


def convertir_fecha_hora(fecha, hora):
    if fecha is None or hora is None:
        return None
    if isinstance(fecha, datetime):
        fecha_obj = fecha.date()
    elif isinstance(fecha, date):
        fecha_obj = fecha
    else:
        try:
            fecha_obj = datetime.strptime(str(fecha)[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    if isinstance(hora, time):
        hora_obj = hora
    elif isinstance(hora, timedelta):
        total = int(hora.total_seconds())
        hora_obj = time((total // 3600) % 24, (total % 3600) // 60, total % 60)
    else:
        texto = str(hora).strip()
        hora_obj = None
        for formato in ("%H:%M:%S", "%H:%M"):
            try:
                hora_obj = datetime.strptime(texto, formato).time()
                break
            except ValueError:
                continue
        if hora_obj is None:
            return None
    return datetime.combine(fecha_obj, hora_obj)


# Alias conservado para pruebas y compatibilidad con scripts anteriores.
def _cita_datetime(fecha, hora):
    return convertir_fecha_hora(fecha, hora)


def obtener_usuarios_cita(cita):
    usuarios = set()
    for campo in ("estudiante_usuario", "acudiente_usuario", "docente_usuario", "creador_usuario"):
        if cita.get(campo):
            usuarios.add(int(cita[campo]))

    filas = consultar("""
        SELECT u.id_usuario
        FROM usuarios u
        INNER JOIN roles r ON r.id = u.id_rol
        WHERE u.estado = 1
          AND r.nombre IN ('Rector', 'Administrador / Coordinador')
    """)
    usuarios.update(int(f["id_usuario"]) for f in filas if f.get("id_usuario"))
    return usuarios


def correos_usuarios(ids):
    ids = sorted({int(x) for x in ids})
    if not ids:
        return {}
    placeholders = ",".join(["%s"] * len(ids))
    filas = consultar(
        f"SELECT id_usuario, correo FROM usuarios WHERE estado=1 AND id_usuario IN ({placeholders})",
        tuple(ids),
    )
    return {int(fila["id_usuario"]): (fila.get("correo") or "").strip() for fila in filas}


def crear_notificacion(cursor, id_usuario, titulo, mensaje, tipo):
    cursor.execute(
        """
        INSERT INTO notificaciones (id_usuario, titulo, mensaje, tipo, leida)
        VALUES (%s, %s, %s, %s, 0)
        """,
        (id_usuario, titulo, mensaje, tipo),
    )


def obtener_citas():
    return consultar("""
        SELECT
            c.id, c.id_estudiante, c.id_acudiente, c.id_docente,
            c.fecha, c.hora, c.lugar, c.observaciones,
            c.recordatorio_24h_enviado, c.recordatorio_2h_enviado,
            e.nombres AS estudiante_nombres,
            e.apellidos AS estudiante_apellidos,
            e.id_usuario AS estudiante_usuario,
            a.id_usuario AS acudiente_usuario,
            d.id_usuario AS docente_usuario,
            c.creado_por AS creador_usuario,
            m.nombre AS motivo,
            ec.nombre AS estado
        FROM citas c
        INNER JOIN estudiantes e ON e.id_estudiante = c.id_estudiante
        LEFT JOIN acudientes a ON a.id_acudiente = c.id_acudiente
        INNER JOIN docentes d ON d.id_docente = c.id_docente
        INNER JOIN motivos m ON m.id = c.id_motivo
        INNER JOIN estados_cita ec ON ec.id = c.id_estado
        WHERE ec.nombre IN ('Pendiente', 'Confirmada', 'Reprogramada')
        ORDER BY c.fecha ASC, c.hora ASC
    """)


def _configuracion_smtp_disponible():
    return bool(MAIL_HOST and MAIL_USERNAME and MAIL_PASSWORD and MAIL_FROM)


def _enviar_un_correo(destinatario, titulo, mensaje):
    msg = EmailMessage()
    msg["Subject"] = titulo
    msg["From"] = MAIL_FROM
    msg["To"] = destinatario
    msg.set_content(f"EDUTURNOS\n\n{mensaje}\n")
    if MAIL_USE_SSL:
        with smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT, timeout=20) as smtp:
            smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(MAIL_HOST, MAIL_PORT, timeout=20) as smtp:
            smtp.ehlo()
            if MAIL_USE_TLS:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
            smtp.send_message(msg)


def _actualizar_entrega_correo(cita_id, usuario_id, tipo, estado, error=None, intento=False):
    cnx = conexion()
    cursor = cnx.cursor()
    try:
        cursor.execute(
            "UPDATE entregas_correo SET estado=%s, intentos=intentos+%s, ultimo_error=%s "
            "WHERE id_cita=%s AND id_usuario=%s AND tipo=%s",
            (estado, int(intento), (str(error)[:150] if error else None), cita_id, usuario_id, tipo),
        )
        cnx.commit()
    except Exception:
        cnx.rollback()
        raise
    finally:
        cursor.close()
        cnx.close()


def enviar_emails_recordatorio(cita_id=None, tipo=None, titulo=None, mensaje=None):
    if not _configuracion_smtp_disponible():
        return 0

    filtros = [
        "e.estado IN ('Pendiente','Fallido')",
        "e.intentos < 3",
        "e.tipo IN ('Recordatorio24h','Recordatorio2h')",
    ]
    params = []
    if cita_id is not None:
        filtros.append("e.id_cita=%s")
        params.append(cita_id)
    if tipo is not None:
        filtros.append("e.tipo=%s")
        params.append(tipo)
    entregas = consultar(
        "SELECT e.id_cita,e.id_usuario,e.tipo,e.intentos,u.correo,"
        "c.fecha,c.hora,c.lugar,CONCAT(es.nombres,' ',es.apellidos) estudiante "
        "FROM entregas_correo e JOIN usuarios u ON u.id_usuario=e.id_usuario "
        "JOIN citas c ON c.id=e.id_cita JOIN estudiantes es ON es.id_estudiante=c.id_estudiante "
        f"WHERE {' AND '.join(filtros)} ORDER BY e.fecha_actualizacion,e.id LIMIT 100",
        tuple(params),
    )
    enviados = 0
    for entrega in entregas:
        correo = (entrega.get("correo") or "").strip()
        if not correo:
            try:
                _actualizar_entrega_correo(entrega["id_cita"], entrega["id_usuario"], entrega["tipo"], "Sin correo")
            except Exception as exc:
                escribir_log(f"No se pudo actualizar entrega de correo para cita {entrega['id_cita']}: {exc}")
            continue
        fecha_hora = convertir_fecha_hora(entrega["fecha"], entrega["hora"])
        if titulo is not None and mensaje is not None:
            asunto, contenido = titulo, mensaje
        elif fecha_hora and entrega["tipo"] == "Recordatorio24h":
            asunto = "Recordatorio de citación · 24 horas"
            contenido = f"La citación del estudiante {entrega['estudiante']} es mañana {fecha_hora:%d/%m/%Y} a las {formatear_hora(fecha_hora)}. Lugar: {entrega.get('lugar') or 'Lugar no especificado'}."
        elif fecha_hora:
            asunto = "Recordatorio de citación · 2 horas"
            contenido = f"La citación del estudiante {entrega['estudiante']} es hoy {fecha_hora:%d/%m/%Y} a las {formatear_hora(fecha_hora)}. Lugar: {entrega.get('lugar') or 'Lugar no especificado'}."
        else:
            _actualizar_entrega_correo(entrega["id_cita"], entrega["id_usuario"], entrega["tipo"], "Fallido", "Fecha u hora no válida", intento=True)
            continue
        try:
            _enviar_un_correo(correo, asunto, contenido)
            _actualizar_entrega_correo(entrega["id_cita"], entrega["id_usuario"], entrega["tipo"], "Enviado", intento=True)
            enviados += 1
        except Exception as exc:
            _actualizar_entrega_correo(entrega["id_cita"], entrega["id_usuario"], entrega["tipo"], "Fallido", type(exc).__name__, intento=True)
            escribir_log(f"Falló la entrega de correo para cita {entrega['id_cita']} usuario {entrega['id_usuario']} ({entrega['tipo']}).")
    return enviados


def procesar_recordatorio(cita, tipo_recordatorio, titulo, mensaje):
    campo = "recordatorio_24h_enviado" if tipo_recordatorio == "24h" else "recordatorio_2h_enviado"
    cnx = conexion()
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute(
            f"SELECT id, {campo} FROM citas WHERE id=%s FOR UPDATE",
            (cita["id"],),
        )
        fila = cursor.fetchone()
        if not fila or fila[campo]:
            cnx.rollback()
            return 0, 0

        usuarios = obtener_usuarios_cita(cita)
        if not usuarios:
            cnx.rollback()
            return 0, 0

        correos = correos_usuarios(usuarios)

        # Notificación interna: es el canal principal y transaccional.
        for id_usuario in usuarios:
            crear_notificacion(cursor, id_usuario, titulo, mensaje, f"Recordatorio {tipo_recordatorio}")
            tipo_entrega = "Recordatorio24h" if tipo_recordatorio == "24h" else "Recordatorio2h"
            estado_correo = "Pendiente" if correos.get(id_usuario) else "Sin correo"
            cursor.execute(
                "INSERT INTO entregas_correo(id_cita,id_usuario,tipo,estado,intentos) "
                "VALUES(%s,%s,%s,%s,0) ON DUPLICATE KEY UPDATE "
                "estado=IF(estado='Enviado','Enviado',VALUES(estado)), "
                "intentos=IF(estado='Enviado',intentos,0), "
                "ultimo_error=IF(estado='Enviado',ultimo_error,NULL)",
                (cita["id"], id_usuario, tipo_entrega, estado_correo),
            )
        cursor.execute(f"UPDATE citas SET {campo}=1 WHERE id=%s", (cita["id"],))
        cnx.commit()

        # SMTP es adicional; las entregas pendientes/fallidas se reintentan en la tarea siguiente.
        tipo_entrega = "Recordatorio24h" if tipo_recordatorio == "24h" else "Recordatorio2h"
        enviados_email = enviar_emails_recordatorio(cita["id"], tipo_entrega, titulo, mensaje)
        escribir_log(
            f"Recordatorio {tipo_recordatorio} cita {cita['id']}: "
            f"{len(usuarios)} notificación(es), {enviados_email} correo(s)."
        )
        return 1, enviados_email
    except Exception:
        cnx.rollback()
        raise
    finally:
        cursor.close()
        cnx.close()


def procesar_recordatorios():
    ahora = datetime.now()
    enviados_24h = enviados_2h = correos = 0
    try:
        correos += enviar_emails_recordatorio()
    except Exception as exc:
        escribir_log(f"No se pudieron reintentar entregas de correo: {type(exc).__name__}")
    ventana = timedelta(minutes=REMINDER_WINDOW_MINUTES)

    for cita in obtener_citas():
        fecha_hora_cita = convertir_fecha_hora(cita["fecha"], cita["hora"])
        if not fecha_hora_cita:
            escribir_log(f"Cita {cita['id']} ignorada: fecha/hora inválida.")
            continue

        estudiante = f"{cita.get('estudiante_nombres','')} {cita.get('estudiante_apellidos','')}".strip()
        fecha_texto = fecha_hora_cita.strftime("%d/%m/%Y")
        hora_texto = formatear_hora(fecha_hora_cita)
        lugar = cita.get("lugar") or "Lugar no especificado"

        objetivo_24 = fecha_hora_cita - timedelta(hours=24)
        objetivo_2 = fecha_hora_cita - timedelta(hours=2)
        mensaje_24 = f"La citación del estudiante {estudiante} es mañana {fecha_texto} a las {hora_texto}. Lugar: {lugar}."
        mensaje_2 = f"La citación del estudiante {estudiante} es hoy {fecha_texto} a las {hora_texto}. Lugar: {lugar}."

        if not cita["recordatorio_24h_enviado"] and abs(ahora - objetivo_24) <= ventana:
            n, e = procesar_recordatorio(cita, "24h", "Recordatorio de citación · 24 horas", mensaje_24)
            enviados_24h += n; correos += e

        if not cita["recordatorio_2h_enviado"] and abs(ahora - objetivo_2) <= ventana:
            n, e = procesar_recordatorio(cita, "2h", "Recordatorio de citación · 2 horas", mensaje_2)
            enviados_2h += n; correos += e

    print("==========================================")
    print(" EDUTURNOS - Recordatorios")
    print("==========================================")
    print(f"Recordatorios 24h procesados: {enviados_24h}")
    print(f"Recordatorios 2h procesados: {enviados_2h}")
    print(f"Correos enviados: {correos}")
    print("Proceso terminado correctamente.")
    print("==========================================")


if __name__ == "__main__":
    if not obtener_bloqueo():
        print("Ya existe otro proceso de recordatorios ejecutándose.")
        sys.exit(0)
    try:
        procesar_recordatorios()
    except Exception as exc:
        escribir_log(f"ERROR GENERAL: {exc}")
        print(f"ERROR AL PROCESAR RECORDATORIOS: {exc}")
        sys.exit(1)
    finally:
        liberar_bloqueo()
