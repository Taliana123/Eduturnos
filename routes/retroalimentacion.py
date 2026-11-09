from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from database.db import consultar, ejecutar
from routes.helpers import roles_permitidos, usuario_actual


retroalimentacion_bp = Blueprint(
    "retroalimentacion", __name__, url_prefix="/retroalimentacion"
)

TIPOS_COMENTARIO = ("Me gusta", "No me gusta", "Queja", "Idea de mejora")
ESTADOS_COMENTARIO = ("Nueva", "En revisión", "Atendida")
ROLES_ENVIO = ("Docente", "Estudiante", "Acudiente")
ROLES_GESTION = ("Rector", "Administrador / Coordinador")


def _institucion_usuario(usuario):
    id_institucion = usuario.get("id_institucion")
    if id_institucion:
        return id_institucion

    rol = usuario["rol_nombre"]
    if rol == "Estudiante":
        consulta = """
            SELECT s.id_institucion
            FROM estudiantes e JOIN sedes s ON s.id=e.id_sede
            WHERE e.id_usuario=%s LIMIT 1
        """
    elif rol == "Docente":
        consulta = """
            SELECT s.id_institucion
            FROM docentes d JOIN sedes s ON s.id=d.id_sede
            WHERE d.id_usuario=%s LIMIT 1
        """
    elif rol == "Acudiente":
        consulta = """
            SELECT COALESCE(a.id_institucion,s.id_institucion) AS id_institucion
            FROM acudientes a
            LEFT JOIN estudiante_acudiente ea ON ea.id_acudiente=a.id_acudiente
            LEFT JOIN estudiantes e ON e.id_estudiante=ea.id_estudiante
            LEFT JOIN sedes s ON s.id=e.id_sede
            WHERE a.id_usuario=%s
            ORDER BY ea.principal DESC,ea.id LIMIT 1
        """
    else:
        return None

    institucion = consultar(consulta, (usuario["id_usuario"],), uno=True)
    return institucion["id_institucion"] if institucion else None


@retroalimentacion_bp.route("/", methods=["GET", "POST"])
@roles_permitidos(*ROLES_ENVIO)
def enviar():
    usuario = usuario_actual()
    id_institucion = _institucion_usuario(usuario)

    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        asunto = request.form.get("asunto", "").strip()
        comentario = request.form.get("comentario", "").strip()

        if tipo not in TIPOS_COMENTARIO:
            flash("Selecciona una categoría válida para tu comentario.", "error")
        elif not asunto or len(asunto) > 120:
            flash("Escribe un asunto de máximo 120 caracteres.", "error")
        elif not comentario or len(comentario) > 4000:
            flash("Escribe tu comentario en un máximo de 4000 caracteres.", "error")
        elif not id_institucion:
            flash(
                "No encontramos la institución asociada a tu cuenta. "
                "Solicita que actualicen tus datos antes de enviar el comentario.",
                "error",
            )
        else:
            ejecutar(
                """INSERT INTO retroalimentacion_usuarios
                   (id_usuario,id_institucion,tipo,asunto,comentario)
                   VALUES(%s,%s,%s,%s,%s)""",
                (
                    usuario["id_usuario"],
                    id_institucion,
                    tipo,
                    asunto,
                    comentario,
                ),
            )
            flash("Tu comentario fue enviado a Rectoría y Coordinación.", "success")
            return redirect(url_for("retroalimentacion.enviar"))

    comentarios = consultar(
        """SELECT tipo,asunto,comentario,estado,fecha_creacion
           FROM retroalimentacion_usuarios
           WHERE id_usuario=%s
           ORDER BY fecha_creacion DESC,id DESC LIMIT 25""",
        (usuario["id_usuario"],),
    )
    return render_template(
        "retroalimentacion/enviar.html",
        tipos_comentario=TIPOS_COMENTARIO,
        comentarios=comentarios,
        sin_institucion=not id_institucion,
    )


@retroalimentacion_bp.route("/administrar", methods=["GET", "POST"])
@roles_permitidos(*ROLES_GESTION)
def administrar():
    usuario = usuario_actual()
    id_institucion = _institucion_usuario(usuario)

    if request.method == "POST":
        id_comentario = request.form.get("id_comentario", type=int)
        estado = request.form.get("estado", "").strip()
        if not id_comentario or estado not in ESTADOS_COMENTARIO:
            abort(400)
        if not id_institucion:
            abort(403)

        comentario = consultar(
            """SELECT id FROM retroalimentacion_usuarios
               WHERE id=%s AND id_institucion=%s""",
            (id_comentario, id_institucion),
            uno=True,
        )
        if not comentario:
            abort(404)

        ejecutar(
            """UPDATE retroalimentacion_usuarios SET estado=%s
               WHERE id=%s AND id_institucion=%s""",
            (estado, id_comentario, id_institucion),
        )
        flash("Se actualizó el estado del comentario.", "success")
        return redirect(url_for("retroalimentacion.administrar"))

    comentarios = []
    conteos = {estado: 0 for estado in ESTADOS_COMENTARIO}
    if id_institucion:
        comentarios = consultar(
            """SELECT r.id,r.tipo,r.asunto,r.comentario,r.estado,r.fecha_creacion,
                      u.nombres,u.apellidos,rol.nombre AS rol_nombre
               FROM retroalimentacion_usuarios r
               JOIN usuarios u ON u.id_usuario=r.id_usuario
               JOIN roles rol ON rol.id=u.id_rol
               WHERE r.id_institucion=%s
               ORDER BY FIELD(r.estado,'Nueva','En revisión','Atendida'),
                        r.fecha_creacion DESC,r.id DESC
               LIMIT 300""",
            (id_institucion,),
        )
        conteos_rows = consultar(
            """SELECT estado,COUNT(*) AS total
               FROM retroalimentacion_usuarios
               WHERE id_institucion=%s GROUP BY estado""",
            (id_institucion,),
        )
        conteos.update({fila["estado"]: fila["total"] for fila in conteos_rows})

    return render_template(
        "retroalimentacion/administrar.html",
        comentarios=comentarios,
        conteos=conteos,
        estados_comentario=ESTADOS_COMENTARIO,
        sin_institucion=not id_institucion,
    )
