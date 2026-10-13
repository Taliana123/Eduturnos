from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent

ARCHIVO = BASE / "templates" / "calendario" / "index.html"
BACKUP = BASE / "templates" / "calendario" / "index.html.backup_calendario_real"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/calendario/index.html")
    raise SystemExit(1)

# ============================================================
# COPIA DE SEGURIDAD
# ============================================================

shutil.copy2(ARCHIVO, BACKUP)

HTML = r'''{% extends 'base.html' %}

{% block title %}Calendario · EDUTURNOS{% endblock %}

{% block content %}

<section class="calendario-pagina">

    <!-- =====================================================
         CABECERA
         ===================================================== -->

    <div class="calendario-cabecera">

        <div class="calendario-cabecera-info">

            <a
                class="calendario-atras"
                href="{{ request.referrer or url_for('auth.dashboard') }}"
            >
                ← Atrás
            </a>

            <div class="calendario-titulo-fila">

                <div class="calendario-icono-titulo">
                    CAL
                </div>

                <div>
                    <span class="badge">Agenda</span>

                    <h1>Calendario</h1>

                    <p>
                        Consulta tus citaciones y actividades programadas.
                    </p>
                </div>

            </div>

        </div>

        <div class="calendario-resumen">

            <span class="calendario-resumen-numero">
                {{ citas|length }}
            </span>

            <span class="calendario-resumen-texto">
                {{ 'citación' if citas|length == 1 else 'citaciones' }}
            </span>

        </div>

    </div>


    <!-- =====================================================
         CONTROLES
         ===================================================== -->

    <section class="calendario-panel">

        <div class="calendario-controles">

            <div class="calendario-controles-izq">

                <button
                    type="button"
                    class="calendario-boton-secundario"
                    id="calendarioAnterior"
                >
                    ‹
                </button>

                <button
                    type="button"
                    class="calendario-boton-secundario"
                    id="calendarioHoy"
                >
                    Hoy
                </button>

                <button
                    type="button"
                    class="calendario-boton-secundario"
                    id="calendarioSiguiente"
                >
                    ›
                </button>

            </div>

            <h2 id="calendarioMes">
                Calendario
            </h2>

            <div class="calendario-leyenda">

                <span>
                    <i class="estado-punto estado-confirmada"></i>
                    Confirmada
                </span>

                <span>
                    <i class="estado-punto estado-pendiente"></i>
                    Pendiente
                </span>

                <span>
                    <i class="estado-punto estado-cancelada"></i>
                    Cancelada
                </span>

            </div>

        </div>


        <!-- =================================================
             DÍAS DE LA SEMANA
             ================================================= -->

        <div class="calendario-semana">

            <span>Lun</span>
            <span>Mar</span>
            <span>Mié</span>
            <span>Jue</span>
            <span>Vie</span>
            <span>Sáb</span>
            <span>Dom</span>

        </div>


        <!-- =================================================
             CUADRÍCULA REAL
             ================================================= -->

        <div
            class="calendario-grid"
            id="calendarioGrid"
        ></div>

    </section>


    <!-- =====================================================
         DETALLE DEL DÍA / CITA
         ===================================================== -->

    <section class="calendario-detalle-panel">

        <div class="calendario-detalle-cabecera">

            <div>

                <span class="badge">Detalle</span>

                <h2 id="detalleTitulo">
                    Selecciona una fecha
                </h2>

                <p id="detalleSubtitulo">
                    Aquí aparecerán las citas del día seleccionado.
                </p>

            </div>

        </div>


        <div
            class="calendario-detalle-lista"
            id="detalleLista"
        >

            <div class="calendario-vacio">

                <div class="calendario-vacio-icono">
                    +
                </div>

                <h3>No hay una fecha seleccionada</h3>

                <p>
                    Haz clic en un día del calendario para consultar
                    sus citaciones.
                </p>

            </div>

        </div>

    </section>


    <!-- =====================================================
         FUENTE DE DATOS REAL DE MYSQL
         ===================================================== -->

    <div
        id="citasFuente"
        hidden
    >

        {% for cita in citas %}

        <article
            class="cita-fuente"

            data-id="{{ cita.id }}"
            data-fecha="{{ cita.fecha }}"
            data-hora="{{ cita.hora }}"
            data-estudiante="{{ cita.estudiante_n }} {{ cita.estudiante_a }}"
            data-docente="{{ cita.docente_n }} {{ cita.docente_a }}"
            data-acudiente="{{ cita.acudiente_n }} {{ cita.acudiente_a }}"
            data-motivo="{{ cita.motivo }}"
            data-estado="{{ cita.estado }}"
            data-lugar="{{ cita.lugar or 'Por definir' }}"
            data-observaciones="{{ cita.observaciones or '' }}"
            data-url="{{ url_for('calendario.descargar_ics', cita_id=cita.id) }}"
        ></article>

        {% endfor %}

    </div>


<style>

/* =========================================================
   CALENDARIO EDUTURNOS
   ========================================================= */

.calendario-pagina {
    width: 100%;
    max-width: 1180px;

    margin: 0 auto;

    padding: 8px 0 35px;

    box-sizing: border-box;
}

/* =========================================================
   CABECERA
   ========================================================= */

.calendario-cabecera {
    display: flex;

    justify-content: space-between;
    align-items: flex-end;

    gap: 25px;

    margin-bottom: 22px;
}

.calendario-cabecera-info {
    min-width: 0;
}

.calendario-atras {
    display: inline-flex;

    margin-bottom: 14px;

    color: #64748b;

    font-size: 14px;

    font-weight: 500;

    text-decoration: none;
}

.calendario-atras:hover {
    color: #2563eb;
}

.calendario-titulo-fila {
    display: flex;

    align-items: center;

    gap: 14px;
}

.calendario-icono-titulo {
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

    font-size: 12px;

    font-weight: 800;
}

.calendario-titulo-fila h1 {
    margin: 7px 0 7px;

    color: #0f172a;

    font-size: 30px;

    line-height: 1.15;
}

.calendario-titulo-fila p {
    margin: 0;

    color: #64748b;

    line-height: 1.5;
}

.calendario-resumen {
    display: flex;

    flex-direction: column;

    align-items: center;
    justify-content: center;

    min-width: 105px;
    min-height: 82px;

    padding: 12px 18px;

    background: #ffffff;

    border: 1px solid #dbe4ee;

    border-radius: 12px;

    box-shadow:
        0 3px 10px rgba(15, 23, 42, 0.05);

    box-sizing: border-box;
}

.calendario-resumen-numero {
    color: #2563eb;

    font-size: 26px;

    font-weight: 750;

    line-height: 1;
}

.calendario-resumen-texto {
    margin-top: 6px;

    color: #64748b;

    font-size: 12px;
}

/* =========================================================
   PANEL CALENDARIO
   ========================================================= */

.calendario-panel,
.calendario-detalle-panel {
    width: 100%;

    background: #ffffff;

    border: 1px solid #dbe4ee;

    border-radius: 16px;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.055);

    box-sizing: border-box;

    overflow: hidden;
}

/* =========================================================
   CONTROLES
   ========================================================= */

.calendario-controles {
    display: grid;

    grid-template-columns:
        1fr auto 1fr;

    align-items: center;

    gap: 15px;

    padding: 18px 20px;

    border-bottom: 1px solid #e7edf4;

    background:
        linear-gradient(
            180deg,
            #ffffff,
            #f8fafc
        );
}

.calendario-controles-izq {
    display: flex;

    align-items: center;

    gap: 7px;
}

.calendario-boton-secundario {
    min-width: 38px;
    min-height: 38px;

    padding: 7px 11px;

    border: 1px solid #d7e0ea;

    border-radius: 8px;

    background: #ffffff;

    color: #334155;

    font-family: inherit;

    font-size: 13px;

    font-weight: 600;

    cursor: pointer;

    transition:
        background .18s ease,
        border-color .18s ease,
        color .18s ease;
}

.calendario-boton-secundario:hover {
    background: #eff6ff;

    border-color: #bfdbfe;

    color: #2563eb;
}

#calendarioMes {
    margin: 0;

    text-align: center;

    color: #0f172a;

    font-size: 21px;

    line-height: 1.2;

    text-transform: capitalize;
}

.calendario-leyenda {
    display: flex;

    justify-content: flex-end;

    align-items: center;

    flex-wrap: wrap;

    gap: 10px 14px;
}

.calendario-leyenda span {
    display: inline-flex;

    align-items: center;

    gap: 5px;

    color: #64748b;

    font-size: 11px;

    font-weight: 500;
}

.estado-punto {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    display: inline-block;
}

.estado-confirmada {
    background: #22c55e;
}

.estado-pendiente {
    background: #f59e0b;
}

.estado-cancelada {
    background: #ef4444;
}

/* =========================================================
   DÍAS SEMANA
   ========================================================= */

.calendario-semana {
    display: grid;

    grid-template-columns:
        repeat(7, minmax(0, 1fr));

    border-bottom: 1px solid #e7edf4;

    background: #f8fafc;
}

.calendario-semana span {
    padding: 12px 8px;

    text-align: center;

    color: #64748b;

    font-size: 11px;

    font-weight: 700;

    text-transform: uppercase;
}

/* =========================================================
   GRID
   ========================================================= */

.calendario-grid {
    display: grid;

    grid-template-columns:
        repeat(7, minmax(0, 1fr));

    min-height: 480px;
}

.calendario-dia {
    position: relative;

    min-width: 0;
    min-height: 92px;

    padding: 9px;

    border-right: 1px solid #edf2f7;
    border-bottom: 1px solid #edf2f7;

    background: #ffffff;

    cursor: pointer;

    transition:
        background .18s ease,
        box-shadow .18s ease;
}

.calendario-dia:hover {
    background: #f8fbff;
}

.calendario-dia:nth-child(7n) {
    border-right: 0;
}

.calendario-dia.otro-mes {
    background: #f8fafc;

    cursor: default;
}

.calendario-dia.otro-mes .calendario-numero {
    color: #cbd5e1;
}

.calendario-dia.hoy {
    background: #f8fbff;
}

.calendario-dia.seleccionado {
    box-shadow:
        inset 0 0 0 2px #2563eb;

    z-index: 2;
}

.calendario-numero {
    display: flex;

    align-items: center;
    justify-content: center;

    width: 27px;
    height: 27px;

    margin-bottom: 6px;

    border-radius: 50%;

    color: #334155;

    font-size: 12px;

    font-weight: 700;
}

.calendario-dia.hoy .calendario-numero {
    background: #2563eb;

    color: #ffffff;
}

/* =========================================================
   EVENTOS
   ========================================================= */

.calendario-eventos {
    display: flex;

    flex-direction: column;

    gap: 4px;
}

.calendario-evento {
    display: flex;

    flex-direction: column;

    width: 100%;

    padding: 5px 6px;

    border: 0;

    border-left: 3px solid #94a3b8;

    border-radius: 5px;

    background: #f8fafc;

    color: #334155;

    text-align: left;

    font-family: inherit;

    cursor: pointer;

    box-sizing: border-box;

    transition:
        background .15s ease,
        border-color .15s ease;
}

.calendario-evento:hover {
    background: #eef6ff;

    border-left-color: #2563eb;
}

.calendario-evento.confirmada {
    border-left-color: #22c55e;

    background: #f0fdf4;
}

.calendario-evento.pendiente {
    border-left-color: #f59e0b;

    background: #fffbeb;
}

.calendario-evento.cancelada {
    border-left-color: #ef4444;

    background: #fef2f2;
}

.calendario-evento.reprogramada {
    border-left-color: #6366f1;

    background: #eef2ff;
}

.calendario-evento-hora {
    color: #475569;

    font-size: 10px;

    font-weight: 700;

    line-height: 1.2;
}

.calendario-evento-texto {
    overflow: hidden;

    margin-top: 2px;

    color: #334155;

    font-size: 10px;

    line-height: 1.25;

    white-space: nowrap;

    text-overflow: ellipsis;
}

/* =========================================================
   DETALLE
   ========================================================= */

.calendario-detalle-panel {
    margin-top: 20px;
}

.calendario-detalle-cabecera {
    padding: 20px 22px;

    border-bottom: 1px solid #e7edf4;

    background:
        linear-gradient(
            180deg,
            #ffffff,
            #f8fafc
        );
}

.calendario-detalle-cabecera h2 {
    margin: 7px 0 6px;

    color: #0f172a;

    font-size: 21px;

    line-height: 1.2;
}

.calendario-detalle-cabecera p {
    margin: 0;

    color: #64748b;

    font-size: 13px;

    line-height: 1.5;
}

.calendario-detalle-lista {
    padding: 18px;
}

.calendario-detalle-item {
    display: grid;

    grid-template-columns:
        110px minmax(0, 1fr) auto;

    gap: 15px;

    align-items: center;

    padding: 16px;

    margin-bottom: 10px;

    border: 1px solid #e2e8f0;

    border-radius: 11px;

    background: #ffffff;

    box-sizing: border-box;
}

.calendario-detalle-item:last-child {
    margin-bottom: 0;
}

.detalle-hora {
    color: #2563eb;

    font-size: 14px;

    font-weight: 750;
}

.detalle-contenido h3 {
    margin: 0 0 5px;

    color: #0f172a;

    font-size: 15px;

    line-height: 1.3;
}

.detalle-contenido p {
    margin: 3px 0;

    color: #64748b;

    font-size: 12px;

    line-height: 1.45;
}

.detalle-estado {
    display: inline-flex;

    align-items: center;

    justify-content: center;

    min-height: 27px;

    padding: 5px 9px;

    border-radius: 999px;

    font-size: 10px;

    font-weight: 700;

    white-space: nowrap;
}

.detalle-estado.confirmada {
    background: #dcfce7;
    color: #166534;
}

.detalle-estado.pendiente {
    background: #fef3c7;
    color: #92400e;
}

.detalle-estado.cancelada {
    background: #fee2e2;
    color: #991b1b;
}

.detalle-estado.reprogramada {
    background: #e0e7ff;
    color: #3730a3;
}

.detalle-ical {
    display: inline-flex;

    align-items: center;
    justify-content: center;

    margin-top: 8px;

    color: #2563eb;

    font-size: 11px;

    font-weight: 600;

    text-decoration: none;
}

.detalle-ical:hover {
    text-decoration: underline;
}

/* =========================================================
   ESTADO VACÍO
   ========================================================= */

.calendario-vacio {
    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    min-height: 220px;

    padding: 30px;

    text-align: center;
}

.calendario-vacio-icono {
    width: 48px;
    height: 48px;

    display: flex;

    align-items: center;
    justify-content: center;

    margin-bottom: 12px;

    border-radius: 50%;

    background: #eef6ff;

    color: #2563eb;

    font-size: 22px;

    font-weight: 400;
}

.calendario-vacio h3 {
    margin: 0 0 7px;

    color: #334155;

    font-size: 15px;
}

.calendario-vacio p {
    max-width: 440px;

    margin: 0;

    color: #64748b;

    font-size: 13px;

    line-height: 1.5;
}

/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 950px) {

    .calendario-cabecera {
        align-items: flex-start;
    }

    .calendario-controles {
        grid-template-columns:
            1fr;
    }

    .calendario-controles-izq {
        justify-content: center;
    }

    .calendario-leyenda {
        justify-content: center;
    }
}

@media (max-width: 700px) {

    .calendario-cabecera {
        flex-direction: column;
    }

    .calendario-resumen {
        align-self: stretch;

        flex-direction: row;

        gap: 7px;

        min-height: 55px;
    }

    .calendario-titulo-fila h1 {
        font-size: 26px;
    }

    .calendario-dia {
        min-height: 76px;

        padding: 6px;
    }

    .calendario-semana span {
        font-size: 9px;
    }

    .calendario-evento-texto {
        display: none;
    }

    .calendario-detalle-item {
        grid-template-columns:
            1fr;

        gap: 9px;
    }

    .detalle-estado {
        width: fit-content;
    }
}

</style>


<script>

document.addEventListener("DOMContentLoaded", function () {

    const grid = document.getElementById("calendarioGrid");
    const tituloMes = document.getElementById("calendarioMes");

    const botonAnterior =
        document.getElementById("calendarioAnterior");

    const botonSiguiente =
        document.getElementById("calendarioSiguiente");

    const botonHoy =
        document.getElementById("calendarioHoy");

    const detalleTitulo =
        document.getElementById("detalleTitulo");

    const detalleSubtitulo =
        document.getElementById("detalleSubtitulo");

    const detalleLista =
        document.getElementById("detalleLista");

    const fuente =
        document.getElementById("citasFuente");


    /* =====================================================
       CARGAR CITAS REALES DESDE JINJA
       ===================================================== */

    const citas = Array.from(
        fuente.querySelectorAll(".cita-fuente")
    ).map(function (elemento) {

        const estadoOriginal =
            elemento.dataset.estado || "Pendiente";

        let claseEstado = estadoOriginal
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/\s+/g, "-");

        return {
            id: elemento.dataset.id,
            fecha: elemento.dataset.fecha || "",
            hora: normalizarHora(elemento.dataset.hora || ""),
            estudiante: elemento.dataset.estudiante || "",
            docente: elemento.dataset.docente || "",
            acudiente: elemento.dataset.acudiente || "",
            motivo: elemento.dataset.motivo || "",
            estado: estadoOriginal,
            claseEstado: claseEstado,
            lugar: elemento.dataset.lugar || "Por definir",
            observaciones:
                elemento.dataset.observaciones || "",
            url: elemento.dataset.url || ""
        };

    });


    function normalizarHora(valor) {

        if (!valor) {
            return "";
        }

        let hora = String(valor).trim();

        /*
           Puede llegar como:
           08:30:00
           08:30
           0:08:30
        */

        const partes = hora.split(":");

        if (partes.length >= 2) {

            let h = partes[0];
            let m = partes[1];

            if (h.length === 1) {
                h = "0" + h;
            }

            return h + ":" + m;
        }

        return hora;
    }


    /* =====================================================
       FECHA INICIAL
       ===================================================== */

    const hoy = new Date();

    hoy.setHours(0, 0, 0, 0);

    let fechaInicial = new Date(hoy);

    const proxima = citas
        .map(function (cita) {
            return fechaValida(cita.fecha);
        })
        .filter(function (fecha) {
            return fecha && fecha >= hoy;
        })
        .sort(function (a, b) {
            return a - b;
        })[0];

    if (proxima) {
        fechaInicial = new Date(proxima);
    }

    let mesActual = new Date(
        fechaInicial.getFullYear(),
        fechaInicial.getMonth(),
        1
    );

    let fechaSeleccionada = null;


    /* =====================================================
       FUNCIONES DE FECHA
       ===================================================== */

    function fechaValida(valor) {

        if (!valor) {
            return null;
        }

        const partes = String(valor).split("-");

        if (partes.length !== 3) {
            return null;
        }

        const año = Number(partes[0]);
        const mes = Number(partes[1]);
        const dia = Number(partes[2]);

        if (
            !Number.isInteger(año) ||
            !Number.isInteger(mes) ||
            !Number.isInteger(dia)
        ) {
            return null;
        }

        return new Date(
            año,
            mes - 1,
            dia
        );
    }


    function claveFecha(fecha) {

        const año = fecha.getFullYear();

        const mes = String(
            fecha.getMonth() + 1
        ).padStart(2, "0");

        const dia = String(
            fecha.getDate()
        ).padStart(2, "0");

        return año + "-" + mes + "-" + dia;
    }


    function capitalizar(texto) {

        if (!texto) {
            return "";
        }

        return texto.charAt(0).toUpperCase()
            + texto.slice(1);
    }


    /* =====================================================
       RENDER CALENDARIO
       ===================================================== */

    function renderCalendario() {

        grid.innerHTML = "";

        const año =
            mesActual.getFullYear();

        const mes =
            mesActual.getMonth();

        const primerDia =
            new Date(año, mes, 1);

        let inicioSemana =
            primerDia.getDay();

        /*
           JS:
           Domingo = 0

           Nosotros queremos:
           Lunes = 0
        */

        inicioSemana =
            inicioSemana === 0
                ? 6
                : inicioSemana - 1;

        const diasMes =
            new Date(año, mes + 1, 0).getDate();

        const diasMesAnterior =
            new Date(año, mes, 0).getDate();


        const nombreMes =
            new Intl.DateTimeFormat(
                "es-CO",
                {
                    month: "long",
                    year: "numeric"
                }
            ).format(mesActual);

        tituloMes.textContent =
            capitalizar(nombreMes);


        /*
           Siempre dibujamos 6 semanas
           para mantener el tamaño uniforme.
        */

        const totalCeldas = 42;

        for (
            let indice = 0;
            indice < totalCeldas;
            indice++
        ) {

            let diaNumero;
            let fechaCelda;
            let otroMes = false;

            if (indice < inicioSemana) {

                diaNumero =
                    diasMesAnterior
                    - inicioSemana
                    + indice
                    + 1;

                fechaCelda =
                    new Date(
                        año,
                        mes - 1,
                        diaNumero
                    );

                otroMes = true;

            } else if (
                indice >=
                inicioSemana + diasMes
            ) {

                diaNumero =
                    indice
                    - inicioSemana
                    - diasMes
                    + 1;

                fechaCelda =
                    new Date(
                        año,
                        mes + 1,
                        diaNumero
                    );

                otroMes = true;

            } else {

                diaNumero =
                    indice - inicioSemana + 1;

                fechaCelda =
                    new Date(
                        año,
                        mes,
                        diaNumero
                    );
            }


            const clave =
                claveFecha(fechaCelda);

            const citasDia =
                citas.filter(function (cita) {
                    return cita.fecha === clave;
                });


            const celda =
                document.createElement("div");

            celda.className =
                "calendario-dia";

            if (otroMes) {
                celda.classList.add("otro-mes");
            }


            if (
                clave === claveFecha(hoy)
            ) {
                celda.classList.add("hoy");
            }


            if (
                fechaSeleccionada &&
                clave ===
                claveFecha(fechaSeleccionada)
            ) {
                celda.classList.add("seleccionado");
            }


            const numero =
                document.createElement("div");

            numero.className =
                "calendario-numero";

            numero.textContent =
                diaNumero;

            celda.appendChild(numero);


            const eventos =
                document.createElement("div");

            eventos.className =
                "calendario-eventos";


            citasDia.slice(0, 3)
                .forEach(function (cita) {

                    const evento =
                        document.createElement("button");

                    evento.type = "button";

                    evento.className =
                        "calendario-evento "
                        + claseEvento(
                            cita.claseEstado
                        );

                    const hora =
                        document.createElement("span");

                    hora.className =
                        "calendario-evento-hora";

                    hora.textContent =
                        cita.hora || "Sin hora";


                    const nombre =
                        document.createElement("span");

                    nombre.className =
                        "calendario-evento-texto";

                    nombre.textContent =
                        cita.estudiante
                        || cita.motivo
                        || "Citación";


                    evento.appendChild(hora);
                    evento.appendChild(nombre);

                    evento.addEventListener(
                        "click",
                        function (e) {

                            e.stopPropagation();

                            fechaSeleccionada =
                                new Date(fechaCelda);

                            renderCalendario();

                            mostrarDetalle(
                                fechaSeleccionada,
                                cita
                            );
                        }
                    );

                    eventos.appendChild(evento);
                });


            if (citasDia.length > 3) {

                const mas =
                    document.createElement("span");

                mas.textContent =
                    "+" +
                    (
                        citasDia.length - 3
                    )
                    + " más";

                mas.className =
                    "calendario-evento-texto";

                mas.style.marginTop = "3px";

                eventos.appendChild(mas);
            }


            celda.appendChild(eventos);


            celda.addEventListener(
                "click",
                function () {

                    if (otroMes) {
                        return;
                    }

                    fechaSeleccionada =
                        new Date(fechaCelda);

                    renderCalendario();

                    mostrarDetalleDia(
                        fechaSeleccionada
                    );
                }
            );


            grid.appendChild(celda);
        }


        /*
           Mostrar automáticamente el primer día
           que tenga citas en el mes.
        */

        if (!fechaSeleccionada) {

            const primeraCita =
                citas.find(function (cita) {

                    const fecha =
                        fechaValida(cita.fecha);

                    return (
                        fecha &&
                        fecha.getFullYear()
                            === año &&
                        fecha.getMonth()
                            === mes
                    );
                });

            if (primeraCita) {

                fechaSeleccionada =
                    fechaValida(
                        primeraCita.fecha
                    );

                renderCalendario();

                mostrarDetalleDia(
                    fechaSeleccionada
                );
            }
        }

    }


    function claseEvento(clase) {

        if (clase.includes("confirm")) {
            return "confirmada";
        }

        if (
            clase.includes("cancel")
            ||
            clase.includes("anulad")
        ) {
            return "cancelada";
        }

        if (clase.includes("reprogram")) {
            return "reprogramada";
        }

        return "pendiente";
    }


    /* =====================================================
       DETALLE DEL DÍA
       ===================================================== */

    function mostrarDetalleDia(fecha) {

        const clave =
            claveFecha(fecha);

        const citasDia =
            citas.filter(function (cita) {
                return cita.fecha === clave;
            });

        const fechaTexto =
            new Intl.DateTimeFormat(
                "es-CO",
                {
                    weekday: "long",
                    day: "numeric",
                    month: "long",
                    year: "numeric"
                }
            ).format(fecha);

        detalleTitulo.textContent =
            capitalizar(fechaTexto);

        detalleSubtitulo.textContent =
            citasDia.length === 0
                ? "No tienes citaciones programadas para este día."
                : citasDia.length === 1
                    ? "Tienes 1 citación programada."
                    : "Tienes "
                        + citasDia.length
                        + " citaciones programadas.";

        detalleLista.innerHTML = "";


        if (citasDia.length === 0) {

            detalleLista.innerHTML = `
                <div class="calendario-vacio">
                    <div class="calendario-vacio-icono">✓</div>
                    <h3>Día disponible</h3>
                    <p>
                        No hay citaciones para esta fecha.
                    </p>
                </div>
            `;

            return;
        }


        citasDia
            .sort(function (a, b) {
                return a.hora.localeCompare(
                    b.hora
                );
            })
            .forEach(function (cita) {

                const item =
                    document.createElement("article");

                item.className =
                    "calendario-detalle-item";


                const hora =
                    document.createElement("div");

                hora.className =
                    "detalle-hora";

                hora.textContent =
                    cita.hora || "Sin hora";


                const contenido =
                    document.createElement("div");

                contenido.className =
                    "detalle-contenido";


                const titulo =
                    document.createElement("h3");

                titulo.textContent =
                    cita.motivo
                    || "Citación";


                contenido.appendChild(titulo);


                agregarLinea(
                    contenido,
                    "Estudiante: ",
                    cita.estudiante
                );

                agregarLinea(
                    contenido,
                    "Docente: ",
                    cita.docente
                );

                if (cita.acudiente) {

                    agregarLinea(
                        contenido,
                        "Acudiente: ",
                        cita.acudiente
                    );
                }


                agregarLinea(
                    contenido,
                    "Lugar: ",
                    cita.lugar
                );


                if (cita.observaciones) {

                    agregarLinea(
                        contenido,
                        "Observaciones: ",
                        cita.observaciones
                    );
                }


                const enlace =
                    document.createElement("a");

                enlace.href =
                    cita.url;

                enlace.className =
                    "detalle-ical";

                enlace.textContent =
                    "Agregar al calendario (.ics)";

                enlace.target = "_blank";

                contenido.appendChild(enlace);


                const estado =
                    document.createElement("span");

                estado.className =
                    "detalle-estado "
                    + claseEvento(
                        cita.claseEstado
                    );

                estado.textContent =
                    cita.estado;


                item.appendChild(hora);
                item.appendChild(contenido);
                item.appendChild(estado);

                detalleLista.appendChild(item);

            });
    }


    function agregarLinea(
        contenedor,
        etiqueta,
        valor
    ) {

        const linea =
            document.createElement("p");

        const fuerte =
            document.createElement("strong");

        fuerte.textContent =
            etiqueta;

        linea.appendChild(fuerte);

        linea.appendChild(
            document.createTextNode(
                valor || "No informado"
            )
        );

        contenedor.appendChild(linea);
    }


    function mostrarDetalle(fecha, cita) {

        mostrarDetalleDia(fecha);

        /*
           El detalle del día ya muestra la cita.
           Al hacer clic en una concreta, hacemos
           desplazamiento suave hasta la sección.
        */

        document
            .querySelector(
                ".calendario-detalle-panel"
            )
            .scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
    }


    /* =====================================================
       CONTROLES
       ===================================================== */

    botonAnterior.addEventListener(
        "click",
        function () {

            mesActual =
                new Date(
                    mesActual.getFullYear(),
                    mesActual.getMonth() - 1,
                    1
                );

            fechaSeleccionada = null;

            renderCalendario();
        }
    );


    botonSiguiente.addEventListener(
        "click",
        function () {

            mesActual =
                new Date(
                    mesActual.getFullYear(),
                    mesActual.getMonth() + 1,
                    1
                );

            fechaSeleccionada = null;

            renderCalendario();
        }
    );


    botonHoy.addEventListener(
        "click",
        function () {

            mesActual =
                new Date(
                    hoy.getFullYear(),
                    hoy.getMonth(),
                    1
                );

            fechaSeleccionada =
                new Date(hoy);

            renderCalendario();

            mostrarDetalleDia(hoy);
        }
    );


    /* =====================================================
       INICIAR
       ===================================================== */

    renderCalendario();

});

</script>

</section>

{% endblock %}
'''

ARCHIVO.write_text(
    HTML,
    encoding="utf-8"
)

print()
print("=" * 65)
print("CALENDARIO REAL INSTALADO")
print("=" * 65)
print()
print(f"Copia de seguridad: {BACKUP}")
print()
print("Incluye:")
print("- calendario mensual real")
print("- citas reales de MySQL")
print("- navegación anterior/siguiente")
print("- botón Hoy")
print("- colores por estado")
print("- detalle de cada día")
print("- estudiante")
print("- docente")
print("- acudiente")
print("- motivo")
print("- lugar")
print("- observaciones")
print("- enlace .ics")
print("- diseño responsive")
print()
print("No se modificó routes/calendario.py")
print("No se modificó MySQL")
print()