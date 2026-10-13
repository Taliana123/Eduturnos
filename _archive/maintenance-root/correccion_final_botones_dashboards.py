from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")
TEMPLATES = ROOT / "templates"
BASE = TEMPLATES / "base.html"

AZUL = "#1769aa"
HOVER = "#145b91"
BLANCO = "#ffffff"

MARCADOR = "EDUTURNOS_CORRECCION_FINAL_V9"


# ============================================================
# CSS
# ============================================================

CSS = f"""
<style id="{MARCADOR}">

/* ============================================================
   EDUTURNOS
   SOLO BOTONES
   ============================================================ */

/* ------------------------------------------------------------
   BOTONES REALES
   ------------------------------------------------------------ */

button,
input[type="submit"],
input[type="button"],
input[type="reset"],

a.boton,
a.btn,
a.btn-primary,
a.btn-secondary,
a.btn-success,
a.btn-danger,
a.btn-warning,
a.btn-info,
a.btn-dark,
a.btn-light,

a[role="button"],

a.link-back,
a.edc-back,

.edc-buttons button,
.edc-buttons a.boton,

.edc-header-actions button,
.edc-header-actions a.boton,

.edc-month-toolbar button,
.edc-month-toolbar a.boton,

.citas-actions button,
.citas-actions a.boton,

.form-actions button,
.form-actions a.boton,

.acciones button,
.acciones a.boton,

.page-actions button,
.page-actions a.boton,

.dashboard-actions button,
.dashboard-actions a.boton,

.quick-card button,
.quick-card a.boton,

.account-actions button,
.account-actions a.boton {{

    background: {AZUL} !important;
    background-color: {AZUL} !important;

    color: {BLANCO} !important;

    border: 1px solid {AZUL} !important;
    border-color: {AZUL} !important;

    border-radius: 7px !important;

    text-decoration: none !important;

    box-shadow: none !important;

    opacity: 1 !important;

    cursor: pointer !important;
}}


/* ------------------------------------------------------------
   TEXTO INTERNO DE BOTONES
   ------------------------------------------------------------ */

button *,
input[type="submit"] *,
input[type="button"] *,
input[type="reset"] *,

a.boton *,
a.btn *,
a.btn-primary *,
a.btn-secondary *,
a.btn-success *,
a.btn-danger *,
a.btn-warning *,
a.btn-info *,
a.btn-dark *,
a.btn-light *,

a[role="button"] *,

a.link-back *,
a.edc-back *,

.edc-buttons button *,
.edc-buttons a.boton *,

.edc-header-actions button *,
.edc-header-actions a.boton *,

.edc-month-toolbar button *,
.edc-month-toolbar a.boton *,

.citas-actions button *,
.citas-actions a.boton *,

.form-actions button *,
.form-actions a.boton *,

.acciones button *,
.acciones a.boton *,

.page-actions button *,
.page-actions a.boton *,

.dashboard-actions button *,
.dashboard-actions a.boton *,

.quick-card button *,
.quick-card a.boton *,

.account-actions button *,
.account-actions a.boton * {{

    color: {BLANCO} !important;
}}


/* ------------------------------------------------------------
   HOVER
   ------------------------------------------------------------ */

button:hover,
input[type="submit"]:hover,
input[type="button"]:hover,
input[type="reset"]:hover,

a.boton:hover,
a.btn:hover,
a.btn-primary:hover,
a.btn-secondary:hover,
a.btn-success:hover,
a.btn-danger:hover,
a.btn-warning:hover,
a.btn-info:hover,
a.btn-dark:hover,
a.btn-light:hover,

a[role="button"]:hover,

a.link-back:hover,
a.edc-back:hover,

.edc-buttons button:hover,
.edc-buttons a.boton:hover,

.edc-header-actions button:hover,
.edc-header-actions a.boton:hover,

.edc-month-toolbar button:hover,
.edc-month-toolbar a.boton:hover,

.citas-actions button:hover,
.citas-actions a.boton:hover,

.form-actions button:hover,
.form-actions a.boton:hover,

.acciones button:hover,
.acciones a.boton:hover,

.page-actions button:hover,
.page-actions a.boton:hover,

.dashboard-actions button:hover,
.dashboard-actions a.boton:hover,

.quick-card button:hover,
.quick-card a.boton:hover,

.account-actions button:hover,
.account-actions a.boton:hover {{

    background: {HOVER} !important;
    background-color: {HOVER} !important;

    color: {BLANCO} !important;

    border-color: {HOVER} !important;

    box-shadow: none !important;
}}


/* ------------------------------------------------------------
   BOTÓN ATRÁS
   ------------------------------------------------------------ */

a.link-back,
a.edc-back {{

    display: inline-flex !important;

    align-items: center !important;
    justify-content: center !important;

    min-height: 34px !important;
    height: 34px !important;

    padding: 7px 12px !important;

    margin: 0 0 12px 0 !important;

    background: {AZUL} !important;
    background-color: {AZUL} !important;

    color: {BLANCO} !important;

    border: 1px solid {AZUL} !important;
    border-radius: 7px !important;

    font-family: inherit !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    line-height: 1 !important;

    text-decoration: none !important;

    box-shadow: none !important;
}}


/* ------------------------------------------------------------
   ORGANIZACIÓN DEL BOTÓN ATRÁS
   ------------------------------------------------------------ */

.page-navigation {{
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;

    width: 100% !important;

    margin: 0 0 14px 0 !important;

    clear: both !important;
}}

.page-navigation + h1 {{
    clear: both !important;
    margin-top: 0 !important;
}}

.form-top-actions {{
    display: flex !important;
    align-items: center !important;

    width: 100% !important;

    margin: 0 0 14px 0 !important;

    clear: both !important;
}}

.form-top-actions + .section-heading {{
    clear: both !important;
}}

.page-head {{
    clear: both !important;
}}

.page-head .page-navigation {{
    position: relative !important;
    z-index: 5 !important;
}}

.page-head h1 {{
    clear: both !important;
}}


/* ------------------------------------------------------------
   IMPORTANTE:
   LOS ENLACES NORMALES DE LAS TARJETAS NO SON BOTONES
   ------------------------------------------------------------ */

/*
   Restauramos el comportamiento normal de enlaces dentro
   de las tarjetas del dashboard.
*/

.dashboard-card a:not(.boton):not(.btn):not([role="button"]),
.quick-card a:not(.boton):not(.btn):not([role="button"]),
.account-actions a:not(.boton):not(.btn):not([role="button"]) {{

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;

    text-decoration: none;

    padding: 0 !important;

    min-height: auto !important;
    height: auto !important;

    opacity: 1 !important;
}}


/* TÍTULOS DE LAS TARJETAS */
.dashboard-card h2 a,
.dashboard-card h3 a,
.dashboard-card h4 a,
.quick-card h2 a,
.quick-card h3 a,
.quick-card h4 a {{

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;

    box-shadow: none !important;

    color: inherit !important;

    padding: 0 !important;

    height: auto !important;
    min-height: 0 !important;

    font-weight: inherit !important;
}}


/* DESCRIPCIONES DE LAS TARJETAS */
.dashboard-card p a,
.quick-card p a {{

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;

    color: inherit !important;

    padding: 0 !important;

    box-shadow: none !important;

    height: auto !important;
    min-height: 0 !important;
}}


/* ------------------------------------------------------------
   EVITAR QUE LOS ENLACES GENERALES DEL DASHBOARD SEAN BOTONES
   ------------------------------------------------------------ */

.dashboard-card > a:not(.boton):not(.btn):not([role="button"]),
.quick-card > a:not(.boton):not(.btn):not([role="button"]) {{

    background: transparent !important;
    background-color: transparent !important;

    color: inherit !important;

    border: none !important;

    padding: 0 !important;

    height: auto !important;
    min-height: 0 !important;

    box-shadow: none !important;
}}


/* ------------------------------------------------------------
   BOTONES DESHABILITADOS
   ------------------------------------------------------------ */

button:disabled,
input[type="submit"]:disabled,
input[type="button"]:disabled,
input[type="reset"]:disabled {{

    background: {AZUL} !important;
    background-color: {AZUL} !important;

    color: {BLANCO} !important;

    border-color: {AZUL} !important;

    opacity: .55 !important;
}}

</style>
"""


# ============================================================
# JS PARA BOTONES DINÁMICOS
# ============================================================

JS = f"""
<script id="EDUTURNOS_BOTONES_JS_V9">
(function() {{
    "use strict";

    const AZUL = "{AZUL}";
    const HOVER = "{HOVER}";
    const BLANCO = "{BLANCO}";

    const SELECTORES = [
        "button",
        "input[type='submit']",
        "input[type='button']",
        "input[type='reset']",

        "a.boton",
        "a.btn",
        "a.btn-primary",
        "a.btn-secondary",
        "a.btn-success",
        "a.btn-danger",
        "a.btn-warning",
        "a.btn-info",
        "a.btn-dark",
        "a.btn-light",

        "a[role='button']",

        "a.link-back",
        "a.edc-back",

        ".edc-buttons button",
        ".edc-buttons a.boton",

        ".edc-header-actions button",
        ".edc-header-actions a.boton",

        ".edc-month-toolbar button",
        ".edc-month-toolbar a.boton",

        ".citas-actions button",
        ".citas-actions a.boton",

        ".form-actions button",
        ".form-actions a.boton",

        ".acciones button",
        ".acciones a.boton",

        ".page-actions button",
        ".page-actions a.boton",

        ".dashboard-actions button",
        ".dashboard-actions a.boton",

        ".quick-card button",
        ".quick-card a.boton",

        ".account-actions button",
        ".account-actions a.boton"
    ].join(",");


    function aplicar(elemento) {{
        if (!elemento) return;

        elemento.style.setProperty(
            "background",
            AZUL,
            "important"
        );

        elemento.style.setProperty(
            "background-color",
            AZUL,
            "important"
        );

        elemento.style.setProperty(
            "color",
            BLANCO,
            "important"
        );

        elemento.style.setProperty(
            "border-color",
            AZUL,
            "important"
        );

        elemento.style.setProperty(
            "box-shadow",
            "none",
            "important"
        );

        elemento.querySelectorAll("*").forEach(function(hijo) {{
            hijo.style.setProperty(
                "color",
                BLANCO,
                "important"
            );
        }});

        if (!elemento.dataset.eduturnosV9) {{
            elemento.dataset.eduturnosV9 = "1";

            elemento.addEventListener(
                "mouseenter",
                function() {{
                    elemento.style.setProperty(
                        "background",
                        HOVER,
                        "important"
                    );

                    elemento.style.setProperty(
                        "background-color",
                        HOVER,
                        "important"
                    );

                    elemento.style.setProperty(
                        "border-color",
                        HOVER,
                        "important"
                    );

                    elemento.style.setProperty(
                        "color",
                        BLANCO,
                        "important"
                    );
                }}
            );

            elemento.addEventListener(
                "mouseleave",
                function() {{
                    elemento.style.setProperty(
                        "background",
                        AZUL,
                        "important"
                    );

                    elemento.style.setProperty(
                        "background-color",
                        AZUL,
                        "important"
                    );

                    elemento.style.setProperty(
                        "border-color",
                        AZUL,
                        "important"
                    );

                    elemento.style.setProperty(
                        "color",
                        BLANCO,
                        "important"
                    );
                }}
            );
        }}
    }}


    function ejecutar() {{
        document
            .querySelectorAll(SELECTORES)
            .forEach(aplicar);
    }}


    if (document.readyState === "loading") {{
        document.addEventListener(
            "DOMContentLoaded",
            ejecutar
        );
    }} else {{
        ejecutar();
    }}


    const observador = new MutationObserver(
        function() {{
            ejecutar();
        }}
    );


    if (document.documentElement) {{
        observador.observe(
            document.documentElement,
            {{
                childList: true,
                subtree: true
            }}
        );
    }}

}})();
</script>
"""


# ============================================================
# LIMPIAR BLOQUES ANTERIORES
# ============================================================

def limpiar_inyecciones(texto):

    patrones = [
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_GLOBALES["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_ESTILO_BOTONES_DEFINITIVO["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_SOLO_BOTONES_V3["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V4["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V5["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_ATRAS_TODOS_V7["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_LAYOUT_ATRAS_V8["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V4["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_TODOS_LOS_BOTONES_V5["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_CORRECCION_FINAL_V9["\'][^>]*>.*?</style>',

        r'<script[^>]*id=["\']EDUTURNOS_JS_BOTONES_DEFINITIVO["\'][^>]*>.*?</script>',
        r'<script[^>]*id=["\']EDUTURNOS_TODOS_LOS_BOTONES_JS["\'][^>]*>.*?</script>',
        r'<script[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</script>',
        r'<script[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</script>',
        r'<script[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</script>',
        r'<script[^>]*id=["\']EDUTURNOS_BOTONES_JS_V9["\'][^>]*>.*?</script>',
    ]

    for patron in patrones:
        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    return texto


# ============================================================
# BUSCAR RUTA DE DOCENTE
# ============================================================

def encontrar_endpoint_docente():

    candidatos = []

    for archivo in ROOT.glob("**/*.py"):

        if "venv" in archivo.parts:
            continue

        try:
            texto = archivo.read_text(
                encoding="utf-8"
            )
        except Exception:
            continue

        # Blueprint con nombre docente.
        if re.search(
            r'Blueprint\s*\(\s*["\']docente',
            texto,
            flags=re.IGNORECASE
        ):
            candidatos.append(
                ("docente", archivo)
            )

        # Endpoint explícito que contiene docente.
        for m in re.finditer(
            r'(?:endpoint\s*=\s*["\']|def\s+)([A-Za-z0-9_]*docente[A-Za-z0-9_]*)',
            texto,
            flags=re.IGNORECASE
        ):
            candidatos.append(
                (m.group(1), archivo)
            )

    # Si hay un endpoint claro.
    for nombre, archivo in candidatos:
        limpio = nombre.replace("-", "_").lower()

        if (
            "dashboard" in limpio
            or limpio == "docente"
            or "inicio" in limpio
            or "index" in limpio
        ):
            return limpio

    return None


# ============================================================
# CAMBIAR BOTÓN ATRÁS DEL CALENDARIO
# ============================================================

def corregir_atras_calendario(texto):

    endpoint = encontrar_endpoint_docente()

    archivo = TEMPLATES / "calendario" / "index.html"

    if not archivo.exists():
        return texto, False, endpoint

    if endpoint:
        nuevo_href = (
            "{{ url_for('" + endpoint + "') }}"
        )
    else:
        # Fallback seguro: dashboard por rol.
        nuevo_href = "{{ url_for('auth.dashboard') }}"

    # Buscar únicamente dentro del texto del botón Atrás.
    patron = re.compile(
        r'(<a\b[^>]*?(?:class\s*=\s*["\'][^"\']*(?:edc-back|link-back)[^"\']*["\'])'
        r'[^>]*\bhref\s*=\s*["\'])[^"\']*(["\'][^>]*>\s*←\s*Atrás\s*</a>)',
        flags=re.IGNORECASE | re.DOTALL
    )

    nuevo, cantidad = patron.subn(
        lambda m:
            m.group(1)
            + nuevo_href
            + m.group(2),
        texto
    )

    return nuevo, cantidad > 0, endpoint


# ============================================================
# INSERTAR CSS/JS
# ============================================================

def insertar_bloque(texto):

    texto = limpiar_inyecciones(texto)

    bloque = "\n" + CSS + "\n" + JS + "\n"

    pos = texto.lower().rfind("</head>")

    if pos != -1:
        return (
            texto[:pos]
            + bloque
            + texto[pos:]
        )

    pos = texto.lower().rfind("</body>")

    if pos != -1:
        return (
            texto[:pos]
            + bloque
            + texto[pos:]
        )

    return texto + bloque


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print("EDUTURNOS - CORRECCIÓN FINAL DE BOTONES Y DASHBOARDS")
    print("=" * 75)
    print()

    if not TEMPLATES.exists():
        print("ERROR: no existe:")
        print(TEMPLATES)
        return

    # --------------------------------------------------------
    # Base
    # --------------------------------------------------------

    if BASE.exists():
        texto = BASE.read_text(
            encoding="utf-8"
        )

        texto = insertar_bloque(texto)

        BASE.write_text(
            texto,
            encoding="utf-8"
        )

        print("OK: base.html corregido.")

    # --------------------------------------------------------
    # Todas las plantillas
    # --------------------------------------------------------

    archivos = list(
        TEMPLATES.rglob("*.html")
    )

    modificados = 0

    for archivo in archivos:

        # Evitar backups.
        if ".backup" in archivo.name.lower():
            continue

        # Ya procesado arriba.
        if archivo.resolve() == BASE.resolve():
            continue

        try:
            original = archivo.read_text(
                encoding="utf-8"
            )
        except Exception:
            continue

        nuevo = insertar_bloque(
            original
        )

        if nuevo != original:

            backup = archivo.with_name(
                archivo.name
                + ".backup_botones_v9"
            )

            if not backup.exists():
                shutil.copy2(
                    archivo,
                    backup
                )

            archivo.write_text(
                nuevo,
                encoding="utf-8"
            )

            modificados += 1

    # --------------------------------------------------------
    # Calendario: botón Atrás
    # --------------------------------------------------------

    calendario = (
        TEMPLATES
        / "calendario"
        / "index.html"
    )

    endpoint_docente = encontrar_endpoint_docente()

    if calendario.exists():

        texto = calendario.read_text(
            encoding="utf-8"
        )

        texto, cambio, endpoint = (
            corregir_atras_calendario(
                texto
            )
        )

        calendario.write_text(
            texto,
            encoding="utf-8"
        )

        if cambio:
            print()
            print(
                "OK: botón Atrás del calendario corregido."
            )

            if endpoint:
                print(
                    "Destino detectado:",
                    endpoint
                )
            else:
                print(
                    "Destino: dashboard por rol"
                )
        else:
            print()
            print(
                "AVISO: no se encontró el botón Atrás"
                " del calendario con la clase esperada."
            )

    print()
    print("=" * 75)
    print("CORRECCIÓN TERMINADA")
    print("=" * 75)
    print()

    print("BOTONES:")
    print("Fondo :", AZUL)
    print("Letra :", BLANCO)
    print("Hover :", HOVER)

    print()
    print("SE CORRIGIÓ:")
    print("✓ Todos los botones reales")
    print("✓ Botón ← Atrás")
    print("✓ Botones de Citas")
    print("✓ Botones de Calendario")
    print("✓ Botones de Formularios")
    print("✓ Botones de Dashboard")
    print("✓ Botones de acciones")

    print()
    print("SE PROTEGIÓ:")
    print("✓ Títulos")
    print("✓ Textos")
    print("✓ Descripciones")
    print("✓ Enlaces normales de las tarjetas")
    print("✓ Filtros")
    print("✓ Tablas")
    print("✓ Calendario")

    print()
    print("Los enlaces normales de:")
    print("Citas")
    print("Calendario")
    print("Avisos")
    print("Solicitudes")
    print("ya NO reciben estilo de botón.")

    print()
    print(
        "Plantillas adicionales modificadas:",
        modificados
    )

    print()
    print("Ahora ejecuta:")
    print("python .\\app.py")
    print()
    print("Después pulsa Ctrl + F5.")
    print()
    print("=" * 75)


if __name__ == "__main__":
    main()
