from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "templates" / "base.html"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/base.html")
    raise SystemExit(1)

texto = ARCHIVO.read_text(encoding="utf-8")

MARCADOR = "EDUTURNOS_AJUSTE_SEDE_COMPLETA"

CSS = r"""
<!-- EDUTURNOS_AJUSTE_SEDE_COMPLETA -->
<style id="eduturnos-ajuste-sede">

/* =========================================================
   EDUTURNOS - SEDE SIN TEXTO CORTADO
   ========================================================= */

/* Hacer más ancha la tarjeta donde están los tres campos */
#contenido .form-card {
    max-width: 1050px !important;
}

/* Código | Sede | Jornada */
#contenido .personal-login .form-grid {
    display: grid !important;

    grid-template-columns:
        200px minmax(360px, 1fr) 190px !important;

    column-gap: 20px !important;
    row-gap: 20px !important;

    width: 100% !important;
}

/* Sede */
#contenido .personal-login .form-grid > label:nth-child(2) {
    min-width: 0 !important;
    width: 100% !important;
}

/* El cuadro de Sede debe ocupar todo el espacio disponible */
#contenido .personal-login .form-grid > label:nth-child(2) select {
    width: 100% !important;
    min-width: 0 !important;

    padding-left: 12px !important;
    padding-right: 12px !important;

    font-size: 14px !important;
    font-weight: 400 !important;

    white-space: nowrap !important;
}

/* También mejora el campo de Jornada */
#contenido .personal-login .form-grid > label:nth-child(3) select {
    width: 100% !important;
    min-width: 0 !important;

    font-size: 14px !important;
    font-weight: 400 !important;
}

/* Código */
#contenido .personal-login .form-grid > label:nth-child(1) input {
    width: 100% !important;
    min-width: 0 !important;
}

/* En pantallas medianas se distribuyen mejor */
@media (max-width: 950px) {

    #contenido .personal-login .form-grid {
        grid-template-columns:
            1fr 1.5fr 1fr !important;
    }

}

/* En móvil, una debajo de otra */
@media (max-width: 650px) {

    #contenido .form-card {
        max-width: 100% !important;
    }

    #contenido .personal-login .form-grid {
        grid-template-columns: 1fr !important;
    }

}

</style>
<!-- FIN EDUTURNOS_AJUSTE_SEDE_COMPLETA -->
"""

# Si ya existe una versión anterior, reemplazarla.
patron = re.compile(
    r'<!-- EDUTURNOS_AJUSTE_SEDE_COMPLETA -->.*?'
    r'<!-- FIN EDUTURNOS_AJUSTE_SEDE_COMPLETA -->',
    re.IGNORECASE | re.DOTALL
)

if patron.search(texto):
    texto = patron.sub(CSS.strip(), texto)
    print("ACTUALIZADO: ajuste anterior de Sede.")
else:
    pos = texto.lower().find("</head>")

    if pos == -1:
        print("[ERROR] No se encontró </head> en base.html")
        raise SystemExit(1)

    texto = (
        texto[:pos]
        + "\n"
        + CSS
        + "\n"
        + texto[pos:]
    )

    print("AGREGADO: ajuste de Sede.")

ARCHIVO.write_text(
    texto,
    encoding="utf-8"
)

print()
print("=" * 60)
print("SEDE AJUSTADA")
print("=" * 60)
print()
print("La tarjeta ahora puede ser más ancha.")
print("La columna de Sede tiene más espacio.")
print("Los nombres largos tendrán mayor área visible.")
print("Código, Sede y Jornada continúan alineados.")
print()