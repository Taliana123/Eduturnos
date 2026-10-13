from flask import Blueprint, render_template

from database.db import consultar
from routes.helpers import login_requerido, usuario_actual

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