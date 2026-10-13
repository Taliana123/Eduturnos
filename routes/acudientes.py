from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import consultar, ejecutar
from routes.helpers import roles_permitidos, auditoria

acudientes_bp=Blueprint("acudientes",__name__,url_prefix="/acudientes")

@acudientes_bp.route("/")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def lista(): return render_template("acudientes/lista.html",acudientes=consultar("SELECT * FROM acudientes ORDER BY apellidos,nombres"))

@acudientes_bp.route("/nuevo",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def nuevo():
    if request.method=="POST":
        d=request.form
        try:
            aid=ejecutar("INSERT INTO acudientes(tipo_documento,documento,nombres,apellidos,telefono,correo,direccion,barrio,municipio,estado) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,1)",(d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],d.get("telefono"),d.get("correo"),d.get("direccion"),d.get("barrio"),d.get("municipio") or "Ibagué")); auditoria("CREAR","Acudientes",aid); flash("Acudiente creado.","success"); return redirect(url_for("acudientes.lista"))
        except Exception: flash("No se pudo crear el acudiente.","error")
    return render_template("acudientes/form.html",acudiente=None)

@acudientes_bp.route("/<int:id>/editar",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def editar(id):
    a=consultar("SELECT * FROM acudientes WHERE id_acudiente=%s",(id,),uno=True)
    if not a: return redirect(url_for("acudientes.lista"))
    if request.method=="POST":
        d=request.form
        try:
            ejecutar("UPDATE acudientes SET tipo_documento=%s,documento=%s,nombres=%s,apellidos=%s,telefono=%s,correo=%s,direccion=%s,barrio=%s,municipio=%s,estado=%s WHERE id_acudiente=%s",(d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],d.get("telefono"),d.get("correo"),d.get("direccion"),d.get("barrio"),d.get("municipio"),d.get("estado","1"),id)); auditoria("ACTUALIZAR","Acudientes",id); flash("Acudiente actualizado.","success"); return redirect(url_for("acudientes.lista"))
        except Exception: flash("No se pudo actualizar el acudiente.","error")
    return render_template("acudientes/form.html",acudiente=a)

@acudientes_bp.route("/<int:id>/relaciones")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def relaciones(id):
    a=consultar("SELECT * FROM acudientes WHERE id_acudiente=%s",(id,),uno=True)
    estudiantes=consultar("""SELECT e.id_estudiante,e.nombres,e.apellidos,e.documento,ea.parentesco,ea.principal FROM estudiante_acudiente ea JOIN estudiantes e ON e.id_estudiante=ea.id_estudiante WHERE ea.id_acudiente=%s AND ea.estado=1 ORDER BY e.apellidos,e.nombres""",(id,))
    todos=consultar("SELECT id_estudiante,nombres,apellidos,documento FROM estudiantes WHERE estado='Activo' ORDER BY apellidos,nombres")
    return render_template("acudientes/relaciones.html",acudiente=a,estudiantes=estudiantes,todos=todos)

@acudientes_bp.post("/<int:id>/relacionar")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def relacionar(id):
    try:
        ejecutar("INSERT INTO estudiante_acudiente(id_estudiante,id_acudiente,parentesco,principal,estado) VALUES(%s,%s,%s,%s,1)",(int(request.form["estudiante"]),id,request.form["parentesco"].strip(),1 if request.form.get("principal") else 0)); auditoria("RELACIONAR","Acudientes",id); flash("Relación creada.","success")
    except Exception: flash("La relación ya existe o es inválida.","error")
    return redirect(url_for("acudientes.relaciones",id=id))
