from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import consultar, ejecutar
from routes.helpers import roles_permitidos, auditoria

estudiantes_bp=Blueprint("estudiantes",__name__,url_prefix="/estudiantes")

def catalogos():
    return {"sedes":consultar("SELECT * FROM sedes WHERE estado=1 ORDER BY nombre"),"jornadas":consultar("SELECT * FROM jornadas WHERE estado=1 ORDER BY CASE nombre WHEN 'Mañana' THEN 1 WHEN 'Tarde' THEN 2 WHEN 'Noche' THEN 3 ELSE 4 END,nombre"),"periodos":consultar("SELECT * FROM periodos_academicos WHERE activo=1 AND cerrado=0 ORDER BY id DESC"),"grados":consultar("SELECT * FROM grados WHERE estado=1 ORDER BY CAST(nombre AS UNSIGNED),nombre"),"grupos":consultar("SELECT g.id,g.nombre,gr.nombre grado FROM grupos g JOIN grados gr ON gr.id=g.id_grado WHERE g.estado=1 ORDER BY CAST(gr.nombre AS UNSIGNED),gr.nombre,CAST(g.nombre AS UNSIGNED),g.nombre")}

@estudiantes_bp.route("/")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador","Docente")
def lista():
    from routes.helpers import usuario_actual
    u=usuario_actual(); q=request.args.get("q","").strip(); like=f"%{q}%"
    base="""SELECT DISTINCT e.*,s.nombre sede,j.nombre jornada,gr.nombre grado,g.nombre grupo,
                     (SELECT GROUP_CONCAT(CONCAT(a.nombres,' ',a.apellidos) ORDER BY ea.principal DESC,a.apellidos,a.nombres SEPARATOR ', ')
                      FROM estudiante_acudiente ea JOIN acudientes a ON a.id_acudiente=ea.id_acudiente
                      WHERE ea.id_estudiante=e.id_estudiante AND ea.estado=1 AND a.estado=1) acudiente FROM estudiantes e
                     LEFT JOIN sedes s ON s.id=e.id_sede LEFT JOIN jornadas j ON j.id=e.id_jornada
                     LEFT JOIN grados gr ON gr.id=e.id_grado LEFT JOIN grupos g ON g.id=e.id_grupo"""
    filtro="""(CONCAT(e.nombres,' ',e.apellidos) LIKE %s OR e.documento LIKE %s OR COALESCE(e.curso,'') LIKE %s
               OR COALESCE(s.nombre,'') LIKE %s OR COALESCE(gr.nombre,'') LIKE %s OR COALESCE(g.nombre,'') LIKE %s)"""
    parametros=(like,)*6
    if u["rol_nombre"]=="Docente":
        rows=consultar(base+""" JOIN asignaciones_docentes ad ON (ad.id_estudiante=e.id_estudiante OR (ad.id_grupo=e.id_grupo AND e.id_grupo IS NOT NULL))
                     JOIN docentes d ON d.id_docente=ad.id_docente
                     WHERE ad.estado=1 AND d.id_usuario=%s AND """+filtro+" ORDER BY e.apellidos,e.nombres",(u["id_usuario"],)+parametros)
    else:
        rows=consultar(base+" WHERE "+filtro+" ORDER BY e.apellidos,e.nombres",parametros)
    return render_template("estudiantes/lista.html",estudiantes=rows,q=q,puede_gestionar=u["rol_nombre"] in ("Super Admin","Rector","Administrador / Coordinador"))

@estudiantes_bp.route("/nuevo",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def nuevo():
    cat=catalogos()
    if request.method=="POST":
        d=request.form
        try:
            eid=ejecutar("""INSERT INTO estudiantes(codigo_estudiantil,tipo_documento,documento,nombres,apellidos,curso,id_sede,id_jornada,id_periodo,id_grado,id_grupo,estado)
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Activo')""",(d["codigo"],d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],d.get("curso"),d["sede"],d["jornada"],d["periodo"],d.get("grado") or None,d.get("grupo") or None))
            auditoria("CREAR","Estudiantes",eid); flash("Estudiante creado.","success"); return redirect(url_for("estudiantes.lista"))
        except Exception: flash("No se pudo crear el estudiante. Revisa los datos únicos y las selecciones.","error")
    return render_template("estudiantes/form.html",catalogos=cat,estudiante=None)

@estudiantes_bp.route("/<int:id>/editar",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def editar(id):
    est=consultar("SELECT * FROM estudiantes WHERE id_estudiante=%s",(id,),uno=True); cat=catalogos()
    if not est: return redirect(url_for("estudiantes.lista"))
    if request.method=="POST":
        d=request.form
        try:
            ejecutar("""UPDATE estudiantes SET codigo_estudiantil=%s,tipo_documento=%s,documento=%s,nombres=%s,apellidos=%s,curso=%s,id_sede=%s,id_jornada=%s,id_periodo=%s,id_grado=%s,id_grupo=%s,estado=%s WHERE id_estudiante=%s""",(d["codigo"],d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],d.get("curso"),d["sede"],d["jornada"],d["periodo"],d.get("grado") or None,d.get("grupo") or None,d.get("estado", "Activo"),id))
            auditoria("ACTUALIZAR","Estudiantes",id); flash("Estudiante actualizado.","success"); return redirect(url_for("estudiantes.lista"))
        except Exception: flash("No se pudo actualizar el estudiante.","error")
    return render_template("estudiantes/form.html",catalogos=cat,estudiante=est)

@estudiantes_bp.post("/<int:id>/desactivar")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def desactivar(id):
    ejecutar("UPDATE estudiantes SET estado='Retirado' WHERE id_estudiante=%s",(id,)); auditoria("RETIRAR","Estudiantes",id); flash("Estudiante retirado.","success"); return redirect(url_for("estudiantes.lista"))
