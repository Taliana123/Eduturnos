from calendar import monthrange
from datetime import date, datetime, timedelta

from flask import (
    Blueprint,
    Response,
    abort,
    jsonify,
    render_template,
    request,
    url_for,
)

from database.db import consultar
from routes.helpers import usuario_actual, login_requerido


calendario_bp = Blueprint(
    "calendario",
    __name__,
    url_prefix="/calendario",
)


def _filtros_usuario(usuario):
    rol = usuario["rol_nombre"]

    filtros = []
    params = []

    if rol in (
        "Super Admin",
        "Rector",
        "Administrador / Coordinador",
    ):
        return filtros, params

    if rol == "Docente":
        filtros.append(
            """(c.id_docente = (
                SELECT d.id_docente
                FROM docentes d
                WHERE d.id_usuario = %s
            ) OR c.destinatario_usuario_id=%s OR c.creado_por=%s OR EXISTS (
                SELECT 1 FROM cita_participantes cp WHERE cp.id_cita=c.id AND cp.id_usuario=%s
            ))"""
        )
        params.extend([usuario["id_usuario"]] * 4)

    elif rol == "Estudiante":
        filtros.append(
            """
            (c.id_estudiante = (
                SELECT e.id_estudiante
                FROM estudiantes e
                WHERE e.id_usuario = %s
            ) OR EXISTS (SELECT 1 FROM cita_participantes cp WHERE cp.id_cita=c.id AND cp.id_usuario=%s))
            """
        )
        params.extend([usuario["id_usuario"]] * 2)

    elif rol == "Acudiente":
        filtros.append(
            """
            (c.id_acudiente = (
                SELECT a.id_acudiente
                FROM acudientes a
                WHERE a.id_usuario = %s
            ) OR EXISTS (SELECT 1 FROM cita_participantes cp WHERE cp.id_cita=c.id AND cp.id_usuario=%s))
            """
        )
        params.extend([usuario["id_usuario"]] * 2)

    else:
        filtros.append("1 = 0")

    return filtros, params


def _normalizar_cita(cita):
    resultado = dict(cita)

    if resultado.get("fecha") is not None:
        valor = resultado["fecha"]

        if hasattr(valor, "isoformat"):
            resultado["fecha"] = valor.isoformat()

    if resultado.get("hora") is not None:
        valor = resultado["hora"]

        if hasattr(valor, "isoformat"):
            resultado["hora"] = valor.isoformat()

    if resultado.get("fecha_creacion") is not None:
        valor = resultado["fecha_creacion"]

        if hasattr(valor, "isoformat"):
            resultado["fecha_creacion"] = valor.isoformat()

    return resultado


def citas_visibles(usuario=None):
    usuario = usuario or usuario_actual()

    filtros, params = _filtros_usuario(usuario)

    where = ""

    if filtros:
        where = " WHERE " + " AND ".join(filtros)

    sql = f"""
        SELECT
            c.id,
            c.id_estudiante,
            c.id_acudiente,
            c.id_docente,
            c.id_motivo,
            c.id_estado,
            c.id_periodo,
            c.creado_por,
            c.destinatario_tipo,
            c.destinatario_usuario_id,
            c.fecha,
            c.hora,
            c.lugar,
            c.observaciones,
            c.fecha_creacion,

            e.id_sede AS id_sede,
            e.id_jornada AS id_jornada,
            e.documento AS estudiante_documento,
            e.codigo_estudiantil,

            COALESCE(NULLIF(CONCAT(e.nombres,' ',e.apellidos),' '),
                CASE WHEN c.destinatario_tipo IS NOT NULL THEN CONCAT(dest.nombres,' ',dest.apellidos) ELSE '' END
            ) AS estudiante,

            CONCAT(
                a.nombres,
                ' ',
                a.apellidos
            ) AS acudiente,

            CONCAT(
                d.nombres,
                ' ',
                d.apellidos
            ) AS docente,

            m.nombre AS motivo_nombre,

            ec.nombre AS estado_nombre,

            s.nombre AS sede_nombre,

            j.nombre AS jornada_nombre,
            creador_rol.nombre AS creador_rol

        FROM citas c

        LEFT JOIN estudiantes e
            ON e.id_estudiante = c.id_estudiante

        LEFT JOIN acudientes a
            ON a.id_acudiente = c.id_acudiente

        LEFT JOIN docentes d
            ON d.id_docente = c.id_docente

        INNER JOIN motivos m
            ON m.id = c.id_motivo

        INNER JOIN estados_cita ec
            ON ec.id = c.id_estado

        LEFT JOIN usuarios creador
            ON creador.id_usuario = c.creado_por

        LEFT JOIN usuarios dest
            ON dest.id_usuario = c.destinatario_usuario_id

        LEFT JOIN roles creador_rol
            ON creador_rol.id = creador.id_rol

        LEFT JOIN sedes s
            ON s.id = e.id_sede

        LEFT JOIN jornadas j
            ON j.id = e.id_jornada

        {where}

        ORDER BY
            c.fecha ASC,
            c.hora ASC,
            c.id ASC

        LIMIT 2000
    """

    registros = consultar(
        sql,
        tuple(params)
    )

    return [
        _normalizar_cita(cita)
        for cita in registros
    ]


def _ajustar_mes(anio, mes):
    while mes < 1:
        anio -= 1
        mes += 12

    while mes > 12:
        anio += 1
        mes -= 12

    return anio, mes


def _fecha_cita(cita):
    fecha = cita.get("fecha")
    hora = cita.get("hora")

    if not fecha:
        return None

    try:
        if isinstance(fecha, str):
            fecha_obj = date.fromisoformat(
                fecha[:10]
            )
        else:
            fecha_obj = fecha

        if isinstance(hora, str):
            partes = hora.split(":")
            h = int(partes[0])
            m = int(partes[1]) if len(partes) > 1 else 0
            s = int(partes[2]) if len(partes) > 2 else 0
        else:
            h = getattr(hora, "hour", 0)
            m = getattr(hora, "minute", 0)
            s = getattr(hora, "second", 0)

        return datetime(
            fecha_obj.year,
            fecha_obj.month,
            fecha_obj.day,
            h,
            m,
            s,
        )

    except Exception:
        return None


def _aplicar_filtros(citas):
    texto = (
        request.args.get("buscar", "")
        .strip()
        .lower()
    )

    sede = (
        request.args.get("sede", "")
        .strip()
    )

    jornada = (
        request.args.get("jornada", "")
        .strip()
    )

    docente = (
        request.args.get("docente", "")
        .strip()
        .lower()
    )

    estado = (
        request.args.get("estado", "")
        .strip()
        .lower()
    )

    desde = (
        request.args.get("desde", "")
        .strip()
    )

    resultado = []

    for cita in citas:

        if texto:
            contenido = " ".join(
                [
                    str(cita.get("estudiante") or ""),
                    str(cita.get("docente") or ""),
                    str(cita.get("acudiente") or ""),
                    str(cita.get("motivo_nombre") or ""),
                    str(cita.get("sede_nombre") or ""),
                    str(cita.get("jornada_nombre") or ""),
                    str(cita.get("lugar") or ""),
                    str(cita.get("observaciones") or ""),
                ]
            ).lower()

            if texto not in contenido:
                continue

        if (
            sede
            and str(cita.get("id_sede"))
            != sede
        ):
            continue

        if (
            jornada
            and str(cita.get("id_jornada"))
            != jornada
        ):
            continue

        if docente:
            nombre_docente = (
                str(cita.get("docente") or "")
                .strip()
                .lower()
            )

            if nombre_docente != docente:
                continue

        if estado:
            nombre_estado = (
                str(cita.get("estado_nombre") or "")
                .strip()
                .lower()
            )

            if nombre_estado != estado:
                continue

        if (
            desde
            and str(cita.get("fecha") or "")
            < desde
        ):
            continue

        resultado.append(cita)

    return resultado


@calendario_bp.route("/")
@login_requerido
def index():
    usuario = usuario_actual()

    hoy = date.today()

    try:
        anio = int(
            request.args.get(
                "anio",
                hoy.year
            )
        )

        mes = int(
            request.args.get(
                "mes",
                hoy.month
            )
        )

    except (TypeError, ValueError):
        anio = hoy.year
        mes = hoy.month

    anio, mes = _ajustar_mes(
        anio,
        mes
    )

    filtros_enlace = {
        clave: valor
        for clave, valor in request.args.items()
        if clave not in {"anio", "mes", "dia"}
    }

    dia_seleccionado = None
    valor_dia = request.args.get("dia", "").strip()

    if valor_dia:
        try:
            dia_seleccionado = date.fromisoformat(valor_dia)
        except ValueError:
            dia_seleccionado = None

    if dia_seleccionado:
        anio, mes = _ajustar_mes(
            dia_seleccionado.year,
            dia_seleccionado.month
        )

    url_calendario_sin_dia = url_for(
        "calendario.index",
        anio=anio,
        mes=mes,
        **filtros_enlace
    )

    citas = citas_visibles(usuario)

    citas = _aplicar_filtros(citas)

    sedes = consultar(
        """
        SELECT
            id,
            nombre
        FROM sedes
        ORDER BY nombre
        """
    )

    jornadas = consultar(
        """
        SELECT
            id,
            nombre
        FROM jornadas
        ORDER BY id
        """
    )

    docentes = sorted(
        {
            str(cita.get("docente"))
            for cita in citas
            if cita.get("docente")
        },
        key=lambda valor: valor.lower()
    )

    roles_disponibilidad = (
        "Super Admin",
        "Rector",
        "Administrador / Coordinador",
        "Docente",
    )
    puede_configurar_disponibilidad = usuario["rol_nombre"] in roles_disponibilidad
    docentes_disponibilidad = []
    docente_disponibilidad_id = None
    franjas_disponibilidad = []
    if puede_configurar_disponibilidad:
        if usuario["rol_nombre"] == "Docente":
            docentes_disponibilidad = consultar(
                "SELECT id_docente, CONCAT(nombres, ' ', apellidos) AS nombre "
                "FROM docentes WHERE id_usuario=%s AND estado=1",
                (usuario["id_usuario"],),
            )
        else:
            docentes_disponibilidad = consultar(
                "SELECT id_docente, CONCAT(nombres, ' ', apellidos) AS nombre "
                "FROM docentes WHERE estado=1 ORDER BY apellidos,nombres"
            )

        ids_docentes = {int(docente["id_docente"]) for docente in docentes_disponibilidad}
        try:
            solicitado = int(request.args.get("docente_disp", ""))
        except (TypeError, ValueError):
            solicitado = None
        docente_disponibilidad_id = (
            solicitado if solicitado in ids_docentes
            else int(docentes_disponibilidad[0]["id_docente"]) if docentes_disponibilidad
            else None
        )
        if docente_disponibilidad_id:
            franjas_disponibilidad = consultar(
                "SELECT id,dia_semana,hora_inicio,hora_fin FROM disponibilidad_docente "
                "WHERE id_docente=%s ORDER BY dia_semana,hora_inicio",
                (docente_disponibilidad_id,),
            )

    primer_dia = date(
        anio,
        mes,
        1
    )

    ultimo_dia = monthrange(
        anio,
        mes
    )[1]

    desplazamiento = primer_dia.weekday()

    inicio_calendario = (
        primer_dia -
        timedelta(
            days=desplazamiento
        )
    )

    total_celdas = 42

    semanas = []

    citas_por_fecha = {}

    for cita in citas:
        fecha = str(
            cita.get("fecha") or ""
        )[:10]

        if not fecha:
            continue

        citas_por_fecha.setdefault(
            fecha,
            []
        ).append(cita)

    citas_del_dia = (
        citas_por_fecha.get(dia_seleccionado.isoformat(), [])
        if dia_seleccionado
        else []
    )

    for indice in range(total_celdas):

        fecha_celda = (
            inicio_calendario +
            timedelta(
                days=indice
            )
        )

        semana_indice = indice // 7

        if len(semanas) <= semana_indice:
            semanas.append([])

        semanas[semana_indice].append(
            {
                "fecha": fecha_celda,
                "iso": fecha_celda.isoformat(),
                "numero": fecha_celda.day,
                "es_mes": (
                    fecha_celda.month == mes
                    and fecha_celda.year == anio
                ),
                "es_hoy": (
                    fecha_celda == hoy
                ),
                "url": url_for(
                    "calendario.index",
                    dia=fecha_celda.isoformat(),
                    **filtros_enlace
                ),
                "citas": citas_por_fecha.get(
                    fecha_celda.isoformat(),
                    []
                ),
            }
        )

    anio_anterior, mes_anterior = _ajustar_mes(
        anio,
        mes - 1
    )

    anio_siguiente, mes_siguiente = _ajustar_mes(
        anio,
        mes + 1
    )

    citas_proximas = []

    for cita in citas:

        fecha_cita = _fecha_cita(cita)

        if not fecha_cita:
            continue

        if fecha_cita >= datetime.now():
            citas_proximas.append(
                (
                    fecha_cita,
                    cita
                )
            )

    citas_proximas.sort(
        key=lambda elemento: elemento[0]
    )

    citas_proximas = [
        cita
        for _, cita in citas_proximas[:10]
    ]

    pendientes = sum(
        1
        for cita in citas
        if "pendiente"
        in str(
            cita.get("estado_nombre") or ""
        ).lower()
    )

    confirmadas = sum(
        1
        for cita in citas
        if "confirm"
        in str(
            cita.get("estado_nombre") or ""
        ).lower()
    )

    citas_hoy = sum(
        1
        for cita in citas
        if str(
            cita.get("fecha") or ""
        )[:10]
        == hoy.isoformat()
    )

    puede_crear = usuario["rol_nombre"] in (
        "Super Admin",
        "Rector",
        "Administrador / Coordinador",
        "Docente",
    )

    return render_template(
        "calendario/index.html",
        anio=anio,
        mes=mes,
        dia_seleccionado=dia_seleccionado,
        citas_del_dia=citas_del_dia,
        url_calendario_sin_dia=url_calendario_sin_dia,
        primer_dia=primer_dia,
        ultimo_dia=ultimo_dia,
        semanas=semanas,
        citas=citas,
        usuario=usuario,
        usuario_id=usuario["id_usuario"],
        rol_usuario=usuario["rol_nombre"],
        citas_proximas=citas_proximas,
        sedes=sedes,
        jornadas=jornadas,
        docentes=docentes,
        citas_hoy=citas_hoy,
        fecha_minima=hoy.isoformat(),
        pendientes=pendientes,
        confirmadas=confirmadas,
        anio_anterior=anio_anterior,
        mes_anterior=mes_anterior,
        anio_siguiente=anio_siguiente,
        mes_siguiente=mes_siguiente,
        puede_crear=puede_crear,
        puede_configurar_disponibilidad=puede_configurar_disponibilidad,
        docentes_disponibilidad=docentes_disponibilidad,
        docente_disponibilidad_id=docente_disponibilidad_id,
        franjas_disponibilidad=franjas_disponibilidad,
        nombres_dias=("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"),
    )


@calendario_bp.route("/api/citas")
@login_requerido
def api_citas():
    usuario = usuario_actual()

    return jsonify(
        {
            "ok": True,
            "citas": citas_visibles(usuario),
        }
    )


@calendario_bp.route("/<int:cita_id>.ics")
@login_requerido
def descargar_ics(cita_id):
    usuario = usuario_actual()

    citas = citas_visibles(usuario)

    ids_visibles = {
        int(cita["id"])
        for cita in citas
    }

    if cita_id not in ids_visibles:
        abort(404)

    cita = consultar(
        """
        SELECT
            c.id,
            c.fecha,
            c.hora,
            c.lugar,
            c.observaciones,

            m.nombre AS motivo,

            ec.nombre AS estado,

            COALESCE(NULLIF(CONCAT(e.nombres,' ',e.apellidos),' '),
                CASE WHEN c.destinatario_tipo IS NOT NULL THEN CONCAT(dest.nombres,' ',dest.apellidos) ELSE '' END
            ) AS estudiante,

            CONCAT(
                d.nombres,
                ' ',
                d.apellidos
            ) AS docente,

            CONCAT(
                a.nombres,
                ' ',
                a.apellidos
            ) AS acudiente

        FROM citas c

        LEFT JOIN estudiantes e
            ON e.id_estudiante = c.id_estudiante

        LEFT JOIN docentes d
            ON d.id_docente = c.id_docente

        LEFT JOIN acudientes a
            ON a.id_acudiente = c.id_acudiente

        LEFT JOIN usuarios dest
            ON dest.id_usuario = c.destinatario_usuario_id

        INNER JOIN motivos m
            ON m.id = c.id_motivo

        INNER JOIN estados_cita ec
            ON ec.id = c.id_estado

        WHERE c.id = %s

        LIMIT 1
        """,
        (cita_id,),
        uno=True,
    )

    if not cita:
        abort(404)

    inicio = datetime.combine(
        cita["fecha"],
        cita["hora"]
    )

    fin = inicio + timedelta(
        minutes=45
    )

    def escapar(valor):
        return (
            str(valor or "")
            .replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\r", "")
            .replace("\n", "\\n")
        )

    descripcion = (
        f"Estado: {cita['estado']} | "
        f"Estudiante: {cita['estudiante']} | "
        f"Docente: {cita['docente']} | "
        f"Acudiente: {cita['acudiente']} | "
        f"{cita['observaciones'] or ''}"
    )

    contenido = "\r\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//EDUTURNOS//ES",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            f"UID:eduturnos-{cita['id']}@eduturnos",
            (
                f"DTSTAMP:"
                f"{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
            ),
            (
                f"DTSTART:"
                f"{inicio.strftime('%Y%m%dT%H%M%S')}"
            ),
            (
                f"DTEND:"
                f"{fin.strftime('%Y%m%dT%H%M%S')}"
            ),
            (
                "SUMMARY:"
                + escapar(
                    "EDUTURNOS - "
                    + cita["motivo"]
                )
            ),
            "LOCATION:" +
            escapar(cita["lugar"]),
            "DESCRIPTION:" +
            escapar(descripcion),
            "END:VEVENT",
            "END:VCALENDAR",
        ]
    )

    contenido += "\r\n"

    return Response(
        contenido,
        mimetype="text/calendar",
        headers={
            "Content-Disposition":
                (
                    'attachment; '
                    f'filename="eduturnos_cita_{cita_id}.ics"'
                )
        },
    )
