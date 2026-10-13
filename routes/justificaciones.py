from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import consultar, ejecutar
from routes.helpers import usuario_actual, roles_permitidos, login_requerido, auditoria, notificar
from security import csrf_protegido

justificaciones_bp = Blueprint("justificaciones", __name__, url_prefix="/justificaciones")


def _puede_ver(cita, u):
    rol = u["rol_nombre"]
    if rol in ("Super Admin", "Rector", "Administrador / Coordinador"):
        return True
    if rol == "Acudiente":
        return consultar("SELECT 1 FROM acudientes WHERE id_acudiente=%s AND id_usuario=%s", (cita["id_acudiente"], u["id_usuario"]), uno=True) is not None
    if rol == "Estudiante":
        return consultar("SELECT 1 FROM estudiantes WHERE id_estudiante=%s AND documento=%s", (cita["id_estudiante"], u["documento"]), uno=True) is not None
    return False


@justificaciones_bp.route("/")
@login_requerido
def index():
    u = usuario_actual()
    if u["rol_nombre"] in ("Super Admin", "Rector", "Administrador / Coordinador"):
        rows = consultar("SELECT j.*,c.fecha,c.hora,CONCAT(e.nombres,' ',e.apellidos) estudiante,a.nombres acudiente_n,a.apellidos acudiente_a FROM justificaciones j JOIN citas c ON c.id=j.id_cita JOIN estudiantes e ON e.id_estudiante=c.id_estudiante JOIN acudientes a ON a.id_acudiente=c.id_acudiente ORDER BY j.fecha_solicitud DESC,j.id DESC LIMIT 300")
    elif u["rol_nombre"] == "Acudiente":
        rows = consultar("SELECT j.*,c.fecha,c.hora,CONCAT(e.nombres,' ',e.apellidos) estudiante FROM justificaciones j JOIN citas c ON c.id=j.id_cita JOIN estudiantes e ON e.id_estudiante=c.id_estudiante JOIN acudientes a ON a.id_acudiente=c.id_acudiente WHERE a.id_usuario=%s ORDER BY j.fecha_solicitud DESC,j.id DESC", (u["id_usuario"],))
    elif u["rol_nombre"] == "Estudiante":
        rows = consultar("SELECT j.*,c.fecha,c.hora,CONCAT(e.nombres,' ',e.apellidos) estudiante FROM justificaciones j JOIN citas c ON c.id=j.id_cita JOIN estudiantes e ON e.id_estudiante=c.id_estudiante WHERE e.documento=%s ORDER BY j.fecha_solicitud DESC,j.id DESC", (u["documento"],))
    else:
        rows = []
    return render_template("justificaciones/index.html", justificaciones=rows, rol=u["rol_nombre"])


@justificaciones_bp.route("/nueva/<int:cita_id>", methods=["GET", "POST"])
@roles_permitidos("Estudiante", "Acudiente")
@csrf_protegido
def nueva(cita_id):
    u = usuario_actual(); cita = consultar("SELECT * FROM citas WHERE id=%s", (cita_id,), uno=True)
    if not cita or not _puede_ver(cita, u):
        flash("No tienes acceso a esa citación.", "error"); return redirect(url_for("citas.index"))
    if request.method == "POST":
        motivo = request.form.get("motivo", "").strip()
        if len(motivo) < 10:
            flash("Explica brevemente el motivo de la solicitud.", "error")
        else:
            ejecutar("INSERT INTO justificaciones(id_cita,motivo) VALUES(%s,%s)", (cita_id, motivo))
            auditoria("SOLICITAR", "Justificaciones", cita_id)
            for uid in consultar("SELECT u.id_usuario FROM usuarios u JOIN roles r ON r.id=u.id_rol WHERE r.nombre IN ('Rector','Administrador / Coordinador') AND u.estado=1"):
                notificar(uid["id_usuario"], "Nueva justificación", f"La cita #{cita_id} tiene una solicitud de justificación pendiente.", "Justificación")
            flash("Solicitud enviada.", "success"); return redirect(url_for("justificaciones.index"))
    return render_template("justificaciones/nueva.html", cita=cita)


@justificaciones_bp.post("/<int:justificacion_id>/resolver")
@roles_permitidos("Super Admin", "Rector", "Administrador / Coordinador")
@csrf_protegido
def resolver(justificacion_id):
    estado = request.form.get("estado", "").strip()
    if estado not in ("Aceptada", "Rechazada"):
        flash("Estado inválido.", "error")
    else:
        j = consultar("SELECT * FROM justificaciones WHERE id=%s", (justificacion_id,), uno=True)
        if j:
            ejecutar("UPDATE justificaciones SET estado=%s,revisado_por=%s,fecha_revision=NOW() WHERE id=%s", (estado, usuario_actual()["id_usuario"], justificacion_id))
            auditoria("RESOLVER", "Justificaciones", justificacion_id, estado)
            cita = consultar("SELECT id_acudiente,id_estudiante FROM citas WHERE id=%s", (j["id_cita"],), uno=True)
            if cita:
                ids = consultar("SELECT id_usuario FROM acudientes WHERE id_acudiente=%s AND id_usuario IS NOT NULL", (cita["id_acudiente"],))
                for uid in ids:
                    notificar(uid["id_usuario"], "Justificación resuelta", f"Tu solicitud de justificación fue {estado.lower()}.", "Justificación")
            flash("Justificación resuelta.", "success")
    return redirect(url_for("justificaciones.index"))
