from datetime import date, datetime, time, timedelta

from database.db import consultar, transaccion

PERSONAL = ("Super Admin", "Rector", "Administrador / Coordinador", "Docente")
HORARIOS_CITAS = tuple(range(7 * 60, 11 * 60 + 31, 30)) + tuple(range(13 * 60, 17 * 60 + 31, 30))


def validar_compromiso(descripcion, responsable, fecha_limite):
    descripcion = descripcion.strip()
    responsable = responsable.strip()
    if not descripcion or len(descripcion) > 2000:
        raise ValueError("El compromiso debe tener entre 1 y 2000 caracteres.")
    if not responsable or len(responsable) > 150:
        raise ValueError("Indica un responsable de hasta 150 caracteres.")
    limite = date.fromisoformat(fecha_limite)
    if limite < date.today():
        raise ValueError("La fecha límite no puede ser anterior a hoy.")
    return descripcion, responsable, limite


def minutos(hora):
    if isinstance(hora, timedelta):
        return int(hora.total_seconds() // 60)
    if isinstance(hora, str):
        hora = time.fromisoformat(hora)
    return hora.hour * 60 + hora.minute


def formatear_hora(hora):
    if hora is None or hora == "":
        return ""
    total = minutos(hora)
    horas, minuto = divmod(total, 60)
    return f"{horas % 12 or 12}:{minuto:02d} {'AM' if horas < 12 else 'PM'}"


def validar_disponibilidad(docente_id, fecha, hora):
    inicio = minutos(hora)
    if inicio not in HORARIOS_CITAS:
        raise ValueError("Selecciona una hora cada 30 minutos: de 7:00 a 11:30 AM o de 1:00 a 5:30 PM.")


def validar_franja(dia, inicio, fin):
    dia = int(dia)
    inicio = time.fromisoformat(inicio)
    fin = time.fromisoformat(fin)
    if dia not in range(7) or minutos(fin) - minutos(inicio) < 30:
        raise ValueError("La franja debe pertenecer a un día válido y durar al menos 30 minutos.")
    return dia, inicio, fin


def datos_escolares(citas, privado=False):
    datos = {cita["id"]: {"compromisos": [], "reprogramaciones": [], "cierre": None, "correos": [], "notas": []} for cita in citas}
    if not datos:
        return datos
    placeholders = ",".join(["%s"] * len(datos))
    ids = tuple(datos)
    for compromiso in consultar(f"SELECT * FROM compromisos_cita WHERE id_cita IN ({placeholders}) ORDER BY fecha_limite,id", ids):
        compromiso["vencido"] = compromiso["estado"] == "Pendiente" and compromiso["fecha_limite"] < date.today()
        datos[compromiso["id_cita"]]["compromisos"].append(compromiso)
    if privado:
        for nota in consultar(
            f"SELECT s.id_cita,s.estado_actual,s.asistencia,s.observaciones,s.fecha_seguimiento,"
            f"CONCAT(u.nombres,' ',u.apellidos) autor FROM seguimiento_citas s "
            f"JOIN usuarios u ON u.id_usuario=s.realizado_por "
            f"WHERE s.id_cita IN ({placeholders}) ORDER BY s.fecha_seguimiento DESC,s.id DESC",
            ids,
        ):
            datos[nota["id_cita"]]["notas"].append(nota)
        for cambio in consultar(f"SELECT r.*,CONCAT(u.nombres,' ',u.apellidos) autor FROM reprogramaciones_cita r JOIN usuarios u ON u.id_usuario=r.realizado_por WHERE r.id_cita IN ({placeholders}) ORDER BY r.fecha_cambio DESC,r.id DESC", ids):
            datos[cambio["id_cita"]]["reprogramaciones"].append(cambio)
        for cierre in consultar(f"SELECT r.*,CONCAT(u.nombres,' ',u.apellidos) autor FROM cierres_cita r JOIN usuarios u ON u.id_usuario=r.cerrado_por WHERE r.id_cita IN ({placeholders})", ids):
            datos[cierre["id_cita"]]["cierre"] = cierre
        for correo in consultar(f"SELECT e.*,CONCAT(u.nombres,' ',u.apellidos) destinatario FROM entregas_correo e JOIN usuarios u ON u.id_usuario=e.id_usuario WHERE e.id_cita IN ({placeholders}) ORDER BY e.fecha_actualizacion DESC", ids):
            datos[correo["id_cita"]]["correos"].append(correo)
    return datos


def resumen_agenda(citas):
    hoy = date.today()
    agenda = [cita for cita in citas if str(cita.get("fecha"))[:10] == hoy.isoformat()]
    agenda.sort(key=lambda cita: minutos(cita["hora"]))
    return agenda


def bloquear_agenda(cursor, docente_id, estudiante_id, acudiente_id):
    for tabla, columna, persona in (("docentes", "id_docente", docente_id), ("estudiantes", "id_estudiante", estudiante_id), ("acudientes", "id_acudiente", acudiente_id)):
        cursor.execute(f"SELECT {columna} FROM {tabla} WHERE {columna}=%s FOR UPDATE", (persona,))
        cursor.fetchone()


def comprobar_hueco(cursor, docente_id, estudiante_id, acudiente_id, fecha, hora, excluir=0):
    cursor.execute(
        "SELECT id FROM citas WHERE fecha=%s AND id<>%s "
        "AND hora<ADDTIME(%s,'00:30:00') AND ADDTIME(hora,'00:30:00')>%s "
        "AND (id_docente=%s OR id_estudiante=%s OR id_acudiente=%s) LIMIT 1 FOR UPDATE",
        (fecha, excluir, hora, hora, docente_id, estudiante_id, acudiente_id),
    )
    if cursor.fetchone():
        raise ValueError("Ese horario se cruza con otra reunión del docente, estudiante o acudiente.")


def reservar_cita(sql, params):
    validar_disponibilidad(params[2], params[6], params[7])
    with transaccion() as cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            bloquear_agenda(cursor, params[2], params[0], params[1])
            comprobar_hueco(cursor, params[2], params[0], params[1], params[6], params[7])
            cursor.execute(sql, params)
            cita_id = cursor.lastrowid
        finally:
            cursor.close()
    try:
        from servicios.google_calendar import sincronizar_cita

        sincronizar_cita(cita_id, params[10])
    except Exception:
        from flask import current_app

        current_app.logger.exception("La cita %s se guardó, pero falló la sincronización opcional con Google.", cita_id)
    return cita_id