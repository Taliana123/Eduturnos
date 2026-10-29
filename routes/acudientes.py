from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import consultar, ejecutar
from routes.helpers import roles_permitidos, auditoria, usuario_actual
from roles import es_correo_gmail

acudientes_bp=Blueprint("acudientes",__name__,url_prefix="/acudientes")

@acudientes_bp.route("/")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def lista():
    u=usuario_actual(); tenant=u.get("id_institucion") if u["rol_nombre"]!="Super Admin" else None
    q = request.args.get("q", "").strip()
    like = f"%{q}%"
    acudientes = consultar(
        """SELECT a.*,
                  GROUP_CONCAT(DISTINCT CONCAT(e.nombres,' ',e.apellidos)
                               ORDER BY e.apellidos,e.nombres SEPARATOR ', ') estudiantes,
                  GROUP_CONCAT(DISTINCT CONCAT(COALESCE(gr.nombre,'-'),' / ',COALESCE(g.nombre,'-'))
                               ORDER BY gr.nombre,g.nombre SEPARATOR ', ') grados_grupos,
                  GROUP_CONCAT(DISTINCT s.nombre ORDER BY s.nombre SEPARATOR ', ') sedes,
                  GROUP_CONCAT(DISTINCT j.nombre ORDER BY j.nombre SEPARATOR ', ') jornadas
           FROM acudientes a
           LEFT JOIN estudiante_acudiente ea ON ea.id_acudiente=a.id_acudiente AND ea.estado=1
           LEFT JOIN estudiantes e ON e.id_estudiante=ea.id_estudiante AND e.estado='Activo'
           LEFT JOIN sedes s ON s.id=e.id_sede
           LEFT JOIN jornadas j ON j.id=e.id_jornada
           LEFT JOIN grados gr ON gr.id=e.id_grado
           LEFT JOIN grupos g ON g.id=e.id_grupo
           WHERE (%s IS NULL OR a.id_institucion=%s)
             AND (CONCAT(a.nombres,' ',a.apellidos) LIKE %s
              OR a.documento LIKE %s
              OR COALESCE(a.correo,'') LIKE %s
              OR COALESCE(a.telefono,'') LIKE %s)
           GROUP BY a.id_acudiente
           ORDER BY a.apellidos,a.nombres""",
        (tenant, tenant, like, like, like, like),
    )
    return render_template("acudientes/lista.html", acudientes=acudientes, q=q)

@acudientes_bp.route("/nuevo",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def nuevo():
    if request.method=="POST":
        d=request.form
        correo=(d.get("correo") or "").strip().lower()
        if not es_correo_gmail(correo):
            flash("El correo del acudiente debe terminar en @gmail.com.","error")
            return render_template("acudientes/form.html",acudiente=None,correo=correo)
        try:
            u=usuario_actual(); tenant=u.get("id_institucion") if u["rol_nombre"]!="Super Admin" else None
            aid=ejecutar("INSERT INTO acudientes(tipo_documento,documento,nombres,apellidos,telefono,correo,direccion,barrio,municipio,estado,id_institucion) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s)",(d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],d.get("telefono"),correo,d.get("direccion"),d.get("barrio"),d.get("municipio") or "Ibagué",tenant)); auditoria("CREAR","Acudientes",aid); flash("Acudiente creado.","success"); return redirect(url_for("acudientes.lista"))
        except Exception: flash("No se pudo crear el acudiente.","error")
    return render_template("acudientes/form.html",acudiente=None)

@acudientes_bp.route("/<int:id>/editar",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def editar(id):
    u=usuario_actual(); a=consultar("SELECT * FROM acudientes WHERE id_acudiente=%s AND (%s='Super Admin' OR id_institucion=%s)",(id,u["rol_nombre"],u.get("id_institucion")),uno=True)
    if not a: return redirect(url_for("acudientes.lista"))
    if request.method=="POST":
        d=request.form
        correo=(d.get("correo") or "").strip().lower()
        if not es_correo_gmail(correo):
            flash("El correo del acudiente debe terminar en @gmail.com.","error")
            return render_template("acudientes/form.html",acudiente=a,correo=correo)
        try:
            ejecutar("UPDATE acudientes SET tipo_documento=%s,documento=%s,nombres=%s,apellidos=%s,telefono=%s,correo=%s,direccion=%s,barrio=%s,municipio=%s,estado=%s WHERE id_acudiente=%s",(d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],d.get("telefono"),correo,d.get("direccion"),d.get("barrio"),d.get("municipio"),d.get("estado","1"),id)); auditoria("ACTUALIZAR","Acudientes",id); flash("Acudiente actualizado.","success"); return redirect(url_for("acudientes.lista"))
        except Exception: flash("No se pudo actualizar el acudiente.","error")
    return render_template("acudientes/form.html",acudiente=a)

@acudientes_bp.route("/<int:id>/relaciones")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def relaciones(id):
    u=usuario_actual(); tenant=u.get("id_institucion")
    a=consultar("SELECT * FROM acudientes WHERE id_acudiente=%s AND (%s='Super Admin' OR id_institucion=%s)",(id,u["rol_nombre"],tenant),uno=True)
    if not a: return redirect(url_for("acudientes.lista"))
    estudiantes=consultar("""SELECT e.id_estudiante,e.nombres,e.apellidos,e.documento,ea.parentesco,ea.principal FROM estudiante_acudiente ea JOIN estudiantes e ON e.id_estudiante=ea.id_estudiante WHERE ea.id_acudiente=%s AND ea.estado=1 ORDER BY e.apellidos,e.nombres""",(id,))
    todos=consultar("SELECT e.id_estudiante,e.nombres,e.apellidos,e.documento FROM estudiantes e JOIN sedes s ON s.id=e.id_sede WHERE e.estado='Activo' AND (%s='Super Admin' OR s.id_institucion=%s) ORDER BY e.apellidos,e.nombres",(u["rol_nombre"],tenant))
    return render_template("acudientes/relaciones.html",acudiente=a,estudiantes=estudiantes,todos=todos)

@acudientes_bp.post("/<int:id>/relacionar")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def relacionar(id):
    u=usuario_actual()
    try:
        acudiente=consultar("SELECT id_acudiente FROM acudientes WHERE id_acudiente=%s AND (%s='Super Admin' OR id_institucion=%s)",(id,u["rol_nombre"],u.get("id_institucion")),uno=True)
        if not acudiente: raise ValueError("El acudiente no pertenece a tu institución.")
        if u["rol_nombre"]!="Super Admin" and not consultar("SELECT e.id_estudiante FROM estudiantes e JOIN sedes s ON s.id=e.id_sede WHERE e.id_estudiante=%s AND s.id_institucion=%s",(request.form.get("estudiante"),u.get("id_institucion")),uno=True):
            raise ValueError("El estudiante no pertenece a tu institución.")
        ejecutar("INSERT INTO estudiante_acudiente(id_estudiante,id_acudiente,parentesco,principal,estado) VALUES(%s,%s,%s,%s,1)",(int(request.form["estudiante"]),id,request.form["parentesco"].strip(),1 if request.form.get("principal") else 0)); auditoria("RELACIONAR","Acudientes",id); flash("Relación creada.","success")
    except Exception: flash("La relación ya existe o es inválida.","error")
    return redirect(url_for("acudientes.relaciones",id=id))
