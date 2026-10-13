from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")
TEMPLATES = ROOT / "templates"

AZUL = "#1769aa"
AZUL_HOVER = "#145b91"
BLANCO = "#ffffff"

MARCADOR_CSS = "EDUTURNOS_BOTONES_REALES_V6"


# ------------------------------------------------------------
# ESTILO DIRECTO PARA ELEMENTOS QUE SON BOTONES
# ------------------------------------------------------------
ESTILO = (
    f"background:{AZUL} !important;"
    f"background-color:{AZUL} !important;"
    f"color:{BLANCO} !important;"
    f"border-color:{AZUL} !important;"
    f"text-decoration:none !important;"
    f"box-shadow:none !important;"
    f"opacity:1 !important;"
    f"cursor:pointer !important;"
)


# ------------------------------------------------------------
# SELECTORES JS
# ------------------------------------------------------------
JS = f"""
<script id="EDUTURNOS_BOTONES_REALES_V6">
(function() {{
    "use strict";

    const azul = "{AZUL}";
    const hover = "{AZUL_HOVER}";
    const blanco = "{BLANCO}";

    const selectores = [
        "button",
        "input[type='submit']",
        "input[type='button']",
        "input[type='reset']",

        "a.boton",
        "a.btn",
        "a[class*='boton']",
        "a[class*='button']",
        "a[class*='btn-']",
        "a[class*='accion']",
        "a[class*='action']",
        "a[role='button']",

        "a.link-back",
        "a.edc-back",

        ".edc-header-actions a",
        ".edc-header-actions button",

        ".edc-buttons a",
        ".edc-buttons button",

        ".edc-month-toolbar a",
        ".edc-month-toolbar button",

        ".citas-actions a",
        ".citas-actions button",

        ".form-actions a",
        ".form-actions button",

        ".acciones a",
        ".acciones button",

        ".page-actions a",
        ".page-actions button",

        ".dashboard-actions a",
        ".dashboard-actions button",

        ".account-actions a",
        ".account-actions button",

        ".quick-card a.boton",
        ".quick-card button",

        ".dashboard-card a.boton",
        ".dashboard-card button"
    ].join(",");


    function aplicar(elemento) {{
        if (!elemento) return;

        elemento.style.setProperty(
            "background",
            azul,
            "important"
        );

        elemento.style.setProperty(
            "background-color",
            azul,
            "important"
        );

        elemento.style.setProperty(
            "color",
            blanco,
            "important"
        );

        elemento.style.setProperty(
            "border-color",
            azul,
            "important"
        );

        elemento.style.setProperty(
            "text-decoration",
            "none",
            "important"
        );

        elemento.style.setProperty(
            "box-shadow",
            "none",
            "important"
        );

        elemento.style.setProperty(
            "opacity",
            "1",
            "important"
        );

        elemento.querySelectorAll("*").forEach(function(hijo) {{
            hijo.style.setProperty(
                "color",
                blanco,
                "important"
            );
        }});

        if (!elemento.dataset.eduturnosBotonV6) {{
            elemento.dataset.eduturnosBotonV6 = "1";

            elemento.addEventListener("mouseenter", function() {{
                elemento.style.setProperty(
                    "background",
                    hover,
                    "important"
                );

                elemento.style.setProperty(
                    "background-color",
                    hover,
                    "important"
                );

                elemento.style.setProperty(
                    "border-color",
                    hover,
                    "important"
                );

                elemento.style.setProperty(
                    "color",
                    blanco,
                    "important"
                );
            }});

            elemento.addEventListener("mouseleave", function() {{
                elemento.style.setProperty(
                    "background",
                    azul,
                    "important"
                );

                elemento.style.setProperty(
                    "background-color",
                    azul,
                    "important"
                );

                elemento.style.setProperty(
                    "border-color",
                    azul,
                    "important"
                );

                elemento.style.setProperty(
                    "color",
                    blanco,
                    "important"
                );
            }});
        }}
    }}


    function buscarBotonesPorTexto() {{
        document.querySelectorAll("a").forEach(function(a) {{
            const texto = (a.textContent || "")
                .trim()
                .toLowerCase();

            const href = (a.getAttribute("href") || "")
                .toLowerCase();

            const palabras = [
                "atrás",
                "atras",
                "nueva citación",
                "nueva cita",
                "ver citas",
                "filtrar",
                "limpiar",
                "editar",
                "eliminar",
                "confirmar",
                "cancelar",
                "reprogramar",
                "descargar",
                "exportar",
                "importar",
                "guardar",
                "enviar",
                "volver",
                "marcar",
                "crear",
                "solicitar"
            ];

            const coincideTexto = palabras.some(function(p) {{
                return texto === p || texto.includes(p);
            }});

            const coincideRuta =
                href.includes("/citas/") ||
                href.includes("/calendario") ||
                href.includes("/notificaciones/") ||
                href.includes("/solicitudes/") ||
                href.includes("/reportes/") ||
                href.includes("/usuarios/") ||
                href.includes("/auth/recuperar");

            const contenedor = a.closest(
                ".edc-header-actions," +
                ".edc-buttons," +
                ".edc-month-toolbar," +
                ".citas-actions," +
                ".form-actions," +
                ".acciones," +
                ".page-actions," +
                ".dashboard-actions," +
                ".dashboard-card," +
                ".quick-card," +
                ".account-actions"
            );

            if (coincideTexto || coincideRuta || contenedor) {{
                aplicar(a);
            }}
        }});
    }}


    function ejecutar() {{
        document.querySelectorAll(selectores).forEach(aplicar);
        buscarBotonesPorTexto();
    }}


    if (document.readyState === "loading") {{
        document.addEventListener("DOMContentLoaded", ejecutar);
    }} else {{
        ejecutar();
    }}


    const observador = new MutationObserver(function() {{
        ejecutar();
    }});

    observador.observe(document.documentElement, {{
        childList: true,
        subtree: true
    }});

}})();
</script>
"""


# ------------------------------------------------------------
# LIMPIAR VERSIONES ANTERIORES DE NUESTROS SCRIPTS
# ------------------------------------------------------------
def limpiar_antiguos(texto):

    patrones = [
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_GLOBALES["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_ESTILO_BOTONES_DEFINITIVO["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_SOLO_BOTONES_V3["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V4["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V5["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</style>',

        r'<script[^>]*id=["\']EDUTURNOS_JS_BOTONES_DEFINITIVO["\'][^>]*>.*?</script>',
        r'<script[^>]*id=["\']EDUTURNOS_TODOS_LOS_BOTONES_JS["\'][^>]*>.*?</script>',
        r'<script[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</script>',
    ]

    for patron in patrones:
        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    return texto


# ------------------------------------------------------------
# INSERTAR STYLE + JS EN LA PLANTILLA
# ------------------------------------------------------------
def insertar_global(texto):

    texto = limpiar_antiguos(texto)

    bloque = f"""
<style id="{MARCADOR_CSS}">
button,
input[type="submit"],
input[type="button"],
input[type="reset"],
a.boton,
a.btn,
a[class*="boton"],
a[class*="button"],
a[class*="btn-"],
a[role="button"],
a.link-back,
a.edc-back,
.edc-header-actions a,
.edc-header-actions button,
.edc-buttons a,
.edc-buttons button,
.edc-month-toolbar a,
.edc-month-toolbar button,
.citas-actions a,
.citas-actions button,
.form-actions a,
.form-actions button,
.acciones a,
.acciones button,
.page-actions a,
.page-actions button,
.dashboard-actions a,
.dashboard-actions button,
.dashboard-card a.boton,
.dashboard-card button,
.quick-card a.boton,
.quick-card button,
.account-actions a.boton,
.account-actions button {{
    background: {AZUL} !important;
    background-color: {AZUL} !important;
    color: {BLANCO} !important;
    border-color: {AZUL} !important;
    text-decoration: none !important;
    box-shadow: none !important;
    opacity: 1 !important;
}}

button:hover,
input[type="submit"]:hover,
input[type="button"]:hover,
input[type="reset"]:hover,
a.boton:hover,
a.btn:hover,
a[class*="boton"]:hover,
a[class*="button"]:hover,
a[class*="btn-"]:hover,
a[role="button"]:hover,
a.link-back:hover,
a.edc-back:hover,
.edc-header-actions a:hover,
.edc-header-actions button:hover,
.edc-buttons a:hover,
.edc-buttons button:hover,
.edc-month-toolbar a:hover,
.edc-month-toolbar button:hover,
.citas-actions a:hover,
.citas-actions button:hover,
.form-actions a:hover,
.form-actions button:hover,
.acciones a:hover,
.acciones button:hover,
.page-actions a:hover,
.page-actions button:hover,
.dashboard-actions a:hover,
.dashboard-actions button:hover,
.dashboard-card a.boton:hover,
.dashboard-card button:hover,
.quick-card a.boton:hover,
.quick-card button:hover,
.account-actions a.boton:hover,
.account-actions button:hover {{
    background: {AZUL_HOVER} !important;
    background-color: {AZUL_HOVER} !important;
    color: {BLANCO} !important;
    border-color: {AZUL_HOVER} !important;
}}

button *,
input[type="submit"] *,
input[type="button"] *,
input[type="reset"] *,
a.boton *,
a.btn *,
a[role="button"] *,
a.link-back *,
a.edc-back *,
.edc-header-actions a *,
.edc-header-actions button *,
.edc-buttons a *,
.edc-buttons button *,
.edc-month-toolbar a *,
.edc-month-toolbar button *,
.citas-actions a *,
.citas-actions button *,
.form-actions a *,
.form-actions button *,
.acciones a *,
.acciones button *,
.page-actions a *,
.page-actions button *,
.dashboard-actions a *,
.dashboard-actions button *,
.dashboard-card a.boton *,
.dashboard-card button *,
.quick-card a.boton *,
.quick-card button *,
.account-actions a.boton *,
.account-actions button * {{
    color: {BLANCO} !important;
}}
</style>
{JS}
"""

    # Insertar antes de </head>.
    pos = texto.lower().rfind("</head>")

    if pos != -1:
        return (
            texto[:pos]
            + bloque
            + "\n"
            + texto[pos:]
        )

    # Si no hay head, antes de </body>.
    pos = texto.lower().rfind("</body>")

    if pos != -1:
        return (
            texto[:pos]
            + bloque
            + "\n"
            + texto[pos:]
        )

    return texto + "\n" + bloque


# ------------------------------------------------------------
# AÑADIR ESTILO INLINE A BOTONES REALES
# ------------------------------------------------------------
def modificar_aperturas(texto):

    patron = re.compile(
        r"<(button|input|a)\b([^>]*)>",
        re.IGNORECASE
    )

    modificados = 0

    def reemplazar(m):

        nonlocal modificados

        tag = m.group(1)
        attrs = m.group(2)

        tag_lower = tag.lower()
        attrs_lower = attrs.lower()

        es_boton = False

        # BUTTON
        if tag_lower == "button":
            es_boton = True

        # INPUTS
        if tag_lower == "input":
            tipo = re.search(
                r'type\s*=\s*["\']([^"\']+)["\']',
                attrs,
                flags=re.IGNORECASE
            )

            if tipo:
                tipo_valor = tipo.group(1).lower()

                if tipo_valor in {
                    "submit",
                    "button",
                    "reset"
                }:
                    es_boton = True

        # ENLACES QUE FUNCIONAN COMO BOTONES
        if tag_lower == "a":

            clases_boton = [
                "boton",
                "button",
                "btn",
                "accion",
                "action",
                "link-back",
                "edc-back"
            ]

            if any(x in attrs_lower for x in clases_boton):
                es_boton = True

            # Contenedores/clases concretos
            contenedores = [
                "edc-header-actions",
                "edc-buttons",
                "edc-month-toolbar",
                "citas-actions",
                "form-actions",
                "page-actions",
                "dashboard-actions",
                "account-actions"
            ]

            if any(x in attrs_lower for x in contenedores):
                es_boton = True

        if not es_boton:
            return m.group(0)

        # Si ya tiene style, agregar al existente.
        style = re.search(
            r'\bstyle\s*=\s*["\']([^"\']*)["\']',
            attrs,
            flags=re.IGNORECASE
        )

        if style:

            estilo_actual = style.group(1)

            nuevo_estilo = (
                estilo_actual.rstrip("; ")
                + ";"
                + ESTILO
            )

            attrs_nuevos = (
                attrs[:style.start(1)]
                + nuevo_estilo
                + attrs[style.end(1):]
            )

        else:

            attrs_nuevos = (
                attrs
                + f' style="{ESTILO}"'
            )

        modificados += 1

        return f"<{tag}{attrs_nuevos}>"

    return patron.sub(reemplazar, texto), modificados


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():

    print()
    print("=" * 72)
    print("EDUTURNOS - TODOS LOS BOTONES - CORRECCION DIRECTA")
    print("=" * 72)

    if not TEMPLATES.exists():
        print()
        print("ERROR:")
        print("No existe:")
        print(TEMPLATES)
        return

    archivos = list(TEMPLATES.rglob("*.html"))

    if not archivos:
        print()
        print("ERROR: No se encontraron plantillas HTML.")
        return

    total_archivos = 0
    total_botones = 0

    for archivo in archivos:

        # No modificar backups.
        if ".backup" in archivo.name.lower():
            continue

        try:
            original = archivo.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            try:
                original = archivo.read_text(
                    encoding="utf-8-sig"
                )
            except Exception:
                print("OMITIDO:", archivo)
                continue

        # Backup individual.
        backup = archivo.with_name(
            archivo.name + ".backup_todos_botones_v6"
        )

        if not backup.exists():
            shutil.copy2(archivo, backup)

        # Limpiar versiones nuestras anteriores.
        nuevo = limpiar_antiguos(original)

        # Insertar CSS y JS.
        nuevo = insertar_global(nuevo)

        # Poner estilo INLINE directamente a botones.
        nuevo, cantidad = modificar_aperturas(nuevo)

        if nuevo != original:
            archivo.write_text(
                nuevo,
                encoding="utf-8"
            )

            total_archivos += 1
            total_botones += cantidad

            print(
                f"OK  {archivo.relative_to(ROOT)}"
                f"   | botones: {cantidad}"
            )

    print()
    print("=" * 72)
    print("TERMINADO")
    print("=" * 72)
    print()
    print("Archivos modificados :", total_archivos)
    print("Botones encontrados   :", total_botones)
    print()
    print("Fondo normal :", AZUL)
    print("Letra        :", BLANCO)
    print("Hover        :", AZUL_HOVER)
    print()
    print("Referencia:")
    print("+ Nueva citación de Citas")
    print()
    print("SOLO se modificaron controles de tipo boton.")
    print()
    print("NO se modificaron:")
    print("- textos normales")
    print("- titulos")
    print("- parrafos")
    print("- tarjetas")
    print("- filtros")
    print("- calendario")
    print("- tablas")
    print()
    print("Ahora reinicia Flask y pulsa Ctrl + F5.")
    print("=" * 72)


if __name__ == "__main__":
    main()
