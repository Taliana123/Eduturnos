from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "templates" / "base.html"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/base.html")
    raise SystemExit(1)

texto = ARCHIVO.read_text(encoding="utf-8")

INICIO = "<!-- EDUTURNOS_CITAS_INTERNO_ELEGANTE -->"
FIN = "<!-- FIN EDUTURNOS_CITAS_INTERNO_ELEGANTE -->"

CSS = r"""
<!-- EDUTURNOS_CITAS_INTERNO_ELEGANTE -->

<style id="eduturnos-citas-interno-elegante">

/* =========================================================
   CITAS - DISEÑO INTERNO ELEGANTE
   ========================================================= */

/* ---------------------------------------------------------
   ENCABEZADO DE LA PÁGINA DE CITAS
   --------------------------------------------------------- */

#contenido .page-head:has(a[href*="/citas/nueva"]) {
    position: relative !important;

    padding: 4px 4px 22px 4px !important;

    margin-bottom: 24px !important;

    border-bottom: 1px solid #e2e8f0 !important;
}

#contenido .page-head:has(a[href*="/citas/nueva"])
.page-navigation {
    margin-bottom: 14px !important;
}

#contenido .page-head:has(a[href*="/citas/nueva"])
.page-navigation .link-back {
    display: inline-flex !important;

    align-items: center !important;
    gap: 6px !important;

    color: #64748b !important;

    font-size: 13px !important;
    font-weight: 500 !important;

    text-decoration: none !important;
}

#contenido .page-head:has(a[href*="/citas/nueva"])
.page-navigation .link-back:hover {
    color: #2563eb !important;
}

/* Título */
#contenido .page-head:has(a[href*="/citas/nueva"]) h1 {
    position: relative !important;

    margin: 0 0 10px 0 !important;
    padding: 0 0 0 34px !important;

    color: #0f172a !important;

    font-size: 31px !important;
    font-weight: 750 !important;

    line-height: 1.15 !important;
}

/* Pequeño detalle visual delante del título */
#contenido .page-head:has(a[href*="/citas/nueva"]) h1::before {
    content: "✓";

    position: absolute;

    left: 0;
    top: 1px;

    width: 24px;
    height: 24px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 7px;

    background: #eaf2ff;

    color: #2563eb;

    font-size: 13px;
    font-weight: 800;
}

/* Descripción */
#contenido .page-head:has(a[href*="/citas/nueva"]) p {
    margin: 0 !important;
    padding-left: 34px !important;

    max-width: 720px !important;

    color: #64748b !important;

    font-size: 14px !important;

    line-height: 1.55 !important;
}

/* ---------------------------------------------------------
   BOTÓN NUEVA CITACIÓN
   --------------------------------------------------------- */

#contenido .page-head:has(a[href*="/citas/nueva"])
a[href*="/citas/nueva"] {

    display: inline-flex !important;

    align-items: center !important;
    justify-content: center !important;

    min-height: 46px !important;

    padding: 11px 17px !important;

    border-radius: 10px !important;

    font-size: 14px !important;
    font-weight: 700 !important;

    text-decoration: none !important;

    box-shadow:
        0 5px 12px rgba(37, 99, 235, 0.14) !important;

    transition:
        box-shadow 0.2s ease,
        transform 0.2s ease !important;
}

#contenido .page-head:has(a[href*="/citas/nueva"])
a[href*="/citas/nueva"]:hover {
    transform: translateY(-1px) !important;

    box-shadow:
        0 8px 18px rgba(37, 99, 235, 0.18) !important;
}


/* ---------------------------------------------------------
   ZONA DE LA TABLA
   --------------------------------------------------------- */

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table {
    margin-top: 2px !important;
}


/* ---------------------------------------------------------
   TABLA PRINCIPAL
   --------------------------------------------------------- */

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table {

    border: 1px solid #dbe4ee !important;

    border-radius: 14px !important;

    overflow: hidden !important;

    background: #ffffff !important;

    box-shadow:
        0 7px 20px rgba(15, 23, 42, 0.06) !important;
}

/* ---------------------------------------------------------
   ENCABEZADO DE TABLA
   --------------------------------------------------------- */

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table thead th {

    position: relative !important;

    padding: 14px 13px !important;

    background:
        linear-gradient(
            180deg,
            #f8fafc 0%,
            #f1f5f9 100%
        ) !important;

    border-bottom: 1px solid #dbe4ee !important;

    color: #334155 !important;

    font-size: 12px !important;

    font-weight: 750 !important;

    letter-spacing: 0.01em !important;

    text-align: left !important;

    white-space: nowrap !important;
}

/* Línea inferior decorativa */
#contenido .page-head:has(a[href*="/citas/nueva"])
~ table thead th:first-child {
    box-shadow:
        inset 3px 0 0 #2563eb !important;
}


/* ---------------------------------------------------------
   FILAS
   --------------------------------------------------------- */

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table tbody tr {

    transition:
        background-color 0.18s ease !important;
}

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table tbody tr:hover {

    background: #f8fbff !important;
}

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table tbody td {

    padding: 14px 13px !important;

    border-bottom: 1px solid #edf2f7 !important;

    color: #334155 !important;

    font-size: 13.5px !important;

    line-height: 1.4 !important;

    vertical-align: middle !important;
}

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table tbody tr:last-child td {

    border-bottom: 0 !important;
}


/* ---------------------------------------------------------
   MENSAJE CUANDO NO HAY CITAS
   --------------------------------------------------------- */

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table tbody td[colspan] {

    padding: 55px 24px !important;

    text-align: center !important;

    color: #64748b !important;

    font-size: 14px !important;

    line-height: 1.6 !important;

    background: #fbfdff !important;
}

/* Detalle visual */
#contenido .page-head:has(a[href*="/citas/nueva"])
~ table tbody td[colspan]::before {

    content: "✓";

    display: flex;

    align-items: center;
    justify-content: center;

    width: 42px;
    height: 42px;

    margin: 0 auto 12px;

    border-radius: 50%;

    background: #eef6ff;

    color: #2563eb;

    font-size: 18px;

    font-weight: 700;
}


/* ---------------------------------------------------------
   BOTONES DENTRO DE LA TABLA
   --------------------------------------------------------- */

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table .boton,
#contenido .page-head:has(a[href*="/citas/nueva"])
~ table a[class*="boton"],
#contenido .page-head:has(a[href*="/citas/nueva"])
~ table button {

    min-height: 34px !important;

    padding: 7px 10px !important;

    border-radius: 7px !important;

    font-size: 12px !important;

    font-weight: 600 !important;

    margin: 2px !important;

    white-space: nowrap !important;
}


/* ---------------------------------------------------------
   ESTADOS
   --------------------------------------------------------- */

#contenido .page-head:has(a[href*="/citas/nueva"])
~ table .estado,
#contenido .page-head:has(a[href*="/citas/nueva"])
~ table .badge {

    display: inline-flex !important;

    align-items: center !important;

    min-height: 27px !important;

    padding: 5px 9px !important;

    border-radius: 999px !important;

    font-size: 11px !important;

    font-weight: 700 !important;

    line-height: 1 !important;
}


/* ---------------------------------------------------------
   RESPONSIVE
   --------------------------------------------------------- */

@media (max-width: 850px) {

    #contenido .page-head:has(a[href*="/citas/nueva"]) {

        flex-direction: column !important;
        align-items: stretch !important;
    }

    #contenido .page-head:has(a[href*="/citas/nueva"])
    a[href*="/citas/nueva"] {

        width: 100% !important;
    }

    #contenido .page-head:has(a[href*="/citas/nueva"]) h1 {
        font-size: 27px !important;
    }

    #contenido .page-head:has(a[href*="/citas/nueva"]) p {
        padding-left: 0 !important;
    }

    #contenido .page-head:has(a[href*="/citas/nueva"]) h1::before {
        display: none;
    }

    #contenido .page-head:has(a[href*="/citas/nueva"])
    ~ table {

        display: block !important;

        overflow-x: auto !important;

        white-space: nowrap !important;
    }
}

</style>

<!-- FIN EDUTURNOS_CITAS_INTERNO_ELEGANTE -->
"""

# Reemplazar una versión anterior si existiera.
patron = re.compile(
    re.escape(INICIO) + r".*?" + re.escape(FIN),
    re.IGNORECASE | re.DOTALL
)

if patron.search(texto):
    texto = patron.sub(CSS.strip(), texto)
    print("ACTUALIZADO: diseño interno de Citas.")
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

    print("AGREGADO: diseño interno de Citas.")

ARCHIVO.write_text(
    texto,
    encoding="utf-8"
)

print()
print("=" * 65)
print("CITAS AHORA TIENE UN DISEÑO INTERNO MÁS ELEGANTE")
print("=" * 65)
print()
print("No se modificaron las rutas.")
print("No se modificaron las consultas.")
print("No se modificó MySQL.")
print("No se modificaron los botones funcionales.")
print()
print("Se mejoró:")
print("- título")
print("- descripción")
print("- botón Nueva citación")
print("- encabezado de tabla")
print("- filas")
print("- mensaje sin citas")
print("- botones")
print("- estados")
print("- responsive")
print()