from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import consultar, ejecutar
from routes.helpers import roles_permitidos, auditoria, usuario_actual
from roles import es_correo_institucional

docentes_bp=Blueprint("docentes",__name__,url_prefix="/docentes")

def catalogos():
    u=usuario_actual(); tenant=u.get("id_institucion") if u and u["rol_nombre"]!="Super Admin" else None
    return {"sedes":consultar("SELECT * FROM sedes WHERE estado=1 AND (%s IS NULL OR id_institucion=%s) ORDER BY nombre",(tenant,tenant)),"jornadas":consultar("SELECT * FROM jornadas WHERE estado=1 ORDER BY CASE nombre WHEN 'Mañana' THEN 1 WHEN 'Tarde' THEN 2 WHEN 'Noche' THEN 3 ELSE 4 END,nombre"),"estudiantes":consultar("SELECT e.id_estudiante,e.nombres,e.apellidos,e.documento FROM estudiantes e JOIN sedes s ON s.id=e.id_sede WHERE e.estado='Activo' AND (%s IS NULL OR s.id_institucion=%s) ORDER BY e.apellidos,e.nombres",(tenant,tenant)),"grupos":consultar("SELECT g.id,g.nombre,gr.nombre grado FROM grupos g JOIN grados gr ON gr.id=g.id_grado WHERE g.estado=1 ORDER BY CAST(gr.nombre AS UNSIGNED),gr.nombre,CAST(g.nombre AS UNSIGNED),g.nombre")}

@docentes_bp.route("/")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def lista():
    u=usuario_actual(); tenant=u.get("id_institucion") if u["rol_nombre"]!="Super Admin" else None
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
           WHERE (%s IS NULL OR s.id_institucion=%s) AND (CONCAT(d.nombres,' ',d.apellidos) LIKE %s
              OR d.documento LIKE %s
              OR d.correo_institucional LIKE %s
              OR COALESCE(d.asignatura,'') LIKE %s
              OR COALESCE(s.nombre,'') LIKE %s
              OR COALESCE(j.nombre,'') LIKE %s
              OR COALESCE(asignaciones.estudiantes,'') LIKE %s
              OR COALESCE(asignaciones.grados_grupos,'') LIKE %s)
           ORDER BY d.apellidos,d.nombres""",
        (tenant, tenant, like, like, like, like, like, like, like, like),
    )
    return render_template("docentes/lista.html", docentes=docentes, q=q)

@docentes_bp.route("/nuevo",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def nuevo():
    cat=catalogos()
    if request.method=="POST":
        d=request.form; correo=d.get("correo","").strip().lower()
        u=usuario_actual(); sede=next((x for x in cat["sedes"] if str(x["id"])==str(d.get("sede"))),None)
        correo_valido=es_correo_institucional(correo) if u.get("requiere_codigo_institucional",1) else ("@" in correo and " " not in correo)
        if not sede: flash("Selecciona una sede de tu institución.","error"); return render_template("docentes/form.html",docente=None,catalogos=cat)
        if not correo_valido: flash("Escribe un correo válido para el docente.","error"); return render_template("docentes/form.html",docente=None,catalogos=cat)
        try:
            did=ejecutar("INSERT INTO docentes(tipo_documento,documento,nombres,apellidos,correo_institucional,telefono,id_sede,id_jornada,area,asignatura,estado) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)",(d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],correo,d.get("telefono"),d["sede"],d["jornada"],d.get("area"),d.get("asignatura"))); auditoria("CREAR","Docentes",did); flash("Docente creado. Para que pueda registrarse, debe existir también en el directorio institucional con su código.","success"); return redirect(url_for("docentes.lista"))
        except Exception: flash("No se pudo crear el docente.","error")
    return render_template("docentes/form.html",docente=None,catalogos=cat)

@docentes_bp.route("/<int:id>/editar",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def editar(id):
    u=usuario_actual(); docente=consultar("SELECT d.* FROM docentes d JOIN sedes s ON s.id=d.id_sede WHERE d.id_docente=%s AND (%s='Super Admin' OR s.id_institucion=%s)",(id,u["rol_nombre"],u.get("id_institucion")),uno=True); cat=catalogos()
    if not docente: return redirect(url_for("docentes.lista"))
    if request.method=="POST":
        d=request.form; correo=d.get("correo","").strip().lower()
        sede=next((x for x in cat["sedes"] if str(x["id"])==str(d.get("sede"))),None)
        correo_valido=es_correo_institucional(correo) if u.get("requiere_codigo_institucional",1) else ("@" in correo and " " not in correo)
        if not sede: flash("Selecciona una sede de tu institución.","error"); return render_template("docentes/form.html",docente=docente,catalogos=cat)
        if not correo_valido: flash("Escribe un correo válido para el docente.","error"); return render_template("docentes/form.html",docente=docente,catalogos=cat)
        try:
            sql="UPDATE docentes SET tipo_documento=%s,documento=%s,nombres=%s,apellidos=%s,correo_institucional=%s,telefono=%s,id_sede=%s,id_jornada=%s,asignatura=%s WHERE id_docente=%s"
            params=(d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],correo,d.get("telefono"),d["sede"],d["jornada"],d.get("asignatura"),id)
            if u["rol_nombre"]!="Super Admin": sql+=" AND id_sede IN (SELECT id FROM sedes WHERE id_institucion=%s)"; params+=(u.get("id_institucion"),)
            ejecutar(sql,params); auditoria("ACTUALIZAR","Docentes",id); flash("Docente actualizado.","success"); return redirect(url_for("docentes.lista"))
        except Exception: flash("No se pudo actualizar el docente.","error")
    return render_template("docentes/form.html",docente=docente,catalogos=cat)

@docentes_bp.route("/<int:id>/asignaciones",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def asignaciones(id):
    u=usuario_actual(); docente=consultar("SELECT d.* FROM docentes d JOIN sedes s ON s.id=d.id_sede WHERE d.id_docente=%s AND (%s='Super Admin' OR s.id_institucion=%s)",(id,u["rol_nombre"],u.get("id_institucion")),uno=True)
    if not docente: return redirect(url_for("docentes.lista"))
    if request.method=="POST":
        try: ejecutar("INSERT INTO asignaciones_docentes(id_docente,id_estudiante,id_grupo,estado) VALUES(%s,%s,%s,1)",(id,request.form.get("estudiante") or None,request.form.get("grupo") or None)); auditoria("ASIGNAR","Docentes",id); flash("Asignación guardada.","success")
        except Exception: flash("No se pudo guardar la asignación. Puede que ya exista.","error")
    datos=consultar("""SELECT a.*,e.nombres estudiante_n,e.apellidos estudiante_a,g.nombre grupo,gr.nombre grado FROM asignaciones_docentes a LEFT JOIN estudiantes e ON e.id_estudiante=a.id_estudiante LEFT JOIN grupos g ON g.id=a.id_grupo LEFT JOIN grados gr ON gr.id=g.id_grado WHERE a.id_docente=%s ORDER BY a.id DESC""",(id,))
    return render_template("docentes/asignaciones.html",docente=docente,asignaciones=datos,catalogos=catalogos())
