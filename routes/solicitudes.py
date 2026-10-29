from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from database.db import consultar, ejecutar
from routes.helpers import roles_permitidos, usuario_actual, login_requerido, auditoria, notificar
from routes.citas import _cita_horario_ocupado
from servicios.reuniones import formatear_hora, reservar_cita

solicitudes_bp = Blueprint("solicitudes", __name__, url_prefix="/solicitudes")

STAFF = ("Super Admin", "Rector", "Administrador / Coordinador")
ROLES_REVISAN_REPROGRAMACION = (
    "Rector",
    "Administrador / Coordinador",
    "Docente",
)


def _validar_fecha_cita(valor):
    try:
        fecha = date.fromisoformat(str(valor or "").strip())
    except ValueError as exc:
        raise ValueError("La fecha de la cita no tiene un formato válido.") from exc
    if fecha < date.today():
        raise ValueError("La fecha de la cita no puede ser anterior a hoy.")
    return fecha.isoformat()


def _estados():
    return [r["nombre"] for r in consultar("SELECT nombre FROM estados_cita ORDER BY id")]


def _cita_desde_solicitud(s, fecha, hora, estado_nombre, creador_id):
    fecha = _validar_fecha_cita(fecha)
    estado = consultar("SELECT id FROM estados_cita WHERE nombre=%s", (estado_nombre,), uno=True)
    periodo = consultar(
        "SELECT id FROM periodos_academicos WHERE activo=1 AND id=COALESCE(%s,(SELECT id FROM periodos_academicos WHERE activo=1 ORDER BY id DESC LIMIT 1)) LIMIT 1",
        (s.get("id_periodo"),), uno=True,
    )
    if not estado or not periodo:
        raise ValueError("No hay estado de cita o periodo académico activo configurado.")
    if s.get("destinatario_tipo"):
        return reservar_cita(
            """INSERT INTO citas(id_estudiante,id_acudiente,id_docente,id_motivo,id_estado,id_periodo,
                               fecha,hora,lugar,observaciones,creado_por,destinatario_tipo,destinatario_usuario_id,motivo_otro)
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (s.get("id_estudiante"), s.get("id_acudiente"), s.get("id_docente"), s["id_motivo"],
             estado["id"], periodo["id"], fecha, hora, s.get("lugar") or "Coordinación",
             s.get("observaciones"), s.get("solicitante_usuario_id") or creador_id, s["destinatario_tipo"],
             s.get("destinatario_usuario_id"), s.get("motivo_otro")),
        )
    return reservar_cita(
        """INSERT INTO citas(id_estudiante,id_acudiente,id_docente,id_motivo,id_estado,id_periodo,fecha,hora,lugar,observaciones,creado_por)
           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (s["id_estudiante"], s["id_acudiente"], s["id_docente"], s["id_motivo"], estado["id"], periodo["id"],
         fecha, hora, "Coordinación", s.get("motivo_texto") or s.get("observaciones"), creador_id),
    )


def _validar_horario_disponible(solicitud, fecha, hora):
    if _cita_horario_ocupado(
        solicitud["id_docente"],
        solicitud["id_estudiante"],
        solicitud["id_acudiente"],
        fecha,
        hora,
    ):
        raise ValueError(
            "El horario ya está ocupado por el docente, estudiante "
            "o acudiente. Elige otro espacio."
        )

    if consultar(
        "SELECT id FROM citas WHERE fecha=%s AND hora<ADDTIME(%s,'00:30:00') "
        "AND ADDTIME(hora,'00:30:00')>%s AND ((%s IS NOT NULL AND destinatario_usuario_id=%s) OR creado_por=%s) LIMIT 1",
        (fecha, hora, hora, solicitud.get("destinatario_usuario_id"), solicitud.get("destinatario_usuario_id"), solicitud.get("solicitante_usuario_id")), uno=True,
    ):
        raise ValueError("El destinatario o quien solicita ya tiene una citacion en ese horario.")


def _notificar_destinatarios_coordinacion(titulo, mensaje):
    usuarios = consultar(
        """SELECT u.id_usuario FROM usuarios u JOIN roles r ON r.id=u.id_rol
           WHERE u.estado=1 AND r.nombre IN ('Super Admin','Rector','Administrador / Coordinador')"""
    )
    for row in usuarios:
        notificar(row["id_usuario"], titulo, mensaje, "Solicitud")


def _puede_ver(s, u):
    rol = u["rol_nombre"]
    if rol in STAFF:
        return True
    if rol == "Acudiente":
        return s["solicitante_usuario_id"] == u["id_usuario"]
    if rol == "Docente":
        return s["solicitante_usuario_id"] == u["id_usuario"]
    return False


def _cargar_catalogos(u):
    rol = u["rol_nombre"]
    estudiantes = []
    docentes = []
    if rol == "Acudiente":
        estudiantes = consultar(
            """SELECT e.id_estudiante, CONCAT(e.nombres,' ',e.apellidos) nombre
               FROM estudiantes e JOIN estudiante_acudiente ea ON ea.id_estudiante=e.id_estudiante
               JOIN acudientes a ON a.id_acudiente=ea.id_acudiente
               WHERE a.id_usuario=%s AND ea.estado=1 AND e.estado='Activo' ORDER BY e.apellidos,e.nombres""",
            (u["id_usuario"],),
        )
        docentes = consultar("SELECT d.id_docente, CONCAT(d.nombres,' ',d.apellidos) nombre FROM docentes d WHERE d.estado=1 ORDER BY d.apellidos,d.nombres")
    elif rol == "Docente":
        docentes = consultar("SELECT d.id_docente, CONCAT(d.nombres,' ',d.apellidos) nombre FROM docentes d WHERE d.id_usuario=%s", (u["id_usuario"],))
        estudiantes = consultar(
            """SELECT DISTINCT e.id_estudiante, CONCAT(e.nombres,' ',e.apellidos) nombre
               FROM estudiantes e JOIN asignaciones_docentes ad ON ad.id_estudiante=e.id_estudiante
               JOIN docentes d ON d.id_docente=ad.id_docente
               WHERE d.id_usuario=%s AND ad.estado=1 AND e.estado='Activo' ORDER BY e.apellidos,e.nombres""",
            (u["id_usuario"],),
        )
    else:
        estudiantes = consultar("SELECT id_estudiante, CONCAT(nombres,' ',apellidos) nombre FROM estudiantes WHERE estado='Activo' ORDER BY apellidos,nombres")
        docentes = consultar("SELECT id_docente, CONCAT(nombres,' ',apellidos) nombre FROM docentes WHERE estado=1 ORDER BY apellidos,nombres")
    motivos = consultar("SELECT id,nombre FROM motivos WHERE estado=1 ORDER BY nombre")
    return estudiantes, docentes, motivos


@solicitudes_bp.route("/")
@login_requerido
def index():
    u = usuario_actual()
    if u["rol_nombre"] in STAFF:
        rows = consultar(
            """SELECT s.*, CONCAT(COALESCE(du.nombres,e.nombres,''),' ',COALESCE(du.apellidos,e.apellidos,'')) estudiante,
                      CONCAT(d.nombres,' ',d.apellidos) docente,
                      CONCAT(a.nombres,' ',a.apellidos) acudiente,
                      COALESCE(NULLIF(s.motivo_otro,''),m.nombre) motivo, r.nombre rol_solicitante
               FROM solicitudes_cita s
               LEFT JOIN estudiantes e ON e.id_estudiante=s.id_estudiante
               LEFT JOIN usuarios du ON du.id_usuario=s.destinatario_usuario_id
               LEFT JOIN docentes d ON d.id_docente=s.id_docente
               LEFT JOIN acudientes a ON a.id_acudiente=s.id_acudiente
               LEFT JOIN motivos m ON m.id=s.id_motivo
               JOIN usuarios u ON u.id_usuario=s.solicitante_usuario_id
               JOIN roles r ON r.id=u.id_rol
               ORDER BY FIELD(s.estado,'Pendiente','Propuesta','Aceptada','Rechazada','Cancelada'), s.fecha_creacion DESC, s.id DESC
               LIMIT 500"""
        )
    else:
        rows = consultar(
            """SELECT s.*, CONCAT(COALESCE(du.nombres,e.nombres,''),' ',COALESCE(du.apellidos,e.apellidos,'')) estudiante,
                      CONCAT(d.nombres,' ',d.apellidos) docente,
                      CONCAT(a.nombres,' ',a.apellidos) acudiente,
                      COALESCE(NULLIF(s.motivo_otro,''),m.nombre) motivo, r.nombre rol_solicitante
               FROM solicitudes_cita s
               LEFT JOIN estudiantes e ON e.id_estudiante=s.id_estudiante
               LEFT JOIN usuarios du ON du.id_usuario=s.destinatario_usuario_id
               LEFT JOIN docentes d ON d.id_docente=s.id_docente
               LEFT JOIN acudientes a ON a.id_acudiente=s.id_acudiente
               LEFT JOIN motivos m ON m.id=s.id_motivo
               JOIN usuarios u ON u.id_usuario=s.solicitante_usuario_id
               JOIN roles r ON r.id=u.id_rol
               WHERE (s.solicitante_usuario_id=%s OR s.destinatario_usuario_id=%s)
               ORDER BY s.fecha_creacion DESC,s.id DESC LIMIT 200""",
            (u["id_usuario"], u["id_usuario"]),
        )
    solicitudes_reprogramacion = []
    if u["rol_nombre"] in ROLES_REVISAN_REPROGRAMACION:
        solicitudes_reprogramacion = consultar(
            """
            SELECT sr.*, c.creado_por AS creador_usuario_id,
                   CONCAT(e.nombres,' ',e.apellidos) AS estudiante,
                   CONCAT(a.nombres,' ',a.apellidos) AS acudiente
            FROM solicitudes_reprogramacion_cita sr
            JOIN citas c ON c.id = sr.id_cita
            JOIN estudiantes e ON e.id_estudiante = c.id_estudiante
            JOIN acudientes a ON a.id_usuario = sr.solicitante_usuario_id
            WHERE sr.creador_usuario_id = %s
            ORDER BY FIELD(sr.estado,'Pendiente','Aceptada','Rechazada'),
                     sr.fecha_creacion DESC, sr.id DESC
            LIMIT 200
            """,
            (u["id_usuario"],),
        )
    elif u["rol_nombre"] == "Acudiente":
        solicitudes_reprogramacion = consultar(
            """
            SELECT sr.*, c.creado_por AS creador_usuario_id,
                   CONCAT(e.nombres,' ',e.apellidos) AS estudiante,
                   CONCAT(a.nombres,' ',a.apellidos) AS acudiente
            FROM solicitudes_reprogramacion_cita sr
            JOIN citas c ON c.id = sr.id_cita
            JOIN estudiantes e ON e.id_estudiante = c.id_estudiante
            JOIN acudientes a ON a.id_usuario = sr.solicitante_usuario_id
            WHERE sr.solicitante_usuario_id = %s
            ORDER BY sr.fecha_creacion DESC, sr.id DESC
            LIMIT 200
            """,
            (u["id_usuario"],),
        )
    return render_template(
        "solicitudes/index.html",
        solicitudes=rows,
        solicitudes_reprogramacion=solicitudes_reprogramacion,
        rol=u["rol_nombre"],
        usuario_id=u["id_usuario"],
    )


@solicitudes_bp.route("/nueva/acudiente", methods=["GET", "POST"])
@roles_permitidos("Acudiente")
def nueva_acudiente():
    u = usuario_actual()
    estudiantes, docentes, motivos = _cargar_catalogos(u)
    if request.method == "POST":
        try:
            fecha = _validar_fecha_cita(request.form.get("fecha") or request.form.get("fecha_solicitada"))
            estudiante_id = int(request.form["id_estudiante"])
            docente_id = int(request.form["id_docente"])
            motivo_id = int(request.form["id_motivo"])
            hora = request.form["hora"]
            lugar = "Coordinación"
            observaciones = request.form.get("observaciones", "").strip()
            ok = consultar(
                """SELECT e.id_estudiante FROM estudiantes e JOIN estudiante_acudiente ea ON ea.id_estudiante=e.id_estudiante
                   JOIN acudientes a ON a.id_acudiente=ea.id_acudiente WHERE e.id_estudiante=%s AND a.id_usuario=%s AND ea.estado=1""",
                (estudiante_id, u["id_usuario"]), uno=True,
            )
            if not ok:
                raise ValueError("Ese estudiante no está asociado a tu cuenta.")
            solicitud_id = ejecutar(
                """INSERT INTO solicitudes_cita(solicitante_usuario_id,tipo_solicitante,id_estudiante,id_acudiente,id_docente,id_motivo,
                   fecha_solicitada,hora_solicitada,lugar,observaciones,estado)
                   VALUES(%s,'Acudiente',%s,(SELECT id_acudiente FROM acudientes WHERE id_usuario=%s),%s,%s,%s,%s,%s,%s,'Pendiente')""",
                (u["id_usuario"], estudiante_id, u["id_usuario"], docente_id, motivo_id, fecha, hora, lugar, observaciones),
            )
            _notificar_destinatarios_coordinacion("Nueva solicitud de cita", f"El acudiente envió la solicitud #{solicitud_id} para revisar una cita con un docente.")
            auditoria("CREAR", "Solicitudes de cita", solicitud_id, "Solicitud creada por acudiente")
            flash("Solicitud enviada a coordinación.", "success")
            return redirect(url_for("solicitudes.index"))
        except (KeyError, ValueError, TypeError) as exc:
            flash(f"Revisa los datos: {exc}", "error")
        except Exception as exc:
            flash(f"No se pudo enviar la solicitud: {exc}", "error")
    return render_template("solicitudes/nueva_acudiente.html", estudiantes=estudiantes, docentes=docentes, motivos=motivos, fecha_minima=date.today().isoformat())


@solicitudes_bp.route("/nueva/docente", methods=["GET", "POST"])
@roles_permitidos("Docente")
def nueva_docente():
    u = usuario_actual()
    estudiantes, docentes, motivos = _cargar_catalogos(u)
    if request.method == "POST":
        try:
            fecha = _validar_fecha_cita(request.form.get("fecha") or request.form.get("fecha_solicitada"))
            estudiante_id = int(request.form["id_estudiante"])
            motivo_id = int(request.form["id_motivo"])
            hora = request.form["hora"]
            observaciones = request.form.get("observaciones", "").strip()
            docente = docentes[0] if docentes else None
            if not docente:
                raise ValueError("Tu usuario no está vinculado a un docente institucional.")
            valid = consultar(
                """SELECT e.id_estudiante FROM estudiantes e JOIN asignaciones_docentes ad ON ad.id_estudiante=e.id_estudiante
                   WHERE ad.id_docente=%s AND ad.estado=1 AND e.id_estudiante=%s""",
                (docente["id_docente"], estudiante_id), uno=True,
            )
            if not valid:
                raise ValueError("El estudiante no está asignado a tu usuario.")
            acudiente = consultar(
                """SELECT a.id_acudiente FROM acudientes a JOIN estudiante_acudiente ea ON ea.id_acudiente=a.id_acudiente
                   WHERE ea.id_estudiante=%s AND ea.estado=1 AND a.estado=1 ORDER BY ea.principal DESC, a.id_acudiente LIMIT 1""",
                (estudiante_id,), uno=True,
            )
            if not acudiente:
                raise ValueError("El estudiante no tiene un acudiente vinculado.")
            solicitud_id = ejecutar(
                """INSERT INTO solicitudes_cita(solicitante_usuario_id,tipo_solicitante,id_estudiante,id_acudiente,id_docente,id_motivo,
                   fecha_solicitada,hora_solicitada,observaciones,estado)
                   VALUES(%s,'Docente',%s,%s,%s,%s,%s,%s,%s,'Pendiente')""",
                (u["id_usuario"], estudiante_id, acudiente["id_acudiente"], docente["id_docente"], motivo_id, fecha, hora, observaciones),
            )
            _notificar_destinatarios_coordinacion("Solicitud docente de seguimiento", f"El docente envió la solicitud #{solicitud_id} para revisión por coordinación.")
            auditoria("CREAR", "Solicitudes de cita", solicitud_id, "Solicitud de seguimiento creada por docente")
            flash("Solicitud enviada a coordinación.", "success")
            return redirect(url_for("solicitudes.index"))
        except (KeyError, ValueError, TypeError) as exc:
            flash(f"Revisa los datos: {exc}", "error")
        except Exception as exc:
            flash(f"No se pudo enviar la solicitud: {exc}", "error")
    return render_template("solicitudes/nueva_docente.html", estudiantes=estudiantes, motivos=motivos, fecha_minima=date.today().isoformat())


@solicitudes_bp.post("/<int:solicitud_id>/resolver")
@roles_permitidos("Super Admin", "Rector", "Administrador / Coordinador")
def resolver(solicitud_id):
    u = usuario_actual()
    s = consultar("SELECT * FROM solicitudes_cita WHERE id=%s", (solicitud_id,), uno=True)
    if not s:
        abort(404)
    accion = request.form.get("accion", "").strip()
    respuesta = request.form.get("respuesta", "").strip()
    fecha = request.form.get("fecha_propuesta", "").strip()
    hora = request.form.get("hora_propuesta", "").strip()
    try:
        if s["estado"] not in ("Pendiente", "Propuesta"):
            raise ValueError("La solicitud ya fue cerrada.")
        if accion == "rechazar":
            ejecutar("UPDATE solicitudes_cita SET estado='Rechazada',respuesta=%s,revisado_por=%s,fecha_revision=NOW(),fecha_actualizacion=NOW() WHERE id=%s", (respuesta or "Solicitud rechazada por coordinación.", u["id_usuario"], solicitud_id))
            notificar(s["solicitante_usuario_id"], "Solicitud rechazada", f"La solicitud #{solicitud_id} fue rechazada. {respuesta}", "Solicitud")
            auditoria("RECHAZAR", "Solicitudes de cita", solicitud_id, respuesta or "Rechazada")
            flash("Solicitud rechazada.", "success")
        elif accion in ("aceptar", "proponer"):
            fecha_final = _validar_fecha_cita(fecha or s["fecha_solicitada"])
            hora_final = hora or s["hora_solicitada"]
            try:
                datetime.strptime(str(fecha_final), "%Y-%m-%d")
                datetime.strptime(str(hora_final), "%H:%M")
            except ValueError:
                raise ValueError("La fecha o la hora no tienen un formato válido.")
            _validar_horario_disponible(s, fecha_final, hora_final)
            if accion == "proponer":
                ejecutar("UPDATE solicitudes_cita SET estado='Propuesta',fecha_propuesta=%s,hora_propuesta=%s,respuesta=%s,revisado_por=%s,fecha_revision=NOW(),fecha_actualizacion=NOW() WHERE id=%s", (fecha_final, hora_final, respuesta or "Coordinación propone un nuevo horario.", u["id_usuario"], solicitud_id))
                notificar(s["solicitante_usuario_id"], "Nueva propuesta de horario", f"La solicitud #{solicitud_id} tiene una nueva propuesta: {fecha_final} {formatear_hora(hora_final)}. {respuesta}", "Solicitud")
                auditoria("PROPONER", "Solicitudes de cita", solicitud_id, f"Nueva propuesta {fecha_final} {formatear_hora(hora_final)}")
                flash("Nueva propuesta enviada.", "success")
            else:
                cita_id = _cita_desde_solicitud(s, fecha_final, hora_final, "Confirmada", u["id_usuario"])
                ejecutar("UPDATE solicitudes_cita SET estado='Aceptada',fecha_propuesta=%s,hora_propuesta=%s,respuesta=%s,revisado_por=%s,cita_id=%s,fecha_revision=NOW(),fecha_actualizacion=NOW() WHERE id=%s", (fecha_final, hora_final, respuesta or "Solicitud aceptada.", u["id_usuario"], cita_id, solicitud_id))
                notificar(s["solicitante_usuario_id"], "Solicitud aceptada", f"La solicitud #{solicitud_id} fue aceptada para {fecha_final} {formatear_hora(hora_final)}.", "Solicitud")
                if s.get("destinatario_usuario_id"):
                    notificar(s["destinatario_usuario_id"], "Citaci?n aprobada", f"La solicitud #{solicitud_id} fue aprobada para {fecha_final} {formatear_hora(hora_final)}.", "Cita")
                if s.get("id_estudiante"):
                    estudiante_user = consultar("SELECT id_usuario FROM estudiantes WHERE id_estudiante=%s", (s["id_estudiante"],), uno=True)
                    if estudiante_user and estudiante_user.get("id_usuario") and estudiante_user["id_usuario"] != s.get("destinatario_usuario_id"):
                        notificar(estudiante_user["id_usuario"], "Citación aprobada", f"La solicitud #{solicitud_id} fue aprobada para {fecha_final} {formatear_hora(hora_final)}.", "Cita")
                if s.get("id_acudiente"):
                    acudiente_user = consultar("SELECT id_usuario FROM acudientes WHERE id_acudiente=%s", (s["id_acudiente"],), uno=True)
                    if acudiente_user and acudiente_user.get("id_usuario") and acudiente_user["id_usuario"] not in (s.get("destinatario_usuario_id"), s.get("solicitante_usuario_id")):
                        notificar(acudiente_user["id_usuario"], "Citación aprobada", f"La solicitud #{solicitud_id} fue aprobada para {fecha_final} {formatear_hora(hora_final)}.", "Cita")
                if s.get("id_docente"):
                    docente_user = consultar("SELECT id_usuario FROM docentes WHERE id_docente=%s", (s["id_docente"],), uno=True)
                    if docente_user and docente_user.get("id_usuario") != s["solicitante_usuario_id"]:
                        notificar(docente_user["id_usuario"], "Cita agendada", f"Se agendó una cita desde la solicitud #{solicitud_id} para {fecha_final} {formatear_hora(hora_final)}.", "Solicitud")
                auditoria("ACEPTAR", "Solicitudes de cita", solicitud_id, f"Cita #{cita_id} creada para {fecha_final} {formatear_hora(hora_final)}")
                flash("Solicitud aceptada y cita agendada.", "success")
        else:
            raise ValueError("Acción no válida.")
    except Exception as exc:
        flash(str(exc), "error")
    return redirect(url_for("solicitudes.index"))


@solicitudes_bp.post("/<int:solicitud_id>/aceptar-propuesta")
@roles_permitidos("Acudiente")
def aceptar_propuesta(solicitud_id):
    u = usuario_actual()
    s = consultar("SELECT * FROM solicitudes_cita WHERE id=%s AND solicitante_usuario_id=%s", (solicitud_id, u["id_usuario"]), uno=True)
    if not s or s["estado"] != "Propuesta":
        flash("No tienes una propuesta pendiente.", "error")
        return redirect(url_for("solicitudes.index"))
    try:
        _validar_fecha_cita(s["fecha_propuesta"])
        _validar_horario_disponible(
            s,
            s["fecha_propuesta"],
            s["hora_propuesta"],
        )
        cita_id = _cita_desde_solicitud(s, s["fecha_propuesta"], s["hora_propuesta"], "Confirmada", u["id_usuario"])
        ejecutar("UPDATE solicitudes_cita SET estado='Aceptada',cita_id=%s,respuesta=CONCAT(COALESCE(respuesta,''),' Acudiente aceptó la propuesta.'),fecha_actualizacion=NOW() WHERE id=%s", (cita_id, solicitud_id))
        docente_user = consultar("SELECT id_usuario FROM docentes WHERE id_docente=%s", (s["id_docente"],), uno=True)
        if docente_user and docente_user.get("id_usuario"):
            notificar(docente_user["id_usuario"], "Cita confirmada", f"El acudiente aceptó la nueva hora de la solicitud #{solicitud_id}.", "Solicitud")
        _notificar_destinatarios_coordinacion("Solicitud confirmada por acudiente", f"La solicitud #{solicitud_id} fue confirmada.")
        auditoria("ACEPTAR_PROPUESTA", "Solicitudes de cita", solicitud_id, f"Cita #{cita_id} aceptada por acudiente")
        flash("Propuesta aceptada. La cita quedó confirmada.", "success")
    except Exception as exc:
        flash(str(exc), "error")
    return redirect(url_for("solicitudes.index"))
