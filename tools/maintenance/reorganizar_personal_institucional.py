from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "templates" / "base.html"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/base.html")
    raise SystemExit(1)

texto = ARCHIVO.read_text(encoding="utf-8")

MARCADOR_INICIO = "<!-- EDUTURNOS_PERSONAL_ORGANIZADO -->"
MARCADOR_FIN = "<!-- FIN EDUTURNOS_PERSONAL_ORGANIZADO -->"

ESTILO = r"""
<!-- EDUTURNOS_PERSONAL_ORGANIZADO -->
<style id="eduturnos-personal-organizado">

/* =========================================================
   PERSONAL INSTITUCIONAL - ORGANIZACIÓN DEFINITIVA
   ========================================================= */

/* Tarjeta principal */
#contenido .formulario .form-card {
    width: 100% !important;
    max-width: 1050px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Bloque completo de Personal institucional */
#contenido .personal-login {
    display: block !important;

    width: 100% !important;
    max-width: 100% !important;

    margin: 0 !important;
    padding: 24px !important;

    box-sizing: border-box !important;

    border: 1px solid #d7e0ea !important;
    border-radius: 12px !important;

    background: #f8fafc !important;

    overflow: visible !important;
}

/* Título */
#contenido .personal-login h3 {
    display: block !important;

    width: 100% !important;

    margin: 0 0 8px 0 !important;
    padding: 0 !important;

    line-height: 1.25 !important;
}

/* Texto explicativo */
#contenido .personal-login > p {
    display: block !important;

    width: 100% !important;

    margin: 0 0 22px 0 !important;
    padding: 0 !important;

    line-height: 1.5 !important;
}

/* =========================================================
   CÓDIGO | SEDE | JORNADA
   ========================================================= */

#contenido .personal-login .form-grid {
    display: grid !important;

    grid-template-columns:
        minmax(0, 1fr)
        minmax(0, 1.35fr)
        minmax(0, 1fr) !important;

    gap: 18px !important;

    width: 100% !important;
    max-width: 100% !important;

    margin: 0 !important;
    padding: 0 !important;

    box-sizing: border-box !important;

    align-items: start !important;
}

/* Cada campo */
#contenido .personal-login .form-grid > label {
    display: flex !important;

    flex-direction: column !important;

    align-items: stretch !important;

    width: 100% !important;
    min-width: 0 !important;

    margin: 0 !important;
    padding: 0 !important;

    gap: 7px !important;

    box-sizing: border-box !important;

    font-size: 14px !important;
    font-weight: 600 !important;

    line-height: 1.35 !important;
}

/* Cuadros */
#contenido .personal-login .form-grid input,
#contenido .personal-login .form-grid select {
    display: block !important;

    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;

    min-height: 46px !important;

    margin: 0 !important;

    padding: 11px 13px !important;

    box-sizing: border-box !important;

    border-radius: 9px !important;

    font-size: 14px !important;
    font-weight: 400 !important;

    line-height: 1.25 !important;

    background: #ffffff !important;
}

/* Sede: más espacio para nombres largos */
#contenido .personal-login .form-grid > label:nth-child(2) select {
    font-size: 13px !important;
}

/* Jornada queda siempre dentro de su columna */
#contenido .personal-login .form-grid > label:nth-child(3) {
    width: 100% !important;
    min-width: 0 !important;
}

/* Evitar que el texto provoque desbordamiento */
#contenido .personal-login .form-grid > label:nth-child(2) select,
#contenido .personal-login .form-grid > label:nth-child(3) select {
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

/* El código también permanece dentro */
#contenido .personal-login .form-grid > label:nth-child(1) {
    min-width: 0 !important;
}

/* =========================================================
   BOTÓN
   ========================================================= */

#contenido .personal-login + * {
    box-sizing: border-box !important;
}

/* =========================================================
   PANTALLAS MEDIANAS
   ========================================================= */

@media (max-width: 900px) {

    #contenido .formulario .form-card {
        max-width: 100% !important;
    }

    #contenido .personal-login .form-grid {
        grid-template-columns:
            minmax(0, 1fr)
            minmax(0, 1.4fr)
            minmax(0, 1fr) !important;

        gap: 14px !important;
    }

    #contenido .personal-login .form-grid > label:nth-child(2) select {
        font-size: 12px !important;
    }
}

/* =========================================================
   CELULAR
   ========================================================= */

@media (max-width: 700px) {

    #contenido .personal-login {
        padding: 18px !important;
    }

    #contenido .personal-login .form-grid {
        grid-template-columns: 1fr !important;

        gap: 16px !important;
    }

    #contenido .personal-login .form-grid > label:nth-child(2) select {
        font-size: 14px !important;
    }
}

</style>
<!-- FIN EDUTURNOS_PERSONAL_ORGANIZADO -->
"""

# Si ya existe una versión anterior, reemplazarla.
patron = re.compile(
    re.escape(MARCADOR_INICIO)
    + r".*?"
    + re.escape(MARCADOR_FIN),
    re.IGNORECASE | re.DOTALL
)

if patron.search(texto):
    texto = patron.sub(ESTILO.strip(), texto)
    print("ACTUALIZADO: organización de Personal institucional.")
else:
    posicion = texto.lower().find("</head>")

    if posicion == -1:
        print("[ERROR] No se encontró </head> en base.html")
        raise SystemExit(1)

    texto = (
        texto[:posicion]
        + "\n"
        + ESTILO
        + "\n"
        + texto[posicion:]
    )

    print("AGREGADO: organización de Personal institucional.")

ARCHIVO.write_text(
    texto,
    encoding="utf-8"
)

print()
print("=" * 65)
print("PERSONAL INSTITUCIONAL REORGANIZADO")
print("=" * 65)
print()
print("Código, Sede y Jornada están dentro de la misma tarjeta.")
print("Los tres quedan alineados.")
print("Jornada no debería salir del cuadro.")
print("Sede recibe más espacio.")
print("El diseño se adapta a pantallas pequeñas.")
print()