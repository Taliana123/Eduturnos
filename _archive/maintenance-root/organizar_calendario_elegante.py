from pathlib import Path

archivo = Path("templates/calendario/index.html")

if not archivo.exists():
    print("ERROR: no existe templates/calendario/index.html")
    raise SystemExit(1)

html = archivo.read_text(encoding="utf-8")

# Evita duplicar el ajuste si se ejecuta otra vez.
marcador = "AJUSTE FINAL · CALENDARIO COMPACTO"

if marcador in html:
    print("El ajuste visual ya está instalado.")
    raise SystemExit(0)


css = r"""
/* =========================================================
   AJUSTE FINAL · CALENDARIO COMPACTO
   Solo modifica presentación visual.
   No modifica la lógica ni la estructura funcional.
   ========================================================= */

.ed-cal-page {
    max-width: 1220px !important;
    padding: 12px 15px 22px !important;
}

/* CABECERA */

.ed-cal-head {
    gap: 10px !important;
    margin-bottom: 11px !important;
}

.ed-cal-head-left {
    min-width: 0 !important;
}

.ed-cal-head-kicker {
    margin-bottom: 2px !important;
    font-size: 8px !important;
    letter-spacing: .06em !important;
}

.ed-cal-head h1 {
    font-size: 23px !important;
    line-height: 1.12 !important;
}

.ed-cal-head p {
    margin-top: 3px !important;
    font-size: 11px !important;
}

.ed-cal-actions {
    gap: 5px !important;
}

.ed-cal-btn {
    min-height: 32px !important;
    padding: 0 10px !important;
    border-radius: 7px !important;
    font-size: 10px !important;
}

/* ESTADISTICAS */

.ed-cal-stats {
    gap: 7px !important;
    margin-bottom: 10px !important;
}

.ed-cal-stat {
    min-height: 58px !important;
    padding: 9px 11px !important;
    border-radius: 8px !important;
}

.ed-cal-stat-label {
    font-size: 8px !important;
    letter-spacing: .02em !important;
}

.ed-cal-stat-value {
    margin-top: 3px !important;
    font-size: 19px !important;
}

/* FILTROS */

.ed-cal-filters {
    padding: 10px 11px !important;
    margin-bottom: 10px !important;
    border-radius: 8px !important;
}

.ed-cal-filter-header {
    margin-bottom: 7px !important;
}

.ed-cal-filter-header-left strong {
    font-size: 11px !important;
}

.ed-cal-filter-header-left span {
    margin-top: 1px !important;
    font-size: 8px !important;
}

.ed-cal-filter-count {
    font-size: 9px !important;
}

.ed-cal-filter-form {
    grid-template-columns:
        1.7fr
        1fr
        1fr
        1fr
        1fr
        .9fr !important;
    gap: 6px !important;
}

.ed-cal-field label {
    margin-bottom: 3px !important;
    font-size: 8px !important;
}

.ed-cal-field input,
.ed-cal-field select {
    height: 33px !important;
    padding: 0 8px !important;
    border-radius: 6px !important;
    font-size: 10px !important;
}

.ed-cal-field input::placeholder {
    font-size: 10px !important;
}

.ed-cal-filter-actions {
    gap: 5px !important;
    margin-top: 7px !important;
    padding-top: 7px !important;
}

.ed-cal-filter-actions .ed-cal-btn {
    min-width: 88px !important;
}

/* NAVEGACION */

.ed-cal-toolbar {
    gap: 8px !important;
    margin-bottom: 6px !important;
}

.ed-cal-nav {
    gap: 4px !important;
}

.ed-cal-nav a,
.ed-cal-today {
    min-width: 30px !important;
    height: 30px !important;
    padding: 0 7px !important;
    border-radius: 6px !important;
    font-size: 10px !important;
}

.ed-cal-periodo {
    margin-left: 5px !important;
    font-size: 17px !important;
}

/* CALENDARIO */

.ed-cal-card {
    padding: 5px !important;
    border-radius: 8px !important;
}

.ed-month {
    min-width: 820px !important;
}

.ed-month th {
    height: 34px !important;
    padding: 4px !important;
    font-size: 9px !important;
}

.ed-day {
    height: 108px !important;
    padding: 4px !important;
}

.ed-day-number {
    width: 23px !important;
    height: 23px !important;
    margin-bottom: 3px !important;
    font-size: 9px !important;
}

.ed-events {
    gap: 2px !important;
}

.ed-cita {
    border-left-width: 3px !important;
    border-radius: 4px !important;
}

.ed-cita summary {
    padding: 3px 4px !important;
    font-size: 8px !important;
    line-height: 1.15 !important;
}

.ed-cita summary::after {
    font-size: 10px !important;
}

.ed-cita-detail {
    margin: 0 2px 3px !important;
    padding: 6px !important;
    font-size: 8px !important;
    line-height: 1.25 !important;
}

.ed-cita-detail div {
    margin-bottom: 2px !important;
}

.ed-cita-label {
    font-size: 7px !important;
}

.ed-cita-link {
    margin-top: 3px !important;
    padding: 3px 5px !important;
    font-size: 7px !important;
}

.ed-more {
    padding: 1px 3px !important;
    font-size: 8px !important;
}

/* AVISO SIN CITAS */

.ed-empty {
    padding: 12px !important;
    font-size: 10px !important;
}

/* PROXIMAS CITAS */

.ed-upcoming {
    margin-top: 10px !important;
    padding: 10px 11px !important;
    border-radius: 8px !important;
}

.ed-upcoming-header {
    margin-bottom: 7px !important;
}

.ed-upcoming h2 {
    font-size: 15px !important;
}

.ed-upcoming-subtitle {
    font-size: 8px !important;
}

.ed-upcoming-list {
    gap: 5px !important;
}

.ed-upcoming-item {
    grid-template-columns: 95px 1fr auto !important;
    gap: 9px !important;
    padding: 8px 9px !important;
}

.ed-upcoming-date {
    font-size: 9px !important;
}

.ed-upcoming-main {
    margin-top: 2px !important;
}

.ed-upcoming-main strong {
    font-size: 10px !important;
}

.ed-upcoming-main span {
    margin-top: 2px !important;
    font-size: 8px !important;
}

.ed-state {
    padding: 3px 6px !important;
    font-size: 7px !important;
}

/* QUITAR PESO VISUAL INNECESARIO */

.ed-cal-stat,
.ed-cal-filters,
.ed-cal-card,
.ed-upcoming {
    box-shadow: none !important;
}

/* RESPONSIVE */

@media (max-width: 1050px) {

    .ed-cal-filter-form {
        grid-template-columns: repeat(3, 1fr) !important;
    }

}

@media (max-width: 760px) {

    .ed-cal-page {
        padding: 9px 8px 18px !important;
    }

    .ed-cal-head h1 {
        font-size: 21px !important;
    }

    .ed-cal-head p {
        font-size: 10px !important;
    }

    .ed-cal-actions {
        width: 100%;
    }

    .ed-cal-actions .ed-cal-btn {
        flex: 1;
    }

    .ed-cal-filter-form {
        grid-template-columns: repeat(2, 1fr) !important;
    }

    .ed-cal-stats {
        gap: 5px !important;
    }

    .ed-cal-stat {
        min-height: 55px !important;
        padding: 8px !important;
    }

    .ed-month {
        min-width: 780px !important;
    }

    .ed-day {
        height: 100px !important;
    }

}

@media (max-width: 500px) {

    .ed-cal-filter-form {
        grid-template-columns: 1fr !important;
    }

    .ed-cal-filter-actions {
        flex-direction: column !important;
        align-items: stretch !important;
    }

    .ed-cal-filter-actions .ed-cal-btn {
        width: 100% !important;
    }

}
"""

posicion = html.find("</style>")

if posicion == -1:
    print("ERROR: no se encontró </style>.")
    raise SystemExit(1)

html = (
    html[:posicion]
    + css
    + "\n"
    + html[posicion:]
)

archivo.write_text(
    html,
    encoding="utf-8"
)

print("=" * 65)
print("CALENDARIO ORGANIZADO Y COMPACTADO")
print("=" * 65)
print()
print("Archivo actualizado:")
print(archivo)
print()
print("Se redujo:")
print("- encabezado")
print("- botones")
print("- estadísticas")
print("- filtros")
print("- navegación")
print("- tamaño de las celdas")
print("- textos internos")
print("- sección de próximas citas")
print()
print("El calendario mantiene su funcionamiento.")
print("No se modificó routes/calendario.py.")
print("No se modificó MySQL.")
print("=" * 65)