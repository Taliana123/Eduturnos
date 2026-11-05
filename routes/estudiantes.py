from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash
from database.db import consultar, ejecutar, transaccion
from routes.helpers import roles_permitidos, auditoria
from roles import es_documento_valido, es_nombre_valido
from servicios.estudiantes import codigo_final, codigo_temporal

estudiantes_bp=Blueprint("estudiantes",__name__,url_prefix="/estudiantes")

def catalogos():
    from routes.helpers import usuario_actual
    u = usuario_actual()
    tenant = u.get("id_institucion") if u and u.get("rol_nombre") != "Super Admin" else None
    return {
        "sedes": consultar("SELECT * FROM sedes WHERE estado=1 AND (%s IS NULL OR id_institucion=%s) ORDER BY nombre", (tenant, tenant)),
        "jornadas": consultar("SELECT * FROM jornadas WHERE estado=1 ORDER BY CASE nombre WHEN 'Mañana' THEN 1 WHEN 'Tarde' THEN 2 WHEN 'Noche' THEN 3 ELSE 4 END,nombre"),
        "periodos": consultar("SELECT * FROM periodos_academicos WHERE activo=1 AND cerrado=0 AND (%s IS NULL OR id_institucion=%s) ORDER BY id DESC", (tenant, tenant)),
        "grados": consultar("SELECT * FROM grados WHERE estado=1 ORDER BY CAST(nombre AS UNSIGNED),nombre"),
        "grupos": consultar(
            "SELECT g.id,g.id_grado,g.nombre,gr.nombre grado FROM grupos g "
            "JOIN grados gr ON gr.id=g.id_grado WHERE g.estado=1 "
            "ORDER BY CAST(gr.nombre AS UNSIGNED),gr.nombre,CAST(g.nombre AS UNSIGNED),g.nombre"
        ),
    }


def validar_formulario(datos):
    campos_obligatorios = ("tipo_documento", "documento", "nombres", "apellidos", "sede", "jornada", "periodo")
    if any(not datos.get(campo, "").strip() for campo in campos_obligatorios):
        return "Completa todos los campos obligatorios."
    if datos.get("tipo_documento") not in {"CC", "TI", "CE", "RC"}:
        return "Selecciona un tipo de documento válido."
    if not es_documento_valido(datos.get("documento", "")):
        return "El documento debe contener solo dígitos y no superar 30 caracteres."
    if not es_nombre_valido(datos.get("nombres", "")) or not es_nombre_valido(datos.get("apellidos", "")):
        return "Los nombres y apellidos solo pueden contener letras y espacios."
    if any(not datos.get(campo, "").isdigit() for campo in ("sede", "jornada", "periodo")):
        return "Selecciona una sede, jornada y periodo válidos."
    from routes.helpers import usuario_actual
    usuario = usuario_actual()
    if usuario and usuario["rol_nombre"] != "Super Admin":
        if not consultar("SELECT id FROM sedes WHERE id=%s AND id_institucion=%s AND estado=1", (datos["sede"], usuario.get("id_institucion")), uno=True):
            return "La sede seleccionada no pertenece a tu institución."
        if not consultar("SELECT id FROM periodos_academicos WHERE id=%s AND id_institucion=%s", (datos["periodo"], usuario.get("id_institucion")), uno=True):
            return "El periodo seleccionado no pertenece a tu institución."

    grado = datos.get("grado", "").strip()
    grupo = datos.get("grupo", "").strip()
    if grado and not grado.isdigit():
        return "Selecciona un grado válido."
    if grupo:
        if not grado or not grupo.isdigit():
            return "Selecciona primero el grado y luego un grupo del 1 al 6."
        existente = consultar(
            "SELECT id FROM grupos WHERE id=%s AND id_grado=%s AND estado=1 "
            "AND nombre IN ('1','2','3','4','5','6') LIMIT 1",
            (grupo, grado),
            uno=True,
        )
        if not existente:
            return "El grupo seleccionado no corresponde al grado."
    return None

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
    if u["rol_nombre"] != "Super Admin" and u.get("id_institucion"):
        filtro += " AND s.id_institucion=%s"
        parametros += (u["id_institucion"],)
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
    datos=request.form if request.method=="POST" else {}
    if request.method=="POST":
        d=request.form
        error=validar_formulario(d)
        if error:
            flash(error,"error")
            return render_template("estudiantes/form.html",catalogos=cat,estudiante=None,datos=datos)
        try:
            with transaccion() as cnx:
                cur = cnx.cursor()
                try:
                    cur.execute(
                        """INSERT INTO estudiantes(codigo_estudiantil,tipo_documento,documento,nombres,apellidos,id_sede,id_jornada,id_periodo,id_grado,id_grupo,estado)
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Activo')""",
                        (
                            codigo_temporal(), d["tipo_documento"], d["documento"],
                            d["nombres"], d["apellidos"], d["sede"], d["jornada"],
                            d["periodo"], d.get("grado") or None, d.get("grupo") or None,
                        ),
                    )
                    eid = cur.lastrowid
                    cur.execute(
                        "UPDATE estudiantes SET codigo_estudiantil=%s WHERE id_estudiante=%s",
                        (codigo_final(eid), eid),
                    )
                finally:
                    cur.close()
            auditoria("CREAR","Estudiantes",eid); flash(f"Estudiante creado. Código institucional: {codigo_final(eid)}","success"); return redirect(url_for("estudiantes.lista"))
        except Exception:
            current_app.logger.exception("No se pudo crear el estudiante.")
            flash("No se pudo crear el estudiante. Revisa los datos únicos y las selecciones.","error")
    return render_template("estudiantes/form.html",catalogos=cat,estudiante=None,datos=datos)

@estudiantes_bp.route("/<int:id>/editar",methods=["GET","POST"])
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def editar(id):
    from routes.helpers import usuario_actual
    u=usuario_actual()
    est=consultar("SELECT e.* FROM estudiantes e JOIN sedes s ON s.id=e.id_sede WHERE e.id_estudiante=%s AND (%s='Super Admin' OR s.id_institucion=%s)",(id,u["rol_nombre"],u.get("id_institucion")),uno=True); cat=catalogos()
    if not est: return redirect(url_for("estudiantes.lista"))
    datos=request.form if request.method=="POST" else {}
    if request.method=="POST":
        d=request.form
        error=validar_formulario(d)
        if error:
            flash(error,"error")
            return render_template("estudiantes/form.html",catalogos=cat,estudiante=est,datos=datos)
        try:
            sql_update="""UPDATE estudiantes SET tipo_documento=%s,documento=%s,nombres=%s,apellidos=%s,id_sede=%s,id_jornada=%s,id_periodo=%s,id_grado=%s,id_grupo=%s,estado=%s WHERE id_estudiante=%s"""
            update_params=(d["tipo_documento"],d["documento"],d["nombres"],d["apellidos"],d["sede"],d["jornada"],d["periodo"],d.get("grado") or None,d.get("grupo") or None,d.get("estado", "Activo"),id)
            if u["rol_nombre"] != "Super Admin":
                sql_update += " AND id_sede IN (SELECT id FROM sedes WHERE id_institucion=%s)"
                update_params += (u.get("id_institucion"),)
            ejecutar(sql_update,update_params)
            auditoria("ACTUALIZAR","Estudiantes",id); flash("Estudiante actualizado.","success"); return redirect(url_for("estudiantes.lista"))
        except Exception:
            current_app.logger.exception("No se pudo actualizar el estudiante %s.", id)
            flash("No se pudo actualizar el estudiante.","error")
    return render_template("estudiantes/form.html",catalogos=cat,estudiante=est,datos=datos)

@estudiantes_bp.post("/<int:id>/desactivar")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def desactivar(id):
    from routes.helpers import usuario_actual
    u=usuario_actual()
    if u["rol_nombre"] == "Super Admin":
        ejecutar("UPDATE estudiantes SET estado='Retirado' WHERE id_estudiante=%s",(id,))
    else:
        ejecutar("UPDATE estudiantes SET estado='Retirado' WHERE id_estudiante=%s AND id_sede IN (SELECT id FROM sedes WHERE id_institucion=%s)",(id,u.get("id_institucion")))
    auditoria("RETIRAR","Estudiantes",id); flash("Estudiante retirado.","success"); return redirect(url_for("estudiantes.lista"))
