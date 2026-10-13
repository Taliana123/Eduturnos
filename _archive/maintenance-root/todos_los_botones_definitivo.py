from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")
BASE = ROOT / "templates" / "base.html"

MARCADOR = "EDUTURNOS_TODOS_LOS_BOTONES_V5"

CSS = r"""
<style id="EDUTURNOS_TODOS_LOS_BOTONES_V5">

/* =========================================================
   EDUTURNOS - TODOS LOS BOTONES
   Referencia: + Nueva citación de Citas
   SOLO afecta controles que funcionan como botones
   ========================================================= */

/* BOTONES HTML */
button,
button.boton,
button.btn,
button[class*="boton"],
button[class*="button"],
button[class*="btn-"],
button[class*="accion"],
button[class*="action"],

/* INPUTS DE ACCIÓN */
input[type="submit"],
input[type="button"],
input[type="reset"],

/* ENLACES QUE SON BOTONES */
a[role="button"],
a.boton,
a.btn,
a.btn-primary,
a.btn-secondary,
a.btn-success,
a.btn-danger,
a.btn-warning,
a.btn-info,
a[class*="boton"],
a[class*="button"],
a[class*="btn-"],
a[class*="accion"],
a[class*="action"],

/* BOTÓN ATRÁS */
a.link-back,
a.edc-back,

/* CONTENEDORES DE BOTONES */
.edc-buttons a,
.edc-buttons button,
.edc-header-actions a.boton,
.edc-header-actions button,
.edc-month-toolbar a.boton,
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
.account-actions button,

/* CLASE GLOBAL */
.eduturnos-boton-global {

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border: 1px solid #1769aa !important;
    border-color: #1769aa !important;

    text-decoration: none !important;
    box-shadow: none !important;

    opacity: 1 !important;

    cursor: pointer !important;
}

/* TEXTO E ICONOS DENTRO DE LOS BOTONES */
button *,
input[type="submit"] *,
input[type="button"] *,
input[type="reset"] *,

a[role="button"] *,
a.boton *,
a.btn *,
a[class*="boton"] *,
a[class*="button"] *,
a[class*="btn-"] *,
a[class*="accion"] *,
a[class*="action"] *,

a.link-back *,
a.edc-back *,

.edc-buttons a *,
.edc-buttons button *,
.edc-header-actions a.boton *,
.edc-header-actions button *,
.edc-month-toolbar a.boton *,
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
.account-actions button *,
.eduturnos-boton-global * {

    color: #ffffff !important;
}

/* HOVER DE TODOS LOS BOTONES */
button:hover,
button.boton:hover,
button.btn:hover,
button[class*="boton"]:hover,
button[class*="button"]:hover,
button[class*="btn-"]:hover,
button[class*="accion"]:hover,
button[class*="action"]:hover,

input[type="submit"]:hover,
input[type="button"]:hover,
input[type="reset"]:hover,

a[role="button"]:hover,
a.boton:hover,
a.btn:hover,
a[class*="boton"]:hover,
a[class*="button"]:hover,
a[class*="btn-"]:hover,
a[class*="accion"]:hover,
a[class*="action"]:hover,

a.link-back:hover,
a.edc-back:hover,

.edc-buttons a:hover,
.edc-buttons button:hover,

.edc-header-actions a.boton:hover,
.edc-header-actions button:hover,

.edc-month-toolbar a.boton:hover,
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
.account-actions button:hover,

.eduturnos-boton-global:hover {

    background: #145b91 !important;
    background-color: #145b91 !important;

    color: #ffffff !important;

    border-color: #145b91 !important;

    box-shadow: none !important;
    opacity: 1 !important;
}

/* HOVER DEL TEXTO/ICONOS */
button:hover *,
input[type="submit"]:hover *,
input[type="button"]:hover *,
input[type="reset"]:hover *,

a[role="button"]:hover *,
a.boton:hover *,
a.btn:hover *,
a[class*="boton"]:hover *,
a[class*="button"]:hover *,
a[class*="btn-"]:hover *,
a[class*="accion"]:hover *,
a[class*="action"]:hover *,

a.link-back:hover *,
a.edc-back:hover *,

.edc-buttons a:hover *,
.edc-buttons button:hover *,
.edc-header-actions a.boton:hover *,
.edc-header-actions button:hover *,
.edc-month-toolbar a.boton:hover *,
.edc-month-toolbar button:hover *,
.citas-actions a:hover *,
.citas-actions button:hover *,
.form-actions a:hover *,
.form-actions button:hover *,
.acciones a:hover *,
.acciones button:hover *,
.page-actions a:hover *,
.page-actions button:hover *,
.dashboard-actions a:hover *,
.dashboard-actions button:hover *,
.dashboard-card a.boton:hover *,
.dashboard-card button:hover *,
.quick-card a.boton:hover *,
.quick-card button:hover *,
.account-actions a.boton:hover *,
.account-actions button:hover *,
.eduturnos-boton-global:hover * {

    color: #ffffff !important;
}

/* BOTÓN ATRÁS CON EL MISMO FORMATO */
a.link-back,
a.edc-back {

    min-height: 34px !important;
    padding: 7px 12px !important;

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border: 1px solid #1769aa !important;
    border-radius: 7px !important;
}

/* BOTONES DESHABILITADOS */
button:disabled,
input[type="submit"]:disabled,
input[type="button"]:disabled,
input[type="reset"]:disabled {

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border-color: #1769aa !important;

    opacity: 0.55 !important;
}

/* =========================================================
   DETECTOR DE BOTONES HECHOS CON <a>
   ========================================================= */
.eduturnos-boton-global {

    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;

    color: #ffffff !important;
    background: #1769aa !important;
    background-color: #1769aa !important;
    border-color: #1769aa !important;

}

</style>

<script id="EDUTURNOS_TODOS_LOS_BOTONES_JS">
(function () {
    "use strict";

    const SELECTORES = [
        "button",
        "input[type='submit']",
        "input[type='button']",
        "input[type='reset']",
        "a[role='button']",
        "a.boton",
        "a.btn",
        "a[class*='boton']",
        "a[class*='button']",
        "a[class*='btn-']",
        "a[class*='accion']",
        "a[class*='action']",
        "a.link-back",
        "a.edc-back",
        ".edc-buttons a",
        ".edc-buttons button",
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
        ".dashboard-card a.boton",
        ".dashboard-card button",
        ".quick-card a.boton",
        ".quick-card button",
        ".account-actions a.boton",
        ".account-actions button"
    ].join(",");

    function aplicar() {
        document.querySelectorAll(SELECTORES).forEach(function (elemento) {

            elemento.classList.add("eduturnos-boton-global");

            elemento.style.setProperty(
                "background",
                "#1769aa",
                "important"
            );

            elemento.style.setProperty(
                "background-color",
                "#1769aa",
                "important"
            );

            elemento.style.setProperty(
                "color",
                "#ffffff",
                "important"
            );

            elemento.style.setProperty(
                "border-color",
                "#1769aa",
                "important"
            );

            elemento.querySelectorAll("*").forEach(function (hijo) {
                hijo.style.setProperty(
                    "color",
                    "#ffffff",
                    "important"
                );
            });
        });
    }

    function iniciar() {
        aplicar();

        const observador = new MutationObserver(function () {
            aplicar();
        });

        observador.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar);
    } else {
        iniciar();
    }
})();
</script>
"""


def limpiar_versiones_anteriores(texto):
    patrones = [
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_GLOBALES["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_ESTILO_BOTONES_DEFINITIVO["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_SOLO_BOTONES_V3["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V4["\'][^>]*>.*?</style>',
        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V5["\'][^>]*>.*?</style>',
        r'<script[^>]*id=["\']EDUTURNOS_JS_BOTONES_DEFINITIVO["\'][^>]*>.*?</script>',
        r'<script[^>]*id=["\']EDUTURNOS_TODOS_LOS_BOTONES_JS["\'][^>]*>.*?</script>',
    ]

    for patron in patrones:
        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    return texto


def main():

    print()
    print("=" * 72)
    print("EDUTURNOS - TODOS LOS BOTONES")
    print("=" * 72)

    if not BASE.exists():
        print()
        print("ERROR: No existe:")
        print(BASE)
        return

    # Backup de seguridad.
    backup = TEMPLATES_BACKUP = BASE.with_name(
        "base.html.backup_todos_botones_v5"
    )

    if not backup.exists():
        shutil.copy2(BASE, backup)
        print()
        print("Backup creado:")
        print(backup)

    contenido = BASE.read_text(encoding="utf-8")

    # Quitar instalaciones anteriores.
    contenido = limpiar_versiones_anteriores(contenido)

    # Evitar duplicación.
    if MARCADOR not in contenido:

        posicion = contenido.lower().rfind("</head>")

        if posicion != -1:
            contenido = (
                contenido[:posicion]
                + "\n"
                + CSS
                + "\n"
                + contenido[posicion:]
            )

        else:

            posicion = contenido.lower().rfind("</body>")

            if posicion != -1:
                contenido = (
                    contenido[:posicion]
                    + "\n"
                    + CSS
                    + "\n"
                    + contenido[posicion:]
                )
            else:
                contenido += "\n" + CSS

    BASE.write_text(
        contenido,
        encoding="utf-8"
    )

    print()
    print("==============================================")
    print("CONFIGURACION TERMINADA")
    print("==============================================")
    print()
    print("TODOS LOS BOTONES usan:")
    print()
    print("Fondo : #1769aa")
    print("Letra : #ffffff")
    print("Hover : #145b91")
    print()
    print("Incluye:")
    print("- button")
    print("- submit")
    print("- input button")
    print("- reset")
    print("- .boton")
    print("- .btn")
    print("- .btn-*")
    print("- .button-*")
    print("- .accion")
    print("- .action")
    print("- link-back")
    print("- edc-back")
    print("- botones del Dashboard")
    print("- botones de Citas")
    print("- botones del Calendario")
    print("- botones de formularios")
    print("- enlaces que funcionan como botones")
    print()
    print("NO cambia los textos normales.")
    print("NO cambia títulos.")
    print("NO cambia tarjetas.")
    print("NO cambia filtros.")
    print("NO cambia tablas.")
    print("NO cambia el calendario.")
    print()
    print("Referencia visual:")
    print("+ Nueva citación")
    print()
    print("Ahora:")
    print("python .\\app.py")
    print()
    print("Y después Ctrl + F5 en el navegador.")
    print()
    print("=" * 72)


if __name__ == "__main__":
    main()
