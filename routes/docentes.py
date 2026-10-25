from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import consultar, ejecutar
from routes.helpers import roles_permitidos, auditoria
from roles import es_correo_institucional

docentes_bp=Blueprint("docentes",__name__,url_prefix="/docentes")

def catalogos():
    return {"sedes":consultar("SELECT * FROM sedes WHERE estado=1 ORDER BY nombre"),"jornadas":consultar("SELECT * FROM jornadas WHERE estado=1 ORDER BY CASE nombre WHEN 'Mañana' THEN 1 WHEN 'Tarde' THEN 2 WHEN 'Noche' THEN 3 ELSE 4 END,nombre"),"estudiantes":consultar("SELECT id_estudiante,nombres,apellidos,documento FROM estudiantes WHERE estado='Activo' ORDER BY apellidos,nombres"),"grupos":consultar("SELECT g.id,g.nombre,gr.nombre grado FROM grupos g JOIN grados gr ON gr.id=g.id_grado WHERE g.estado=1 ORDER BY CAST(gr.nombre AS UNSIGNED),gr.nombre,CAST(g.nombre AS UNSIGNED),g.nombre")}

@docentes_bp.route("/")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def lista():
    q = request.args.get("q", "").strip()
    like = f"%{q}%"
    docentes = consultar(
        """SELECT d.*,s.nombre sede,j.nombre jornada,
                  asignaciones.estudiantes,asignaciones.grados_grupos
           FROM docentes d
           LEFT JOIN sedes s ON s.id=d.id_sede
           LEFT JOIN jornadas j ON j.id=d.id_jornada
           LEFT JOIN (
               SELECT ad.id_docente,
                      GROUP_CONCAT(DISTINCT CONCAT(e.nombres,' ',e.apellidos)
                                   ORDER BY e.apellidos,e.nombres SEPARATOR ', ') estudiantes,
                      GROUP_CONCAT(DISTINCT CONCAT(COALESCE(gr.nombre,'-'),' / ',COALESCE(g.nombre,'-'))
                                   ORDER BY gr.nombre,g.nombre SEPARATOR ', ') grados_grupos
               FROM asignaciones_docentes ad
               LEFT JOIN estudiantes e ON e.estado='Activo'
                   AND (ad.id_estudiante=e.id_estudiante
                        OR (ad.id_grupo IS NOT NULL AND ad.id_grupo=e.id_grupo))
               LEFT JOIN grupos g ON g.id=COALESCE(ad.id_grupo,e.id_grupo)
               LEFT JOIN grados gr ON gr.id=COALESCE(g.id_grado,e.id_grado)
               WHERE ad.estado=1
               GROUP BY ad.id_docente
           ) asignaciones ON asignaciones.id_docente=d.id_docente
           WHERE CONCAT(d.nombres,' ',d.apellidos) LIKE %s
              OR d.documento LIKE %s
              OR d.correo_institucional LIKE %s
              OR COALESCE(d.asignatura,'') LIKE %s
              OR COALESCE(s.nombre,'') LIKE %s
              OR COALESCE(j.nombre,'') LIKE %s
              OR COALESCE(asignaciones.estudiantes,'') LIKE %s
              OR COALESCE(asignaciones.grados_grupos,'') LIKE %s
           ORDER BY d.apellidos,d.nombres""",
        (like, like, like, like, like, like, like, like),
    )
    return render_template("docentes/lista.html", docentes=docentes, q=q)

@docentes_bp.route("/nuevo",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def nuevo():
    cat=catalogos()
    if request.method=="POST":
        d=request.form; correo=d.get("correo","").strip().lower()
        if not es_correo_institucional(correo): flash("El correo debe terminar en @jjfh.edu.co.","error"); return render_template("docentes/form.html",docente=None,catalogos=cat)
        try:
            did=ejecutar("INSERT INTO docentes(tipo_documento,documento,nombres,apellidos,correo_institucional,telefono,id_sede,id_jornada,area,asignatura,estado) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)",(d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],correo,d.get("telefono"),d["sede"],d["jornada"],d.get("area"),d.get("asignatura"))); auditoria("CREAR","Docentes",did); flash("Docente creado. Para que pueda registrarse, debe existir también en el directorio institucional con su código.","success"); return redirect(url_for("docentes.lista"))
        except Exception: flash("No se pudo crear el docente.","error")
    return render_template("docentes/form.html",docente=None,catalogos=cat)

@docentes_bp.route("/<int:id>/editar",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def editar(id):
    docente=consultar("SELECT * FROM docentes WHERE id_docente=%s",(id,),uno=True); cat=catalogos()
    if not docente: return redirect(url_for("docentes.lista"))
    if request.method=="POST":
        d=request.form; correo=d.get("correo","").strip().lower()
        if not es_correo_institucional(correo): flash("El correo debe terminar en @jjfh.edu.co.","error"); return render_template("docentes/form.html",docente=docente,catalogos=cat)
        try:
            ejecutar("UPDATE docentes SET tipo_documento=%s,documento=%s,nombres=%s,apellidos=%s,correo_institucional=%s,telefono=%s,id_sede=%s,id_jornada=%s,asignatura=%s WHERE id_docente=%s",(d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],correo,d.get("telefono"),d["sede"],d["jornada"],d.get("asignatura"),id)); auditoria("ACTUALIZAR","Docentes",id); flash("Docente actualizado.","success"); return redirect(url_for("docentes.lista"))
        except Exception: flash("No se pudo actualizar el docente.","error")
    return render_template("docentes/form.html",docente=docente,catalogos=cat)

@docentes_bp.route("/<int:id>/asignaciones",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def asignaciones(id):
    docente=consultar("SELECT * FROM docentes WHERE id_docente=%s",(id,),uno=True)
    if not docente: return redirect(url_for("docentes.lista"))
    if request.method=="POST":
        try: ejecutar("INSERT INTO asignaciones_docentes(id_docente,id_estudiante,id_grupo,estado) VALUES(%s,%s,%s,1)",(id,request.form.get("estudiante") or None,request.form.get("grupo") or None)); auditoria("ASIGNAR","Docentes",id); flash("Asignación guardada.","success")
        except Exception: flash("No se pudo guardar la asignación. Puede que ya exista.","error")
    datos=consultar("""SELECT a.*,e.nombres estudiante_n,e.apellidos estudiante_a,g.nombre grupo,gr.nombre grado FROM asignaciones_docentes a LEFT JOIN estudiantes e ON e.id_estudiante=a.id_estudiante LEFT JOIN grupos g ON g.id=a.id_grupo LEFT JOIN grados gr ON gr.id=g.id_grado WHERE a.id_docente=%s ORDER BY a.id DESC""",(id,))
    return render_template("docentes/asignaciones.html",docente=docente,asignaciones=datos,catalogos=catalogos())
