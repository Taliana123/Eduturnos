from flask import Blueprint, jsonify, render_template, request

from database.db import consultar
from routes.helpers import login_requerido, usuario_actual
from servicios.avatar import guardar_avatar

cuenta_bp = Blueprint("cuenta", __name__, url_prefix="/cuenta")


@cuenta_bp.get("/")
@login_requerido
def index():
    usuario = usuario_actual()
    rol = usuario["rol_nombre"]
    perfil = {}

    if rol == "Docente":
        perfil = consultar(
            "SELECT d.correo_institucional AS correo, d.telefono, s.nombre AS sede, "
            "j.nombre AS jornada, d.area, d.asignatura FROM docentes d "
            "LEFT JOIN sedes s ON s.id=d.id_sede LEFT JOIN jornadas j ON j.id=d.id_jornada "
            "WHERE d.id_usuario=%s",
            (usuario["id_usuario"],), uno=True,
        ) or {}
    elif rol == "Estudiante":
        perfil = consultar(
            "SELECT e.codigo_estudiantil, e.curso, g.nombre AS grado, gr.nombre AS grupo, "
            "s.nombre AS sede, j.nombre AS jornada FROM estudiantes e "
            "LEFT JOIN grados g ON g.id=e.id_grado LEFT JOIN grupos gr ON gr.id=e.id_grupo "
            "LEFT JOIN sedes s ON s.id=e.id_sede LEFT JOIN jornadas j ON j.id=e.id_jornada "
            "WHERE e.id_usuario=%s",
            (usuario["id_usuario"],), uno=True,
        ) or {}
    elif rol == "Acudiente":
        perfil = consultar(
            "SELECT a.telefono, a.correo, a.direccion, a.barrio, a.municipio "
            "FROM acudientes a WHERE a.id_usuario=%s",
            (usuario["id_usuario"],), uno=True,
        ) or {}

    return render_template(
        "cuenta/index.html",
        usuario=usuario,
        perfil=perfil,
        puede_configurar=rol in ("Super Admin", "Rector", "Administrador / Coordinador"),
    )


@cuenta_bp.post("/avatar")
@login_requerido
def actualizar_avatar():
    usuario = usuario_actual()
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envía una configuración de personaje válida."}), 400

    try:
        avatar = guardar_avatar(usuario["id_usuario"], payload)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, "avatar": avatar})