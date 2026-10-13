from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent

TEMPLATE = BASE / "templates" / "calendario" / "index.html"

JS = BASE / "static" / "vendor" / "fullcalendar" / "fullcalendar.global.js"
CSS = BASE / "static" / "vendor" / "fullcalendar" / "skeleton.css"
LOCALE = BASE / "static" / "vendor" / "fullcalendar" / "locales" / "es.global.js"

if not TEMPLATE.exists():
    print("[ERROR] No existe:")
    print(TEMPLATE)
    raise SystemExit(1)

if not JS.exists():
    print("[ERROR] No existe FullCalendar:")
    print(JS)
    raise SystemExit(1)

if not CSS.exists():
    print("[ERROR] No existe:")
    print(CSS)
    raise SystemExit(1)

if not LOCALE.exists():
    print("[ERROR] No existe el idioma español:")
    print(LOCALE)
    raise SystemExit(1)

BACKUP = TEMPLATE.with_name(
    "index.html.backup_antes_fullcalendar_real"
)

shutil.copy2(TEMPLATE, BACKUP)

contenido = r'''
{% extends "base.html" %}

{% block title %}Calendario de Citas · EDUTURNOS{% endblock %}

{% block content %}

<style>

.ed-cal-page {
    max-width: 1500px;
    margin: 0 auto;
}

.ed-cal-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 20px;
    margin-bottom: 18px;
    flex-wrap: wrap;
}

.ed-cal-header h1 {
    margin: 8px 0 5px;
    font-size: 1.9rem;
}

.ed-cal-header p {
    margin: 0;
    color: #667085;
}

.ed-cal-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.ed-cal-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 15px;
}

.ed-cal-stat {
    background: #fff;
    border: 1px solid #e4e8ee;
    border-radius: 14px;
    padding: 14px 16px;
}

.ed-cal-stat small {
    display: block;
    color: #667085;
    font-weight: 600;
    margin-bottom: 4px;
}

.ed-cal-stat strong {
    font-size: 1.45rem;
}

.ed-cal-filtros {
    background: #fff;
    border: 1px solid #e4e8ee;
    border-radius: 14px;
    padding: 13px;
    margin-bottom: 15px;
}

.ed-cal-filtros-grid {
    display: grid;
    grid-template-columns: 2fr repeat(5, 1fr);
    gap: 9px;
}

.ed-cal-filtros input,
.ed-cal-filtros select {
    width: 100%;
    min-height: 42px;
    box-sizing: border-box;
}

.ed-cal-filtros-bottom {
    display: flex;
    justify-content: space-between;
    gap: 9px;
    margin-top: 9px;
    flex-wrap: wrap;
}

.ed-cal-fechas {
    display: flex;
    gap: 9px;
    flex-wrap: wrap;
}

.ed-cal-fechas input {
    width: 170px;
}

.ed-cal-card {
    background: #fff;
    border: 1px solid #e0e5eb;
    border-radius: 16px;
    box-shadow: 0 6px 22px rgba(16,24,40,.06);
    overflow: hidden;
}

.ed-cal-toolbar-extra {
    padding: 10px 15px;
    border-bottom: 1px solid #edf0f4;
    display: flex;
    justify-content: space-between;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}

.ed-cal-conteo {
    color: #667085;
    font-size: .84rem;
}

#calendar {
    padding: 12px;
}

.fc {
    font-family: inherit;
}

.fc .fc-toolbar-title {
    font-size: 1.18rem;
    font-weight: 750;
}

.fc .fc-button {
    border-radius: 8px !important;
    box-shadow: none !important;
    border-width: 1px !important;
}

.fc .fc-daygrid-day-number {
    font-weight: 650;
}

.fc .fc-daygrid-day.fc-day-today {
    background: rgba(31,79,143,.07);
}

.fc .fc-event {
    border-radius: 6px;
    border-width: 0 0 0 3px;
    padding: 2px 5px;
    cursor: pointer;
}

.fc .fc-event-title {
    font-weight: 650;
}

.fc-event.ed-pendiente {
    background: #fff4cc !important;
    border-left-color: #d39b00 !important;
    color: #7f5f00 !important;
}

.fc-event.ed-confirmada {
    background: #e4f6ed !important;
    border-left-color: #178457 !important;
    color: #166747 !important;
}

.fc-event.ed-cancelada {
    background: #fdeaea !important;
    border-left-color: #bc3d3d !important;
    color: #982d2d !important;
}

.fc-event.ed-reprogramada {
    background: #e7efff !important;
    border-left-color: #4a73b8 !important;
    color: #2d5a9a !important;
}

.fc-event.ed-otro {
    background: #edf1f5 !important;
    border-left-color: #667085 !important;
    color: #475467 !important;
}

.ed-cal-modal {
    position: fixed;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: rgba(17,24,39,.58);
    z-index: 10000;
}

.ed-cal-modal.open {
    display: flex;
}

.ed-cal-modal-box {
    width: min(760px, 100%);
    max-height: 90vh;
    overflow-y: auto;
    background: #fff;
    border-radius: 18px;
    box-shadow: 0 25px 70px rgba(0,0,0,.25);
}

.ed-cal-modal-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 15px;
    padding: 20px 22px 15px;
    border-bottom: 1px solid #edf0f4;
}

.ed-cal-modal-head h2 {
    margin: 7px 0 0;
}

.ed-cal-close {
    width: 38px;
    height: 38px;
    border: 0;
    border-radius: 9px;
    background: #eef2f6;
    cursor: pointer;
    font-size: 21px;
}

.ed-cal-modal-body {
    padding: 18px 22px 22px;
}

.ed-cal-details {
    display: grid;
    grid-template-columns: repeat(2, minmax(0,1fr));
    gap: 11px;
}

.ed-cal-detail {
    padding: 12px;
    background: #f8fafc;
    border-radius: 10px;
}

.ed-cal-detail.full {
    grid-column: 1 / -1;
}

.ed-cal-detail small {
    display: block;
    color: #667085;
    font-weight: 700;
    margin-bottom: 4px;
}

.ed-cal-modal-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 17px;
}

.ed-cal-proximas {
    margin-top: 15px;
}

.ed-cal-proximas-list {
    padding: 0 15px;
}

.ed-cal-proxima {
    display: grid;
    grid-template-columns: 115px 1fr auto;
    gap: 14px;
    align-items: center;
    padding: 13px 0;
    border-bottom: 1px solid #edf0f4;
}

.ed-cal-proxima:last-child {
    border-bottom: 0;
}

.ed-cal-proxima-fecha {
    font-weight: 750;
}

.ed-cal-proxima-info strong {
    display: block;
    margin-bottom: 3px;
}

.ed-cal-proxima-info span {
    color: #667085;
    font-size: .83rem;
}

.ed-cal-status {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    padding: 5px 9px;
    font-size: .72rem;
    font-weight: 750;
    white-space: nowrap;
    background: #eef1f4;
    color: #475467;
}

.ed-cal-status.ed-pendiente {
    background: #fff4cc;
    color: #7f5f00;
}

.ed-cal-status.ed-confirmada {
    background: #e4f6ed;
    color: #166747;
}

.ed-cal-status.ed-cancelada {
    background: #fdeaea;
    color: #982d2d;
}

.ed-cal-status.ed-reprogramada {
    background: #e7efff;
    color: #2d5a9a;
}

.ed-cal-empty {
    text-align: center;
    padding: 30px;
    color: #667085;
}

@media (max-width: 1100px) {

    .ed-cal-filtros-grid {
        grid-template-columns: repeat(3, 1fr);
    }

}

@media (max-width: 750px) {

    .ed-cal-stats {
        grid-template-columns: repeat(2, 1fr);
    }

    .ed-cal-filtros-grid {
        grid-template-columns: 1fr 1fr;
    }

    .ed-cal-fechas input {
        width: 100%;
    }

    .ed-cal-proxima {
        grid-template-columns: 1fr;
        gap: 6px;
    }

    .ed-cal-details {
        grid-template-columns: 1fr;
    }

    .ed-cal-detail.full {
        grid-column: auto;
    }

}

@media (max-width: 520px) {

    .ed-cal-stats {
        grid-template-columns: 1fr;
    }

    .ed-cal-filtros-grid {
        grid-template-columns: 1fr;
    }

    .fc .fc-toolbar {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .fc .fc-toolbar-chunk {
        display: flex;
        justify-content: center;
    }

    #calendar {
        padding: 5px;
    }

}

</style>


<section class="ed-cal-page">

    <div class="ed-cal-header">

        <div>

            <a
                class="link-back"
                href="{{ request.referrer or url_for('auth.dashboard') }}"
            >
                ← Atrás
            </a>

            <h1>Calendario de Citas</h1>

            <p>
                Consulta y administra las citaciones programadas de la institución.
            </p>

        </div>

        <div class="ed-cal-actions">

            <a
                class="boton"
                href="{{ url_for('citas.index') }}"
            >
                Ver citas
            </a>

            {% if puede_crear %}

                <a
                    class="boton"
                    href="{{ url_for('citas.nueva') }}"
                >
                    + Nueva cita
                </a>

            {% endif %}

        </div>

    </div>


    <div class="ed-cal-stats">

        <div class="ed-cal-stat">
            <small>Citas visibles</small>
            <strong id="statTotal">0</strong>
        </div>

        <div class="ed-cal-stat">
            <small>Citas de hoy</small>
            <strong id="statHoy">0</strong>
        </div>

        <div class="ed-cal-stat">
            <small>Pendientes</small>
            <strong id="statPendientes">0</strong>
        </div>

        <div class="ed-cal-stat">
            <small>Confirmadas</small>
            <strong id="statConfirmadas">0</strong>
        </div>

    </div>


    <div class="ed-cal-filtros">

        <div class="ed-cal-filtros-grid">

            <input
                type="search"
                id="filtroTexto"
                placeholder="Buscar estudiante, documento, docente o motivo..."
            >


            <select id="filtroSede">

                <option value="">
                    Todas las sedes
                </option>

                {% for sede in sedes %}

                    <option value="{{ sede.id }}">
                        {{ sede.nombre }}
                    </option>

                {% endfor %}

            </select>


            <select id="filtroJornada">

                <option value="">
                    Todas las jornadas
                </option>

                {% for jornada in jornadas %}

                    <option value="{{ jornada.id }}">
                        {{ jornada.nombre }}
                    </option>

                {% endfor %}

            </select>


            <select id="filtroDocente">

                <option value="">
                    Todos los docentes
                </option>

                {% for docente in docentes %}

                    <option value="{{ docente.id }}">
                        {{ docente.nombre }}
                    </option>

                {% endfor %}

            </select>


            <select id="filtroMotivo">

                <option value="">
                    Todos los motivos
                </option>

                {% for motivo in motivos %}

                    <option value="{{ motivo.id }}">
                        {{ motivo.nombre }}
                    </option>

                {% endfor %}

            </select>


            <select id="filtroEstado">

                <option value="">
                    Todos los estados
                </option>

                {% for estado in estados %}

                    <option value="{{ estado.id }}">
                        {{ estado.nombre }}
                    </option>

                {% endfor %}

            </select>

        </div>


        <div class="ed-cal-filtros-bottom">

            <div class="ed-cal-fechas">

                <input
                    type="date"
                    id="filtroDesde"
                    title="Fecha desde"
                >

                <input
                    type="date"
                    id="filtroHasta"
                    title="Fecha hasta"
                >

            </div>


            <button
                type="button"
                class="boton"
                id="limpiarFiltros"
            >
                Limpiar filtros
            </button>

        </div>

    </div>


    <div class="ed-cal-card">

        <div class="ed-cal-toolbar-extra">

            <div class="ed-cal-conteo" id="conteoCalendario">
                Cargando citas...
            </div>

            <div class="ed-cal-conteo">
                Haz clic sobre una cita para ver sus detalles.
            </div>

        </div>


        <div id="calendar"></div>

    </div>


    <div class="ed-cal-card ed-cal-proximas">

        <div class="ed-cal-toolbar-extra">
            <strong>Próximas citas</strong>
        </div>

        <div
            class="ed-cal-proximas-list"
            id="proximas"
        ></div>

    </div>

</section>


<div
    class="ed-cal-modal"
    id="modalCita"
    aria-hidden="true"
>

    <div class="ed-cal-modal-box">

        <div class="ed-cal-modal-head">

            <div>

                <span class="badge">
                    Detalle de citación
                </span>

                <h2 id="modalTitulo">
                    Citación
                </h2>

            </div>


            <button
                type="button"
                class="ed-cal-close"
                id="cerrarModal"
            >
                ×
            </button>

        </div>


        <div class="ed-cal-modal-body">

            <div class="ed-cal-details">

                <div class="ed-cal-detail">
                    <small>Fecha</small>
                    <div id="modalFecha">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Hora</small>
                    <div id="modalHora">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Estudiante</small>
                    <div id="modalEstudiante">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Documento</small>
                    <div id="modalDocumento">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Acudiente</small>
                    <div id="modalAcudiente">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Docente</small>
                    <div id="modalDocente">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Motivo</small>
                    <div id="modalMotivo">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Estado</small>
                    <div id="modalEstado">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Sede</small>
                    <div id="modalSede">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Jornada</small>
                    <div id="modalJornada">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Lugar</small>
                    <div id="modalLugar">—</div>
                </div>

                <div class="ed-cal-detail">
                    <small>Creada</small>
                    <div id="modalCreacion">—</div>
                </div>

                <div class="ed-cal-detail full">
                    <small>Observaciones</small>
                    <div id="modalObservaciones">—</div>
                </div>

            </div>


            <div class="ed-cal-modal-actions">

                <a
                    id="modalICS"
                    class="boton"
                    href="#"
                >
                    Descargar .ics
                </a>


                <a
                    class="boton"
                    href="{{ url_for('citas.index') }}"
                >
                    Gestionar citas
                </a>


                <button
                    type="button"
                    class="boton"
                    id="cerrarModal2"
                >
                    Cerrar
                </button>

            </div>

        </div>

    </div>

</div>


<link
    rel="stylesheet"
    href="{{ url_for(
        'static',
        filename='vendor/fullcalendar/skeleton.css'
    ) }}"
>


<script src="{{ url_for(
    'static',
    filename='vendor/fullcalendar/fullcalendar.global.js'
) }}"></script>


<script src="{{ url_for(
    'static',
    filename='vendor/fullcalendar/locales/es.global.js'
) }}"></script>


<script>

const CITAS_REALES =
    {{ citas|tojson }};

let calendario = null;


function escapeHtml(valor) {

    return String(valor || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


function estadoClase(estado) {

    const texto =
        String(estado || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");

    if (texto.includes("pend")) {
        return "ed-pendiente";
    }

    if (texto.includes("confirm")) {
        return "ed-confirmada";
    }

    if (
        texto.includes("cancel") ||
        texto.includes("venc")
    ) {
        return "ed-cancelada";
    }

    if (texto.includes("reprogram")) {
        return "ed-reprogramada";
    }

    return "ed-otro";

}


function fechaBonita(valor) {

    if (!valor) {
        return "—";
    }

    const partes =
        String(valor)
            .substring(0,10)
            .split("-");

    if (partes.length !== 3) {
        return valor;
    }

    const fecha =
        new Date(
            Number(partes[0]),
            Number(partes[1]) - 1,
            Number(partes[2])
        );

    return fecha.toLocaleDateString(
        "es-CO",
        {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }
    );

}


function hoyClave() {

    const fecha = new Date();

    return [
        fecha.getFullYear(),
        String(fecha.getMonth()+1).padStart(2,"0"),
        String(fecha.getDate()).padStart(2,"0")
    ].join("-");

}


function citaCumpleFiltros(cita) {

    const texto =
        document
            .getElementById("filtroTexto")
            .value
            .trim()
            .toLowerCase();

    const sede =
        document.getElementById(
            "filtroSede"
        ).value;

    const jornada =
        document.getElementById(
            "filtroJornada"
        ).value;

    const docente =
        document.getElementById(
            "filtroDocente"
        ).value;

    const motivo =
        document.getElementById(
            "filtroMotivo"
        ).value;

    const estado =
        document.getElementById(
            "filtroEstado"
        ).value;

    const desde =
        document.getElementById(
            "filtroDesde"
        ).value;

    const hasta =
        document.getElementById(
            "filtroHasta"
        ).value;


    const contenido = [
        cita.estudiante,
        cita.documento_estudiante,
        cita.codigo_estudiantil,
        cita.acudiente,
        cita.docente,
        cita.motivo,
        cita.lugar,
        cita.estado,
        cita.sede,
        cita.jornada
    ]
        .join(" ")
        .toLowerCase();


    if (
        texto &&
        !contenido.includes(texto)
    ) {
        return false;
    }


    if (
        sede &&
        String(cita.id_sede) !== sede
    ) {
        return false;
    }


    if (
        jornada &&
        String(cita.id_jornada) !== jornada
    ) {
        return false;
    }


    if (
        docente &&
        String(cita.id_docente) !== docente
    ) {
        return false;
    }


    if (
        motivo &&
        String(cita.id_motivo) !== motivo
    ) {
        return false;
    }


    if (
        estado &&
        String(cita.id_estado) !== estado
    ) {
        return false;
    }


    if (
        desde &&
        cita.fecha < desde
    ) {
        return false;
    }


    if (
        hasta &&
        cita.fecha > hasta
    ) {
        return false;
    }


    return true;

}


function obtenerCitasFiltradas() {

    return CITAS_REALES.filter(
        citaCumpleFiltros
    );

}


function actualizarEstadisticas(lista) {

    document.getElementById(
        "statTotal"
    ).textContent =
        lista.length;


    const hoy =
        hoyClave();


    document.getElementById(
        "statHoy"
    ).textContent =
        lista.filter(
            cita =>
                cita.fecha === hoy
        ).length;


    document.getElementById(
        "statPendientes"
    ).textContent =
        lista.filter(
            cita =>
                estadoClase(cita.estado) ===
                "ed-pendiente"
        ).length;


    document.getElementById(
        "statConfirmadas"
    ).textContent =
        lista.filter(
            cita =>
                estadoClase(cita.estado) ===
                "ed-confirmada"
        ).length;


    document.getElementById(
        "conteoCalendario"
    ).textContent =
        lista.length === 1
            ? "1 cita visible"
            : lista.length + " citas visibles";

}


function crearEventos(lista) {

    return lista.map(function(cita) {

        return {

            id: String(cita.id),

            title:
                String(
                    cita.hora || ""
                ).substring(0,5)
                + " · "
                + (
                    cita.estudiante ||
                    cita.motivo ||
                    "Citación"
                ),

            start:
                cita.fecha
                + "T"
                + String(
                    cita.hora || "00:00:00"
                ).substring(0,8),

            end:
                cita.fecha
                + "T"
                + calcularHoraFin(
                    cita.hora
                ),

            classNames: [
                estadoClase(
                    cita.estado
                )
            ],

            extendedProps: {
                cita: cita
            }

        };

    });

}


function calcularHoraFin(hora) {

    const partes =
        String(
            hora || "00:00:00"
        )
        .substring(0,8)
        .split(":");


    let horas =
        Number(partes[0] || 0);

    let minutos =
        Number(partes[1] || 0);


    minutos += 45;


    if (minutos >= 60) {
        horas += 1;
        minutos -= 60;
    }


    if (horas >= 24) {
        horas = 23;
        minutos = 59;
    }


    return String(horas).padStart(2,"0")
        + ":"
        + String(minutos).padStart(2,"0")
        + ":00";

}


function inicializarCalendario() {

    const elemento =
        document.getElementById(
            "calendar"
        );


    calendario =
        new FullCalendar.Calendar(
            elemento,
            {

                locale: "es",

                firstDay: 1,

                initialView:
                    "dayGridMonth",

                height: "auto",

                nowIndicator: true,

                dayMaxEvents: 3,

                navLinks: true,

                editable: false,

                selectable: false,

                eventTimeFormat: {
                    hour: "2-digit",
                    minute: "2-digit",
                    hour12: true
                },


                headerToolbar: {

                    left:
                        "prev,next today",

                    center:
                        "title",

                    right:
                        "dayGridMonth,timeGridWeek,timeGridDay,listWeek"

                },


                buttonText: {

                    today:
                        "Hoy",

                    month:
                        "Mes",

                    week:
                        "Semana",

                    day:
                        "Día",

                    list:
                        "Agenda"

                },


                events:
                    crearEventos(
                        obtenerCitasFiltradas()
                    ),


                eventClick:
                    function(info) {

                        const cita =
                            info.event
                                .extendedProps
                                .cita;

                        abrirModal(cita);

                    },


                dateClick:
                    function(info) {

                        {% if puede_crear %}

                        const nueva =
                            "{{ url_for('citas.nueva') }}";

                        window.location.href =
                            nueva
                            + "?fecha="
                            + encodeURIComponent(
                                info.dateStr
                            );

                        {% endif %}

                    }

            }
        );


    calendario.render();

}


function actualizarCalendario() {

    const lista =
        obtenerCitasFiltradas();


    actualizarEstadisticas(
        lista
    );


    if (!calendario) {
        return;
    }


    calendario.removeAllEvents();


    calendario.addEventSource(
        crearEventos(lista)
    );


    renderProximas(lista);

}


function renderProximas(lista) {

    const contenedor =
        document.getElementById(
            "proximas"
        );


    const hoy =
        hoyClave();


    const proximas =
        [...lista]
            .filter(
                cita =>
                    cita.fecha >= hoy
            )
            .sort(
                function(a,b) {

                    return (
                        a.fecha
                        + " "
                        + a.hora
                    ).localeCompare(
                        b.fecha
                        + " "
                        + b.hora
                    );

                }
            )
            .slice(0,8);


    if (!proximas.length) {

        contenedor.innerHTML =
            '<div class="ed-cal-empty">' +
            "No hay citas que coincidan con los filtros." +
            "</div>";

        return;

    }


    contenedor.innerHTML = "";


    proximas.forEach(
        function(cita) {

            const fila =
                document.createElement(
                    "div"
                );

            fila.className =
                "ed-cal-proxima";


            fila.innerHTML =

                "<div class='ed-cal-proxima-fecha'>" +

                escapeHtml(
                    cita.fecha
                ) +

                "<br>" +

                escapeHtml(
                    String(
                        cita.hora || ""
                    ).substring(0,5)
                ) +

                "</div>" +


                "<div class='ed-cal-proxima-info'>" +

                "<strong>" +

                escapeHtml(
                    cita.motivo ||
                    "Citación"
                ) +

                "</strong>" +

                "<span>" +

                escapeHtml(
                    cita.estudiante ||
                    ""
                ) +

                " · " +

                escapeHtml(
                    cita.lugar ||
                    ""
                ) +

                "</span>" +

                "</div>" +


                "<div>" +

                "<span class='ed-cal-status " +

                estadoClase(
                    cita.estado
                ) +

                "'>" +

                escapeHtml(
                    cita.estado ||
                    ""
                ) +

                "</span>" +

                "</div>";


            fila.addEventListener(
                "click",
                function() {

                    abrirModal(cita);

                }
            );


            fila.style.cursor =
                "pointer";


            contenedor.appendChild(
                fila
            );

        }
    );

}


function abrirModal(cita) {

    document.getElementById(
        "modalTitulo"
    ).textContent =
        cita.motivo ||
        "Citación";


    document.getElementById(
        "modalFecha"
    ).textContent =
        fechaBonita(
            cita.fecha
        );


    document.getElementById(
        "modalHora"
    ).textContent =
        cita.hora ||
        "—";


    document.getElementById(
        "modalEstudiante"
    ).textContent =
        cita.estudiante ||
        "—";


    document.getElementById(
        "modalDocumento"
    ).textContent =
        cita.documento_estudiante ||
        "—";


    document.getElementById(
        "modalAcudiente"
    ).textContent =
        cita.acudiente ||
        "—";


    document.getElementById(
        "modalDocente"
    ).textContent =
        cita.docente ||
        "—";


    document.getElementById(
        "modalMotivo"
    ).textContent =
        cita.motivo ||
        "—";


    document.getElementById(
        "modalEstado"
    ).textContent =
        cita.estado ||
        "—";


    document.getElementById(
        "modalSede"
    ).textContent =
        cita.sede ||
        "—";


    document.getElementById(
        "modalJornada"
    ).textContent =
        cita.jornada ||
        "—";


    document.getElementById(
        "modalLugar"
    ).textContent =
        cita.lugar ||
        "—";


    document.getElementById(
        "modalCreacion"
    ).textContent =
        cita.fecha_creacion ||
        "—";


    document.getElementById(
        "modalObservaciones"
    ).textContent =
        cita.observaciones ||
        "—";


    document.getElementById(
        "modalICS"
    ).href =
        cita.ics ||
        "#";


    document.getElementById(
        "modalCita"
    ).classList.add(
        "open"
    );


    document.getElementById(
        "modalCita"
    ).setAttribute(
        "aria-hidden",
        "false"
    );

}


function cerrarModal() {

    document.getElementById(
        "modalCita"
    ).classList.remove(
        "open"
    );


    document.getElementById(
        "modalCita"
    ).setAttribute(
        "aria-hidden",
        "true"
    );

}


document.addEventListener(
    "DOMContentLoaded",
    function() {

        inicializarCalendario();


        actualizarEstadisticas(
            obtenerCitasFiltradas()
        );


        renderProximas(
            obtenerCitasFiltradas()
        );


        [

            "filtroTexto",
            "filtroSede",
            "filtroJornada",
            "filtroDocente",
            "filtroMotivo",
            "filtroEstado",
            "filtroDesde",
            "filtroHasta"

        ].forEach(
            function(id) {

                document.getElementById(
                    id
                ).addEventListener(
                    "input",
                    actualizarCalendario
                );


                document.getElementById(
                    id
                ).addEventListener(
                    "change",
                    actualizarCalendario
                );

            }
        );


        document.getElementById(
            "limpiarFiltros"
        ).addEventListener(
            "click",
            function() {

                [

                    "filtroTexto",
                    "filtroSede",
                    "filtroJornada",
                    "filtroDocente",
                    "filtroMotivo",
                    "filtroEstado",
                    "filtroDesde",
                    "filtroHasta"

                ].forEach(
                    function(id) {

                        document.getElementById(
                            id
                        ).value = "";

                    }
                );


                actualizarCalendario();

            }
        );


        document.getElementById(
            "cerrarModal"
        ).addEventListener(
            "click",
            cerrarModal
        );


        document.getElementById(
            "cerrarModal2"
        ).addEventListener(
            "click",
            cerrarModal
        );


        document.getElementById(
            "modalCita"
        ).addEventListener(
            "click",
            function(evento) {

                if (
                    evento.target === this
                ) {
                    cerrarModal();
                }

            }
        );


        document.addEventListener(
            "keydown",
            function(evento) {

                if (
                    evento.key === "Escape"
                ) {
                    cerrarModal();
                }

            }
        );

    }
);

</script>

{% endblock %}
'''

TEMPLATE.write_text(
    contenido,
    encoding="utf-8"
)

print()
print("=" * 72)
print("EDUTURNOS - CALENDARIO CON FORMATO FULLCALENDAR")
print("=" * 72)
print()
print("Plantilla:")
print(TEMPLATE)
print()
print("Backup:")
print(BACKUP)
print()
print("FullCalendar encontrado:")
print(JS)
print()
print("Funciones:")
print("- calendario mensual real")
print("- vista semanal")
print("- vista diaria")
print("- vista agenda")
print("- Hoy")
print("- anterior / siguiente")
print("- citas reales desde MySQL")
print("- eventos clicables")
print("- modal de detalle")
print("- filtros")
print("- estadísticas")
print("- próximas citas")
print("- descarga .ics")
print("- botón Nueva cita")
print("- clic sobre fecha para nueva cita")
print("- responsive")
print()
print("NO se modificó MySQL.")
print("NO se modificaron las rutas existentes de citas.")
print()