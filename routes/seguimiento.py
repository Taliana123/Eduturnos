from flask import Blueprint, render_template, redirect, url_for

from database.db import consultar
from routes.helpers import roles_permitidos, usuario_actual

seguimiento_bp = Blueprint("seguimiento", __name__, url_prefix="/seguimiento")


@seguimiento_bp.route("/")
@roles_permitidos("Super Admin", "Rector", "Administrador / Coordinador", "Docente")
def lista():
    usuario = usuario_actual()
    params = []
    extra = ""
    if usuario["rol_nombre"] == "Docente":
        extra = " AND (c.id_docente=(SELECT d.id_docente FROM docentes d WHERE d.id_usuario=%s) OR c.creado_por=%s)"
        params.extend((usuario["id_usuario"], usuario["id_usuario"]))

    rows = consultar(
        f"""SELECT s.*,c.fecha,c.hora,e.nombres,e.apellidos,
                   u.nombres usuario_n,u.apellidos usuario_a
            FROM seguimiento_citas s JOIN citas c ON c.id=s.id_cita
            JOIN estudiantes e ON e.id_estudiante=c.id_estudiante
            JOIN usuarios u ON u.id_usuario=s.realizado_por
            WHERE 1=1{extra} ORDER BY s.fecha_seguimiento DESC,s.id DESC""",
        tuple(params),
    )
    procesos = consultar(
        f"""SELECT c.id,COALESCE(e.nombres,dest.nombres) nombres,COALESCE(e.apellidos,dest.apellidos) apellidos,ec.nombre estado,
                   c.fecha,c.hora,c.lugar,c.observaciones,g.nombre grado,gr.nombre grupo,
                   sede.nombre sede,m.nombre motivo,CONCAT(a.nombres,' ',a.apellidos) acudiente,
                   COALESCE((SELECT NULLIF(TRIM(s.observaciones),'') FROM seguimiento_citas s
                             WHERE s.id_cita=c.id ORDER BY s.fecha_seguimiento DESC,s.id DESC LIMIT 1),
                            NULLIF(TRIM(c.observaciones),'')) descripcion,
                   cierre.asistencia,cierre.resultado,
                   COALESCE(cierre.requiere_otra_cita,0) requiere_otra_cita,
                   COALESCE(cierre.requiere_acompanamiento,0) requiere_acompanamiento
            FROM citas c LEFT JOIN estudiantes e ON e.id_estudiante=c.id_estudiante
            LEFT JOIN usuarios dest ON dest.id_usuario=c.destinatario_usuario_id
            JOIN estados_cita ec ON ec.id=c.id_estado
            LEFT JOIN cierres_cita cierre ON cierre.id_cita=c.id
            LEFT JOIN grupos gr ON gr.id=e.id_grupo
            LEFT JOIN grados g ON g.id=gr.id_grado
            LEFT JOIN sedes sede ON sede.id=e.id_sede
            LEFT JOIN motivos m ON m.id=c.id_motivo
            LEFT JOIN acudientes a ON a.id_acudiente=c.id_acudiente
            WHERE 1=1{extra}
            ORDER BY (ec.nombre='Realizada') ASC,c.fecha DESC,c.hora DESC,c.id DESC""",
        tuple(params),
    )
    compromisos = consultar(
        f"SELECT cc.* FROM compromisos_cita cc JOIN citas c ON c.id=cc.id_cita "
        f"WHERE 1=1{extra} ORDER BY cc.fecha_limite,cc.id",
        tuple(params),
    )
    compromisos_por_cita = {}
    for compromiso in compromisos:
        compromisos_por_cita.setdefault(compromiso["id_cita"], []).append(compromiso)

    historial_por_cita = {}
    for registro in rows:
        historial_por_cita.setdefault(registro["id_cita"], []).append(registro)
    return render_template(
        "seguimiento/lista.html",
        seguimientos=rows[:500],
        procesos=procesos,
        historial_por_cita=historial_por_cita,
        compromisos_por_cita=compromisos_por_cita,
    )


@seguimiento_bp.get("/cita/<int:id>")
@roles_permitidos("Super Admin", "Rector", "Administrador / Coordinador", "Docente")
def registrar(id):
    # Conserva enlaces antiguos sin ofrecer el formulario de registro eliminado.
    return redirect(url_for("seguimiento.lista", _anchor=f"seguimiento-detalle-{id}"))
