from pathlib import Path
import shutil
import urllib.request

BASE = Path(__file__).resolve().parent

TEMPLATE = BASE / "templates" / "calendario" / "index.html"

VENDOR = BASE / "static" / "vendor" / "fullcalendar"

JS_FILE = VENDOR / "fullcalendar.global.js"
CSS_FILE = VENDOR / "skeleton.css"
LOCALE_FILE = VENDOR / "locales-es.global.js"

BACKUP = TEMPLATE.with_name(
    "index.html.backup_fullcalendar"
)

VERSION = "7.1.0"

URL_JS = (
    f"https://cdn.jsdelivr.net/npm/"
    f"fullcalendar@{VERSION}/all/global.js"
)

URL_CSS = (
    f"https://cdn.jsdelivr.net/npm/"
    f"fullcalendar@{VERSION}/skeleton.css"
)

URL_LOCALE = "https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/locales/es/global.js"
    f"https://cdn.jsdelivr.net/npm/"
    f"@fullcalendar/core@{VERSION}/locales/es/global.js"
)


def descargar(url, destino):
    print(f"DESCARGANDO: {url}")

    destino.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        urllib.request.urlretrieve(
            url,
            destino
        )
    except Exception as exc:
        print(f"[ERROR] No se pudo descargar:")
        print(url)
        print(exc)
        raise

    if not destino.exists() or destino.stat().st_size == 0:
        raise RuntimeError(
            f"El archivo descargado está vacío: {destino}"
        )

    print(f"OK: {destino}")


def instalar_biblioteca():

    descargar(
        URL_JS,
        JS_FILE
    )

    descargar(
        URL_CSS,
        CSS_FILE
    )

    descargar(
        URL_LOCALE,
        LOCALE_FILE
    )


def crear_template():

    if not TEMPLATE.exists():
        print(
            "[ERROR] No existe "
            "templates/calendario/index.html"
        )
        raise SystemExit(1)

    shutil.copy2(
        TEMPLATE,
        BACKUP
    )

    print(
        f"COPIA DE SEGURIDAD: {BACKUP}"
    )

    HTML = r'''{% extends 'base.html' %}

{% block title %}Calendario · EDUTURNOS{% endblock %}

{% block content %}

<section class="fc-eduturnos-page">

    <!-- =====================================================
         CABECERA
         ===================================================== -->

    <header class="fc-eduturnos-header">

        <div class="fc-eduturnos-heading">

            <a
                class="fc-eduturnos-back"
                href="{{ request.referrer or url_for('auth.dashboard') }}"
            >
                ← Atrás
            </a>

            <div class="fc-eduturnos-title-row">

                <div class="fc-eduturnos-title-icon">
                    CAL
                </div>

                <div>

                    <span class="badge">
                        Agenda institucional
                    </span>

                    <h1>
                        Calendario
                    </h1>

                    <p>
                        Consulta tus citaciones y actividades programadas.
                    </p>

                </div>

            </div>

        </div>


        <div class="fc-eduturnos-header-actions">

            <div class="fc-eduturnos-counter">

                <strong id="fcTotal">
                    {{ citas|length }}
                </strong>

                <span>
                    {{ 'citación' if citas|length == 1 else 'citaciones' }}
                </span>

            </div>

            <button
                type="button"
                id="fcActualizar"
                class="fc-btn fc-btn-light"
            >
                ↻ Actualizar
            </button>

            <a
                class="fc-btn fc-btn-primary"
                href="{{ url_for('citas.index') }}"
            >
                Ver citas
            </a>

            {% if usuario_sesion and usuario_sesion.rol_nombre in [
                'Docente',
                'Administrador / Coordinador',
                'Rector',
                'Super Admin'
            ] %}

            <a
                class="fc-btn fc-btn-main"
                href="{{ url_for('citas.nueva') }}"
            >
                + Nueva citación
            </a>

            {% endif %}

        </div>

    </header>


    <!-- =====================================================
         PANEL DEL CALENDARIO
         ===================================================== -->

    <section class="fc-eduturnos-card">


        <div class="fc-tools">

            <div class="fc-tools-left">

                <label for="fcBuscar">
                    Buscar
                </label>

                <input
                    id="fcBuscar"
                    type="search"
                    placeholder="Estudiante, motivo o lugar..."
                    autocomplete="off"
                >

            </div>


            <div class="fc-tools-right">

                <label for="fcEstado">
                    Estado
                </label>

                <select id="fcEstado">

                    <option value="Todos">
                        Todos
                    </option>

                    <option value="Pendiente">
                        Pendientes
                    </option>

                    <option value="Confirmada">
                        Confirmadas
                    </option>

                    <option value="Reprogramada">
                        Reprogramadas
                    </option>

                    <option value="Cancelada">
                        Canceladas
                    </option>

                </select>

            </div>

        </div>


        <div class="fc-calendar-wrapper">

            <div
                id="eduturnosCalendar"
                class="fc-eduturnos-calendar"
            ></div>

        </div>


        <div class="fc-legend">

            <span>
                <i class="fc-dot fc-green"></i>
                Confirmada
            </span>

            <span>
                <i class="fc-dot fc-yellow"></i>
                Pendiente
            </span>

            <span>
                <i class="fc-dot fc-blue"></i>
                Reprogramada
            </span>

            <span>
                <i class="fc-dot fc-red"></i>
                Cancelada
            </span>

        </div>

    </section>


    <!-- =====================================================
         PRÓXIMAS CITAS
         ===================================================== -->

    <section class="fc-upcoming-card">

        <div class="fc-upcoming-heading">

            <div>

                <span class="badge">
                    Agenda
                </span>

                <h2>
                    Próximas citaciones
                </h2>

                <p>
                    Consulta rápidamente tus siguientes citas.
                </p>

            </div>

        </div>


        <div
            id="fcUpcoming"
            class="fc-upcoming-grid"
        ></div>

    </section>


    <!-- =====================================================
         MODAL DE DETALLE
         ===================================================== -->

    <div
        id="fcModal"
        class="fc-modal"
        aria-hidden="true"
    >

        <div
            class="fc-modal-backdrop"
            data-cerrar-modal
        ></div>

        <div
            class="fc-modal-box"
            role="dialog"
            aria-modal="true"
            aria-labelledby="fcModalTitulo"
        >

            <button
                type="button"
                class="fc-modal-close"
                id="fcCerrarModal"
                aria-label="Cerrar"
            >
                ×
            </button>


            <span class="badge">
                Detalle de citación
            </span>

            <h2 id="fcModalTitulo">
                Citación
            </h2>

            <div
                id="fcModalEstado"
                class="fc-modal-status"
            ></div>


            <div class="fc-detail-grid">

                <div class="fc-detail-item">
                    <span>Fecha</span>
                    <strong id="fcModalFecha">—</strong>
                </div>

                <div class="fc-detail-item">
                    <span>Hora</span>
                    <strong id="fcModalHora">—</strong>
                </div>

                <div class="fc-detail-item">
                    <span>Estudiante</span>
                    <strong id="fcModalEstudiante">—</strong>
                </div>

                <div class="fc-detail-item">
                    <span>Docente</span>
                    <strong id="fcModalDocente">—</strong>
                </div>

                <div class="fc-detail-item">
                    <span>Acudiente</span>
                    <strong id="fcModalAcudiente">—</strong>
                </div>

                <div class="fc-detail-item">
                    <span>Lugar</span>
                    <strong id="fcModalLugar">—</strong>
                </div>

            </div>


            <div class="fc-detail-observaciones">

                <span>
                    Motivo
                </span>

                <p id="fcModalMotivo">
                    —
                </p>

            </div>


            <div class="fc-detail-observaciones">

                <span>
                    Observaciones
                </span>

                <p id="fcModalObservaciones">
                    Sin observaciones.
                </p>

            </div>


            <div class="fc-modal-actions">

                <a
                    id="fcModalICS"
                    class="fc-btn fc-btn-primary"
                    href="#"
                >
                    Agregar al calendario
                </a>

                <button
                    type="button"
                    class="fc-btn fc-btn-light"
                    id="fcCerrarModal2"
                >
                    Cerrar
                </button>

            </div>

        </div>

    </div>


<style>

/* =========================================================
   EDUTURNOS + FULLCALENDAR
   ========================================================= */

.fc-eduturnos-page {
    width: 100%;
    max-width: 1180px;

    margin: 0 auto;

    padding: 8px 0 40px;

    box-sizing: border-box;
}


/* =========================================================
   CABECERA
   ========================================================= */

.fc-eduturnos-header {
    display: flex;

    justify-content: space-between;
    align-items: flex-end;

    gap: 25px;

    margin-bottom: 22px;
}

.fc-eduturnos-heading {
    min-width: 0;
}

.fc-eduturnos-back {
    display: inline-flex;

    margin-bottom: 14px;

    color: #64748b;

    text-decoration: none;

    font-size: 14px;
}

.fc-eduturnos-back:hover {
    color: #2563eb;
}

.fc-eduturnos-title-row {
    display: flex;

    align-items: center;

    gap: 14px;
}

.fc-eduturnos-title-icon {
    width: 48px;
    height: 48px;

    display: flex;

    align-items: center;
    justify-content: center;

    flex-shrink: 0;

    border-radius: 12px;

    background:
        linear-gradient(
            135deg,
            #eaf2ff,
            #dceaff
        );

    color: #2563eb;

    font-size: 11px;

    font-weight: 800;
}

.fc-eduturnos-title-row h1 {
    margin: 7px 0;

    color: #0f172a;

    font-size: 30px;

    line-height: 1.15;
}

.fc-eduturnos-title-row p {
    margin: 0;

    color: #64748b;

    font-size: 14px;

    line-height: 1.5;
}

.fc-eduturnos-header-actions {
    display: flex;

    align-items: center;
    justify-content: flex-end;

    flex-wrap: wrap;

    gap: 8px;
}

.fc-eduturnos-counter {
    display: flex;

    align-items: center;

    gap: 6px;

    min-height: 42px;

    padding: 0 12px;

    background: #ffffff;

    border: 1px solid #dbe4ee;

    border-radius: 9px;
}

.fc-eduturnos-counter strong {
    color: #2563eb;

    font-size: 19px;
}

.fc-eduturnos-counter span {
    color: #64748b;

    font-size: 12px;
}


/* =========================================================
   BOTONES
   ========================================================= */

.fc-btn {
    min-height: 42px;

    display: inline-flex;

    align-items: center;
    justify-content: center;

    padding: 0 13px;

    border-radius: 9px;

    font-family: inherit;

    font-size: 13px;

    font-weight: 700;

    text-decoration: none;

    cursor: pointer;

    box-sizing: border-box;
}

.fc-btn-light {
    background: #ffffff;

    border: 1px solid #d7e0ea;

    color: #334155;
}

.fc-btn-light:hover {
    background: #f8fafc;

    border-color: #bfdbfe;

    color: #2563eb;
}

.fc-btn-primary {
    background: #ffffff;

    border: 1px solid #bfdbfe;

    color: #2563eb;
}

.fc-btn-main {
    background: #2563eb;

    border: 1px solid #2563eb;

    color: #ffffff;
}


/* =========================================================
   PANEL
   ========================================================= */

.fc-eduturnos-card,
.fc-upcoming-card {
    width: 100%;

    background: #ffffff;

    border: 1px solid #dbe4ee;

    border-radius: 16px;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, .055);

    box-sizing: border-box;

    overflow: hidden;
}


/* =========================================================
   FILTROS
   ========================================================= */

.fc-tools {
    display: flex;

    justify-content: space-between;
    align-items: center;

    gap: 18px;

    padding: 15px 18px;

    border-bottom: 1px solid #e7edf4;

    background: #fbfdff;
}

.fc-tools-left,
.fc-tools-right {
    display: flex;

    align-items: center;

    gap: 8px;
}

.fc-tools label {
    color: #64748b;

    font-size: 12px;

    font-weight: 600;
}

.fc-tools input,
.fc-tools select {
    min-height: 38px;

    padding: 8px 11px;

    background: #ffffff;

    border: 1px solid #d7e0ea;

    border-radius: 8px;

    color: #334155;

    font-family: inherit;

    font-size: 12px;

    box-sizing: border-box;
}

.fc-tools input {
    width: 300px;
}

.fc-tools input:focus,
.fc-tools select:focus {
    outline: none;

    border-color: #2563eb;

    box-shadow:
        0 0 0 3px rgba(37, 99, 235, .10);
}


/* =========================================================
   FULLCALENDAR
   ========================================================= */

.fc-eduturnos-calendar {
    padding: 16px;
}

.fc {
    --fc-border-color: #e7edf4;

    --fc-button-border-color: #d7e0ea;

    --fc-button-bg-color: #ffffff;

    --fc-button-text-color: #334155;

    --fc-button-hover-bg-color: #eff6ff;

    --fc-button-hover-border-color: #bfdbfe;

    --fc-button-hover-text-color: #2563eb;

    --fc-today-bg-color: #f3f7ff;

    --fc-page-bg-color: #ffffff;

    font-family: inherit !important;
}

.fc .fc-toolbar {
    margin-bottom: 16px !important;
}

.fc .fc-toolbar-title {
    color: #0f172a;

    font-size: 21px;

    font-weight: 700;
}

.fc .fc-button {
    border-radius: 8px;

    box-shadow: none;

    font-family: inherit;

    font-size: 12px;

    font-weight: 600;
}

.fc .fc-button-primary:not(:disabled).fc-button-active,
.fc .fc-button-primary:not(:disabled):active {
    background: #2563eb;

    border-color: #2563eb;

    color: #ffffff;
}

.fc .fc-daygrid-day-number {
    color: #475569;

    font-size: 12px;

    font-weight: 600;

    padding: 7px;
}

.fc .fc-col-header-cell-cushion {
    color: #64748b;

    font-size: 10px;

    font-weight: 700;

    text-transform: uppercase;

    text-decoration: none;
}

.fc .fc-daygrid-day {
    min-height: 100px;
}

.fc .fc-daygrid-event {
    border-radius: 5px;

    padding: 3px 5px;

    font-size: 10px;

    border: 0;
}

.fc .fc-event-title {
    font-weight: 600;
}

.fc .fc-day-today {
    background: #f3f7ff !important;
}

.fc .fc-more-link {
    color: #2563eb;

    font-size: 10px;

    font-weight: 700;
}

.fc-event-confirmada {
    background: #dcfce7 !important;
    color: #166534 !important;
}

.fc-event-pendiente {
    background: #fef3c7 !important;
    color: #92400e !important;
}

.fc-event-reprogramada {
    background: #e0e7ff !important;
    color: #3730a3 !important;
}

.fc-event-cancelada {
    background: #fee2e2 !important;
    color: #991b1b !important;
}


/* =========================================================
   LEYENDA
   ========================================================= */

.fc-legend {
    display: flex;

    justify-content: flex-end;

    flex-wrap: wrap;

    gap: 12px;

    padding: 11px 17px;

    border-top: 1px solid #edf2f7;

    background: #fbfdff;
}

.fc-legend span {
    display: inline-flex;

    align-items: center;

    gap: 5px;

    color: #64748b;

    font-size: 11px;
}

.fc-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;
}

.fc-green {
    background: #22c55e;
}

.fc-yellow {
    background: #f59e0b;
}

.fc-blue {
    background: #6366f1;
}

.fc-red {
    background: #ef4444;
}


/* =========================================================
   PRÓXIMAS CITAS
   ========================================================= */

.fc-upcoming-card {
    margin-top: 18px;
}

.fc-upcoming-heading {
    padding: 19px 20px;

    border-bottom: 1px solid #e7edf4;

    background: #fbfdff;
}

.fc-upcoming-heading h2 {
    margin: 7px 0 6px;

    color: #0f172a;

    font-size: 20px;

    line-height: 1.2;
}

.fc-upcoming-heading p {
    margin: 0;

    color: #64748b;

    font-size: 13px;
}

.fc-upcoming-grid {
    display: grid;

    grid-template-columns:
        repeat(3, minmax(0, 1fr));

    gap: 12px;

    padding: 15px;
}

.fc-upcoming-item {
    display: grid;

    grid-template-columns: 52px minmax(0, 1fr);

    gap: 11px;

    padding: 12px;

    border: 1px solid #e2e8f0;

    border-radius: 10px;

    background: #ffffff;
}

.fc-upcoming-date {
    display: flex;

    flex-direction: column;

    align-items: center;
    justify-content: center;

    min-height: 50px;

    border-radius: 8px;

    background: #eef6ff;

    color: #2563eb;
}

.fc-upcoming-date strong {
    font-size: 18px;
    line-height: 1;
}

.fc-upcoming-date span {
    margin-top: 3px;

    font-size: 9px;

    font-weight: 700;

    text-transform: uppercase;
}

.fc-upcoming-content h3 {
    margin: 0 0 4px;

    color: #0f172a;

    font-size: 13px;
}

.fc-upcoming-content p {
    margin: 3px 0;

    color: #64748b;

    font-size: 11px;

    line-height: 1.35;
}


/* =========================================================
   MODAL
   ========================================================= */

.fc-modal {
    display: none;

    position: fixed;

    inset: 0;

    z-index: 100000;

    align-items: center;
    justify-content: center;

    padding: 20px;

    box-sizing: border-box;
}

.fc-modal.abierto {
    display: flex;
}

.fc-modal-backdrop {
    position: absolute;

    inset: 0;

    background: rgba(15, 23, 42, .46);
}

.fc-modal-box {
    position: relative;

    z-index: 2;

    width: 100%;

    max-width: 650px;

    max-height: 90vh;

    overflow-y: auto;

    padding: 26px;

    background: #ffffff;

    border-radius: 16px;

    box-shadow:
        0 20px 55px rgba(15, 23, 42, .22);

    box-sizing: border-box;
}

.fc-modal-box h2 {
    margin: 9px 0 8px;

    color: #0f172a;

    font-size: 22px;
}

.fc-modal-close {
    position: absolute;

    top: 13px;
    right: 14px;

    width: 34px;
    height: 34px;

    border: 0;

    border-radius: 50%;

    background: #f1f5f9;

    color: #475569;

    font-size: 21px;

    cursor: pointer;
}

.fc-modal-close:hover {
    background: #e2e8f0;
}

.fc-modal-status {
    display: inline-flex;

    margin-bottom: 18px;

    padding: 6px 10px;

    border-radius: 999px;

    font-size: 11px;

    font-weight: 700;
}

.fc-modal-status.confirmada {
    background: #dcfce7;
    color: #166534;
}

.fc-modal-status.pendiente {
    background: #fef3c7;
    color: #92400e;
}

.fc-modal-status.reprogramada {
    background: #e0e7ff;
    color: #3730a3;
}

.fc-modal-status.cancelada {
    background: #fee2e2;
    color: #991b1b;
}

.fc-detail-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 10px;

    margin-bottom: 14px;
}

.fc-detail-item {
    padding: 11px;

    border: 1px solid #e2e8f0;

    border-radius: 9px;

    background: #f8fafc;
}

.fc-detail-item span,
.fc-detail-observaciones > span {
    display: block;

    margin-bottom: 4px;

    color: #64748b;

    font-size: 10px;

    font-weight: 700;

    text-transform: uppercase;
}

.fc-detail-item strong {
    color: #334155;

    font-size: 12px;

    line-height: 1.4;

    word-break: break-word;
}

.fc-detail-observaciones {
    margin-top: 10px;

    padding: 12px;

    border: 1px solid #e2e8f0;

    border-radius: 9px;
}

.fc-detail-observaciones p {
    margin: 0;

    color: #334155;

    font-size: 12px;

    line-height: 1.5;
}

.fc-modal-actions {
    display: flex;

    justify-content: flex-end;

    gap: 8px;

    margin-top: 20px;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1000px) {

    .fc-eduturnos-header {
        flex-direction: column;
        align-items: stretch;
    }

    .fc-eduturnos-header-actions {
        justify-content: flex-start;
    }

    .fc-upcoming-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 700px) {

    .fc-tools {
        flex-direction: column;

        align-items: stretch;
    }

    .fc-tools-left,
    .fc-tools-right {
        width: 100%;
    }

    .fc-tools input,
    .fc-tools select {
        width: 100%;
    }

    .fc-upcoming-grid {
        grid-template-columns: 1fr;
    }

    .fc-detail-grid {
        grid-template-columns: 1fr;
    }

    .fc-calendar-wrapper {
        overflow-x: auto;
    }

    .fc-eduturnos-calendar {
        min-width: 680px;
    }
}

</style>


<!-- =====================================================
     FULLCALENDAR LOCAL
     ===================================================== -->

<script src="{{ url_for('static', filename='vendor/fullcalendar/fullcalendar.global.js') }}"></script>

<script src="{{ url_for('static', filename='vendor/fullcalendar/locales-es.global.js') }}"></script>


<script>

document.addEventListener("DOMContentLoaded", function () {

    const elemento =
        document.getElementById("eduturnosCalendar");

    if (!elemento) {
        return;
    }


    /* =====================================================
       DATOS REALES DE MYSQL
       ===================================================== */

    const eventosOriginales = [

        {% for cita in citas %}

        {
            id: {{ cita.id|tojson }},

            title:
                {{ (cita.motivo or 'Citación')|tojson }},

            start:
                {{ (
                    (cita.fecha|string)
                    ~ 'T'
                    ~ (cita.hora|string)
                )|tojson }},

            classNames: [
                "fc-event-{{ (
                    cita.estado or 'Pendiente'
                )|lower
                    |replace('ó','o')
                    |replace('í','i')
                    |replace(' ','-')
                ) }}"
            ],

            extendedProps: {

                estudiante:
                    {{ (
                        (cita.estudiante_n or '')
                        ~ ' '
                        ~ (cita.estudiante_a or '')
                    )|tojson }},

                docente:
                    {{ (
                        (cita.docente_n or '')
                        ~ ' '
                        ~ (cita.docente_a or '')
                    )|tojson }},

                acudiente:
                    {{ (
                        (cita.acudiente_n or '')
                        ~ ' '
                        ~ (cita.acudiente_a or '')
                    )|tojson }},

                motivo:
                    {{ (cita.motivo or '')|tojson }},

                estado:
                    {{ (cita.estado or 'Pendiente')|tojson }},

                lugar:
                    {{ (cita.lugar or 'Por definir')|tojson }},

                observaciones:
                    {{ (cita.observaciones or '')|tojson }},

                ics:
                    {{ url_for(
                        'calendario.descargar_ics',
                        cita_id=cita.id
                    )|tojson }}

            }

        }{% if not loop.last %},{% endif %}

        {% endfor %}

    ];


    let eventosActivos =
        eventosOriginales.slice();


    /* =====================================================
       CALENDARIO
       ===================================================== */

    const calendar =
        new FullCalendar.Calendar(
            elemento,
            {

                locale: "es",

                initialView: "dayGridMonth",

                height: "auto",

                expandRows: true,

                navLinks: true,

                nowIndicator: true,

                dayMaxEvents: 3,

                eventDisplay: "block",

                headerToolbar: {

                    left:
                        "prev,next today",

                    center:
                        "title",

                    right:
                        "dayGridMonth,timeGridWeek,timeGridDay,listWeek"

                },

                buttonText: {

                    today: "Hoy",

                    month: "Mes",

                    week: "Semana",

                    day: "Día",

                    list: "Agenda"

                },


                events:
                    eventosActivos,


                eventTimeFormat: {

                    hour: "2-digit",

                    minute: "2-digit",

                    hour12: false

                },


                eventClick:
                    function (info) {

                        info.jsEvent.preventDefault();

                        abrirModal(
                            info.event
                        );

                    },


                dateClick:
                    function (info) {

                        mostrarProximasDesdeFecha(
                            info.date
                        );

                    }

            }
        );


    calendar.render();


    /* =====================================================
       FILTRO
       ===================================================== */

    const filtro =
        document.getElementById("fcEstado");


    const busqueda =
        document.getElementById("fcBuscar");


    function aplicarFiltros() {

        const estado =
            filtro.value;


        const texto =
            busqueda.value
                .trim()
                .toLowerCase();


        eventosActivos =
            eventosOriginales.filter(
                function (evento) {

                    const estadoOk =
                        estado === "Todos"
                        ||
                        evento.extendedProps.estado
                            === estado;


                    const textoCompleto =
                        [
                            evento.title,

                            evento.extendedProps.estudiante,

                            evento.extendedProps.docente,

                            evento.extendedProps.acudiente,

                            evento.extendedProps.lugar,

                            evento.extendedProps.motivo,

                            evento.extendedProps.observaciones

                        ]
                            .join(" ")
                            .toLowerCase();


                    const textoOk =
                        !texto
                        ||
                        textoCompleto.includes(texto);


                    return estadoOk && textoOk;
                }
            );


        calendar.removeAllEvents();

        calendar.addEventSource(
            eventosActivos
        );

        renderProximas();
    }


    filtro.addEventListener(
        "change",
        aplicarFiltros
    );


    busqueda.addEventListener(
        "input",
        aplicarFiltros
    );


    /* =====================================================
       ACTUALIZAR
       ===================================================== */

    document
        .getElementById("fcActualizar")
        .addEventListener(
            "click",
            function () {

                window.location.reload();

            }
        );


    /* =====================================================
       MODAL
       ===================================================== */

    const modal =
        document.getElementById("fcModal");


    const cerrar =
        function () {

            modal.classList.remove(
                "abierto"
            );

            modal.setAttribute(
                "aria-hidden",
                "true"
            );

        };


    document
        .getElementById("fcCerrarModal")
        .addEventListener(
            "click",
            cerrar
        );


    document
        .getElementById("fcCerrarModal2")
        .addEventListener(
            "click",
            cerrar
        );


    document
        .querySelector(
            "[data-cerrar-modal]"
        )
        .addEventListener(
            "click",
            cerrar
        );


    document.addEventListener(
        "keydown",
        function (evento) {

            if (
                evento.key === "Escape"
            ) {
                cerrar();
            }

        }
    );


    function abrirModal(evento) {

        const props =
            evento.extendedProps;


        document
            .getElementById(
                "fcModalTitulo"
            )
            .textContent =
                props.motivo
                || evento.title
                || "Citación";


        document
            .getElementById(
                "fcModalFecha"
            )
            .textContent =
                new Intl.DateTimeFormat(
                    "es-CO",
                    {
                        weekday: "long",
                        day: "numeric",
                        month: "long",
                        year: "numeric"
                    }
                ).format(
                    evento.start
                );


        document
            .getElementById(
                "fcModalHora"
            )
            .textContent =
                new Intl.DateTimeFormat(
                    "es-CO",
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: false
                    }
                ).format(
                    evento.start
                );


        document
            .getElementById(
                "fcModalEstudiante"
            )
            .textContent =
                props.estudiante
                || "No informado";


        document
            .getElementById(
                "fcModalDocente"
            )
            .textContent =
                props.docente
                || "No informado";


        document
            .getElementById(
                "fcModalAcudiente"
            )
            .textContent =
                props.acudiente
                || "No informado";


        document
            .getElementById(
                "fcModalLugar"
            )
            .textContent =
                props.lugar
                || "Por definir";


        document
            .getElementById(
                "fcModalMotivo"
            )
            .textContent =
                props.motivo
                || "No informado";


        document
            .getElementById(
                "fcModalObservaciones"
            )
            .textContent =
                props.observaciones
                || "Sin observaciones.";


        const estado =
            document.getElementById(
                "fcModalEstado"
            );


        estado.textContent =
            props.estado
            || "Pendiente";


        estado.className =
            "fc-modal-status "
            + claseEstado(
                props.estado
            );


        const enlaceICS =
            document.getElementById(
                "fcModalICS"
            );


        enlaceICS.href =
            props.ics
            || "#";


        modal.classList.add(
            "abierto"
        );


        modal.setAttribute(
            "aria-hidden",
            "false"
        );

    }


    function claseEstado(estado) {

        const valor =
            String(estado || "")
                .toLowerCase()
                .normalize("NFD")
                .replace(
                    /[\u0300-\u036f]/g,
                    ""
                );


        if (
            valor.includes("confirm")
        ) {
            return "confirmada";
        }


        if (
            valor.includes("reprogram")
        ) {
            return "reprogramada";
        }


        if (
            valor.includes("cancel")
            ||
            valor.includes("anulad")
        ) {
            return "cancelada";
        }


        return "pendiente";
    }


    /* =====================================================
       PRÓXIMAS CITACIONES
       ===================================================== */

    function renderProximas() {

        const contenedor =
            document.getElementById(
                "fcUpcoming"
            );


        const ahora =
            new Date();


        const siguientes =
            eventosActivos
                .map(
                    function (evento) {

                        return {
                            evento:
                                evento,

                            fecha:
                                new Date(
                                    evento.start
                                )
                        };

                    }
                )
                .filter(
                    function (item) {

                        return (
                            item.fecha >= ahora
                            &&
                            claseEstado(
                                item.evento
                                    .extendedProps
                                    .estado
                            )
                            !== "cancelada"
                        );

                    }
                )
                .sort(
                    function (a, b) {

                        return (
                            a.fecha - b.fecha
                        );

                    }
                )
                .slice(0, 6);


        contenedor.innerHTML = "";


        if (
            siguientes.length === 0
        ) {

            contenedor.innerHTML = `
                <div class="cal-upcoming-empty">
                    No hay próximas citaciones.
                </div>
            `;

            return;
        }


        siguientes.forEach(
            function (item) {

                const evento =
                    item.evento;


                const fecha =
                    item.fecha;


                const caja =
                    document.createElement(
                        "article"
                    );


                caja.className =
                    "fc-upcoming-item";


                const fechaCaja =
                    document.createElement(
                        "div"
                    );


                fechaCaja.className =
                    "fc-upcoming-date";


                fechaCaja.innerHTML =
                    `
                        <strong>
                            ${fecha.getDate()}
                        </strong>

                        <span>
                            ${
                                new Intl.DateTimeFormat(
                                    "es-CO",
                                    {
                                        month: "short"
                                    }
                                ).format(fecha)
                            }
                        </span>
                    `;


                const contenido =
                    document.createElement(
                        "div"
                    );


                contenido.className =
                    "fc-upcoming-content";


                contenido.innerHTML =
                    `
                        <h3>
                            ${
                                evento.title
                                || "Citación"
                            }
                        </h3>

                        <p>
                            ${
                                new Intl.DateTimeFormat(
                                    "es-CO",
                                    {
                                        hour: "2-digit",
                                        minute: "2-digit",
                                        hour12: false
                                    }
                                ).format(fecha)
                            }
                            ·
                            ${
                                evento.extendedProps
                                    .estudiante
                                || "Estudiante"
                            }
                        </p>

                        <p>
                            ${
                                evento.extendedProps
                                    .estado
                                || "Pendiente"
                            }
                        </p>
                    `;


                caja.appendChild(
                    fechaCaja
                );


                caja.appendChild(
                    contenido
                );


                caja.addEventListener(
                    "click",
                    function () {

                        calendar.gotoDate(
                            fecha
                        );

                        abrirModal(
                            calendar.getEventById(
                                String(evento.id)
                            )
                        );

                    }
                );


                caja.style.cursor =
                    "pointer";


                contenedor.appendChild(
                    caja
                );

            }
        );

    }


    function mostrarProximasDesdeFecha(
        fecha
    ) {

        const dia =
            new Date(fecha);


        dia.setHours(
            0,
            0,
            0,
            0
        );


        const siguientes =
            eventosActivos.filter(
                function (evento) {

                    const fechaEvento =
                        new Date(
                            evento.start
                        );


                    fechaEvento.setHours(
                        0,
                        0,
                        0,
                        0
                    );


                    return (
                        fechaEvento.getTime()
                        ===
                        dia.getTime()
                    );

                }
            );


        if (
            siguientes.length
            &&
            calendar
        ) {

            const evento =
                calendar.getEventById(
                    String(
                        siguientes[0].id
                    )
                );


            if (evento) {
                abrirModal(evento);
            }

        }

        renderProximas();

    }


    /* =====================================================
       INICIALIZAR
       ===================================================== */

    renderProximas();

});

</script>

{% endblock %}
'''

    TEMPLATE.write_text(
        HTML,
        encoding="utf-8"
    )

    print(
        "CORRECTO: templates/calendario/index.html"
    )


def main():

    print()
    print("=" * 70)
    print("EDUTURNOS - INSTALADOR DE CALENDARIO REAL")
    print("=" * 70)
    print()

    instalar_biblioteca()

    crear_template()

    print()
    print("=" * 70)
    print("CALENDARIO REAL INSTALADO CORRECTAMENTE")
    print("=" * 70)
    print()
    print("Incluye:")
    print("- FullCalendar 7.1.0")
    print("- Vista mensual")
    print("- Vista semanal")
    print("- Vista diaria")
    print("- Vista agenda")
    print("- Navegación anterior/siguiente")
    print("- Botón Hoy")
    print("- Búsqueda")
    print("- Filtro por estado")
    print("- Citas reales de MySQL")
    print("- Detalle de cada cita")
    print("- Estudiante")
    print("- Docente")
    print("- Acudiente")
    print("- Lugar")
    print("- Motivo")
    print("- Observaciones")
    print("- Estado")
    print("- Agregar al calendario (.ics)")
    print("- Próximas citaciones")
    print("- Botón Actualizar")
    print("- Botón Ver citas")
    print()
    print("No se modificó routes/calendario.py")
    print("No se modificó la base de datos")
    print()


if __name__ == "__main__":
    main()