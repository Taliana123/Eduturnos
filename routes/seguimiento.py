from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import consultar, ejecutar
from routes.helpers import roles_permitidos, usuario_actual, auditoria, notificar

seguimiento_bp=Blueprint("seguimiento",__name__,url_prefix="/seguimiento")

@seguimiento_bp.route("/")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador","Docente")
def lista():
    u=usuario_actual(); params=[]; extra=""
    if u["rol_nombre"]=="Docente": extra=" AND c.id_docente=(SELECT d.id_docente FROM docentes d WHERE d.id_usuario=%s)"; params.append(u["id_usuario"])
    rows=consultar(f"""SELECT s.*,c.fecha,c.hora,e.nombres,e.apellidos,u.nombres usuario_n,u.apellidos usuario_a FROM seguimiento_citas s JOIN citas c ON c.id=s.id_cita JOIN estudiantes e ON e.id_estudiante=c.id_estudiante JOIN usuarios u ON u.id_usuario=s.realizado_por WHERE 1=1{extra} ORDER BY s.fecha_seguimiento DESC,s.id DESC""",tuple(params))
    procesos=consultar(f"""SELECT c.id,e.nombres,e.apellidos,ec.nombre estado,
        c.fecha,c.hora,c.lugar,c.observaciones,g.nombre grado,gr.nombre grupo,
        sede.nombre sede,m.nombre motivo,CONCAT(a.nombres,' ',a.apellidos) acudiente,
        COALESCE((SELECT NULLIF(TRIM(s.observaciones),'') FROM seguimiento_citas s
                  WHERE s.id_cita=c.id ORDER BY s.fecha_seguimiento DESC,s.id DESC LIMIT 1),
                 NULLIF(TRIM(c.observaciones),'')) descripcion
        FROM citas c JOIN estudiantes e ON e.id_estudiante=c.id_estudiante
        JOIN estados_cita ec ON ec.id=c.id_estado
        LEFT JOIN grupos gr ON gr.id=e.id_grupo
        LEFT JOIN grados g ON g.id=gr.id_grado
        LEFT JOIN sedes sede ON sede.id=e.id_sede
        LEFT JOIN motivos m ON m.id=c.id_motivo
        LEFT JOIN acudientes a ON a.id_acudiente=c.id_acudiente WHERE 1=1{extra}
        ORDER BY c.fecha DESC,c.hora DESC,c.id DESC""",tuple(params))
    historial_por_cita={}
    for registro in rows:
        historial_por_cita.setdefault(registro["id_cita"],[]).append(registro)
    return render_template("seguimiento/lista.html",seguimientos=rows[:500],procesos=procesos,historial_por_cita=historial_por_cita)

@seguimiento_bp.route("/cita/<int:id>",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador","Docente")
def registrar(id):
    u=usuario_actual(); cita=consultar("SELECT c.*,e.nombres estudiante_n,e.apellidos estudiante_a,ec.nombre estado FROM citas c JOIN estudiantes e ON e.id_estudiante=c.id_estudiante JOIN estados_cita ec ON ec.id=c.id_estado WHERE c.id=%s",(id,),uno=True)
    if not cita: return redirect(url_for("citas.index"))
    if u["rol_nombre"]=="Docente":
        ok=consultar("SELECT 1 FROM citas c JOIN docentes d ON d.id_docente=c.id_docente WHERE c.id=%s AND d.id_usuario=%s",(id,u["id_usuario"]),uno=True)
        if not ok: return redirect(url_for("citas.index"))
    if request.method=="POST":
        asistencia=request.form.get("asistencia","Pendiente"); obs=request.form.get("observaciones","").strip()
        estado_nombre="Realizada" if asistencia=="Asistió" else "No asistió" if asistencia=="No asistió" else cita["estado"]
        ejecutar("INSERT INTO seguimiento_citas(id_cita,estado_actual,asistencia,observaciones,realizado_por) VALUES(%s,%s,%s,%s,%s)",(id,estado_nombre,asistencia,obs,u["id_usuario"]))
        estado=consultar("SELECT id FROM estados_cita WHERE nombre=%s",(estado_nombre,),uno=True)
        if estado: ejecutar("UPDATE citas SET id_estado=%s WHERE id=%s",(estado["id"],id))
        if asistencia=="No asistió":
            ac=consultar("SELECT a.id_usuario FROM citas c JOIN acudientes a ON a.id_acudiente=c.id_acudiente WHERE c.id=%s",(id,),uno=True)
            if ac and ac.get("id_usuario"): notificar(ac["id_usuario"],"Inasistencia registrada","Se registró una inasistencia en tu citación.","Seguimiento")
        auditoria("REGISTRAR","Seguimiento",id); flash("Seguimiento registrado.","success"); return redirect(url_for("seguimiento.lista"))
    return render_template("seguimiento/form.html",cita=cita)
