from pathlib import Path
import urllib.request
import shutil

BASE = Path(__file__).resolve().parent

STATIC = BASE / "static" / "vendor" / "fullcalendar"
LOCALES = STATIC / "locales"
TEMPLATE = BASE / "templates" / "calendario" / "index.html"

STATIC.mkdir(parents=True, exist_ok=True)
LOCALES.mkdir(parents=True, exist_ok=True)

URL_JS = "https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/all/global.js"
URL_CSS = "https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/skeleton.css"
URL_ES = "https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/locales/es/global.js"

FILE_JS = STATIC / "fullcalendar.global.js"
FILE_CSS = STATIC / "skeleton.css"
FILE_ES = LOCALES / "es.global.js"

print()
print("=" * 72)
print("EDUTURNOS - INSTALACION FINAL DEL CALENDARIO REAL")
print("=" * 72)
print()

def descargar(url, destino):
    print("DESCARGANDO:")
    print(url)
    urllib.request.urlretrieve(url, destino)
    print("OK:")
    print(destino)
    print()

try:
    descargar(URL_JS, FILE_JS)
    descargar(URL_CSS, FILE_CSS)
    descargar(URL_ES, FILE_ES)
except Exception as e:
    print()
    print("[ERROR] No se pudo descargar una biblioteca.")
    print(e)
    raise SystemExit(1)

if TEMPLATE.exists():
    backup = TEMPLATE.with_name("index.html.backup_antes_fullcalendar")
    shutil.copy2(TEMPLATE, backup)
    print("COPIA DE SEGURIDAD:")
    print(backup)
    print()

template = r"""{% extends 'base.html' %}

{% block title %}Calendario · EDUTURNOS{% endblock %}

{% block content %}

<style>
.calendario-real {
    max-width: 1400px;
    margin: 0 auto;
}

.calendario-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    margin-bottom: 18px;
    flex-wrap: wrap;
}

.calendario-header h1 {
    margin: 0;
}

.calendario-header p {
    margin: 6px 0 0;
}

.calendario-acciones {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}

.calendario-filtros {
    display: grid;
    grid-template-columns: minmax(220px, 1fr) 220px;
    gap: 12px;
    margin-bottom: 16px;
}

.calendario-filtros input,
.calendario-filtros select {
    width: 100%;
    box-sizing: border-box;
}

.calendario-card {
    background: #fff;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 8px 28px rgba(0,0,0,.08);
}

#eduturnosCalendar {
    min-height: 720px;
}

.fc {
    font-family: inherit;
}

.fc .fc-toolbar-title {
    font-size: 1.35rem;
    font-weight: 700;
}

.fc .fc-button {
    border-radius: 9px;
    box-shadow: none;
}

.fc .fc-daygrid-day.fc-day-today {
    background: rgba(37, 99, 235, .08);
}

.fc .fc-event {
    cursor: pointer;
    border-radius: 6px;
    padding: 2px 5px;
}

.calendario-proximas {
    margin-top: 18px;
}

.cita-proxima {
    display: grid;
    grid-template-columns: 110px 1fr auto;
    gap: 14px;
    align-items: center;
    padding: 13px 0;
    border-bottom: 1px solid #e8edf3;
}

.cita-proxima:last-child {
    border-bottom: 0;
}

.estado {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: .78rem;
    font-weight: 700;
    white-space: nowrap;
}

.estado-pendiente {
    background: #fff3cd;
    color: #856404;
}

.estado-confirmada,
.estado-confirmado {
    background: #d1fae5;
    color: #065f46;
}

.estado-cancelada,
.estado-cancelado {
    background: #fee2e2;
    color: #991b1b;
}

.estado-reprogramada,
.estado-reprogramado {
    background: #dbeafe;
    color: #1e40af;
}

.estado-default {
    background: #eef2f7;
    color: #475569;
}

.modal-cita {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, .58);
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
    z-index: 9999;
}

.modal-cita.activo {
    display: flex;
}

.modal-contenido {
    width: min(680px, 100%);
    max-height: 90vh;
    overflow: auto;
    background: white;
    border-radius: 18px;
    padding: 24px;
}

.modal-cabecera {
    display: flex;
    justify-content: space-between;
    gap: 15px;
    align-items: flex-start;
    margin-bottom: 18px;
}

.modal-cabecera h2 {
    margin: 0;
}

.modal-cerrar {
    border: 0;
    background: #eef2f7;
    border-radius: 8px;
    padding: 8px 11px;
    cursor: pointer;
    font-size: 18px;
}

.detalle-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.detalle-item {
    padding: 12px;
    background: #f8fafc;
    border-radius: 10px;
}

.detalle-item strong {
    display: block;
    margin-bottom: 5px;
    font-size: .82rem;
    color: #64748b;
}

.detalle-ancho {
    grid-column: 1 / -1;
}

.modal-acciones {
    display: flex;
    gap: 10px;
    margin-top: 18px;
    flex-wrap: wrap;
}

.sin-citas {
    text-align: center;
    padding: 30px 15px;
    color: #64748b;
}

@media (max-width: 800px) {
    .calendario-filtros {
        grid-template-columns: 1fr;
    }

    .detalle-grid {
        grid-template-columns: 1fr;
    }

    .detalle-ancho {
        grid-column: auto;
    }

    .cita-proxima {
        grid-template-columns: 1fr;
        gap: 7px;
    }

    #eduturnosCalendar {
        min-height: 600px;
    }
}
</style>

<section class="calendario-real">

    <div class="calendario-header">

        <div>
            <a
                class="link-back"
                href="{{ request.referrer or url_for('auth.dashboard') }}"
            >
                ← Atrás
            </a>

            <h1>Calendario</h1>
            <p>Consulta tus citaciones directamente desde la agenda de EDUTURNOS.</p>
        </div>

        <div class="calendario-acciones">

            <a
                class="boton"
                href="{{ url_for('citas.index') }}"
            >
                Ver citas
            </a>

            {% if usuario_sesion is defined and usuario_sesion %}
                {% if usuario_sesion.rol_nombre in ['Docente', 'Administrador / Coordinador', 'Rector', 'Super Admin'] %}
                    <a
                        class="boton"
                        href="{{ url_for('citas.nueva') }}"
                    >
                        + Nueva citación
                    </a>
                {% endif %}
            {% endif %}

            <button
                type="button"
                class="boton"
                id="btnActualizar"
            >
                ↻ Actualizar
            </button>

        </div>

    </div>

    <div class="calendario-filtros">

        <input
            type="search"
            id="buscarCita"
            placeholder="Buscar estudiante, docente, motivo o lugar..."
            autocomplete="off"
        >

        <select id="filtroEstado">
            <option value="">Todos los estados</option>
            {% for cita in citas %}
                <option value="{{ cita.estado }}">{{ cita.estado }}</option>
            {% endfor %}
        </select>

    </div>

    <div class="calendario-card">

        <div id="eduturnosCalendar"></div>

    </div>

    <div class="calendario-card calendario-proximas">

        <h2>Próximas citas</h2>

        {% if citas %}
            {% for cita in citas[:8] %}
                <div class="cita-proxima">

                    <div>
                        <strong>{{ cita.fecha }}</strong><br>
                        <span>{{ cita.hora }}</span>
                    </div>

                    <div>
                        <strong>{{ cita.motivo }}</strong><br>
                        <span>
                            {{ cita.estudiante_n }} {{ cita.estudiante_a }}
                            · {{ cita.lugar }}
                        </span>
                    </div>

                    <span
                        class="estado estado-default"
                        data-estado="{{ cita.estado }}"
                    >
                        {{ cita.estado }}
                    </span>

                </div>
            {% endfor %}
        {% else %}
            <div class="sin-citas">
                No tienes citas registradas.
            </div>
        {% endif %}

    </div>

</section>

<div
    class="modal-cita"
    id="modalCita"
    aria-hidden="true"
>
    <div class="modal-contenido">

        <div class="modal-cabecera">

            <div>
                <span class="badge">Detalle de citación</span>
                <h2 id="modalTitulo">Citación</h2>
            </div>

            <button
                type="button"
                class="modal-cerrar"
                id="cerrarModal"
                aria-label="Cerrar"
            >
                ×
            </button>

        </div>

        <div class="detalle-grid">

            <div class="detalle-item">
                <strong>Fecha</strong>
                <span id="detalleFecha">—</span>
            </div>

            <div class="detalle-item">
                <strong>Hora</strong>
                <span id="detalleHora">—</span>
            </div>

            <div class="detalle-item">
                <strong>Estudiante</strong>
                <span id="detalleEstudiante">—</span>
            </div>

            <div class="detalle-item">
                <strong>Docente</strong>
                <span id="detalleDocente">—</span>
            </div>

            <div class="detalle-item">
                <strong>Acudiente</strong>
                <span id="detalleAcudiente">—</span>
            </div>

            <div class="detalle-item">
                <strong>Lugar</strong>
                <span id="detalleLugar">—</span>
            </div>

            <div class="detalle-item">
                <strong>Motivo</strong>
                <span id="detalleMotivo">—</span>
            </div>

            <div class="detalle-item">
                <strong>Estado</strong>
                <span id="detalleEstado">—</span>
            </div>

            <div class="detalle-item detalle-ancho">
                <strong>Observaciones</strong>
                <span id="detalleObservaciones">—</span>
            </div>

        </div>

        <div class="modal-acciones">

            <a
                id="btnIcs"
                class="boton"
                href="#"
            >
                Descargar .ics
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

<link
    rel="stylesheet"
    href="{{ url_for('static', filename='vendor/fullcalendar/skeleton.css') }}"
>

<script src="{{ url_for('static', filename='vendor/fullcalendar/fullcalendar.global.js') }}"></script>

<script src="{{ url_for('static', filename='vendor/fullcalendar/locales/es.global.js') }}"></script>

<script>

const citasOriginales = [
{% for cita in citas %}
    {
        id: {{ cita.id }},
        title: {{ (cita.motivo or 'Citación')|tojson }},
        start: {{ ((cita.fecha|string) ~ 'T' ~ (cita.hora|string))|tojson }},
        allDay: false,
        extendedProps: {
            estudiante: {{ ((cita.estudiante_n or '') ~ ' ' ~ (cita.estudiante_a or ''))|trim|tojson }},
            docente: {{ ((cita.docente_n or '') ~ ' ' ~ (cita.docente_a or ''))|trim|tojson }},
            acudiente: {{ ((cita.acudiente_n or '') ~ ' ' ~ (cita.acudiente_a or ''))|trim|tojson }},
            motivo: {{ (cita.motivo or '')|tojson }},
            lugar: {{ (cita.lugar or '')|tojson }},
            observaciones: {{ (cita.observaciones or '')|tojson }},
            estado: {{ (cita.estado or '')|tojson }},
            fecha: {{ (cita.fecha|string)|tojson }},
            hora: {{ (cita.hora|string)|tojson }},
            ics: {{ url_for('calendario.descargar_ics', cita_id=cita.id)|tojson }}
        }
    }{% if not loop.last %},{% endif %}
{% endfor %}
];

let calendar;

function obtenerEstadoClase(estado) {
    const e = (estado || '').toLowerCase();

    if (e.includes('pend')) return 'estado-pendiente';
    if (e.includes('confirm')) return 'estado-confirmada';
    if (e.includes('cancel')) return 'estado-cancelada';
    if (e.includes('reprogram')) return 'estado-reprogramada';

    return 'estado-default';
}

document.addEventListener('DOMContentLoaded', function () {

    const calendarEl = document.getElementById('eduturnosCalendar');

    calendar = new FullCalendar.Calendar(calendarEl, {

        locale: 'es',

        initialView: 'dayGridMonth',

        height: 'auto',

        dayMaxEvents: true,

        nowIndicator: true,

        navLinkDayClick: true,

        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },

        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Agenda'
        },

        events: citasOriginales,

        eventClick: function(info) {

            const p = info.event.extendedProps;

            document.getElementById('modalTitulo').textContent =
                p.motivo || info.event.title || 'Citación';

            document.getElementById('detalleFecha').textContent =
                p.fecha || '—';

            document.getElementById('detalleHora').textContent =
                p.hora || '—';

            document.getElementById('detalleEstudiante').textContent =
                p.estudiante || '—';

            document.getElementById('detalleDocente').textContent =
                p.docente || '—';

            document.getElementById('detalleAcudiente').textContent =
                p.acudiente || '—';

            document.getElementById('detalleLugar').textContent =
                p.lugar || '—';

            document.getElementById('detalleMotivo').textContent =
                p.motivo || '—';

            document.getElementById('detalleEstado').textContent =
                p.estado || '—';

            document.getElementById('detalleObservaciones').textContent =
                p.observaciones || '—';

            document.getElementById('btnIcs').href =
                p.ics || '#';

            document.getElementById('modalCita').classList.add('activo');
            document.getElementById('modalCita').setAttribute('aria-hidden', 'false');
        }

    });

    calendar.render();

    aplicarEstados();

    document
        .getElementById('buscarCita')
        .addEventListener('input', filtrarEventos);

    document
        .getElementById('filtroEstado')
        .addEventListener('change', filtrarEventos);

    document
        .getElementById('btnActualizar')
        .addEventListener('click', function () {
            calendar.removeAllEvents();
            calendar.addEventSource(citasOriginales);
            filtrarEventos();
            calendar.render();
        });

});

function filtrarEventos() {

    const texto = document
        .getElementById('buscarCita')
        .value
        .trim()
        .toLowerCase();

    const estado = document
        .getElementById('filtroEstado')
        .value
        .trim()
        .toLowerCase();

    const filtrados = citasOriginales.filter(function (cita) {

        const p = cita.extendedProps;

        const contenido = [
            cita.title,
            p.estudiante,
            p.docente,
            p.acudiente,
            p.motivo,
            p.lugar,
            p.observaciones,
            p.estado
        ]
        .join(' ')
        .toLowerCase();

        const coincideTexto =
            !texto || contenido.includes(texto);

        const coincideEstado =
            !estado ||
            (p.estado || '').toLowerCase() === estado;

        return coincideTexto && coincideEstado;
    });

    calendar.removeAllEvents();
    calendar.addEventSource(filtrados);
}

function aplicarEstados() {

    document.querySelectorAll('[data-estado]').forEach(function (elemento) {

        const clase = obtenerEstadoClase(
            elemento.getAttribute('data-estado')
        );

        elemento.classList.remove(
            'estado-default',
            'estado-pendiente',
            'estado-confirmada',
            'estado-cancelada',
            'estado-reprogramada'
        );

        elemento.classList.add(clase);
    });
}

function cerrarModal() {
    document.getElementById('modalCita').classList.remove('activo');
    document.getElementById('modalCita').setAttribute('aria-hidden', 'true');
}

document
    .getElementById('cerrarModal')
    .addEventListener('click', cerrarModal);

document
    .getElementById('cerrarModal2')
    .addEventListener('click', cerrarModal);

document
    .getElementById('modalCita')
    .addEventListener('click', function (e) {
        if (e.target === this) {
            cerrarModal();
        }
    });

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        cerrarModal();
    }
});

</script>

{% endblock %}
"""

TEMPLATE.write_text(template, encoding="utf-8")

print("=" * 72)
print("CALENDARIO REAL INSTALADO CORRECTAMENTE")
print("=" * 72)
print()
print("Archivos:")
print(FILE_JS)
print(FILE_CSS)
print(FILE_ES)
print(TEMPLATE)
print()
print("Funciones:")
print("- calendario mensual real")
print("- Semana")
print("- Día")
print("- Agenda")
print("- Hoy")
print("- anterior / siguiente")
print("- citas reales de MySQL")
print("- búsqueda")
print("- filtro por estado")
print("- detalle completo de la cita")
print("- descarga .ics")
print("- responsive")
print()
print("NO se modificó routes/calendario.py")
print("NO se modificó MySQL")
print()