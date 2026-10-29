from datetime import date, datetime
from html import escape
from io import BytesIO

from flask import Blueprint, Response, render_template, request, redirect, url_for, flash, abort, jsonify

from database.db import consultar, ejecutar, transaccion
from servicios.reuniones import PERSONAL, bloquear_agenda, comprobar_hueco, datos_escolares, formatear_hora, reservar_cita, validar_compromiso, validar_disponibilidad, validar_franja
from routes.helpers import (
    usuario_actual,
    login_requerido,
    roles_permitidos,
    notificar,
    auditoria,
)


citas_bp = Blueprint("citas", __name__, url_prefix="/citas")
ROLES_CREADORES_CITA = {
    "Rector",
    "Administrador / Coordinador",
    "Docente",
}


def _acudiente_puede_confirmar(estado_actual, estado_nuevo):
    return (
        estado_nuevo == "Confirmada"
        and estado_actual in {"Pendiente", "Reprogramada"}
    )


TRANSICIONES_ESTADO = {
    "Pendiente": {"Confirmada", "Cancelada", "Reprogramada"},
    "Confirmada": {"Cancelada", "Reprogramada"},
    "Reprogramada": {"Pendiente", "Confirmada", "Cancelada"},
    "Realizada": set(),
    "No asistió": {"Justificada"},
    "Cancelada": set(),
    "Justificada": set(),
}
def _motivo_cita(motivo_id, usuario):
    motivo = consultar(
        "SELECT id,nombre FROM motivos WHERE id=%s AND estado=1",
        (motivo_id,),
        uno=True,
    )
    if not motivo:
        raise ValueError("El motivo seleccionado no está disponible.")
    texto = None
    if str(motivo.get("nombre", "")).strip().casefold() == "otro":
        texto = (request.form.get("motivo_otro") or "").strip()
        if not texto or len(texto) > 255:
            raise ValueError("Describe el motivo en un máximo de 255 caracteres.")
    return motivo, texto


def _transicion_estado_permitida(rol, actual, nuevo):
    if rol == "Acudiente":
        return _acudiente_puede_confirmar(actual, nuevo)
    return nuevo in TRANSICIONES_ESTADO.get(actual, set())


def _validar_fecha_cita(fecha):
    fecha_obj = date.fromisoformat(fecha)

    if fecha_obj < date.today():
        raise ValueError(
            "La fecha de la cita no puede ser anterior a hoy."
        )

    return fecha_obj


def _destino_cita_creada(fecha):
    es_movil = request.form.get("vista_movil") == "1" or any(
        dispositivo in request.user_agent.string
        for dispositivo in ("Android", "iPhone", "iPad")
    )
    if es_movil:
        fecha_obj = date.fromisoformat(fecha)
        return url_for(
            "calendario.index",
            anio=fecha_obj.year,
            mes=fecha_obj.month,
            dia=fecha,
        )
    return url_for("citas.index")


def _validar_cierre_cita(asistencia, resultado):
    if asistencia not in ("Asistió", "No asistió"):
        raise ValueError("Selecciona si los participantes asistieron a la cita.")
    resultado = resultado.strip()
    if not resultado or len(resultado) > 10000:
        raise ValueError("Registra un resultado de entre 1 y 10000 caracteres.")
    return "Realizada" if asistencia == "Asistió" else "No asistió", resultado


def _es_creador_habilitado(usuario, cita):
    return (
        usuario["rol_nombre"] in ROLES_CREADORES_CITA
        and cita.get("creado_por") is not None
        and int(cita["creado_por"]) == int(usuario["id_usuario"])
    )


@citas_bp.post("/<int:cita_id>/cerrar")
@roles_permitidos("Super Admin", "Rector", "Administrador / Coordinador", "Docente")
def cerrar_cita(cita_id):
    usuario = usuario_actual()
    try:
        estado_nombre, resultado = _validar_cierre_cita(
            request.form.get("asistencia", ""), request.form.get("resultado", "")
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))
    where, params = _visible(usuario)
    where = f"{where} AND c.id = %s" if where else " WHERE c.id = %s"
    with transaccion() as conexion:
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT c.id, c.id_estado, ec.nombre AS estado FROM citas c "
                "JOIN estados_cita ec ON ec.id = c.id_estado" + where + " FOR UPDATE",
                tuple(params + [cita_id]),
            )
            cita = cursor.fetchone()
            if not cita:
                abort(404)
            if cita["estado"] != "Confirmada":
                abort(409, description="Solo se puede cerrar una cita confirmada y aún abierta.")
            cursor.execute("SELECT id FROM estados_cita WHERE nombre=%s AND estado=1", (estado_nombre,))
            estado = cursor.fetchone()
            if not estado:
                abort(409, description="No está disponible el estado de cierre.")
            cursor.execute(
                "INSERT INTO seguimiento_citas(id_cita,estado_actual,asistencia,observaciones,realizado_por) "
                "VALUES(%s,%s,%s,%s,%s)",
                (cita_id, estado_nombre, request.form["asistencia"], resultado, usuario["id_usuario"]),
            )
            cursor.execute("INSERT INTO cierres_cita(id_cita,asistencia,resultado,cerrado_por) VALUES(%s,%s,%s,%s)", (cita_id, request.form["asistencia"], resultado, usuario["id_usuario"]))
            cursor.execute("UPDATE citas SET id_estado=%s WHERE id=%s AND id_estado=%s", (estado["id"], cita_id, cita["id_estado"]))
            if cursor.rowcount != 1:
                abort(409, description="La cita cambió mientras se guardaba. Recarga la página.")
        finally:
            cursor.close()
    auditoria("CERRAR", "Citas", cita_id, f"Asistencia: {request.form['asistencia']}")
    _notificar(cita_id, "Resultado de la citación", f"La citación ahora está en estado: {estado_nombre}.")
    flash("Cita cerrada y resultado registrado.", "success")
    return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))


def _cita_horario_ocupado(docente_id, estudiante_id, acudiente_id, fecha, hora):
    return consultar(
        """
        SELECT id
        FROM citas
        WHERE fecha = %s
          AND hora = %s
          AND (
              id_docente = %s
              OR id_estudiante = %s
              OR id_acudiente = %s
          )
        LIMIT 1
        """,
        (fecha, hora, docente_id, estudiante_id, acudiente_id),
        uno=True,
    )


# =========================================================
# VISIBILIDAD DE CITAS SEGÚN EL ROL
# =========================================================

def _visible(usuario):
    rol = usuario["rol_nombre"]
    params = []
    filtros = []

    # Estos roles pueden consultar todas las citas.
    if rol not in (
        "Super Admin",
        "Rector",
        "Administrador / Coordinador",
    ):

        if rol == "Docente":
            relacion = "c.id_docente=(SELECT d.id_docente FROM docentes d WHERE d.id_usuario=%s)"
            relacion_params = [usuario["id_usuario"]]
        elif rol == "Estudiante":
            relacion = "c.id_estudiante=(SELECT e.id_estudiante FROM estudiantes e WHERE e.documento=%s)"
            relacion_params = [usuario["documento"]]
        elif rol == "Acudiente":
            relacion = "c.id_acudiente=(SELECT a.id_acudiente FROM acudientes a WHERE a.id_usuario=%s)"
            relacion_params = [usuario["id_usuario"]]
        else:
            relacion = "1=0"
            relacion_params = []

        filtros.append(
            f"({relacion} OR c.destinatario_usuario_id=%s OR c.creado_por=%s "
            "OR EXISTS (SELECT 1 FROM cita_participantes cp "
            "WHERE cp.id_cita=c.id AND cp.id_usuario=%s))"
        )
        params.extend(relacion_params + [usuario["id_usuario"]] * 3)

    if filtros:
        return " WHERE " + " AND ".join(filtros), params

    return "", params


# =========================================================
# CONSULTAR CITAS
# =========================================================

def consultar_citas(usuario):
    where, params = _visible(usuario)

    sql = f"""
        SELECT
            c.id,
            c.id_estudiante,
            c.id_acudiente,
            c.creado_por,
            c.destinatario_usuario_id,
            c.fecha,
            c.hora,
            c.lugar,
            c.observaciones,
            gr.nombre AS grado,
            grupo.nombre AS grupo,
            jornada.nombre AS jornada,
            sede.nombre AS sede,

            CASE WHEN c.destinatario_tipo IS NOT NULL
                THEN CONCAT(COALESCE(dest.nombres,''), ' ', COALESCE(dest.apellidos,''))
                ELSE CONCAT(COALESCE(e.nombres,''), ' ', COALESCE(e.apellidos,'')) END AS estudiante,
            c.destinatario_tipo,
            CONCAT(COALESCE(d.nombres,''), ' ', COALESCE(d.apellidos,'')) AS docente,
            CONCAT(COALESCE(a.nombres,''), ' ', COALESCE(a.apellidos,'')) AS acudiente,

            COALESCE(NULLIF(c.motivo_otro,''),m.nombre) AS motivo,

            ec.nombre AS estado,
            creador_rol.nombre AS creador_rol

        FROM citas c

        LEFT JOIN estudiantes e
            ON e.id_estudiante = c.id_estudiante
        LEFT JOIN usuarios dest ON dest.id_usuario=c.destinatario_usuario_id

        LEFT JOIN grados gr ON gr.id=e.id_grado
        LEFT JOIN grupos grupo ON grupo.id=e.id_grupo
        LEFT JOIN jornadas jornada ON jornada.id=e.id_jornada
        LEFT JOIN sedes sede ON sede.id=e.id_sede

        LEFT JOIN docentes d
            ON d.id_docente = c.id_docente

        LEFT JOIN acudientes a
            ON a.id_acudiente = c.id_acudiente

        JOIN motivos m
            ON m.id = c.id_motivo

        JOIN estados_cita ec
            ON ec.id = c.id_estado
        LEFT JOIN usuarios creador
            ON creador.id_usuario = c.creado_por
        LEFT JOIN roles creador_rol
            ON creador_rol.id = creador.id_rol

        {where}

        ORDER BY
            c.fecha DESC,
            c.hora DESC,
            c.id DESC
    """

    return consultar(sql, tuple(params))


# =========================================================
# CATÁLOGOS PARA CREAR UNA CITA
# =========================================================

def catalogos(usuario=None):
    # The GET route passes the logged-in user; callers that only need the
    # public catalogs can omit it without requiring a Flask request context.
    return {
        "estudiantes": consultar(
            """
            SELECT
                e.id_estudiante,
                e.documento,
                (SELECT ea.id_acudiente FROM estudiante_acudiente ea
                 JOIN acudientes ap ON ap.id_acudiente=ea.id_acudiente AND ap.estado=1
                 WHERE ea.id_estudiante=e.id_estudiante AND ea.estado=1
                 ORDER BY ea.principal DESC,ea.id_acudiente ASC LIMIT 1) AS acudiente_principal_id,
                CONCAT(e.nombres, ' ', e.apellidos) AS nombre,
                g.nombre AS grado,
                jornada.nombre AS jornada

            FROM estudiantes e

            LEFT JOIN grados g
                ON g.id = e.id_grado
            LEFT JOIN jornadas jornada
                ON jornada.id = e.id_jornada

            WHERE e.estado = 'Activo'

            ORDER BY
                e.apellidos,
                e.nombres
            """
        ),

        "docentes": consultar(
            """
            SELECT
                d.id_docente,
                CONCAT(d.nombres, ' ', d.apellidos) AS nombre,
                asignaciones.grados AS grado,
                jornada.nombre AS jornada

            FROM docentes d
            LEFT JOIN jornadas jornada
                ON jornada.id = d.id_jornada
            LEFT JOIN (
                SELECT
                    asignacion.id_docente,
                    GROUP_CONCAT(
                        DISTINCT COALESCE(grado_estudiante.nombre, grado_grupo.nombre)
                        ORDER BY COALESCE(grado_estudiante.nombre, grado_grupo.nombre)
                        SEPARATOR ', '
                    ) AS grados
                FROM asignaciones_docentes asignacion
                LEFT JOIN estudiantes estudiante
                    ON estudiante.id_estudiante = asignacion.id_estudiante
                LEFT JOIN grados grado_estudiante
                    ON grado_estudiante.id = estudiante.id_grado
                LEFT JOIN grupos grupo
                    ON grupo.id = asignacion.id_grupo
                LEFT JOIN grados grado_grupo
                    ON grado_grupo.id = grupo.id_grado
                WHERE asignacion.estado = 1
                GROUP BY asignacion.id_docente
            ) asignaciones
                ON asignaciones.id_docente = d.id_docente

            WHERE d.estado = 1

            ORDER BY
                d.apellidos,
                d.nombres
            """
        ),

        "acudientes": consultar(
            """
            SELECT
                acudiente.id_acudiente,
                CONCAT(acudiente.nombres, ' ', acudiente.apellidos) AS nombre,
                contexto.grados AS grado,
                contexto.jornadas AS jornada

            FROM acudientes acudiente
            LEFT JOIN (
                SELECT
                    relacion.id_acudiente,
                    GROUP_CONCAT(
                        DISTINCT grado.nombre
                        ORDER BY grado.nombre
                        SEPARATOR ', '
                    ) AS grados,
                    GROUP_CONCAT(
                        DISTINCT jornada.nombre
                        ORDER BY jornada.nombre
                        SEPARATOR ', '
                    ) AS jornadas
                FROM estudiante_acudiente relacion
                JOIN estudiantes estudiante
                    ON estudiante.id_estudiante = relacion.id_estudiante
                LEFT JOIN grados grado
                    ON grado.id = estudiante.id_grado
                LEFT JOIN jornadas jornada
                    ON jornada.id = estudiante.id_jornada
                WHERE relacion.estado = 1
                  AND estudiante.estado = 'Activo'
                GROUP BY relacion.id_acudiente
            ) contexto
                ON contexto.id_acudiente = acudiente.id_acudiente

            WHERE acudiente.estado = 1

            ORDER BY
                acudiente.apellidos,
                acudiente.nombres
            """
        ),

        "motivos": consultar(
            """
            SELECT
                id,
                nombre

            FROM motivos

            WHERE estado = 1

            ORDER BY nombre
            """
        ),

        "periodos": consultar(
            """
            SELECT id,nombre FROM periodos_academicos
            WHERE activo=1 AND cerrado=0 ORDER BY id DESC
            """
        ),
        "personal_destinatarios": consultar(
            "SELECT u.id_usuario,u.nombres,u.apellidos,u.correo,r.nombre AS rol_nombre, "
            "COALESCE(d.documento,u.documento,'') AS documento, "
            "COALESCE(NULLIF(d.asignatura,''),NULLIF(d.area,''),'') AS materia, "
            "d.id_docente FROM usuarios u JOIN roles r ON r.id=u.id_rol "
            "LEFT JOIN docentes d ON d.id_usuario=u.id_usuario AND d.estado=1 "
            "WHERE u.estado=1 AND r.nombre IN ('Rector','Administrador / Coordinador','Docente') "
            "ORDER BY r.nombre,u.apellidos,u.nombres"
        ),
        "mi_docente_id": (consultar("SELECT id_docente FROM docentes WHERE id_usuario=%s AND estado=1", (usuario["id_usuario"],), uno=True) or {}).get("id_docente") if usuario else None,
    }


@citas_bp.get("/buscar-estudiante-documento")
@roles_permitidos("Super Admin", "Rector", "Administrador / Coordinador", "Docente")
def buscar_estudiante_documento():
    """Busca por documento y devuelve solo el estudiante y sus acudientes vinculados."""
    documento = request.args.get("documento", "").strip()
    if not documento or len(documento) > 30:
        return jsonify({"ok": False, "error": "Ingresa un número de documento válido."}), 400

    estudiante = consultar(
        """SELECT e.id_estudiante, e.documento,
                  CONCAT(e.nombres, ' ', e.apellidos) AS nombre,
                  COALESCE(g.nombre, '') AS grado,
                  COALESCE(j.nombre, '') AS jornada
           FROM estudiantes e
           LEFT JOIN grados g ON g.id = e.id_grado
           LEFT JOIN jornadas j ON j.id = e.id_jornada
           WHERE e.documento = %s AND e.estado = 'Activo'
           LIMIT 1""",
        (documento,), uno=True,
    )
    if not estudiante:
        return jsonify({"ok": False, "error": "No hay un estudiante activo con ese documento."}), 404

    usuario = usuario_actual()
    if usuario.get("rol_nombre") == "Docente":
        asignado = consultar(
            """SELECT 1 FROM docentes d
               JOIN asignaciones_docentes ad ON ad.id_docente = d.id_docente AND ad.estado = 1
               JOIN estudiantes e ON e.id_estudiante = %s
               WHERE d.id_usuario = %s
                 AND (ad.id_estudiante = e.id_estudiante OR
                      (ad.id_estudiante IS NULL AND ad.id_grupo = e.id_grupo))
               LIMIT 1""",
            (estudiante["id_estudiante"], usuario["id_usuario"]), uno=True,
        )
        if not asignado:
            return jsonify({"ok": False, "error": "Ese estudiante no está asignado a tu usuario."}), 403

    acudientes = consultar(
        """SELECT a.id_acudiente, CONCAT(a.nombres, ' ', a.apellidos) AS nombre, ea.principal
           FROM estudiante_acudiente ea
           JOIN acudientes a ON a.id_acudiente = ea.id_acudiente
           WHERE ea.id_estudiante = %s AND ea.estado = 1 AND a.estado = 1
           ORDER BY ea.principal DESC, a.apellidos, a.nombres""",
        (estudiante["id_estudiante"],),
    )
    principal = next((item for item in acudientes if item.get("principal")), None)
    return jsonify({
        "ok": True,
        "estudiante": estudiante,
        "acudientes": acudientes,
        "acudiente_principal_id": principal.get("id_acudiente") if principal else None,
    })


@citas_bp.get("/buscar-destinatario-documento")
@roles_permitidos("Super Admin", "Rector", "Administrador / Coordinador", "Docente")
def buscar_destinatario_documento():
    documento = request.args.get("documento", "").strip()
    tipo = request.args.get("tipo", "").strip()
    usuario = usuario_actual()
    tipos_permitidos = {
        "Super Admin": {"Docente", "Administrador / Coordinador"},
        "Rector": {"Docente", "Administrador / Coordinador"},
        "Administrador / Coordinador": {"Rector", "Docente"},
        "Docente": {"Rector", "Administrador / Coordinador"},
    }
    if not documento or len(documento) > 30:
        return jsonify({"ok": False, "error": "Ingresa un número de documento válido."}), 400
    if tipo not in tipos_permitidos.get(usuario["rol_nombre"], set()):
        return jsonify({"ok": False, "error": "No puedes buscar ese tipo de destinatario."}), 403

    destinatario = consultar(
        "SELECT u.id_usuario,u.nombres,u.apellidos, "
        "COALESCE(NULLIF(d.documento,''),u.documento,'') AS documento, "
        "r.nombre AS rol_nombre,d.id_docente "
        "FROM usuarios u JOIN roles r ON r.id=u.id_rol "
        "LEFT JOIN docentes d ON d.id_usuario=u.id_usuario AND d.estado=1 "
        "WHERE u.estado=1 AND r.nombre=%s "
        "AND COALESCE(NULLIF(d.documento,''),u.documento,'')=%s LIMIT 1",
        (tipo, documento),
        uno=True,
    )
    if not destinatario:
        return jsonify({"ok": False, "error": "No se encontró una cuenta activa con ese documento y rol."}), 404
    if tipo == "Docente" and not destinatario.get("id_docente"):
        return jsonify({"ok": False, "error": "El docente no está vinculado al directorio institucional."}), 404
    return jsonify({"ok": True, "destinatario": destinatario})


# =========================================================
# NOTIFICACIONES DE UNA CITA
# =========================================================

def _notificar(cita_id, titulo, mensaje, creador_id=None):
    """
    Envía una notificación interna a los usuarios relacionados
    con una cita.

    Reciben la notificación:

    - estudiante citado
    - acudiente
    - docente
    - quien creó la cita
    - rector
    - coordinadores

    Las notificaciones son internas y se almacenan en MySQL.
    """

    cita = consultar(
        """
        SELECT
            c.id,
            c.id_estudiante,
            c.id_acudiente,
            c.id_docente,
            c.creado_por,
            c.destinatario_usuario_id,

            e.id_usuario AS estudiante_usuario,

            a.id_usuario AS acudiente_usuario,

            d.id_usuario AS docente_usuario

        FROM citas c

        LEFT JOIN estudiantes e
            ON e.id_estudiante = c.id_estudiante

        LEFT JOIN acudientes a
            ON a.id_acudiente = c.id_acudiente

        LEFT JOIN docentes d
            ON d.id_docente = c.id_docente

        WHERE c.id = %s

        LIMIT 1
        """,
        (cita_id,),
        uno=True,
    )

    if not cita:
        return

    usuarios = set()

    # -----------------------------------------------------
    # 1. ESTUDIANTE CITADO
    # -----------------------------------------------------

    if cita.get("estudiante_usuario"):
        usuarios.add(cita["estudiante_usuario"])

    elif cita.get("id_estudiante"):
        # Compatibilidad con estudiantes cuyo registro todavía
        # no tenga id_usuario asociado.
        estudiante = consultar(
            """
            SELECT
                u.id_usuario

            FROM usuarios u

            JOIN estudiantes e
                ON e.documento = u.documento

            WHERE e.id_estudiante = %s
              AND u.estado = 1

            LIMIT 1
            """,
            (cita["id_estudiante"],),
            uno=True,
        )

        if estudiante and estudiante.get("id_usuario"):
            usuarios.add(estudiante["id_usuario"])

    # -----------------------------------------------------
    # 2. ACUDIENTE
    # -----------------------------------------------------

    if cita.get("acudiente_usuario"):
        usuarios.add(cita["acudiente_usuario"])

    # -----------------------------------------------------
    # 3. DOCENTE
    # -----------------------------------------------------

    if cita.get("docente_usuario"):
        usuarios.add(cita["docente_usuario"])

    if cita.get("destinatario_usuario_id"):
        usuarios.add(cita["destinatario_usuario_id"])

    for participante in consultar(
        "SELECT id_usuario FROM cita_participantes WHERE id_cita=%s",
        (cita_id,),
    ):
        if participante.get("id_usuario"):
            usuarios.add(participante["id_usuario"])

    # -----------------------------------------------------
    # 4. QUIEN CREÓ LA CITA
    # -----------------------------------------------------

    creador = creador_id or cita.get("creado_por")

    if creador:
        usuarios.add(creador)

    # -----------------------------------------------------
    # 5. RECTOR Y COORDINADORES
    # -----------------------------------------------------

    responsables = consultar(
        """
        SELECT
            u.id_usuario

        FROM usuarios u

        JOIN roles r
            ON r.id = u.id_rol

        WHERE r.nombre IN (
            'Rector',
            'Administrador / Coordinador'
        )

        AND u.estado = 1
        """
    )

    for responsable in responsables:
        if responsable.get("id_usuario"):
            usuarios.add(responsable["id_usuario"])

    # -----------------------------------------------------
    # 6. CREAR NOTIFICACIONES
    # -----------------------------------------------------

    for id_usuario in usuarios:

        try:

            if creador and id_usuario == creador:

                mensaje_final = (
                    "Has creado una citación en EDUTURNOS. "
                    + mensaje
                )

            else:

                mensaje_final = mensaje

            notificar(
                id_usuario,
                titulo,
                mensaje_final,
                "Cita",
            )

        except Exception as exc:

            try:
                from flask import current_app

                current_app.logger.warning(
                    "No se pudo crear la notificación "
                    "para el usuario %s: %s",
                    id_usuario,
                    exc,
                )

            except Exception:
                pass


# =========================================================
# LISTADO DE CITAS
# =========================================================

@citas_bp.route("/")
@login_requerido
def index():

    usuario = usuario_actual()
    citas = consultar_citas(usuario)
    puede_anotar = usuario["rol_nombre"] in (
        "Super Admin",
        "Rector",
        "Administrador / Coordinador",
        "Docente",
    )
    detalles_escolares = datos_escolares(citas, privado=puede_anotar)
    if not puede_anotar:
        citas = [dict(cita, observaciones=None) for cita in citas]
    notas_por_cita = {}
    if puede_anotar and citas:
        placeholders = ",".join(["%s"] * len(citas))
        notas = consultar(
            f"""
            SELECT s.id_cita, s.observaciones, s.fecha_seguimiento,
                   CONCAT(u.nombres, ' ', u.apellidos) AS autor
            FROM seguimiento_citas s
            JOIN usuarios u ON u.id_usuario = s.realizado_por
            WHERE s.id_cita IN ({placeholders})
              AND s.observaciones IS NOT NULL
              AND s.observaciones <> ''
            ORDER BY s.fecha_seguimiento DESC, s.id DESC
            """,
            tuple(cita["id"] for cita in citas),
        )
        for nota in notas:
            notas_por_cita.setdefault(nota["id_cita"], []).append(nota)

    eventos_google_por_cita = {}
    if puede_anotar and citas:
        placeholders = ",".join(["%s"] * len(citas))
        for evento in consultar(
            f"SELECT id_cita,scope_key,estado,ultimo_error FROM eventos_google "
            f"WHERE id_cita IN ({placeholders}) ORDER BY scope_key",
            tuple(cita["id"] for cita in citas),
        ):
            eventos_google_por_cita.setdefault(evento["id_cita"], []).append(evento)

    fecha_minima = date.today().isoformat()

    return render_template(
        "citas/index.html",
        citas=citas,
        notas_por_cita=notas_por_cita,
        puede_anotar=puede_anotar,
        usuario_id=usuario["id_usuario"],
        detalles_escolares=detalles_escolares,
        eventos_google_por_cita=eventos_google_por_cita,
        fecha_minima=fecha_minima,
        rol=usuario["rol_nombre"],
        puede_crear=usuario["rol_nombre"]
        in (
            "Super Admin",
            "Rector",
            "Administrador / Coordinador",
            "Docente",
        ),
    )


@citas_bp.post("/<int:cita_id>/notas")
@roles_permitidos("Super Admin", "Rector", "Administrador / Coordinador", "Docente")
def guardar_nota(cita_id):
    usuario = usuario_actual()
    where, params = _visible(usuario)
    where = f"{where} AND c.id = %s" if where else " WHERE c.id = %s"
    cita = consultar(
        "SELECT c.id, ec.nombre AS estado FROM citas c "
        "JOIN estados_cita ec ON ec.id = c.id_estado" + where,
        tuple(params + [cita_id]),
        uno=True,
    )
    if not cita:
        abort(404)

    nota = request.form.get("nota", "").strip()
    if not nota or len(nota) > 10000:
        flash("Escribe una nota de entre 1 y 10000 caracteres.", "error")
        return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))

    ejecutar(
        "INSERT INTO seguimiento_citas"
        "(id_cita,estado_actual,asistencia,observaciones,realizado_por) "
        "VALUES(%s,%s,%s,%s,%s)",
        (cita_id, cita["estado"], "Pendiente", nota, usuario["id_usuario"]),
    )
    auditoria("ANOTAR", "Citas", cita_id, "Nota registrada durante la cita")
    flash("Nota de la cita guardada.", "success")
    return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))


# =========================================================
# CREAR NUEVA CITA
# =========================================================

def _crear_cita_para_personal(usuario):
    tipo = (request.form.get("destinatario_tipo") or "").strip()
    matriz = {
        "Super Admin": {"Docente", "Administrador / Coordinador"},
        "Rector": {"Docente", "Administrador / Coordinador"},
        "Administrador / Coordinador": {"Rector", "Docente"},
        "Docente": {"Rector", "Administrador / Coordinador"},
    }
    if tipo not in matriz.get(usuario["rol_nombre"], set()):
        raise ValueError("Tu rol no puede crear una citaci?n para ese tipo de destinatario.")
    try:
        destinatario_id = int(request.form.get("destinatario_usuario_id", ""))
        motivo_id = int(request.form.get("id_motivo", ""))
        periodo_id = int(request.form.get("id_periodo", ""))
    except (TypeError, ValueError):
        raise ValueError("Selecciona el destinatario, motivo y periodo.")
    if destinatario_id == int(usuario["id_usuario"]):
        raise ValueError("No puedes crear una citaci?n para tu propia cuenta.")
    persona = consultar(
        "SELECT u.id_usuario,r.nombre AS rol_nombre,d.id_docente FROM usuarios u "
        "JOIN roles r ON r.id=u.id_rol LEFT JOIN docentes d ON d.id_usuario=u.id_usuario AND d.estado=1 "
        "WHERE u.id_usuario=%s AND u.estado=1", (destinatario_id,), uno=True,
    )
    if not persona or persona["rol_nombre"] != tipo:
        raise ValueError("El destinatario no corresponde al rol seleccionado o est? inactivo.")
    if tipo == "Docente" and not persona.get("id_docente"):
        raise ValueError("El docente no est? vinculado al directorio institucional.")
    fecha = (request.form.get("fecha") or "").strip()
    fecha_obj = _validar_fecha_cita(fecha)
    hora = (request.form.get("hora") or "").strip()
    try:
        datetime.strptime(hora, "%H:%M")
    except ValueError:
        raise ValueError("La hora de la citaci?n no es v?lida.")
    validar_disponibilidad(persona.get("id_docente"), fecha_obj, hora)
    motivo, motivo_otro = _motivo_cita(motivo_id, usuario)
    periodo = consultar("SELECT id FROM periodos_academicos WHERE id=%s AND activo=1 AND cerrado=0", (periodo_id,), uno=True)
    estado = consultar("SELECT id FROM estados_cita WHERE nombre='Pendiente' AND estado=1", uno=True)
    if not motivo or not periodo or not estado:
        raise ValueError("El motivo, el periodo o el estado inicial no est?n disponibles.")
    conflicto = consultar(
        "SELECT c.id FROM citas c WHERE c.fecha=%s AND c.hora<ADDTIME(%s,'00:30:00') "
        "AND ADDTIME(c.hora,'00:30:00')>%s AND (c.destinatario_usuario_id=%s OR c.creado_por=%s "
        "OR (%s IS NOT NULL AND c.id_docente=%s)) LIMIT 1",
        (fecha, hora, hora, destinatario_id, usuario["id_usuario"], persona.get("id_docente"), persona.get("id_docente")), uno=True,
    )
    if conflicto:
        raise ValueError("El destinatario o quien crea la cita ya tiene una citaci?n a esa hora.")
    with transaccion() as conexion:
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE id_usuario=%s AND estado=1 FOR UPDATE", (destinatario_id,))
            if not cursor.fetchone():
                raise ValueError("El destinatario dej? de estar activo. Recarga y vuelve a intentar.")
            cursor.execute(
                "INSERT INTO citas(id_estudiante,id_acudiente,id_docente,destinatario_tipo,destinatario_usuario_id,"
        "id_motivo,motivo_otro,id_estado,id_periodo,fecha,hora,lugar,observaciones,creado_por) "
        "VALUES(NULL,NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Coordinación','',%s)",
        (persona.get("id_docente"), tipo, destinatario_id, motivo_id, motivo_otro, estado["id"], periodo_id, fecha, hora, usuario["id_usuario"]),
            )
            cita_id = cursor.lastrowid
            cursor.execute("INSERT INTO cita_participantes(id_cita,id_usuario,tipo) VALUES(%s,%s,'Organizador')", (cita_id, usuario["id_usuario"]))
            cursor.execute("INSERT INTO cita_participantes(id_cita,id_usuario,tipo) VALUES(%s,%s,'Destinatario')", (cita_id, destinatario_id))
            from servicios.google_calendar import encolar_cita_cursor
            encolar_cita_cursor(cursor, cita_id, usuario["id_usuario"])
        finally:
            cursor.close()
    _notificar(cita_id, "Nueva citaci?n en EDUTURNOS", f"Tienes una citaci?n programada para el {fecha} a las {formatear_hora(hora)}.", creador_id=usuario["id_usuario"])
    auditoria("CREAR", "Citas", cita_id, "Citaci?n institucional dirigida a " + tipo)
    flash("Citaci?n creada y enviada al destinatario.", "success")
    return redirect(_destino_cita_creada(fecha))


@citas_bp.route("/nueva", methods=["GET", "POST"])
@roles_permitidos(
    "Super Admin",
    "Rector",
    "Administrador / Coordinador",
    "Docente",
)
def nueva():

    usuario = usuario_actual()
    cat = catalogos(usuario)

    if request.method == "POST":

        try:
            if request.form.get("destinatario_tipo", "Estudiante") != "Estudiante":
                return _crear_cita_para_personal(usuario)

            # ---------------------------------------------
            # DATOS DEL FORMULARIO
            # ---------------------------------------------

            estudiante_id = int(request.form["id_estudiante"])
            docente_id = int(request.form["id_docente"]) if request.form.get("id_docente") else None
            if usuario["rol_nombre"] == "Docente" and docente_id is None:
                perfil_docente = consultar(
                    "SELECT id_docente FROM docentes WHERE id_usuario=%s AND estado=1 LIMIT 1",
                    (usuario["id_usuario"],),
                    uno=True,
                )
                docente_id = (perfil_docente or {}).get("id_docente")
            acudiente_id = int(request.form["id_acudiente"]) if request.form.get("id_acudiente") else None
            motivo_id = int(request.form["id_motivo"])
            periodo_id = int(request.form["id_periodo"])

            fecha = request.form["fecha"].strip()
            hora = request.form["hora"].strip()

            lugar = "Coordinación"

            observaciones = request.form.get(
                "observaciones",
                "",
            ).strip()

            # ---------------------------------------------
            # VALIDAR FECHA
            # ---------------------------------------------

            fecha_obj = _validar_fecha_cita(fecha)

            # ---------------------------------------------
            # VALIDAR HORA
            # ---------------------------------------------

            try:
                datetime.strptime(hora, "%H:%M")

            except ValueError:
                raise ValueError(
                    "La hora de la cita no tiene un formato válido."
                )

            # ---------------------------------------------
            # VALIDAR ESTUDIANTE
            # ---------------------------------------------

            estudiante = consultar(
                """
                SELECT
                    id_estudiante,
                    id_usuario,
                    nombres,
                    apellidos

                FROM estudiantes

                WHERE id_estudiante = %s
                  AND estado = 'Activo'

                LIMIT 1
                """,
                (estudiante_id,),
                uno=True,
            )

            if not estudiante:
                raise ValueError(
                    "El estudiante seleccionado no está activo."
                )

            # ---------------------------------------------
            # VALIDAR ACUDIENTE
            # ---------------------------------------------

            if not acudiente_id:
                principal = consultar(
                    "SELECT ea.id_acudiente FROM estudiante_acudiente ea JOIN acudientes a "
                    "ON a.id_acudiente=ea.id_acudiente AND a.estado=1 "
                    "WHERE ea.id_estudiante=%s AND ea.estado=1 ORDER BY ea.principal DESC,ea.id_acudiente LIMIT 1",
                    (estudiante_id,), uno=True,
                )
                acudiente_id = (principal or {}).get("id_acudiente")
            if not acudiente_id:
                raise ValueError("El estudiante no tiene acudiente activo relacionado.")
            relacion = consultar(
                """
                SELECT
                    1

                FROM estudiante_acudiente

                WHERE id_estudiante = %s
                  AND id_acudiente = %s
                  AND estado = 1

                LIMIT 1
                """,
                (
                    estudiante_id,
                    acudiente_id,
                ),
                uno=True,
            )

            if not relacion:
                raise ValueError(
                    "El acudiente seleccionado no está relacionado "
                    "con el estudiante."
                )

            # ---------------------------------------------
            # VALIDAR DOCENTE
            # ---------------------------------------------

            docente = None
            if docente_id is not None:
                docente = consultar(
                    "SELECT id_docente,id_usuario,nombres,apellidos FROM docentes "
                    "WHERE id_docente=%s AND estado=1 LIMIT 1", (docente_id,), uno=True,
                )
                if not docente:
                    raise ValueError("El docente seleccionado no est? activo.")

            # REGLA PARA DOCENTES
            # ---------------------------------------------

            if usuario["rol_nombre"] == "Docente":

                docente_usuario = consultar(
                    """
                    SELECT
                        id_docente

                    FROM docentes

                    WHERE id_usuario = %s

                    LIMIT 1
                    """,
                    (usuario["id_usuario"],),
                    uno=True,
                )

                if not docente_usuario:
                    raise ValueError(
                        "Tu usuario no está asociado a un docente."
                    )

                mi_docente_id = docente_usuario["id_docente"]

                if docente_id != mi_docente_id:
                    raise ValueError(
                        "Solo puedes crear citas utilizando "
                        "tu usuario como docente."
                    )

                asignacion = consultar(
                    """
                    SELECT
                        1

                    FROM asignaciones_docentes ad

                    JOIN estudiantes e
                        ON e.id_estudiante = %s

                    WHERE ad.id_docente = %s
                      AND ad.estado = 1

                      AND (
                            ad.id_estudiante = %s

                            OR (
                                ad.id_estudiante IS NULL
                                AND ad.id_grupo = e.id_grupo
                            )
                      )

                    LIMIT 1
                    """,
                    (
                        estudiante_id,
                        mi_docente_id,
                        estudiante_id,
                    ),
                    uno=True,
                )

                if not asignacion:
                    raise ValueError(
                        "Solo puedes crear citas para estudiantes "
                        "que tienes asignados."
                    )

            # ---------------------------------------------
            # VALIDAR MOTIVO
            # ---------------------------------------------

            motivo, motivo_otro = _motivo_cita(motivo_id, usuario)

            # ---------------------------------------------
            # VALIDAR PERIODO
            # ---------------------------------------------

            periodo = consultar(
                """
                SELECT
                    id,
                    nombre

                FROM periodos_academicos

                WHERE id = %s
                  AND activo = 1
                  AND cerrado = 0

                LIMIT 1
                """,
                (periodo_id,),
                uno=True,
            )

            if not periodo:
                raise ValueError(
                    "El periodo académico seleccionado "
                    "no está disponible."
                )

            # ---------------------------------------------
            # VALIDAR ESTADO INICIAL
            # ---------------------------------------------

            estado = consultar(
                """
                SELECT
                    id,
                    nombre

                FROM estados_cita

                WHERE nombre = 'Pendiente'
                  AND estado = 1

                LIMIT 1
                """,
                uno=True,
            )

            if not estado:
                raise ValueError(
                    "No existe el estado inicial 'Pendiente'."
                )

            # ---------------------------------------------
            # EVITAR DUPLICACIÓN DE HORARIO DEL DOCENTE
            # ---------------------------------------------

            cita_existente = _cita_horario_ocupado(
                docente_id,
                estudiante_id,
                acudiente_id,
                fecha,
                hora,
            )

            if cita_existente:
                raise ValueError(
                    "El docente, estudiante o acudiente ya tiene "
                    "una citación registrada para esa fecha y hora."
                )

            # ---------------------------------------------
            # CREAR CITA
            # ---------------------------------------------

            validar_disponibilidad(docente_id, fecha_obj, hora)
            cita_id = reservar_cita(
                """
                INSERT INTO citas (
                    id_estudiante,id_acudiente,id_docente,id_motivo,motivo_otro,id_estado,id_periodo,
                    fecha,hora,lugar,observaciones,creado_por,destinatario_tipo,destinatario_usuario_id
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Estudiante',%s)
                """,
                (
                    estudiante_id, acudiente_id, docente_id, motivo_id, motivo_otro, estado["id"],
                    periodo_id, fecha, hora, lugar, observaciones, usuario["id_usuario"],
                    estudiante.get("id_usuario"),
                ),
            )

            # NOTIFICAR CREACIÓN
            # ---------------------------------------------

            _notificar(
                cita_id,
                "Nueva citación en EDUTURNOS",
                (
                    f"Tienes una citación programada para "
                    f"el {fecha} a las {formatear_hora(hora)}."
                ),
                creador_id=usuario["id_usuario"],
            )

            # ---------------------------------------------
            # AUDITORÍA
            # ---------------------------------------------

            auditoria(
                "CREAR",
                "Citas",
                cita_id,
                f"Cita creada para {fecha} {formatear_hora(hora)}",
            )

            flash(
                "Citación creada correctamente.",
                "success",
            )

            return redirect(
                _destino_cita_creada(fecha)
            )

        except Exception as exc:

            flash(
                str(exc),
                "error",
            )

    cat["estudiantes"] = []
    cat["acudientes"] = []
    return render_template(
        "citas/nueva.html",
        usuario=usuario,
        fecha_minima=date.today().isoformat(),
        **cat,
    )


# =========================================================
# CAMBIAR ESTADO DE UNA CITA
# =========================================================

@citas_bp.post("/<int:cita_id>/estado")
@roles_permitidos(
    "Super Admin",
    "Rector",
    "Administrador / Coordinador",
    "Docente",
    "Acudiente",
)
def cambiar_estado(cita_id):

    usuario = usuario_actual()

    nuevo = request.form.get(
        "estado",
        "",
    ).strip()

    # ---------------------------------------------
    # BUSCAR CITA
    # ---------------------------------------------

    cita = consultar(
        """
        SELECT *
        FROM citas
        WHERE id = %s
        LIMIT 1
        """,
        (cita_id,),
        uno=True,
    )

    # ---------------------------------------------
    # BUSCAR NUEVO ESTADO
    # ---------------------------------------------

    estado_nuevo = consultar(
        """
        SELECT
            id,
            nombre

        FROM estados_cita

        WHERE nombre = %s
          AND estado = 1

        LIMIT 1
        """,
        (nuevo,),
        uno=True,
    )

    if not cita or not estado_nuevo:

        flash(
            "Citación o estado no encontrado.",
            "error",
        )

        return redirect(
            url_for("citas.index")
        )

    estado_actual = consultar(
        "SELECT nombre FROM estados_cita WHERE id = %s LIMIT 1",
        (cita["id_estado"],),
        uno=True,
    )
    actual = estado_actual["nombre"] if estado_actual else None

    # ---------------------------------------------
    # VALIDACIÓN PARA ACUDIENTE
    # ---------------------------------------------

    if usuario["rol_nombre"] == "Acudiente":

        acudiente = consultar(
            """
            SELECT
                id_acudiente

            FROM acudientes

            WHERE id_usuario = %s

            LIMIT 1
            """,
            (usuario["id_usuario"],),
            uno=True,
        )

        acudiente_id = (
            acudiente["id_acudiente"]
            if acudiente
            else None
        )

        if (
            not _acudiente_puede_confirmar(actual, nuevo)
            or cita["id_acudiente"] != acudiente_id
        ):

            flash(
                "No puedes cambiar esa citación de esa forma.",
                "error",
            )

            return redirect(
                url_for("citas.index")
            )

    # ---------------------------------------------
    # VALIDACIÓN PARA DOCENTE
    # ---------------------------------------------

    if usuario["rol_nombre"] == "Docente":

        docente = consultar(
            """
            SELECT
                id_docente

            FROM docentes

            WHERE id_usuario = %s

            LIMIT 1
            """,
            (usuario["id_usuario"],),
            uno=True,
        )

        docente_id = (
            docente["id_docente"]
            if docente
            else None
        )

        if cita["id_docente"] != docente_id:
            abort(403)

        if nuevo not in (
            "Confirmada",
            "Cancelada",
            "Reprogramada",
        ):

            flash(
                "Estado no permitido para docente.",
                "error",
            )

            return redirect(
                url_for("citas.index")
            )

    # ---------------------------------------------
    # TRANSICIONES PERMITIDAS
    # ---------------------------------------------

    if not _transicion_estado_permitida(usuario["rol_nombre"], actual, nuevo):

        flash(
            f"No se puede pasar de {actual} a {nuevo}.",
            "error",
        )

        return redirect(
            url_for("citas.index")
        )

    # ---------------------------------------------
    # ACTUALIZAR ESTADO
    # ---------------------------------------------

    with transaccion() as cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(
                "UPDATE citas SET id_estado=%s WHERE id=%s AND id_estado=%s",
                (estado_nuevo["id"], cita_id, cita["id_estado"]),
            )
            if cursor.rowcount != 1:
                flash(
                    "La citación cambió mientras se procesaba. Recarga e inténtalo de nuevo.",
                    "error",
                )
                return redirect(url_for("citas.index"))
            from servicios.google_calendar import encolar_cita_cursor

            encolar_cita_cursor(
                cursor,
                cita_id,
                cita.get("creado_por") or usuario["id_usuario"],
                "delete" if estado_nuevo["nombre"] == "Cancelada" else "upsert",
            )
        finally:
            cursor.close()

    # ---------------------------------------------
    # NOTIFICAR CAMBIO
    # ---------------------------------------------

    _notificar(
        cita_id,
        "Citación actualizada",
        (
            f"La citación ahora está en estado: "
            f"{estado_nuevo['nombre']}."
        ),
        creador_id=cita.get("creado_por"),
    )

    # ---------------------------------------------
    # AUDITORÍA
    # ---------------------------------------------

    auditoria(
        "ACTUALIZAR",
        "Citas",
        cita_id,
        f"Estado: {actual} -> {estado_nuevo['nombre']}",
    )

    flash(
        "Estado actualizado correctamente.",
        "success",
    )

    return redirect(
        url_for("citas.index")
    )


def _cita_autorizada(usuario, cita_id):
    where, params = _visible(usuario)
    where = f"{where} AND c.id=%s" if where else " WHERE c.id=%s"
    cita = consultar(
        "SELECT c.*,ec.nombre estado,CONCAT(e.nombres,' ',e.apellidos) estudiante,"
        "CONCAT(d.nombres,' ',d.apellidos) docente,CONCAT(a.nombres,' ',a.apellidos) acudiente,"
        "COALESCE(NULLIF(c.motivo_otro,''),m.nombre) motivo FROM citas c JOIN estados_cita ec ON ec.id=c.id_estado "
        "LEFT JOIN estudiantes e ON e.id_estudiante=c.id_estudiante LEFT JOIN docentes d ON d.id_docente=c.id_docente "
        "LEFT JOIN acudientes a ON a.id_acudiente=c.id_acudiente JOIN motivos m ON m.id=c.id_motivo" + where,
        tuple(params + [cita_id]), uno=True,
    )
    if not cita:
        abort(404)
    return cita


@citas_bp.post("/<int:cita_id>/compromisos")
@roles_permitidos(*PERSONAL)
def agregar_compromiso(cita_id):
    usuario = usuario_actual()
    cita = _cita_autorizada(usuario, cita_id)
    if cita["estado"] in ("Cancelada", "No asistió", "Justificada"):
        abort(409, description="No se pueden añadir acuerdos a una cita cancelada o sin asistencia.")
    try:
        descripcion, responsable, limite = validar_compromiso(request.form.get("descripcion", ""), request.form.get("responsable", ""), request.form.get("fecha_limite", ""))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))
    ejecutar("INSERT INTO compromisos_cita(id_cita,descripcion,responsable,fecha_limite,creado_por) VALUES(%s,%s,%s,%s,%s)", (cita_id, descripcion, responsable, limite, usuario["id_usuario"]))
    auditoria("COMPROMISO", "Citas", cita_id, f"Fecha límite: {limite}")
    _notificar(cita_id, "Nuevo compromiso", "Se registró un compromiso en tu citación. Consulta su responsable y plazo.")
    flash("Compromiso registrado.", "success")
    return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))


@citas_bp.post("/<int:cita_id>/compromisos/<int:compromiso_id>")
@roles_permitidos(*PERSONAL)
def actualizar_compromiso(cita_id, compromiso_id):
    usuario = usuario_actual()
    _cita_autorizada(usuario, cita_id)
    estado = request.form.get("estado", "")
    if estado not in ("Cumplido", "Cancelado"):
        abort(400)
    with transaccion() as cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT estado FROM compromisos_cita WHERE id=%s AND id_cita=%s FOR UPDATE", (compromiso_id, cita_id))
            compromiso = cursor.fetchone()
            if not compromiso:
                abort(404)
            if compromiso["estado"] != "Pendiente":
                abort(409, description="El compromiso ya fue actualizado.")
            cursor.execute("UPDATE compromisos_cita SET estado=%s,actualizado_por=%s WHERE id=%s AND id_cita=%s", (estado, usuario["id_usuario"], compromiso_id, cita_id))
        finally:
            cursor.close()
    auditoria("ACTUALIZAR", "Compromisos", compromiso_id, estado)
    flash("Compromiso actualizado.", "success")
    return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))


@citas_bp.post("/<int:cita_id>/reprogramar")
@roles_permitidos(*PERSONAL)
def reprogramar_cita(cita_id):
    usuario = usuario_actual()
    cita = _cita_autorizada(usuario, cita_id)
    if not _es_creador_habilitado(usuario, cita):
        abort(403)
    try:
        fecha = _validar_fecha_cita(request.form.get("fecha", ""))
        hora = datetime.strptime(request.form.get("hora", ""), "%H:%M").time()
        motivo = request.form.get("motivo", "").strip()
        if not motivo or len(motivo) > 2000:
            raise ValueError("Indica el motivo del cambio de fecha, hasta 2000 caracteres.")
        validar_disponibilidad(cita["id_docente"], fecha, hora)
        with transaccion() as cnx:
            cursor = cnx.cursor(dictionary=True)
            try:
                bloquear_agenda(cursor, cita["id_docente"], cita["id_estudiante"], cita["id_acudiente"])
                cursor.execute("SELECT c.fecha,c.hora,c.id_estado,ec.nombre estado FROM citas c JOIN estados_cita ec ON ec.id=c.id_estado WHERE c.id=%s FOR UPDATE", (cita_id,))
                actual = cursor.fetchone()
                if not actual or actual["estado"] != "Realizada":
                    abort(409, description="Solo se puede reprogramar una cita realizada.")
                comprobar_hueco(cursor, cita["id_docente"], cita["id_estudiante"], cita["id_acudiente"], fecha, hora, excluir=cita_id)
                cursor.execute("SELECT id FROM estados_cita WHERE nombre='Reprogramada' AND estado=1")
                estado = cursor.fetchone()
                if not estado:
                    abort(409)
                cursor.execute(
                    "INSERT INTO citas(id_estudiante,id_acudiente,id_docente,id_motivo,id_estado,id_periodo,fecha,hora,lugar,observaciones,creado_por) "
                    "SELECT id_estudiante,id_acudiente,id_docente,id_motivo,%s,id_periodo,%s,%s,%s,'',%s FROM citas WHERE id=%s",
                    (estado["id"], fecha, hora, "Coordinación", usuario["id_usuario"], cita_id),
                )
                nueva_cita_id = cursor.lastrowid
                cursor.execute("INSERT INTO reprogramaciones_cita(id_cita,fecha_anterior,hora_anterior,fecha_nueva,hora_nueva,motivo,realizado_por) VALUES(%s,%s,%s,%s,%s,%s,%s)", (nueva_cita_id, actual["fecha"], actual["hora"], fecha, hora, motivo, usuario["id_usuario"]))
                from servicios.google_calendar import encolar_cita_cursor

                encolar_cita_cursor(cursor, nueva_cita_id, usuario["id_usuario"])
            finally:
                cursor.close()
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))
    auditoria("REPROGRAMAR", "Citas", nueva_cita_id, f"Cita anterior: {cita_id}. Nueva fecha: {fecha} {formatear_hora(hora)}")
    _notificar(nueva_cita_id, "Citación reprogramada", f"La nueva fecha de tu citación es {fecha} a las {formatear_hora(hora)}.")
    flash("Cita reprogramada y participantes notificados.", "success")
    return redirect(url_for("calendario.index", dia=fecha.isoformat()))


@citas_bp.post("/<int:cita_id>/solicitar-reprogramacion")
@roles_permitidos("Acudiente")
def solicitar_reprogramacion_cita(cita_id):
    usuario = usuario_actual()
    try:
        fecha = _validar_fecha_cita(request.form.get("fecha", ""))
        hora = datetime.strptime(
            request.form.get("hora", ""),
            "%H:%M",
        ).time()
        motivo = request.form.get("motivo", "").strip()
        if not motivo or len(motivo) > 2000:
            raise ValueError("Indica el motivo del cambio, hasta 2000 caracteres.")

        with transaccion() as conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute(
                    """
                    SELECT c.id, c.id_estudiante, c.id_acudiente,
                           c.id_docente, c.creado_por, c.fecha, c.hora,
                           ec.nombre AS estado, r.nombre AS creador_rol
                    FROM citas c
                    JOIN estados_cita ec ON ec.id = c.id_estado
                    JOIN acudientes a ON a.id_acudiente = c.id_acudiente
                    JOIN usuarios creador ON creador.id_usuario = c.creado_por
                    JOIN roles r ON r.id = creador.id_rol
                    WHERE c.id = %s AND a.id_usuario = %s
                    FOR UPDATE
                    """,
                    (cita_id, usuario["id_usuario"]),
                )
                cita = cursor.fetchone()
                if not cita:
                    abort(404)
                if cita["creador_rol"] not in ROLES_CREADORES_CITA:
                    raise ValueError(
                        "Esta citación no tiene un creador habilitado para revisar cambios."
                    )
                if cita["estado"] not in ("Pendiente", "Confirmada", "Reprogramada"):
                    raise ValueError(
                        "Solo puedes solicitar cambios para una cita activa."
                    )
                validar_disponibilidad(cita["id_docente"], fecha, hora)

                bloquear_agenda(
                    cursor,
                    cita["id_docente"],
                    cita["id_estudiante"],
                    cita["id_acudiente"],
                )
                cursor.execute(
                    """
                    SELECT id
                    FROM solicitudes_reprogramacion_cita
                    WHERE id_cita = %s AND estado = 'Pendiente'
                    LIMIT 1
                    FOR UPDATE
                    """,
                    (cita_id,),
                )
                if cursor.fetchone():
                    raise ValueError(
                        "Ya hay una solicitud de cambio pendiente para esta cita."
                    )
                comprobar_hueco(
                    cursor,
                    cita["id_docente"],
                    cita["id_estudiante"],
                    cita["id_acudiente"],
                    fecha,
                    hora,
                    excluir=cita_id,
                )
                cursor.execute(
                    """
                    INSERT INTO solicitudes_reprogramacion_cita (
                        id_cita, solicitante_usuario_id, creador_usuario_id,
                        fecha_anterior, hora_anterior, fecha_solicitada,
                        hora_solicitada, motivo
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        cita_id,
                        usuario["id_usuario"],
                        cita["creado_por"],
                        cita["fecha"],
                        cita["hora"],
                        fecha,
                        hora,
                        motivo,
                    ),
                )
                solicitud_id = cursor.lastrowid
            finally:
                cursor.close()
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))

    notificar(
        cita["creado_por"],
        "Solicitud para cambiar una citación",
        f"El acudiente solicitó cambiar la cita #{cita_id} para "
        f"{fecha.isoformat()} a las {formatear_hora(hora)}. "
        "Revisa la solicitud en Solicitudes.",
        "Solicitud",
    )
    auditoria(
        "SOLICITAR_REPROGRAMACION",
        "Citas",
        cita_id,
        f"Solicitud #{solicitud_id} enviada por acudiente",
    )
    flash("Solicitud enviada a la persona que creó la citación.", "success")
    return redirect(url_for("citas.index", _anchor=f"cita-dialog-{cita_id}"))


@citas_bp.post("/solicitudes-reprogramacion/<int:solicitud_id>/resolver")
@roles_permitidos(*PERSONAL)
def resolver_solicitud_reprogramacion(solicitud_id):
    usuario = usuario_actual()
    if not _es_creador_habilitado(usuario, {"creado_por": usuario["id_usuario"]}):
        abort(403)

    accion = request.form.get("accion", "").strip()
    respuesta = request.form.get("respuesta", "").strip()
    if accion not in ("aceptar", "rechazar"):
        abort(400)
    if len(respuesta) > 2000:
        flash("La respuesta no puede superar 2000 caracteres.", "error")
        return redirect(url_for("solicitudes.index"))

    solicitud = None
    aceptada = accion == "aceptar"
    try:
        with transaccion() as conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute(
                    """
                    SELECT *
                    FROM solicitudes_reprogramacion_cita
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (solicitud_id,),
                )
                solicitud = cursor.fetchone()
                if not solicitud:
                    abort(404)
                if int(solicitud["creador_usuario_id"]) != int(usuario["id_usuario"]):
                    abort(403)
                if solicitud["estado"] != "Pendiente":
                    abort(409, description="La solicitud ya fue resuelta.")

                if accion == "rechazar":
                    cursor.execute(
                        """
                        UPDATE solicitudes_reprogramacion_cita
                        SET estado='Rechazada', respuesta=%s,
                            revisado_por=%s, fecha_revision=NOW()
                        WHERE id=%s AND estado='Pendiente'
                        """,
                        (
                            respuesta or "La persona responsable rechazó el cambio.",
                            usuario["id_usuario"],
                            solicitud_id,
                        ),
                    )
                    if cursor.rowcount != 1:
                        abort(409, description="La solicitud ya fue resuelta.")
                else:
                    fecha = _validar_fecha_cita(
                        solicitud["fecha_solicitada"].isoformat()
                        if hasattr(solicitud["fecha_solicitada"], "isoformat")
                        else solicitud["fecha_solicitada"]
                    )
                    hora = datetime.strptime(
                        str(solicitud["hora_solicitada"])[:5],
                        "%H:%M",
                    ).time()
                    cursor.execute(
                        """
                        SELECT c.id, c.id_docente, c.id_estudiante, c.id_acudiente,
                               c.creado_por, ec.nombre AS estado
                        FROM citas c
                        JOIN estados_cita ec ON ec.id = c.id_estado
                        WHERE c.id = %s
                        FOR UPDATE
                        """,
                        (solicitud["id_cita"],),
                    )
                    cita = cursor.fetchone()
                    if (
                        not cita
                        or int(cita["creado_por"]) != int(usuario["id_usuario"])
                        or cita["estado"] not in ("Pendiente", "Confirmada", "Reprogramada")
                    ):
                        abort(409, description="La citación ya no admite cambios.")

                    validar_disponibilidad(cita["id_docente"], fecha, hora)
                    bloquear_agenda(
                        cursor,
                        cita["id_docente"],
                        cita["id_estudiante"],
                        cita["id_acudiente"],
                    )
                    comprobar_hueco(
                        cursor,
                        cita["id_docente"],
                        cita["id_estudiante"],
                        cita["id_acudiente"],
                        fecha,
                        hora,
                        excluir=solicitud["id_cita"],
                    )
                    cursor.execute(
                        "SELECT id FROM estados_cita WHERE nombre='Reprogramada' AND estado=1"
                    )
                    estado = cursor.fetchone()
                    if not estado:
                        abort(409, description="No está disponible el estado Reprogramada.")
                    cursor.execute(
                        """
                        UPDATE citas
                        SET fecha=%s, hora=%s, id_estado=%s
                        WHERE id=%s AND creado_por=%s
                          AND fecha=%s AND hora=%s
                          AND id_estado IN (
                              SELECT id FROM estados_cita
                              WHERE nombre IN ('Pendiente','Confirmada','Reprogramada')
                          )
                        """,
                        (
                            fecha,
                            hora,
                            estado["id"],
                            solicitud["id_cita"],
                            usuario["id_usuario"],
                            solicitud["fecha_anterior"],
                            solicitud["hora_anterior"],
                        ),
                    )
                    if cursor.rowcount != 1:
                        abort(409, description="La cita cambió desde que se envió la solicitud.")
                    cursor.execute(
                        """
                        INSERT INTO reprogramaciones_cita (
                            id_cita, fecha_anterior, hora_anterior,
                            fecha_nueva, hora_nueva, motivo, realizado_por
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            solicitud["id_cita"],
                            solicitud["fecha_anterior"],
                            solicitud["hora_anterior"],
                            fecha,
                            hora,
                            solicitud["motivo"],
                            usuario["id_usuario"],
                        ),
                    )
                    from servicios.google_calendar import encolar_cita_cursor

                    encolar_cita_cursor(
                        cursor,
                        solicitud["id_cita"],
                        usuario["id_usuario"],
                    )
                    cursor.execute(
                        """
                        UPDATE solicitudes_reprogramacion_cita
                        SET estado='Aceptada', respuesta=%s,
                            revisado_por=%s, fecha_revision=NOW()
                        WHERE id=%s AND estado='Pendiente'
                        """,
                        (
                            respuesta or "La persona responsable aceptó el cambio.",
                            usuario["id_usuario"],
                            solicitud_id,
                        ),
                    )
                    if cursor.rowcount != 1:
                        abort(409, description="La solicitud ya fue resuelta.")
            finally:
                cursor.close()
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("solicitudes.index"))

    if aceptada:
        auditoria(
            "ACEPTAR_REPROGRAMACION",
            "Citas",
            solicitud["id_cita"],
            f"Solicitud #{solicitud_id} aceptada",
        )
        _notificar(
            solicitud["id_cita"],
            "Citación reprogramada",
            f"La nueva fecha de la citación es {fecha.isoformat()} "
            f"a las {formatear_hora(hora)}.",
        )
        flash("Solicitud aceptada y citación actualizada.", "success")
    else:
        notificar(
            solicitud["solicitante_usuario_id"],
            "Solicitud de cambio rechazada",
            respuesta or "La persona responsable rechazó el cambio solicitado.",
            "Solicitud",
        )
        auditoria(
            "RECHAZAR_REPROGRAMACION",
            "Citas",
            solicitud["id_cita"],
            f"Solicitud #{solicitud_id} rechazada",
        )
        flash("Solicitud rechazada.", "success")
    return redirect(url_for("solicitudes.index"))


@citas_bp.post("/disponibilidad/<int:docente_id>")
@roles_permitidos(*PERSONAL)
def guardar_disponibilidad(docente_id):
    usuario = usuario_actual()
    docente = consultar("SELECT id_docente,id_usuario FROM docentes WHERE id_docente=%s AND estado=1", (docente_id,), uno=True)
    if not docente or (usuario["rol_nombre"] == "Docente" and docente["id_usuario"] != usuario["id_usuario"]):
        abort(403)
    try:
        dia, inicio, fin = validar_franja(request.form.get("dia_semana", ""), request.form.get("hora_inicio", ""), request.form.get("hora_fin", ""))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("calendario.index", docente_disp=docente_id, anio=request.form.get("anio") or None, mes=request.form.get("mes") or None))
    ejecutar("INSERT INTO disponibilidad_docente(id_docente,dia_semana,hora_inicio,hora_fin,creado_por) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE hora_fin=VALUES(hora_fin)", (docente_id, dia, inicio, fin, usuario["id_usuario"]))
    auditoria("HORARIO", "Docentes", docente_id)
    flash("Disponibilidad del docente guardada.", "success")
    return redirect(url_for("calendario.index", docente_disp=docente_id, anio=request.form.get("anio") or None, mes=request.form.get("mes") or None))


@citas_bp.post("/disponibilidad/<int:docente_id>/<int:franja_id>/eliminar")
@roles_permitidos(*PERSONAL)
def eliminar_disponibilidad(docente_id, franja_id):
    usuario = usuario_actual()
    docente = consultar("SELECT id_usuario FROM docentes WHERE id_docente=%s", (docente_id,), uno=True)
    if not docente or (usuario["rol_nombre"] == "Docente" and docente["id_usuario"] != usuario["id_usuario"]):
        abort(403)
    ejecutar("DELETE FROM disponibilidad_docente WHERE id=%s AND id_docente=%s", (franja_id, docente_id))
    auditoria("HORARIO", "Docentes", docente_id, "Franja retirada")
    return redirect(url_for("calendario.index", docente_disp=docente_id, anio=request.form.get("anio") or None, mes=request.form.get("mes") or None))


@citas_bp.get("/<int:cita_id>/acta.pdf")
@roles_permitidos(*PERSONAL)
def acta_cita(cita_id):
    cita = _cita_autorizada(usuario_actual(), cita_id)
    cierre = consultar("SELECT r.*,CONCAT(u.nombres,' ',u.apellidos) autor FROM cierres_cita r JOIN usuarios u ON u.id_usuario=r.cerrado_por WHERE r.id_cita=%s", (cita_id,), uno=True)
    if not cierre:
        abort(409, description="El acta estará disponible después del cierre formal de la cita.")
    compromisos = consultar("SELECT descripcion,responsable,fecha_limite,estado FROM compromisos_cita WHERE id_cita=%s ORDER BY fecha_limite,id", (cita_id,))
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from reportlab.lib import colors
    salida = BytesIO()
    documento = SimpleDocTemplate(salida, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    estilos = getSampleStyleSheet()
    parrafo = lambda texto: Paragraph(escape(str(texto or "")).replace("\n", "<br/>"), estilos["BodyText"])
    elementos = [Paragraph("EDUTURNOS · Acta de reunión", estilos["Title"]), Spacer(1, 12)]
    for etiqueta, valor in (("Estudiante", cita["estudiante"]), ("Docente", cita["docente"]), ("Acudiente", cita["acudiente"]), ("Fecha y hora", f"{cita['fecha']} {formatear_hora(cita['hora'])}"), ("Lugar", cita["lugar"]), ("Motivo", cita["motivo"]), ("Asistencia", cierre["asistencia"])):
        elementos.append(parrafo(f"{etiqueta}: {valor}"))
    elementos.extend([Spacer(1, 14), Paragraph("Resultado de la reunión", estilos["Heading2"]), parrafo(cierre["resultado"]), Spacer(1, 12), Paragraph("Compromisos", estilos["Heading2"])])
    if compromisos:
        filas = [[parrafo("Compromiso"), parrafo("Responsable"), parrafo("Plazo / estado")]]
        filas.extend([parrafo(compromiso["descripcion"]), parrafo(compromiso["responsable"]), parrafo(f"{compromiso['fecha_limite']} / {compromiso['estado']}")] for compromiso in compromisos)
        tabla = Table(filas, colWidths=[255, 130, 138], repeatRows=1)
        tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf3ff")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        elementos.append(tabla)
    else:
        elementos.append(parrafo("Sin compromisos registrados."))
    elementos.extend([Spacer(1, 16), parrafo(f"Registro realizado por {cierre['autor']} el {cierre['fecha_cierre']}"), parrafo("Constancia institucional de registro. No equivale a una firma digital.")])
    documento.build(elementos)
    auditoria("DESCARGAR", "Actas", cita_id)
    return Response(salida.getvalue(), mimetype="application/pdf", headers={"Content-Disposition": f'attachment; filename="acta_cita_{cita_id}.pdf"', "Cache-Control": "no-store"})


@citas_bp.get("/estudiante/<int:estudiante_id>/historial")
@roles_permitidos(*PERSONAL)
def historial_estudiante(estudiante_id):
    usuario = usuario_actual()
    citas = [cita for cita in consultar_citas(usuario) if cita.get("id_estudiante") == estudiante_id]
    if not citas:
        abort(404)
    return render_template("citas/historial.html", citas=citas, detalles=datos_escolares(citas, privado=True), estudiante=citas[0]["estudiante"])
