from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "templates" / "base.html"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/base.html")
    raise SystemExit(1)

texto = ARCHIVO.read_text(encoding="utf-8")

INICIO = "<!-- EDUTURNOS_CITAS_ESTILO_V2 -->"
FIN = "<!-- FIN EDUTURNOS_CITAS_ESTILO_V2 -->"

CSS = r"""
<!-- EDUTURNOS_CITAS_ESTILO_V2 -->

<style id="eduturnos-citas-estilo-v2">

/* =========================================================
   EDUTURNOS - ACCESOS DEL DASHBOARD
   ========================================================= */

.dashboard-action-grid {
    display: grid !important;

    grid-template-columns:
        repeat(4, minmax(0, 1fr)) !important;

    gap: 16px !important;

    align-items: stretch !important;

    width: 100% !important;
}

.dashboard-action,
.quick-card {
    position: relative !important;

    display: flex !important;

    flex-direction: column !important;

    justify-content: flex-start !important;
    align-items: stretch !important;

    min-width: 0 !important;

    min-height: 185px !important;

    padding: 20px !important;

    background: #ffffff !important;

    border: 1px solid #dbe3ec !important;

    border-radius: 14px !important;

    text-decoration: none !important;

    box-shadow:
        0 3px 10px rgba(15, 23, 42, 0.05) !important;

    transition:
        transform .18s ease,
        box-shadow .18s ease,
        border-color .18s ease !important;
}

.dashboard-action:hover,
.quick-card:hover {
    transform: translateY(-3px) !important;

    border-color: #bfdbfe !important;

    box-shadow:
        0 10px 22px rgba(15, 23, 42, 0.09) !important;
}

.dashboard-action-top,
.quick-card .quick-icon {
    margin-bottom: 14px !important;
}

.dashboard-action-icon,
.quick-card .quick-icon {
    display: inline-flex !important;

    align-items: center !important;

    width: fit-content !important;

    padding: 7px 11px !important;

    border-radius: 8px !important;

    background: #eaf2ff !important;

    color: #2563eb !important;

    font-size: 12px !important;

    font-weight: 600 !important;

    line-height: 1.1 !important;
}

.dashboard-action h3,
.quick-card strong {
    display: block !important;

    margin: 0 0 8px 0 !important;

    color: #0f172a !important;

    font-size: 18px !important;

    font-weight: 700 !important;

    line-height: 1.25 !important;
}

.dashboard-action p,
.quick-card > span:not(.quick-icon) {
    flex: 1 !important;

    margin: 0 !important;

    color: #64748b !important;

    font-size: 13.5px !important;

    line-height: 1.5 !important;
}

.dashboard-action-link,
.quick-card small {
    display: block !important;

    margin-top: 16px !important;

    color: #2563eb !important;

    font-size: 13px !important;

    font-weight: 600 !important;

    line-height: 1.3 !important;
}


/* =========================================================
   PAGINAS INTERNAS
   ========================================================= */

#contenido .page-head {
    width: 100% !important;

    display: flex !important;

    justify-content: space-between !important;

    align-items: flex-start !important;

    gap: 22px !important;

    margin: 0 0 24px 0 !important;

    padding: 0 !important;

    box-sizing: border-box !important;
}

#contenido .page-head > div:first-child {
    min-width: 0 !important;
}

#contenido .page-navigation {
    margin-bottom: 12px !important;
}

#contenido .page-head h1 {
    margin: 0 0 8px 0 !important;

    color: #0f172a !important;

    font-size: 30px !important;

    line-height: 1.2 !important;
}

#contenido .page-head p {
    margin: 0 !important;

    color: #64748b !important;

    line-height: 1.55 !important;
}

#contenido .page-head .link-back {
    display: inline-flex !important;

    align-items: center !important;

    text-decoration: none !important;

    font-size: 14px !important;

    font-weight: 500 !important;
}

#contenido .page-head .link-back:hover {
    text-decoration: underline !important;
}


/* =========================================================
   BOTÓN NUEVA CITACIÓN
   ========================================================= */

#contenido .page-head .boton,
#contenido .page-head a[class*="boton"] {
    display: inline-flex !important;

    align-items: center !important;
    justify-content: center !important;

    min-height: 44px !important;

    padding: 10px 16px !important;

    border-radius: 9px !important;

    text-decoration: none !important;

    white-space: nowrap !important;

    font-size: 14px !important;

    font-weight: 600 !important;

    box-sizing: border-box !important;
}


/* =========================================================
   CONTENEDOR DE TABLAS
   ========================================================= */

#contenido table {
    width: 100% !important;

    border-collapse: separate !important;

    border-spacing: 0 !important;

    background: #ffffff !important;

    border: 1px solid #dbe3ec !important;

    border-radius: 12px !important;

    overflow: hidden !important;

    box-shadow:
        0 3px 10px rgba(15, 23, 42, 0.05) !important;
}


/* Encabezado */
#contenido table thead th {
    padding: 13px 14px !important;

    background: #f1f5f9 !important;

    border-bottom: 1px solid #dbe3ec !important;

    color: #334155 !important;

    font-size: 12px !important;

    font-weight: 700 !important;

    line-height: 1.3 !important;

    text-align: left !important;

    white-space: nowrap !important;
}


/* Celdas */
#contenido table tbody td {
    padding: 13px 14px !important;

    border-bottom: 1px solid #edf2f7 !important;

    color: #334155 !important;

    font-size: 13.5px !important;

    line-height: 1.4 !important;

    vertical-align: middle !important;
}

#contenido table tbody tr:last-child td {
    border-bottom: 0 !important;
}

#contenido table tbody tr:hover td {
    background: #f8fafc !important;
}


/* =========================================================
   TABLA DE CITAS
   ========================================================= */

#contenido table th:first-child,
#contenido table td:first-child {
    white-space: nowrap !important;
}

#contenido table th:last-child,
#contenido table td:last-child {
    text-align: center !important;
}


/* =========================================================
   MENSAJE "NO HAY CITAS"
   ========================================================= */

#contenido table tbody td[colspan] {
    padding: 38px 20px !important;

    text-align: center !important;

    color: #64748b !important;

    font-size: 14px !important;

    line-height: 1.5 !important;
}


/* =========================================================
   BOTONES DENTRO DE TABLAS
   ========================================================= */

#contenido table .boton,
#contenido table a[class*="boton"],
#contenido table button {
    display: inline-flex !important;

    align-items: center !important;

    justify-content: center !important;

    min-height: 34px !important;

    padding: 7px 11px !important;

    margin: 2px !important;

    border-radius: 7px !important;

    font-size: 12px !important;

    line-height: 1.2 !important;

    white-space: nowrap !important;
}


/* =========================================================
   TARJETAS GENERALES DE PAGINAS
   ========================================================= */

#contenido .page-card,
#contenido .table-card,
#contenido .tabla-card,
#contenido .contenido-card {
    width: 100% !important;

    box-sizing: border-box !important;

    background: #ffffff !important;

    border: 1px solid #dbe3ec !important;

    border-radius: 14px !important;

    box-shadow:
        0 3px 10px rgba(15, 23, 42, 0.05) !important;

    overflow-x: auto !important;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1000px) {

    .dashboard-action-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;
    }
}

@media (max-width: 750px) {

    #contenido .page-head {
        flex-direction: column !important;

        align-items: stretch !important;
    }

    #contenido .page-head > div:last-child {
        width: 100% !important;
    }

    #contenido .page-head .boton,
    #contenido .page-head a[class*="boton"] {
        width: 100% !important;
    }

    #contenido table {
        min-width: 900px !important;
    }
}

@media (max-width: 600px) {

    .dashboard-action-grid {
        grid-template-columns: 1fr !important;
    }

    .dashboard-action,
    .quick-card {
        min-height: 0 !important;
    }
}

</style>

<!-- FIN EDUTURNOS_CITAS_ESTILO_V2 -->
"""

patron = re.compile(
    re.escape(INICIO)
    + r".*?"
    + re.escape(FIN),
    re.IGNORECASE | re.DOTALL
)

if patron.search(texto):
    texto = patron.sub(CSS.strip(), texto)
    print("ACTUALIZADO: diseño de Citas y accesos.")
else:
    posicion = texto.lower().find("</head>")

    if posicion == -1:
        print("[ERROR] No se encontró </head> en base.html")
        raise SystemExit(1)

    texto = (
        texto[:posicion]
        + "\n"
        + CSS
        + "\n"
        + texto[posicion:]
    )

    print("AGREGADO: diseño de Citas y accesos.")

ARCHIVO.write_text(texto, encoding="utf-8")

print()
print("=" * 65)
print("DISEÑO DE CITAS APLICADO")
print("=" * 65)
print()
print("Accesos del dashboard mejorados.")
print("Cabecera de Citas mejorada.")
print("Botón Nueva citación mejorado.")
print("Tabla organizada.")
print("Filas y columnas con mejor separación.")
print("Mensaje sin citas centrado.")
print("Botones de acciones uniformes.")
print("Diseño responsive.")
print()