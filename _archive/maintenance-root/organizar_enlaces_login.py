from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "templates" / "base.html"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/base.html")
    raise SystemExit(1)

texto = ARCHIVO.read_text(encoding="utf-8")

MARCADOR_INICIO = "<!-- EDUTURNOS_ENLACES_LOGIN -->"
MARCADOR_FIN = "<!-- FIN EDUTURNOS_ENLACES_LOGIN -->"

CSS = r"""
<!-- EDUTURNOS_ENLACES_LOGIN -->

<style id="eduturnos-enlaces-login">

/* =========================================================
   ENLACES INFERIORES DEL LOGIN
   ========================================================= */

#contenido .form-links {
    width: 100% !important;

    display: flex !important;

    align-items: center !important;

    justify-content: space-between !important;

    gap: 20px !important;

    margin-top: 20px !important;

    padding: 0 !important;

    box-sizing: border-box !important;
}

#contenido .form-links a {
    display: inline-block !important;

    margin: 0 !important;
    padding: 0 !important;

    font-size: 14px !important;
    font-weight: 400 !important;

    line-height: 1.4 !important;

    white-space: nowrap !important;
}

#contenido .form-links a:first-child {
    text-align: left !important;
}

#contenido .form-links a:last-child {
    text-align: right !important;
}

@media (max-width: 600px) {

    #contenido .form-links {
        flex-direction: column !important;

        align-items: stretch !important;

        gap: 10px !important;
    }

    #contenido .form-links a:first-child,
    #contenido .form-links a:last-child {
        text-align: center !important;
    }
}

</style>

<!-- FIN EDUTURNOS_ENLACES_LOGIN -->
"""

patron = re.compile(
    re.escape(MARCADOR_INICIO)
    + r".*?"
    + re.escape(MARCADOR_FIN),
    re.IGNORECASE | re.DOTALL
)

if patron.search(texto):
    texto = patron.sub(CSS.strip(), texto)
    print("ACTUALIZADO: enlaces del login.")
else:
    posicion = texto.lower().find("</head>")

    if posicion == -1:
        print("[ERROR] No se encontró </head>")
        raise SystemExit(1)

    texto = (
        texto[:posicion]
        + "\n"
        + CSS
        + "\n"
        + texto[posicion:]
    )

    print("AGREGADO: organización de enlaces del login.")

ARCHIVO.write_text(
    texto,
    encoding="utf-8"
)

print()
print("=" * 60)
print("ENLACES ORGANIZADOS")
print("=" * 60)
print()
print("Un enlace quedará a la izquierda.")
print("El otro quedará a la derecha.")
print("En celular se colocarán uno debajo del otro.")