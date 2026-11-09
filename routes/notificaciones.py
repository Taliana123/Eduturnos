from datetime import date, datetime, time, timedelta, timezone

from flask import Blueprint, jsonify, redirect, url_for, flash, render_template
from database.db import consultar, ejecutar
from routes.helpers import usuario_actual, login_requerido

notificaciones_bp=Blueprint("notificaciones",__name__,url_prefix="/notificaciones")


@notificaciones_bp.get("/api/citas-futuras")
def citas_futuras_api():
    usuario = usuario_actual()
    if not usuario:
        return jsonify({"error": "authentication_required"}), 401

    from routes.calendario import citas_visibles

    bogota = timezone(timedelta(hours=-5))
    ahora = datetime.now(bogota)
    citas_recordatorio = []
    for cita in citas_visibles(usuario):
        estado = str(cita.get("estado_nombre") or "").strip().lower()
        if estado not in {"pendiente", "confirmada", "reprogramada"}:
            continue
        try:
            fecha_valor = cita.get("fecha")
            hora_valor = cita.get("hora")
            fecha = (
                fecha_valor
                if isinstance(fecha_valor, date)
                else date.fromisoformat(str(fecha_valor)[:10])
            )
            hora = (
                hora_valor
                if isinstance(hora_valor, time)
                else time.fromisoformat(str(hora_valor))
            )
            inicio = datetime.combine(fecha, hora, tzinfo=bogota)
            cita_id = int(cita["id"])
        except (KeyError, TypeError, ValueError):
            continue
        if inicio <= ahora:
            continue
        citas_recordatorio.append({
            "id": cita_id,
            "startAt": int(inicio.timestamp() * 1000),
        })
    return jsonify({"appointments": citas_recordatorio})


@notificaciones_bp.app_context_processor
def contador():
    u=usuario_actual(); total=0
    if u:
        try:
            row=consultar("SELECT COUNT(*) total FROM notificaciones WHERE id_usuario=%s AND leida=0",(u["id_usuario"],),uno=True); total=row["total"] if row else 0
        except Exception:
            total=0
    return {"notificaciones_no_leidas":total}

@notificaciones_bp.route("/")
@login_requerido
def index():
    u=usuario_actual(); avisos=consultar("SELECT id,titulo,mensaje,tipo,leida,fecha_creacion FROM notificaciones WHERE id_usuario=%s ORDER BY fecha_creacion DESC,id DESC LIMIT 100",(u["id_usuario"],)); return render_template("notificaciones/index.html",avisos=avisos)

@notificaciones_bp.post("/<int:notificacion_id>/leer")
@login_requerido
def marcar_leida(notificacion_id):
    u=usuario_actual(); ejecutar("UPDATE notificaciones SET leida=1 WHERE id=%s AND id_usuario=%s",(notificacion_id,u["id_usuario"])); return redirect(url_for("notificaciones.index"))

@notificaciones_bp.post("/leer-todas")
@login_requerido
def marcar_todas():
    u=usuario_actual(); ejecutar("UPDATE notificaciones SET leida=1 WHERE id_usuario=%s",(u["id_usuario"],)); flash("Notificaciones marcadas como leídas.","success"); return redirect(url_for("notificaciones.index"))
