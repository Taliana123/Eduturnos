from pathlib import Path

archivo = Path("templates/calendario/index.html")

if not archivo.exists():
    print("ERROR: no existe templates/calendario/index.html")
    raise SystemExit(1)

contenido = archivo.read_text(encoding="utf-8")

css = r"""
/* =========================================================
   EDUTURNOS · AJUSTE VISUAL COMPACTO
   Solo diseño. No modifica la lógica del calendario.
   ========================================================= */

.ed-cal-page {
    max-width: 1320px !important;
    padding: 14px 18px 28px !important;
}

/* CABECERA */

.ed-cal-head {
    gap: 12px !important;
    margin-bottom: 12px !important;
}

.ed-cal-head-left {
    min-width: 0 !important;
}

.ed-cal-head-kicker {
    margin-bottom: 3px !important;
    font-size: 9px !important;
}

.ed-cal-head h1 {
    font-size: 25px !important;
}

.ed-cal-head p {
    margin-top: 4px !important;
    font-size: 12px !important;
}

.ed-cal-actions {
    gap: 6px !important;
}

.ed-cal-btn {
    min-height: 34px !important;
    padding: 0 11px !important;
    border-radius: 7px !important;
    font-size: 11px !important;
}

/* ESTADISTICAS */

.ed-cal-stats {
    gap: 8px !important;
    margin-bottom: 11px !important;
}

.ed-cal-stat {
    min-height: 66px !important;
    padding: 10px 12px !important;
    border-radius: 9px !important;
}

.ed-cal-stat-label {
    font-size: 9px !important;
}

.ed-cal-stat-value {
    margin-top: 4px !important;
    font-size: 20px !important;
}

/* FILTROS */

.ed-cal-filters {
    padding: 11px !important;
    margin-bottom: 11px !important;
    border-radius: 9px !important;
}

.ed-cal-filter-header {
    margin-bottom: 8px !important;
}

.ed-cal-filter-header-left strong {
    font-size: 12px !important;
}

.ed-cal-filter-header-left span {
    font-size: 9px !important;
}

.ed-cal-filter-count {
    font-size: 10px !important;
}

.ed-cal-filter-form {
    gap: 7px !important;
}

.ed-cal-field label {
    margin-bottom: 3px !important;
    font-size: 9px !important;
}

.ed-cal-field input,
.ed-cal-field select {
    height: 34px !important;
    padding: 0 8px !important;
    border-radius: 6px !important;
    font-size: 11px !important;
}

.ed-cal-filter-actions {
    gap: 6px !important;
    margin-top: 8px !important;
    padding-top: 8px !important;
}

.ed-cal-filter-actions .ed-cal-btn {
    min-width: 95px !important;
}

/* NAVEGACION */

.ed-cal-toolbar {
    gap: 10px !important;
    margin-bottom: 7px !important;
}

.ed-cal-nav {
    gap: 4px !important;
}

.ed-cal-nav a,
.ed-cal-today {
    min-width: 32px !important;
    height: 32px !important;
    padding: 0 8px !important;
    border-radius: 6px !important;
    font-size: 11px !important;
}

.ed-cal-periodo {
    margin-left: 5px !important;
    font-size: 18px !important;
}

/* CALENDARIO
   Se mantiene la estructura actual.
   Solo se hace un poco más compacto. */

.ed-cal-card {
    padding: 6px !important;
    border-radius: 9px !important;
}

.ed-month {
    min-width: 900px !important;
}

.ed-month th {
    height: 37px !important;
    padding: 5px !important;
    font-size: 10px !important;
}

.ed-day {
    height: 125px !important;
    padding: 5px !important;
}

.ed-day-number {
    width: 24px !important;
    height: 24px !important;
    margin-bottom: 4px !important;
    font-size: 10px !important;
}

.ed-events {
    gap: 2px !important;
}

.ed-cita {
    border-left-width: 3px !important;
    border-radius: 4px !important;
}

.ed-cita summary {
    padding: 4px 5px !important;
    font-size: 9px !important;
    line-height: 1.2 !important;
}

.ed-cita summary::after {
    font-size: 11px !important;
}

.ed-cita-detail {
    margin: 0 3px 4px !important;
    padding: 6px !important;
    font-size: 9px !important;
}

.ed-cita-detail div {
    margin-bottom: 3px !important;
}

.ed-cita-label {
    font-size: 8px !important;
}

.ed-cita-link {
    margin-top: 4px !important;
    padding: 3px 6px !important;
    font-size: 8px !important;
}

.ed-more {
    padding: 1px 3px !important;
    font-size: 9px !important;
}

/* PROXIMAS CITAS */

.ed-upcoming {
    margin-top: 11px !important;
    padding: 11px !important;
    border-radius: 9px !important;
}

.ed-upcoming-header {
    margin-bottom: 7px !important;
}

.ed-upcoming h2 {
    margin: 0 !important;
    font-size: 15px !important;
}

.ed-upcoming-subtitle {
    font-size: 9px !important;
}

.ed-upcoming-list {
    gap: 5px !important;
}

.ed-upcoming-item {
    padding: 8px 9px !important;
    gap: 8px !important;
}

.ed-upcoming-date {
    font-size: 10px !important;
}

.ed-upcoming-main {
    margin-top: 3px !important;
}

.ed-upcoming-main strong {
    font-size: 11px !important;
}

.ed-upcoming-main span {
    margin-top: 2px !important;
    font-size: 9px !important;
}

.ed-state {
    padding: 4px 6px !important;
    font-size: 8px !important;
}

/* ESPACIADO GENERAL */

.ed-cal-page > * {
    margin-left: 0;
    margin-right: 0;
}

/* EVITA QUE EL CONTENIDO SE VEA ENORME */

.ed-cal-page,
.ed-cal-head,
.ed-cal-filters,
.ed-cal-toolbar,
.ed-cal-card,
.ed-upcoming {
    box-shadow: none !important;
}

/* MÓVIL */

@media (max-width: 850px) {

    .ed-cal-page {
        padding: 10px !important;
    }

    .ed-cal-stats {
        gap: 6px !important;
    }

    .ed-cal-stat {
        min-height: 60px !important;
        padding: 9px !important;
    }

    .ed-cal-filter-form {
        gap: 6px !important;
    }

}

@media (max-width: 600px) {

    .ed-cal-head h1 {
        font-size: 22px !important;
    }

    .ed-cal-head p {
        font-size: 11px !important;
    }

    .ed-cal-actions .ed-cal-btn {
        min-height: 32px !important;
        padding: 0 9px !important;
        font-size: 10px !important;
    }

    .ed-month {
        min-width: 850px !important;
    }

    .ed-day {
        height: 110px !important;
    }

}
"""

# Insertar el nuevo ajuste antes del cierre del primer bloque style.
posicion = contenido.find("</style>")

if posicion == -1:
    print("ERROR: no se encontró </style> en la plantilla.")
    raise SystemExit(1)

# Evitar duplicarlo si se ejecuta más de una vez.
if "EDUTURNOS · AJUSTE VISUAL COMPACTO" not in contenido:
    contenido = (
        contenido[:posicion]
        + css
        + "\n"
        + contenido[posicion:]
    )

    archivo.write_text(
        contenido,
        encoding="utf-8"
    )

    print("=" * 65)
    print("CALENDARIO COMPACTADO CORRECTAMENTE")
    print("=" * 65)
    print()
    print("Archivo actualizado:")
    print(archivo)
    print()
    print("NO se modificó:")
    print("- routes/calendario.py")
    print("- MySQL")
    print("- lógica de citas")
    print("- estructura del calendario")
    print("- navegación")
    print("- descarga .ics")
    print()
else:
    print("El ajuste visual ya estaba instalado.")