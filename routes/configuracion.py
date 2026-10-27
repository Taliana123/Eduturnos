from __future__ import annotations

from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from mysql.connector import Error as MySQLError

from database.db import consultar, ejecutar
from routes.helpers import auditoria, roles_permitidos

configuracion_bp = Blueprint("configuracion", __name__, url_prefix="/configuracion")

OWNER = ("Super Admin", "Rector")
CONFIG_ROLES = ("Super Admin", "Rector", "Administrador / Coordinador")


def _texto(nombre: str, max_len: int, required: bool = True) -> str:
    value = (request.form.get(nombre) or "").strip()
    if required and not value:
        raise ValueError(f"El campo '{nombre}' es obligatorio.")
    if len(value) > max_len:
        raise ValueError(f"El campo '{nombre}' no puede superar {max_len} caracteres.")
    return value


def _entero(nombre: str, required: bool = True):
    value = (request.form.get(nombre) or "").strip()
    if not value and not required:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"El campo '{nombre}' debe ser válido.")


def _activo(nombre: str = "estado") -> int:
    return 1 if request.form.get(nombre) in {"1", "on", "true", "True"} else 0


def _fijar_estado(tabla: str, columna_id: str, registro_id: int) -> None:
    estado_objetivo = request.form.get("estado_objetivo")
    if estado_objetivo in {"0", "1"}:
        ejecutar(
            f"UPDATE {tabla} SET estado=%s WHERE {columna_id}=%s",
            (int(estado_objetivo), registro_id),
        )
    else:
        ejecutar(
            f"UPDATE {tabla} SET estado=1-estado WHERE {columna_id}=%s",
            (registro_id,),
        )


def _institucion_actual():
    return consultar("SELECT * FROM instituciones ORDER BY id LIMIT 1", uno=True)


@configuracion_bp.get("/")
@roles_permitidos(*CONFIG_ROLES)
def index():
    cuentas = []
    total_cuentas = 0
    if usuario_rol() in OWNER:
        cuentas = consultar(
            "SELECT u.id_usuario,u.tipo_documento,u.documento,u.nombres,u.apellidos,u.correo, "
            "u.estado,u.bloqueado_hasta,u.fecha_creacion,r.nombre AS rol_nombre "
            "FROM usuarios u JOIN roles r ON r.id=u.id_rol "
            "ORDER BY u.fecha_creacion DESC,u.id_usuario DESC"
        )
        total_cuentas = (consultar("SELECT COUNT(*) total FROM usuarios", uno=True) or {}).get("total", 0)
    return render_template(
        "configuracion/index.html",
        institucion=_institucion_actual(),
        periodos=consultar("SELECT * FROM periodos_academicos ORDER BY fecha_inicio DESC, id DESC"),
        sedes=consultar(
            "SELECT s.*, i.nombre AS institucion_nombre FROM sedes s "
            "JOIN instituciones i ON i.id=s.id_institucion ORDER BY s.estado DESC, s.nombre"
        ),
        jornadas=consultar(
            "SELECT * FROM jornadas ORDER BY estado DESC, "
            "CASE nombre WHEN 'Mañana' THEN 1 WHEN 'Tarde' THEN 2 "
            "WHEN 'Noche' THEN 3 ELSE 4 END, nombre"
        ),
        grados=consultar("SELECT * FROM grados ORDER BY CAST(nombre AS UNSIGNED), nombre"),
        grupos=consultar(
            "SELECT g.*, gr.nombre AS grado_nombre FROM grupos g JOIN grados gr ON gr.id=g.id_grado "
            "ORDER BY CAST(gr.nombre AS UNSIGNED), gr.nombre, CAST(g.nombre AS UNSIGNED), g.nombre"
        ),
        motivos=consultar("SELECT * FROM motivos ORDER BY estado DESC, nombre"),
        estados=consultar("SELECT * FROM estados_cita ORDER BY estado DESC, id"),
        puede_editar_institucion=usuario_rol() in OWNER,
        cuentas=cuentas,
        total_cuentas=total_cuentas,
        usuario_sesion_id=session.get("usuario_id"),
    )


def usuario_rol() -> str:
    from routes.helpers import usuario_actual
    usuario = usuario_actual()
    return usuario["rol_nombre"] if usuario else ""


# ---------------------------------------------------------------------------
# Institución y periodos: Rector/Super Admin.
# ---------------------------------------------------------------------------

@configuracion_bp.post("/institucion/guardar")
@roles_permitidos(*OWNER)
def guardar_institucion():
    try:
        institucion_id = _entero("id_institucion", required=False)
        nombre = _texto("nombre", 180)
        ciudad = _texto("ciudad", 100)
        departamento = _texto("departamento", 100)
        if institucion_id:
            ejecutar(
                "UPDATE instituciones SET nombre=%s,ciudad=%s,departamento=%s WHERE id=%s",
                (nombre, ciudad, departamento, institucion_id),
            )
        else:
            institucion_id = ejecutar(
                "INSERT INTO instituciones(nombre,ciudad,departamento) VALUES(%s,%s,%s)",
                (nombre, ciudad, departamento),
            )
        auditoria("ACTUALIZAR", "Configuración", institucion_id, "Institución actualizada")
        flash("Datos de la institución guardados en MySQL.", "success")
    except (ValueError, MySQLError) as exc:
        flash(f"No se pudo guardar la institución: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/institucion/<int:institucion_id>/toggle")
@roles_permitidos(*OWNER)
def toggle_institucion(institucion_id):
    try:
        _fijar_estado("instituciones", "id", institucion_id)
        auditoria("CAMBIAR_ESTADO", "Configuración", institucion_id, "Estado de institución cambiado")
        flash("Estado de la institución actualizado.", "success")
    except MySQLError as exc:
        flash(f"No se pudo cambiar el estado: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/periodo/nuevo")
@roles_permitidos(*OWNER)
def nuevo_periodo():
    try:
        nombre = _texto("nombre", 80)
        inicio = _texto("inicio", 10)
        fin = _texto("fin", 10)
        inicio_d = date.fromisoformat(inicio)
        fin_d = date.fromisoformat(fin)
        if fin_d < inicio_d:
            raise ValueError("La fecha final no puede ser anterior a la fecha inicial.")
        ejecutar(
            "INSERT INTO periodos_academicos(nombre,fecha_inicio,fecha_fin,activo,cerrado) VALUES(%s,%s,%s,0,0)",
            (nombre, inicio, fin),
        )
        auditoria("CREAR", "Configuración", None, f"Periodo {nombre}")
        flash("Periodo creado correctamente.", "success")
    except (ValueError, MySQLError) as exc:
        flash(f"No se pudo crear el periodo: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/periodo/<int:periodo_id>/activar")
@roles_permitidos(*OWNER)
def activar_periodo(periodo_id):
    periodo = consultar("SELECT * FROM periodos_academicos WHERE id=%s", (periodo_id,), uno=True)
    if not periodo or periodo["cerrado"]:
        flash("El periodo no existe o ya está cerrado.", "error")
        return redirect(url_for("configuracion.index"))
    ejecutar("UPDATE periodos_academicos SET activo=0")
    ejecutar("UPDATE periodos_academicos SET activo=1 WHERE id=%s AND cerrado=0", (periodo_id,))
    auditoria("ACTIVAR", "Configuración", periodo_id, "Periodo académico activado")
    flash("Periodo activo actualizado.", "success")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/periodo/<int:periodo_id>/cerrar")
@roles_permitidos(*OWNER)
def cerrar_periodo(periodo_id):
    ejecutar("UPDATE periodos_academicos SET activo=0,cerrado=1 WHERE id=%s", (periodo_id,))
    auditoria("CERRAR", "Configuración", periodo_id, "Periodo académico cerrado")
    flash("Periodo cerrado.", "success")
    return redirect(url_for("configuracion.index"))


# ---------------------------------------------------------------------------
# Catálogos: Super Admin, Rector y Coordinador.
# ---------------------------------------------------------------------------

@configuracion_bp.post("/sede/guardar")
@roles_permitidos(*CONFIG_ROLES)
def guardar_sede():
    try:
        sede_id = _entero("id_sede", required=False)
        institucion_id = _entero("id_institucion")
        nombre = _texto("nombre", 140)
        direccion = _texto("direccion", 255, required=False)
        codigo = _texto("codigo_sede", 6, required=False)
        if codigo and (len(codigo) != 6 or not codigo.isdigit()):
            raise ValueError("El código de sede debe tener 6 dígitos.")
        estado = _activo()
        if not consultar("SELECT id FROM instituciones WHERE id=%s", (institucion_id,), uno=True):
            raise ValueError("La institución seleccionada no existe.")
        if sede_id:
            ejecutar(
                "UPDATE sedes SET id_institucion=%s,nombre=%s,direccion=%s,codigo_sede=%s,estado=%s WHERE id=%s",
                (institucion_id, nombre, direccion or None, codigo or None, estado, sede_id),
            )
        else:
            sede_id = ejecutar(
                "INSERT INTO sedes(id_institucion,nombre,direccion,codigo_sede,estado) VALUES(%s,%s,%s,%s,%s)",
                (institucion_id, nombre, direccion or None, codigo or None, estado),
            )
        auditoria("GUARDAR", "Configuración", sede_id, f"Sede {nombre}")
        flash("Sede guardada en MySQL.", "success")
    except (ValueError, MySQLError) as exc:
        flash(f"No se pudo guardar la sede: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/sede/<int:sede_id>/toggle")
@roles_permitidos(*CONFIG_ROLES)
def toggle_sede(sede_id):
    try:
        _fijar_estado("sedes", "id", sede_id)
        auditoria("CAMBIAR_ESTADO", "Configuración", sede_id, "Estado de sede cambiado")
        flash("Estado de sede actualizado.", "success")
    except MySQLError as exc:
        flash(f"No se pudo cambiar el estado de la sede: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/jornada/guardar")
@roles_permitidos(*CONFIG_ROLES)
def guardar_jornada():
    try:
        jornada_id = _entero("id_jornada", required=False)
        nombre = _texto("nombre", 50)
        estado = _activo()
        if jornada_id:
            ejecutar("UPDATE jornadas SET nombre=%s,estado=%s WHERE id=%s", (nombre, estado, jornada_id))
        else:
            jornada_id = ejecutar("INSERT INTO jornadas(nombre,estado) VALUES(%s,%s)", (nombre, estado))
        auditoria("GUARDAR", "Configuración", jornada_id, f"Jornada {nombre}")
        flash("Jornada guardada en MySQL.", "success")
    except (ValueError, MySQLError) as exc:
        flash(f"No se pudo guardar la jornada: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/jornada/<int:jornada_id>/toggle")
@roles_permitidos(*CONFIG_ROLES)
def toggle_jornada(jornada_id):
    try:
        _fijar_estado("jornadas", "id", jornada_id)
        auditoria("CAMBIAR_ESTADO", "Configuración", jornada_id, "Estado de jornada cambiado")
        flash("Estado de jornada actualizado.", "success")
    except MySQLError as exc:
        flash(f"No se pudo cambiar el estado: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/grado/guardar")
@roles_permitidos(*CONFIG_ROLES)
def guardar_grado():
    try:
        grado_id = _entero("id_grado", required=False)
        nombre = _texto("nombre", 30)
        estado = _activo()
        if grado_id:
            ejecutar("UPDATE grados SET nombre=%s,estado=%s WHERE id=%s", (nombre, estado, grado_id))
        else:
            grado_id = ejecutar("INSERT INTO grados(nombre,estado) VALUES(%s,%s)", (nombre, estado))
        auditoria("GUARDAR", "Configuración", grado_id, f"Grado {nombre}")
        flash("Grado guardado en MySQL.", "success")
    except (ValueError, MySQLError) as exc:
        flash(f"No se pudo guardar el grado: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/grado/<int:grado_id>/toggle")
@roles_permitidos(*CONFIG_ROLES)
def toggle_grado(grado_id):
    try:
        _fijar_estado("grados", "id", grado_id)
        auditoria("CAMBIAR_ESTADO", "Configuración", grado_id, "Estado de grado cambiado")
        flash("Estado de grado actualizado.", "success")
    except MySQLError as exc:
        flash(f"No se pudo cambiar el estado: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/grupo/guardar")
@roles_permitidos(*CONFIG_ROLES)
def guardar_grupo():
    try:
        grupo_id = _entero("id_grupo", required=False)
        grado_id = _entero("id_grado")
        nombre = _texto("nombre", 20)
        estado = _activo()
        if not consultar("SELECT id FROM grados WHERE id=%s", (grado_id,), uno=True):
            raise ValueError("El grado seleccionado no existe.")
        if grupo_id:
            ejecutar("UPDATE grupos SET id_grado=%s,nombre=%s,estado=%s WHERE id=%s", (grado_id, nombre, estado, grupo_id))
        else:
            grupo_id = ejecutar("INSERT INTO grupos(id_grado,nombre,estado) VALUES(%s,%s,%s)", (grado_id, nombre, estado))
        auditoria("GUARDAR", "Configuración", grupo_id, f"Grupo {nombre}")
        flash("Grupo guardado en MySQL.", "success")
    except (ValueError, MySQLError) as exc:
        flash(f"No se pudo guardar el grupo: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/grupo/<int:grupo_id>/toggle")
@roles_permitidos(*CONFIG_ROLES)
def toggle_grupo(grupo_id):
    try:
        _fijar_estado("grupos", "id", grupo_id)
        auditoria("CAMBIAR_ESTADO", "Configuración", grupo_id, "Estado de grupo cambiado")
        flash("Estado de grupo actualizado.", "success")
    except MySQLError as exc:
        flash(f"No se pudo cambiar el estado: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/motivo/guardar")
@roles_permitidos(*CONFIG_ROLES)
def guardar_motivo():
    try:
        motivo_id = _entero("id_motivo", required=False)
        nombre = _texto("nombre", 120)
        estado = _activo()
        if motivo_id:
            ejecutar("UPDATE motivos SET nombre=%s,estado=%s WHERE id=%s", (nombre, estado, motivo_id))
        else:
            motivo_id = ejecutar("INSERT INTO motivos(nombre,estado) VALUES(%s,%s)", (nombre, estado))
        auditoria("GUARDAR", "Configuración", motivo_id, f"Motivo {nombre}")
        flash("Motivo guardado en MySQL.", "success")
    except (ValueError, MySQLError) as exc:
        flash(f"No se pudo guardar el motivo: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/motivo/<int:motivo_id>/toggle")
@roles_permitidos(*CONFIG_ROLES)
def toggle_motivo(motivo_id):
    try:
        _fijar_estado("motivos", "id", motivo_id)
        auditoria("CAMBIAR_ESTADO", "Configuración", motivo_id, "Estado de motivo cambiado")
        flash("Estado de motivo actualizado.", "success")
    except MySQLError as exc:
        flash(f"No se pudo cambiar el estado: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/estado/guardar")
@roles_permitidos(*CONFIG_ROLES)
def guardar_estado():
    try:
        estado_id = _entero("id_estado", required=False)
        nombre = _texto("nombre", 40)
        activo = _activo()
        if estado_id:
            ejecutar("UPDATE estados_cita SET nombre=%s,estado=%s WHERE id=%s", (nombre, activo, estado_id))
        else:
            estado_id = ejecutar("INSERT INTO estados_cita(nombre,estado) VALUES(%s,%s)", (nombre, activo))
        auditoria("GUARDAR", "Configuración", estado_id, f"Estado de cita {nombre}")
        flash("Estado de citación guardado en MySQL.", "success")
    except (ValueError, MySQLError) as exc:
        flash(f"No se pudo guardar el estado: {exc}", "error")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/estado/<int:estado_id>/toggle")
@roles_permitidos(*CONFIG_ROLES)
def toggle_estado(estado_id):
    try:
        _fijar_estado("estados_cita", "id", estado_id)
        auditoria("CAMBIAR_ESTADO", "Configuración", estado_id, "Estado de citación cambiado")
        flash("Estado de citación actualizado.", "success")
    except MySQLError as exc:
        flash(f"No se pudo cambiar el estado: {exc}", "error")
    return redirect(url_for("configuracion.index"))




@configuracion_bp.post("/cuenta/<int:usuario_id>/bloquear")
@roles_permitidos(*OWNER)
def bloquear_cuenta(usuario_id):
    if usuario_id == session.get("usuario_id"):
        flash("No puedes bloquear tu propia cuenta mientras tienes la sesi?n abierta.", "error")
        return redirect(url_for("configuracion.index"))
    cuenta = consultar("SELECT id_usuario,estado FROM usuarios WHERE id_usuario=%s", (usuario_id,), uno=True)
    if not cuenta or not cuenta.get("estado"):
        flash("La cuenta no est? activa.", "error")
    else:
        ejecutar("UPDATE usuarios SET bloqueado_hasta='9999-12-31 23:59:59' WHERE id_usuario=%s", (usuario_id,))
        auditoria("BLOQUEAR", "Usuarios", usuario_id, "Cuenta bloqueada desde Configuraci?n institucional")
        flash("Cuenta bloqueada. Su historial se conserva.", "success")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/cuenta/<int:usuario_id>/desbloquear")
@roles_permitidos(*OWNER)
def desbloquear_cuenta(usuario_id):
    ejecutar("UPDATE usuarios SET bloqueado_hasta=NULL WHERE id_usuario=%s AND estado=1", (usuario_id,))
    auditoria("DESBLOQUEAR", "Usuarios", usuario_id, "Bloqueo de cuenta retirado")
    flash("Cuenta desbloqueada.", "success")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/cuenta/<int:usuario_id>/reactivar")
@roles_permitidos(*OWNER)
def reactivar_cuenta(usuario_id):
    cuenta = consultar("SELECT id_usuario FROM usuarios WHERE id_usuario=%s", (usuario_id,), uno=True)
    if not cuenta:
        flash("La cuenta no existe.", "error")
    else:
        ejecutar("UPDATE usuarios SET estado=1,bloqueado_hasta=NULL WHERE id_usuario=%s", (usuario_id,))
        auditoria("REACTIVAR", "Usuarios", usuario_id, "Cuenta reactivada desde Configuraci?n institucional")
        flash("Cuenta reactivada.", "success")
    return redirect(url_for("configuracion.index"))


@configuracion_bp.post("/cuenta/<int:usuario_id>/retirar-acceso")
@roles_permitidos(*OWNER)
def retirar_acceso_cuenta(usuario_id):
    if usuario_id == session.get("usuario_id"):
        flash("No puedes retirar el acceso de tu propia cuenta.", "error")
        return redirect(url_for("configuracion.index"))
    cuenta = consultar("SELECT u.id_usuario,u.estado,r.nombre rol FROM usuarios u JOIN roles r ON r.id=u.id_rol WHERE u.id_usuario=%s", (usuario_id,), uno=True)
    if not cuenta:
        flash("La cuenta no existe.", "error")
    elif cuenta["rol"] == "Super Admin" and int((consultar("SELECT COUNT(*) total FROM usuarios u JOIN roles r ON r.id=u.id_rol WHERE r.nombre='Super Admin' AND u.estado=1", uno=True) or {}).get("total", 0)) <= 1:
        flash("No se puede retirar el acceso del ?ltimo Super Admin activo.", "error")
    else:
        ejecutar("UPDATE usuarios SET estado=0,bloqueado_hasta=NULL WHERE id_usuario=%s", (usuario_id,))
        auditoria("RETIRAR_ACCESO", "Usuarios", usuario_id, "Cuenta desactivada; historial conservado")
        flash("Acceso retirado. El registro y las citas hist?ricas se conservan.", "success")
    return redirect(url_for("configuracion.index"))


# Acceso informativo y auditoría.
@configuracion_bp.get("/arquitectura")
@roles_permitidos(*CONFIG_ROLES, "Docente", "Acudiente", "Estudiante")
def arquitectura():
    return render_template("configuracion/arquitectura.html")


@configuracion_bp.get("/auditoria")
@roles_permitidos(*OWNER)
def auditoria_view():
    datos = consultar(
        "SELECT a.*,u.nombres,u.apellidos FROM auditoria a "
        "LEFT JOIN usuarios u ON u.id_usuario=a.id_usuario "
        "ORDER BY a.fecha_creacion DESC LIMIT 500"
    )
    return render_template("configuracion/auditoria.html", datos=datos)
