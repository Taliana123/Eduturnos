from __future__ import annotations

import secrets
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from database.db import consultar, ejecutar
from routes.helpers import login_requerido, roles_permitidos, usuario_actual
from servicios.google_calendar import (
    configuracion_lista,
    correo_google,
    error_google_seguro,
    guardar_conexion,
    intercambiar_codigo,
    encolar_cita,
    encolar_citas_futuras,
    estado_cola_google,
    calendar_id_objetivo,
    apps_script_configurada,
    configuracion_oauth_lista,
    procesar_cola_google,
    probar_conexion_calendario,
    probar_apps_script,
    reintentar_fallidas_google,
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
    oauth_activo = configuracion_oauth_lista()
    puente_activo = apps_script_configurada()
    personal = None
    personal_sync = None
    if usuario["rol_nombre"] in ROLES_PERSONAL and oauth_activo:
        personal = consultar(
            "SELECT correo_google,calendar_id,fecha_actualizacion,fecha_prueba FROM integraciones_google WHERE scope_key=%s",
            (f"usuario:{usuario['id_usuario']}",), uno=True,
        )
        personal_sync = estado_cola_google(f"usuario:{usuario['id_usuario']}")
    institucional = None
    institucional_sync = None
    if usuario["rol_nombre"] in ("Super Admin", "Rector"):
        institucional = (
            {"correo_google": "Puente institucional (Apps Script)", "fecha_prueba": None}
            if puente_activo
            else consultar(
                "SELECT correo_google,calendar_id,fecha_actualizacion,fecha_prueba FROM integraciones_google WHERE scope_key='institucional'",
                uno=True,
            )
        )
        institucional_sync = estado_cola_google("institucional")
    return render_template(
        "integraciones_google.html",
        usuario=usuario,
        personal=personal,
        institucional=institucional,
        personal_sync=personal_sync,
        institucional_sync=institucional_sync,
        puede_personal=usuario["rol_nombre"] in ROLES_PERSONAL and oauth_activo,
        puede_institucional=usuario["rol_nombre"] in ("Super Admin", "Rector"),
        apps_script_activo=puente_activo,
        oauth_activo=oauth_activo,
        configuracion_lista=configuracion_lista(),
        callback_url=(uri_callback() if oauth_activo else "/integraciones-google/callback"),
    )


@integraciones_google_bp.get("/conectar/<scope>")
@login_requerido
def conectar(scope):
    if scope not in ("personal", "institucional"):
        abort(404)
    usuario = usuario_actual()
    if not _permite(scope, usuario["rol_nombre"]):
        abort(403)
    if scope == "institucional" and apps_script_configurada():
        try:
            probar_apps_script()
            flash("El puente de Google Calendar está conectado y puede acceder a la agenda institucional.", "success")
        except Exception as exc:
            current_app.logger.exception("Falló la prueba del puente de Google Calendar")
            flash(f"No se pudo probar el puente de Google Calendar: {error_google_seguro(exc)}", "error")
        return redirect(url_for("integraciones_google.index"))
    if not configuracion_oauth_lista():
        flash("La conexión personal de Google Calendar no está configurada en el servidor.", "error")
        return redirect(url_for("integraciones_google.index"))
    if not configuracion_lista():
        flash("Configura dominio HTTPS y credenciales OAuth de Google en el servidor para habilitar la conexión.", "error")
        return redirect(url_for("integraciones_google.index"))
    state = secrets.token_urlsafe(32)
    session["google_oauth_state"] = state
    session["google_oauth_scope"] = scope
    return redirect(url_autorizacion(state))


@integraciones_google_bp.post("/reintentar-institucional")
@roles_permitidos("Super Admin", "Rector")
def reintentar_institucional():
    if not apps_script_configurada():
        flash("El puente de Google Calendar no está configurado en el servidor.", "error")
        return redirect(url_for("integraciones_google.index"))
    try:
        probar_apps_script()
        cantidad = reintentar_fallidas_google("institucional")
        if cantidad:
            resultado = procesar_cola_google(limite=20)
            if not resultado["fallidas"]:
                if not resultado["procesadas"]:
                    flash("No había tareas listas para enviar a Google Calendar.", "info")
                else:
                    flash(f"Google Calendar aceptó {resultado['sincronizadas']} citas.", "success")
        else:
            flash("No hay citas fallidas pendientes de reintento.", "info")
    except Exception as exc:
        current_app.logger.exception("Falló el reintento de citas del calendario institucional")
        flash(f"No se pudieron reintentar las citas: {error_google_seguro(exc)}", "error")
    return redirect(url_for("integraciones_google.index"))


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
        scope_key = "institucional" if scope == "institucional" else f"usuario:{usuario['id_usuario']}"
        probar_conexion_calendario(
            token["access_token"],
            calendar_id_objetivo(scope_key),
        )
        email = correo_google(token["access_token"])
        user_id = None if scope == "institucional" else usuario["id_usuario"]
        guardar_conexion(scope_key, "Institucional" if scope == "institucional" else "Personal", user_id, email, token)
        try:
            resumen = encolar_citas_futuras(scope_key, user_id)
            if resumen["encoladas"]:
                flash(
                    f"Google Calendar quedó conectado. Se encolaron "
                    f"{resumen['citas']} citas futuras para sincronización automática.",
                    "success",
                )
            else:
                flash("Google Calendar quedó conectado; no hay citas futuras pendientes de sincronización.", "success")
        except Exception:
            current_app.logger.exception("Falló la sincronización inicial de Google Calendar")
            flash("Google Calendar quedó conectado, pero no se pudieron sincronizar las citas futuras.", "warning")
    except Exception as exc:
        current_app.logger.exception("Falló el callback OAuth de Google Calendar")
        flash(f"No fue posible conectar Google Calendar: {error_google_seguro(exc)}", "error")
    return redirect(url_for("integraciones_google.index"))


@integraciones_google_bp.post("/desconectar/<scope>")
@login_requerido
def desconectar(scope):
    if scope not in ("personal", "institucional"):
        abort(404)
    usuario = usuario_actual()
    if not _permite(scope, usuario["rol_nombre"]):
        abort(403)
    if scope == "institucional" and apps_script_configurada():
        flash("El puente institucional se administra en la configuración protegida del servidor.", "info")
        return redirect(url_for("integraciones_google.index"))
    scope_key = "institucional" if scope == "institucional" else f"usuario:{usuario['id_usuario']}"
    ejecutar("DELETE FROM integraciones_google WHERE scope_key=%s", (scope_key,))
    flash("Calendario de Google desconectado.", "success")
    return redirect(url_for("integraciones_google.index"))


@integraciones_google_bp.post("/reintentar/<int:cita_id>")
@roles_permitidos(*ROLES_PERSONAL)
def reintentar(cita_id):
    from routes.calendario import citas_visibles

    usuario = usuario_actual()
    cita = next(
        (
            item
            for item in citas_visibles(usuario)
            if int(item["id"]) == cita_id
        ),
        None,
    )
    if not cita:
        abort(404)
    operacion = "delete" if cita.get("estado_nombre") == "Cancelada" else "upsert"
    cantidad = encolar_cita(cita_id, usuario["id_usuario"], operacion)
    if cantidad:
        flash("La sincronización quedó en cola y se reintentará automáticamente.", "success")
    else:
        flash("No hay calendarios conectados para esta cita.", "error")
    return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))
