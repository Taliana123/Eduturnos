from __future__ import annotations

import secrets
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from database.db import consultar, ejecutar
from routes.helpers import login_requerido, roles_permitidos, usuario_actual
from servicios.google_calendar import (
    configuracion_lista,
    correo_google,
    guardar_conexion,
    intercambiar_codigo,
    sincronizar_citas_futuras,
    uri_callback,
    url_autorizacion,
)

integraciones_google_bp = Blueprint("integraciones_google", __name__, url_prefix="/integraciones-google")
ROLES_INSTITUCIONALES = ("Super Admin", "Rector", "Administrador / Coordinador")
ROLES_PERSONAL = ROLES_INSTITUCIONALES + ("Docente", "Acudiente", "Estudiante")


def _permite(scope: str, rol: str) -> bool:
    if scope == "personal":
        return rol in ROLES_PERSONAL
    return scope == "institucional" and rol in ("Super Admin", "Rector")


@integraciones_google_bp.get("/")
@login_requerido
def index():
    usuario = usuario_actual()
    personal = None
    if usuario["rol_nombre"] in ROLES_PERSONAL:
        personal = consultar(
            "SELECT correo_google,calendar_id,fecha_actualizacion FROM integraciones_google WHERE scope_key=%s",
            (f"usuario:{usuario['id_usuario']}",), uno=True,
        )
    institucional = None
    if usuario["rol_nombre"] in ("Super Admin", "Rector"):
        institucional = consultar(
            "SELECT correo_google,calendar_id,fecha_actualizacion FROM integraciones_google WHERE scope_key='institucional'",
            uno=True,
        )
    return render_template(
        "integraciones_google.html",
        usuario=usuario,
        personal=personal,
        institucional=institucional,
        puede_personal=usuario["rol_nombre"] in ROLES_PERSONAL,
        puede_institucional=usuario["rol_nombre"] in ("Super Admin", "Rector"),
        configuracion_lista=configuracion_lista(),
        callback_url=(uri_callback() if configuracion_lista() else "/integraciones-google/callback"),
    )


@integraciones_google_bp.get("/conectar/<scope>")
@login_requerido
def conectar(scope):
    if scope not in ("personal", "institucional"):
        abort(404)
    usuario = usuario_actual()
    if not _permite(scope, usuario["rol_nombre"]):
        abort(403)
    if not configuracion_lista():
        flash("Configura dominio HTTPS y credenciales OAuth de Google en el servidor para habilitar la conexión.", "error")
        return redirect(url_for("integraciones_google.index"))
    state = secrets.token_urlsafe(32)
    session["google_oauth_state"] = state
    session["google_oauth_scope"] = scope
    return redirect(url_autorizacion(state))


@integraciones_google_bp.get("/callback")
@login_requerido
def callback():
    state = request.args.get("state", "")
    scope = session.pop("google_oauth_scope", "")
    expected = session.pop("google_oauth_state", "")
    if not state or not expected or not secrets.compare_digest(state, expected):
        abort(400, description="La autorización de Google no coincide con esta sesión. Inténtalo nuevamente.")
    if request.args.get("error"):
        flash("Google canceló la conexión del calendario.", "error")
        return redirect(url_for("integraciones_google.index"))
    code = request.args.get("code", "")
    if not code:
        abort(400)
    usuario = usuario_actual()
    if scope not in ("personal", "institucional") or not _permite(scope, usuario["rol_nombre"]):
        abort(403)
    try:
        token = intercambiar_codigo(code)
        email = correo_google(token["access_token"])
        scope_key = "institucional" if scope == "institucional" else f"usuario:{usuario['id_usuario']}"
        user_id = None if scope == "institucional" else usuario["id_usuario"]
        guardar_conexion(scope_key, "Institucional" if scope == "institucional" else "Personal", user_id, email, token)
        try:
            resumen = sincronizar_citas_futuras(scope_key, user_id)
            if resumen["fallidas"]:
                flash(
                    f"Google Calendar quedó conectado; {resumen['fallidas']} de "
                    f"{resumen['citas']} citas futuras no se pudieron sincronizar.",
                    "warning",
                )
            else:
                flash(
                    f"Google Calendar quedó conectado y se sincronizaron "
                    f"{resumen['citas']} citas futuras con recordatorios.",
                    "success",
                )
        except Exception:
            current_app.logger.exception("Falló la sincronización inicial de Google Calendar")
            flash("Google Calendar quedó conectado, pero no se pudieron sincronizar las citas futuras.", "warning")
    except Exception as exc:
        current_app.logger.exception("Falló el callback OAuth de Google Calendar")
        flash(f"No fue posible conectar Google Calendar: {exc}", "error")
    return redirect(url_for("integraciones_google.index"))


@integraciones_google_bp.post("/desconectar/<scope>")
@login_requerido
def desconectar(scope):
    if scope not in ("personal", "institucional"):
        abort(404)
    usuario = usuario_actual()
    if not _permite(scope, usuario["rol_nombre"]):
        abort(403)
    scope_key = "institucional" if scope == "institucional" else f"usuario:{usuario['id_usuario']}"
    ejecutar("DELETE FROM integraciones_google WHERE scope_key=%s", (scope_key,))
    flash("Calendario de Google desconectado.", "success")
    return redirect(url_for("integraciones_google.index"))


@integraciones_google_bp.post("/reintentar/<int:cita_id>")
@roles_permitidos(*ROLES_PERSONAL)
def reintentar(cita_id):
    from routes.calendario import citas_visibles
    from servicios.google_calendar import sincronizar_cita

    usuario = usuario_actual()
    if cita_id not in {int(cita["id"]) for cita in citas_visibles(usuario)}:
        abort(404)
    resultados = sincronizar_cita(cita_id, usuario["id_usuario"])
    if any(resultado["estado"] == "Sincronizado" for resultado in resultados):
        flash("Cita sincronizada con los calendarios conectados.", "success")
    elif resultados:
        flash("Google no pudo sincronizar la cita. Revisa la conexión del calendario.", "error")
    else:
        flash("No hay calendarios conectados para esta cita.", "error")
    return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))
