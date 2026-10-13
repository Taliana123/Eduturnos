from functools import wraps
from flask import session, redirect, url_for, flash, abort
from database.db import consultar, ejecutar
from flask import current_app


def usuario_actual():
    uid = session.get("usuario_id")
    if not uid:
        return None
    if session.get("creado_en") and __import__("time").time() - session["creado_en"] > 3600:
        session.clear()
        return None
    try:
        return consultar(
            "SELECT u.*, r.nombre AS rol_nombre FROM usuarios u JOIN roles r ON r.id=u.id_rol WHERE u.id_usuario=%s AND u.estado=1",
            (uid,), uno=True,
        )
    except Exception:
        return None


def login_requerido(func):
    @wraps(func)
    def envoltura(*args, **kwargs):
        if not usuario_actual():
            flash("Debes iniciar sesión.", "error")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return envoltura


def roles_permitidos(*roles):
    def decorador(func):
        @wraps(func)
        def envoltura(*args, **kwargs):
            usuario = usuario_actual()
            if not usuario:
                flash("Debes iniciar sesión.", "error")
                return redirect(url_for("auth.login"))
            if usuario["rol_nombre"] not in roles:
                abort(403)
            return func(*args, **kwargs)
        return envoltura
    return decorador


def auditoria(accion, modulo, registro_id=None, detalle=""):
    uid = session.get("usuario_id")
    try:
        ejecutar(
            "INSERT INTO auditoria(id_usuario,accion,modulo,registro_id,detalle) VALUES(%s,%s,%s,%s,%s)",
            (uid, accion, modulo, registro_id, detalle[:255]),
        )
    except Exception as exc:
        current_app.logger.warning("No se pudo registrar auditoría: %s", exc)


def notificar(id_usuario, titulo, mensaje, tipo="Sistema"):
    if id_usuario:
        try:
            ejecutar(
                "INSERT INTO notificaciones(id_usuario,titulo,mensaje,tipo) VALUES(%s,%s,%s,%s)",
                (id_usuario, titulo, mensaje, tipo),
            )
        except Exception:
            pass
