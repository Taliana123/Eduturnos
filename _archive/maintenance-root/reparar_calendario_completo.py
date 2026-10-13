from pathlib import Path
import shutil


BASE = Path(__file__).resolve().parent

ROUTES = BASE / "routes"
TEMPLATES = BASE / "templates" / "calendario"

ROUTE_FILE = ROUTES / "calendario.py"
TEMPLATE_FILE = TEMPLATES / "index.html"


ROUTES.mkdir(parents=True, exist_ok=True)
TEMPLATES.mkdir(parents=True, exist_ok=True)


def backup_archivo(path, sufijo):
    if path.exists():
        destino = path.with_name(
            path.name + sufijo
        )
        shutil.copy2(path, destino)
        return destino
    return None


backup_route = backup_archivo(
    ROUTE_FILE,
    ".backup_calendario_completo"
)

backup_template = backup_archivo(
    TEMPLATE_FILE,
    ".backup_calendario_completo"
)


ROUTE_CODE = r'''
from calendar import monthrange
from datetime import date, datetime, timedelta

from flask import (
    Blueprint,
    Response,
    abort,
    jsonify,
    render_template,
    request,
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
            """
            c.id_docente = (
                SELECT d.id_docente
                FROM docentes d
                WHERE d.id_usuario = %s
            )
            """
        )
        params.append(usuario["id_usuario"])

    elif rol == "Estudiante":
        filtros.append(
            """
            c.id_estudiante = (
                SELECT e.id_estudiante
                FROM estudiantes e
                WHERE e.id_usuario = %s
            )
            """
        )
        params.append(usuario["id_usuario"])

    elif rol == "Acudiente":
        filtros.append(
            """
            c.id_acudiente = (
                SELECT a.id_acudiente
                FROM acudientes a
                WHERE a.id_usuario = %s
            )
            """
        )
        params.append(usuario["id_usuario"])

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
            c.fecha,
            c.hora,
            c.lugar,
            c.observaciones,
            c.fecha_creacion,

            e.id_sede AS id_sede,
            e.id_jornada AS id_jornada,
            e.documento AS estudiante_documento,
            e.codigo_estudiantil,

            CONCAT(
                e.nombres,
                ' ',
                e.apellidos
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

            j.nombre AS jornada_nombre

        FROM citas c

        INNER JOIN estudiantes e
            ON e.id_estudiante = c.id_estudiante

        INNER JOIN acudientes a
            ON a.id_acudiente = c.id_acudiente

        INNER JOIN docentes d
            ON d.id_docente = c.id_docente

        INNER JOIN motivos m
            ON m.id = c.id_motivo

        INNER JOIN estados_cita ec
            ON ec.id = c.id_estado

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
        primer_dia=primer_dia,
        ultimo_dia=ultimo_dia,
        semanas=semanas,
        citas=citas,
        citas_proximas=citas_proximas,
        sedes=sedes,
        jornadas=jornadas,
        docentes=docentes,
        citas_hoy=citas_hoy,
        pendientes=pendientes,
        confirmadas=confirmadas,
        anio_anterior=anio_anterior,
        mes_anterior=mes_anterior,
        anio_siguiente=anio_siguiente,
        mes_siguiente=mes_siguiente,
        puede_crear=puede_crear,
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

            CONCAT(
                e.nombres,
                ' ',
                e.apellidos
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

        INNER JOIN estudiantes e
            ON e.id_estudiante = c.id_estudiante

        INNER JOIN docentes d
            ON d.id_docente = c.id_docente

        INNER JOIN acudientes a
            ON a.id_acudiente = c.id_acudiente

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
'''


TEMPLATE_CODE = r'''
{% extends "base.html" %}

{% block title %}Calendario de citas | EDUTURNOS{% endblock %}

{% block content %}

<style>

.ed-cal-page {
    width: 100%;
    max-width: 1500px;
    margin: 0 auto;
    padding: 22px;
    color: #1e293b;
}

.ed-cal-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 18px;
    margin-bottom: 18px;
    flex-wrap: wrap;
}

.ed-cal-head h1 {
    margin: 0;
    color: #123b68;
    font-size: 30px;
    font-weight: 800;
}

.ed-cal-head p {
    margin: 6px 0 0;
    color: #68778a;
    font-size: 14px;
}

.ed-cal-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.ed-cal-btn {
    min-height: 39px;
    padding: 0 13px;
    border: 1px solid #d4dde6;
    border-radius: 8px;
    background: #fff;
    color: #29415d;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 13px;
    font-weight: 700;
}

.ed-cal-btn:hover {
    background: #f5f8fb;
}

.ed-cal-btn-primary {
    background: #123b68;
    border-color: #123b68;
    color: white;
}

.ed-cal-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 11px;
    margin-bottom: 15px;
}

.ed-cal-stat {
    background: #fff;
    border: 1px solid #e0e6ed;
    border-radius: 10px;
    padding: 13px 15px;
}

.ed-cal-stat-label {
    color: #77869a;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
}

.ed-cal-stat-value {
    margin-top: 5px;
    color: #123b68;
    font-size: 24px;
    font-weight: 800;
}

.ed-cal-filters {
    background: #fff;
    border: 1px solid #e0e6ed;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 15px;
}

.ed-cal-filter-form {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr 1fr auto;
    gap: 8px;
    align-items: center;
}

.ed-cal-filter-form input,
.ed-cal-filter-form select {
    width: 100%;
    height: 38px;
    border: 1px solid #ccd6e0;
    border-radius: 7px;
    background: #fff;
    color: #263b54;
    padding: 0 10px;
    font-size: 12px;
    outline: none;
}

.ed-cal-filter-form input:focus,
.ed-cal-filter-form select:focus {
    border-color: #3675b2;
}

.ed-cal-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}

.ed-cal-nav {
    display: flex;
    align-items: center;
    gap: 6px;
}

.ed-cal-nav a,
.ed-cal-today {
    min-width: 37px;
    height: 37px;
    padding: 0 10px;
    border: 1px solid #d1dbe5;
    border-radius: 7px;
    background: #fff;
    color: #263b54;
    text-decoration: none;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    font-size: 13px;
    font-weight: 800;
}

.ed-cal-nav a:hover,
.ed-cal-today:hover {
    background: #f3f7fa;
}

.ed-cal-periodo {
    margin-left: 6px;
    color: #123b68;
    font-size: 21px;
    font-weight: 800;
    text-transform: capitalize;
}

.ed-cal-card {
    background: #fff;
    border: 1px solid #dce4eb;
    border-radius: 11px;
    overflow-x: auto;
    padding: 8px;
}

.ed-month {
    width: 100%;
    min-width: 1000px;
    border-collapse: separate;
    border-spacing: 0;
    table-layout: fixed;
    border: 1px solid #d8e1e9;
}

.ed-month th {
    height: 42px;
    padding: 7px;
    background: #f3f6f9;
    border-right: 1px solid #dbe3ea;
    border-bottom: 1px solid #dbe3ea;
    color: #526176;
    text-align: center;
    font-size: 11px;
    font-weight: 800;
}

.ed-month th:last-child {
    border-right: 0;
}

.ed-day {
    height: 145px;
    vertical-align: top;
    padding: 6px;
    border-right: 1px solid #e0e6ec;
    border-bottom: 1px solid #e0e6ec;
    background: #fff;
}

.ed-day:last-child {
    border-right: 0;
}

.ed-day.other {
    background: #fafbfd;
}

.ed-day.today {
    background: #f1f7fc;
}

.ed-day-number {
    width: 27px;
    height: 27px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;
    margin-bottom: 5px;
    color: #394b60;
    font-size: 11px;
    font-weight: 800;
}

.ed-day.other .ed-day-number {
    color: #a3afbd;
}

.ed-day.today .ed-day-number {
    background: #123b68;
    color: #fff;
}

.ed-events {
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.ed-cita {
    width: 100%;
    border: 1px solid transparent;
    border-left: 4px solid #2b699f;
    border-radius: 5px;
    background: #edf4fb;
    color: #203e60;
    overflow: hidden;
}

.ed-cita summary {
    list-style: none;
    cursor: pointer;
    padding: 5px 6px;
    font-size: 10px;
    line-height: 1.25;
    font-weight: 700;
}

.ed-cita summary::-webkit-details-marker {
    display: none;
}

.ed-cita summary::after {
    content: "›";
    float: right;
    font-size: 13px;
    font-weight: 900;
}

.ed-cita.pendiente {
    border-left-color: #d3931d;
    background: #fff7e5;
    color: #75510d;
}

.ed-cita.confirmada {
    border-left-color: #258b59;
    background: #edf8f1;
    color: #195e3d;
}

.ed-cita.cancelada {
    border-left-color: #c74b4b;
    background: #fff0f0;
    color: #792b2b;
    opacity: .78;
}

.ed-cita.reprogramada {
    border-left-color: #7653ac;
    background: #f4effb;
    color: #573d82;
}

.ed-cita.completada {
    border-left-color: #2e6d9e;
    background: #edf5fb;
    color: #245378;
}

.ed-cita-time {
    font-weight: 800;
}

.ed-cita-detail {
    position: relative;
    z-index: 20;
    margin: 0 4px 5px;
    padding: 8px;
    border-radius: 7px;
    background: #fff;
    border: 1px solid #dce4eb;
    color: #26384f;
    box-shadow: 0 6px 18px rgba(15,23,42,.10);
    font-size: 10px;
}

.ed-cita-detail div {
    margin-bottom: 4px;
}

.ed-cita-detail div:last-child {
    margin-bottom: 0;
}

.ed-cita-label {
    color: #7a8899;
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
}

.ed-cita-link {
    display: inline-flex;
    margin-top: 5px;
    padding: 4px 7px;
    border-radius: 5px;
    background: #123b68;
    color: #fff;
    text-decoration: none;
    font-size: 9px;
    font-weight: 800;
}

.ed-more {
    color: #65758a;
    padding: 2px 4px;
    font-size: 10px;
    font-weight: 800;
}

.ed-upcoming {
    margin-top: 15px;
    background: #fff;
    border: 1px solid #e0e6ed;
    border-radius: 10px;
    padding: 14px;
}

.ed-upcoming h2 {
    margin: 0 0 10px;
    color: #123b68;
    font-size: 18px;
}

.ed-upcoming-list {
    display: grid;
    gap: 7px;
}

.ed-upcoming-item {
    display: grid;
    grid-template-columns: 110px 1fr auto;
    gap: 12px;
    align-items: center;
    padding: 10px;
    border: 1px solid #e3e9ef;
    border-radius: 8px;
    background: #fafcfd;
}

.ed-upcoming-date {
    color: #123b68;
    font-size: 11px;
    font-weight: 800;
}

.ed-upcoming-main strong {
    display: block;
    color: #26384f;
    font-size: 12px;
}

.ed-upcoming-main span {
    display: block;
    margin-top: 3px;
    color: #788699;
    font-size: 10px;
}

.ed-state {
    padding: 5px 8px;
    border-radius: 999px;
    background: #edf1f5;
    color: #4c5d72;
    font-size: 9px;
    font-weight: 800;
}

.ed-empty {
    padding: 38px 15px;
    text-align: center;
    color: #7c8a9c;
    font-size: 12px;
}

@media (max-width: 1050px) {
    .ed-cal-filter-form {
        grid-template-columns: repeat(3, 1fr);
    }

    .ed-cal-stats {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 650px) {
    .ed-cal-page {
        padding: 10px;
    }

    .ed-cal-filter-form {
        grid-template-columns: 1fr;
    }

    .ed-cal-stats {
        grid-template-columns: 1fr 1fr;
    }

    .ed-cal-head h1 {
        font-size: 25px;
    }

    .ed-month {
        min-width: 920px;
    }
}

</style>


<div class="ed-cal-page">

    <div class="ed-cal-head">

        <div>

            <h1>Calendario de citas</h1>

            <p>
                Consulta las citaciones programadas dentro del calendario institucional.
            </p>

        </div>


        <div class="ed-cal-actions">

            <a
                class="ed-cal-btn"
                href="{{ url_for('auth.dashboard') }}"
            >
                ← Atrás
            </a>

            <a
                class="ed-cal-btn"
                href="{{ url_for('citas.index') }}"
            >
                Ver citas
            </a>

            {% if puede_crear %}

            <a
                class="ed-cal-btn ed-cal-btn-primary"
                href="{{ url_for('citas.nueva') }}"
            >
                + Nueva cita
            </a>

            {% endif %}

        </div>

    </div>


    <div class="ed-cal-stats">

        <div class="ed-cal-stat">

            <div class="ed-cal-stat-label">
                Citas visibles
            </div>

            <div class="ed-cal-stat-value">
                {{ citas|length }}
            </div>

        </div>


        <div class="ed-cal-stat">

            <div class="ed-cal-stat-label">
                Citas de hoy
            </div>

            <div class="ed-cal-stat-value">
                {{ citas_hoy }}
            </div>

        </div>


        <div class="ed-cal-stat">

            <div class="ed-cal-stat-label">
                Pendientes
            </div>

            <div class="ed-cal-stat-value">
                {{ pendientes }}
            </div>

        </div>


        <div class="ed-cal-stat">

            <div class="ed-cal-stat-label">
                Confirmadas
            </div>

            <div class="ed-cal-stat-value">
                {{ confirmadas }}
            </div>

        </div>

    </div>


    <div class="ed-cal-filters">

        <form
            method="get"
            action="{{ url_for('calendario.index') }}"
            class="ed-cal-filter-form"
        >

            <input
                name="buscar"
                type="search"
                value="{{ request.args.get('buscar', '') }}"
                placeholder="Buscar estudiante, docente, acudiente o motivo..."
            >


            <select name="sede">

                <option value="">
                    Todas las sedes
                </option>

                {% for sede in sedes %}

                <option
                    value="{{ sede.id }}"
                    {% if request.args.get('sede') == sede.id|string %}selected{% endif %}
                >
                    {{ sede.nombre }}
                </option>

                {% endfor %}

            </select>


            <select name="jornada">

                <option value="">
                    Todas las jornadas
                </option>

                {% for jornada in jornadas %}

                <option
                    value="{{ jornada.id }}"
                    {% if request.args.get('jornada') == jornada.id|string %}selected{% endif %}
                >
                    {{ jornada.nombre }}
                </option>

                {% endfor %}

            </select>


            <select name="docente">

                <option value="">
                    Todos los docentes
                </option>

                {% for docente in docentes %}

                <option
                    value="{{ docente }}"
                    {% if request.args.get('docente', '').lower() == docente.lower() %}selected{% endif %}
                >
                    {{ docente }}
                </option>

                {% endfor %}

            </select>


            <select name="estado">

                <option value="">
                    Todos los estados
                </option>

                {% for estado in [
                    "Pendiente",
                    "Confirmada",
                    "Cancelada",
                    "Reprogramada",
                    "Completada"
                ] %}

                <option
                    value="{{ estado }}"
                    {% if request.args.get('estado', '').lower() == estado.lower() %}selected{% endif %}
                >
                    {{ estado }}
                </option>

                {% endfor %}

            </select>


            <input
                name="desde"
                type="date"
                value="{{ request.args.get('desde', '') }}"
            >


            <button
                class="ed-cal-btn ed-cal-btn-primary"
                type="submit"
            >
                Filtrar
            </button>

        </form>


        <div style="margin-top:8px;">

            <a
                class="ed-cal-btn"
                href="{{ url_for(
                    'calendario.index',
                    anio=anio,
                    mes=mes
                ) }}"
            >
                Limpiar filtros
            </a>

        </div>

    </div>


    <div class="ed-cal-toolbar">

        <div class="ed-cal-nav">

            <a
                href="{{ url_for(
                    'calendario.index',
                    anio=anio_anterior,
                    mes=mes_anterior,
                    buscar=request.args.get('buscar', ''),
                    sede=request.args.get('sede', ''),
                    jornada=request.args.get('jornada', ''),
                    docente=request.args.get('docente', ''),
                    estado=request.args.get('estado', ''),
                    desde=request.args.get('desde', '')
                ) }}"
                title="Mes anterior"
            >
                ‹
            </a>


            <a
                href="{{ url_for(
                    'calendario.index',
                    anio=anio,
                    mes=mes
                ) }}"
                class="ed-cal-today"
            >
                Hoy
            </a>


            <a
                href="{{ url_for(
                    'calendario.index',
                    anio=anio_siguiente,
                    mes=mes_siguiente,
                    buscar=request.args.get('buscar', ''),
                    sede=request.args.get('sede', ''),
                    jornada=request.args.get('jornada', ''),
                    docente=request.args.get('docente', ''),
                    estado=request.args.get('estado', ''),
                    desde=request.args.get('desde', '')
                ) }}"
                title="Mes siguiente"
            >
                ›
            </a>


            <span class="ed-cal-periodo">

                {% set meses = [
                    "enero",
                    "febrero",
                    "marzo",
                    "abril",
                    "mayo",
                    "junio",
                    "julio",
                    "agosto",
                    "septiembre",
                    "octubre",
                    "noviembre",
                    "diciembre"
                ] %}

                {{ meses[mes - 1] }}
                {{ anio }}

            </span>

        </div>

    </div>


    <div class="ed-cal-card">

        <table class="ed-month">

            <thead>

                <tr>

                    <th>Lunes</th>
                    <th>Martes</th>
                    <th>Miércoles</th>
                    <th>Jueves</th>
                    <th>Viernes</th>
                    <th>Sábado</th>
                    <th>Domingo</th>

                </tr>

            </thead>


            <tbody>

                {% for semana in semanas %}

                <tr>

                    {% for dia in semana %}

                    <td
                        class="
                            ed-day
                            {% if not dia.es_mes %}other{% endif %}
                            {% if dia.es_hoy %}today{% endif %}
                        "
                    >

                        <div class="ed-day-number">
                            {{ dia.numero }}
                        </div>


                        <div class="ed-events">

                            {% for cita in dia.citas[:4] %}

                            <details
                                class="ed-cita
                                {% set estado = (cita.estado_nombre or '')|lower %}
                                {% if 'confirm' in estado %}
                                    confirmada
                                {% elif 'cancel' in estado %}
                                    cancelada
                                {% elif 'reprogram' in estado %}
                                    reprogramada
                                {% elif 'complet' in estado %}
                                    completada
                                {% else %}
                                    pendiente
                                {% endif %}
                                "
                            >

                                <summary>

                                    <span class="ed-cita-time">
                                        {{ (cita.hora|string)[:5] }}
                                    </span>

                                    ·

                                    {{ cita.motivo_nombre or "Cita" }}

                                </summary>


                                <div class="ed-cita-detail">

                                    <div>
                                        <span class="ed-cita-label">
                                            Estudiante
                                        </span>
                                        <br>
                                        {{ cita.estudiante or "—" }}
                                    </div>


                                    <div>
                                        <span class="ed-cita-label">
                                            Docente
                                        </span>
                                        <br>
                                        {{ cita.docente or "—" }}
                                    </div>


                                    <div>
                                        <span class="ed-cita-label">
                                            Acudiente
                                        </span>
                                        <br>
                                        {{ cita.acudiente or "—" }}
                                    </div>


                                    <div>
                                        <span class="ed-cita-label">
                                            Motivo
                                        </span>
                                        <br>
                                        {{ cita.motivo_nombre or "—" }}
                                    </div>


                                    <div>
                                        <span class="ed-cita-label">
                                            Sede
                                        </span>
                                        <br>
                                        {{ cita.sede_nombre or "—" }}
                                    </div>


                                    <div>
                                        <span class="ed-cita-label">
                                            Jornada
                                        </span>
                                        <br>
                                        {{ cita.jornada_nombre or "—" }}
                                    </div>


                                    <div>
                                        <span class="ed-cita-label">
                                            Lugar
                                        </span>
                                        <br>
                                        {{ cita.lugar or "—" }}
                                    </div>


                                    <div>
                                        <span class="ed-cita-label">
                                            Observaciones
                                        </span>
                                        <br>
                                        {{ cita.observaciones or "Sin observaciones." }}
                                    </div>


                                    <a
                                        class="ed-cita-link"
                                        href="{{ url_for(
                                            'calendario.descargar_ics',
                                            cita_id=cita.id
                                        ) }}"
                                    >
                                        Agregar al calendario
                                    </a>

                                </div>

                            </details>

                            {% endfor %}


                            {% if dia.citas|length > 4 %}

                            <div class="ed-more">

                                + {{ dia.citas|length - 4 }} citas más

                            </div>

                            {% endif %}

                        </div>

                    </td>

                    {% endfor %}

                </tr>

                {% endfor %}

            </tbody>

        </table>


        {% if not citas %}

        <div class="ed-empty">

            No hay citas que coincidan con los filtros seleccionados.

        </div>

        {% endif %}

    </div>


    <div class="ed-upcoming">

        <h2>
            Próximas citas
        </h2>


        {% if citas_proximas %}

        <div class="ed-upcoming-list">

            {% for cita in citas_proximas %}

            <details class="ed-cita">

                <summary>

                    <span class="ed-cita-time">
                        {{ (cita.hora|string)[:5] }}
                    </span>

                    ·

                    {{ cita.motivo_nombre or "Cita escolar" }}

                </summary>


                <div class="ed-cita-detail">

                    <div>
                        <span class="ed-cita-label">
                            Fecha
                        </span>
                        <br>
                        {{ cita.fecha }}
                    </div>

                    <div>
                        <span class="ed-cita-label">
                            Estudiante
                        </span>
                        <br>
                        {{ cita.estudiante or "—" }}
                    </div>

                    <div>
                        <span class="ed-cita-label">
                            Docente
                        </span>
                        <br>
                        {{ cita.docente or "—" }}
                    </div>

                    <div>
                        <span class="ed-cita-label">
                            Lugar
                        </span>
                        <br>
                        {{ cita.lugar or "—" }}
                    </div>

                    <div>
                        <span class="ed-cita-label">
                            Estado
                        </span>
                        <br>
                        {{ cita.estado_nombre or "—" }}
                    </div>

                    <a
                        class="ed-cita-link"
                        href="{{ url_for(
                            'calendario.descargar_ics',
                            cita_id=cita.id
                        ) }}"
                    >
                        Agregar al calendario
                    </a>

                </div>

            </details>

            {% endfor %}

        </div>

        {% else %}

        <div class="ed-empty">

            No hay próximas citas registradas.

        </div>

        {% endif %}

    </div>

</div>

{% endblock %}
'''


ROUTE_FILE.write_text(
    ROUTE_CODE.strip() + "\n",
    encoding="utf-8",
)

TEMPLATE_FILE.write_text(
    TEMPLATE_CODE.strip() + "\n",
    encoding="utf-8",
)


print()
print("=" * 72)
print("EDUTURNOS - CALENDARIO COMPLETAMENTE REPARADO")
print("=" * 72)
print()
print("ARCHIVOS ACTUALIZADOS:")
print(ROUTE_FILE)
print(TEMPLATE_FILE)
print()
print("BACKUPS:")
print(backup_route or "No existía routes/calendario.py")
print(backup_template or "No existía templates/calendario/index.html")
print()
print("CAMBIOS:")
print("- Calendario mensual generado por el servidor")
print("- 7 columnas: lunes a domingo")
print("- 42 casillas para cubrir todos los meses")
print("- Números de los días visibles")
print("- Citas dentro de cada fecha")
print("- Detalle de cada cita")
print("- Estudiante")
print("- Docente")
print("- Acudiente")
print("- Motivo")
print("- Sede")
print("- Jornada")
print("- Lugar")
print("- Observaciones")
print("- Descarga .ics")
print("- Próximas citas")
print("- Filtros")
print("- Anterior / Hoy / Siguiente")
print("- Funciona aunque existan 0 citas")
print()
print("NO SE MODIFICO MYSQL.")
print()
print("NO DEPENDE DE FULLCALENDAR.")
print()
print("=" * 72)