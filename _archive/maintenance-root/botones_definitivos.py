from pathlib import Path
import shutil

BASE = Path(r"F:\edu_Final\templates\base.html")

MARCADOR = "EDUTURNOS_ESTILO_BOTONES_DEFINITIVO"

ESTILO = r"""
<style id="EDUTURNOS_ESTILO_BOTONES_DEFINITIVO">

/* =========================================================
   EDUTURNOS - ESTILO DEFINITIVO DE BOTONES
   MISMO ESTILO DEL "← ATRÁS" DEL CALENDARIO
   ========================================================= */

button,
input[type="submit"],
input[type="button"],
input[type="reset"],
a.boton,
.boton,
.btn,
.btn-primary,
.btn-secondary,
.btn-success,
.btn-danger,
.btn-warning,
.btn-info,
.btn-dark,
.btn-light,
.action-button,
.boton-accion,
.accion,
.role-button,
.link-back,
.edc-back,
.dashboard-card a,
.dashboard-card button,
.dashboard-card input[type="submit"],
.dashboard-card input[type="button"],
.quick-card a,
.quick-card button,
.quick-card input[type="submit"],
.quick-card input[type="button"],
.account-actions a,
.account-actions button,
.account-actions input[type="submit"],
.account-actions input[type="button"],
.citas-actions a,
.citas-actions button,
.citas-actions input[type="submit"],
.citas-actions input[type="button"],
.edc-header-actions a,
.edc-header-actions button,
.edc-buttons a,
.edc-buttons button,
.edc-month-toolbar a,
.edc-month-toolbar button {
    background: #1769aa !important;
    background-color: #1769aa !important;
    color: #ffffff !important;
    border-color: #1769aa !important;
    border-radius: 7px !important;
    box-shadow: none !important;
    opacity: 1 !important;
    text-decoration: none !important;
}

/* ATRÁS */
a.link-back,
a.edc-back,
.page-navigation a.link-back {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;

    height: 34px !important;
    min-height: 34px !important;

    padding: 7px 12px !important;
    margin: 0 !important;

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border: 1px solid #1769aa !important;
    border-radius: 7px !important;

    font-family: inherit !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    line-height: 1 !important;

    box-shadow: none !important;
    text-decoration: none !important;
}

/* HOVER */
button:hover,
input[type="submit"]:hover,
input[type="button"]:hover,
input[type="reset"]:hover,
a.boton:hover,
.boton:hover,
.btn:hover,
.btn-primary:hover,
.btn-secondary:hover,
.btn-success:hover,
.btn-danger:hover,
.btn-warning:hover,
.btn-info:hover,
.btn-dark:hover,
.btn-light:hover,
.action-button:hover,
.boton-accion:hover,
.accion:hover,
.role-button:hover,
.link-back:hover,
.edc-back:hover,
.dashboard-card a:hover,
.dashboard-card button:hover,
.dashboard-card input[type="submit"]:hover,
.dashboard-card input[type="button"]:hover,
.quick-card a:hover,
.quick-card button:hover,
.quick-card input[type="submit"]:hover,
.quick-card input[type="button"]:hover,
.account-actions a:hover,
.account-actions button:hover,
.account-actions input[type="submit"]:hover,
.account-actions input[type="button"]:hover,
.citas-actions a:hover,
.citas-actions button:hover,
.citas-actions input[type="submit"]:hover,
.citas-actions input[type="button"]:hover,
.edc-header-actions a:hover,
.edc-header-actions button:hover,
.edc-buttons a:hover,
.edc-buttons button:hover,
.edc-month-toolbar a:hover,
.edc-month-toolbar button:hover {
    background: #145b91 !important;
    background-color: #145b91 !important;
    color: #ffffff !important;
    border-color: #145b91 !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

/* TEXTO E ICONOS DENTRO */
button *,
input[type="submit"] *,
input[type="button"] *,
input[type="reset"] *,
a.boton *,
.boton *,
.btn *,
.link-back *,
.edc-back *,
.dashboard-card a *,
.dashboard-card button *,
.quick-card a *,
.quick-card button *,
.account-actions a *,
.account-actions button *,
.citas-actions a *,
.citas-actions button * {
    color: #ffffff !important;
}

/* DESHABILITADOS */
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

</style>
"""

JAVASCRIPT = r"""
<script id="EDUTURNOS_JS_BOTONES_DEFINITIVO">
(function () {
    "use strict";

    const FONDO = "#1769aa";
    const HOVER = "#145b91";
    const TEXTO = "#ffffff";
    const BORDE = "#1769aa";

    function esBotonEDUTURNOS(el) {
        if (!el || !(el instanceof HTMLElement)) {
            return false;
        }

        const tag = el.tagName.toLowerCase();

        if (
            tag === "button" ||
            tag === "input" &&
            ["submit", "button", "reset"].includes(
                (el.getAttribute("type") || "").toLowerCase()
            )
        ) {
            return true;
        }

        if (tag === "a") {
            const clase = el.className || "";
            const texto = (el.textContent || "").trim().toLowerCase();

            if (
                el.matches(
                    ".boton, .btn, .btn-primary, .btn-secondary, .btn-success, " +
                    ".btn-danger, .btn-warning, .btn-info, .btn-dark, .btn-light, " +
                    ".action-button, .boton-accion, .accion, .role-button, " +
                    ".link-back, .edc-back, .dashboard-card a, .quick-card a, " +
                    ".account-actions a, .citas-actions a, .edc-header-actions a, " +
                    ".edc-buttons a, .edc-month-toolbar a"
                )
            ) {
                return true;
            }

            if (texto === "← atrás" || texto === "atras") {
                return true;
            }
        }

        return false;
    }

    function aplicarBoton(el) {
        if (!esBotonEDUTURNOS(el)) {
            return;
        }

        el.style.setProperty("background", FONDO, "important");
        el.style.setProperty("background-color", FONDO, "important");
        el.style.setProperty("color", TEXTO, "important");
        el.style.setProperty("border-color", BORDE, "important");
        el.style.setProperty("box-shadow", "none", "important");
        el.style.setProperty("opacity", "1", "important");
        el.style.setProperty("text-decoration", "none", "important");

        if (el.matches(".link-back, .edc-back")) {
            el.style.setProperty("border-radius", "7px", "important");
            el.style.setProperty("font-weight", "600", "important");
            el.style.setProperty("font-size", "13px", "important");
            el.style.setProperty("min-height", "34px", "important");
            el.style.setProperty("height", "34px", "important");
        }

        el.addEventListener("mouseenter", function () {
            el.style.setProperty("background", HOVER, "important");
            el.style.setProperty("background-color", HOVER, "important");
            el.style.setProperty("color", TEXTO, "important");
            el.style.setProperty("border-color", HOVER, "important");
        });

        el.addEventListener("mouseleave", function () {
            el.style.setProperty("background", FONDO, "important");
            el.style.setProperty("background-color", FONDO, "important");
            el.style.setProperty("color", TEXTO, "important");
            el.style.setProperty("border-color", BORDE, "important");
        });

        el.querySelectorAll("*").forEach(function (hijo) {
            hijo.style.setProperty("color", TEXTO, "important");
        });
    }

    function aplicarTodos() {
        document.querySelectorAll(
            "button, input[type='submit'], input[type='button'], input[type='reset'], " +
            "a, .boton, .btn, .link-back, .edc-back"
        ).forEach(aplicarBoton);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", aplicarTodos);
    } else {
        aplicarTodos();
    }

    const observador = new MutationObserver(function () {
        aplicarTodos();
    });

    observador.observe(document.documentElement, {
        childList: true,
        subtree: true
    });

})();
</script>
"""


def main():
    print()
    print("=" * 65)
    print("EDUTURNOS - CONFIGURACION DEFINITIVA DE BOTONES")
    print("=" * 65)

    if not BASE.exists():
        print()
        print("ERROR: No existe:")
        print(BASE)
        input("Presiona ENTER para cerrar...")
        return

    contenido = BASE.read_text(encoding="utf-8")

    # Eliminar versiones anteriores que pudieran haber quedado instaladas.
    marcadores = [
        "EDUTURNOS_BOTONES_GLOBALES",
        "EDUTURNOS_ESTILO_BOTONES_DEFINITIVO",
        "EDUTURNOS_JS_BOTONES_DEFINITIVO"
    ]

    if MARCADOR in contenido:
        print()
        print("La configuracion definitiva ya existe.")
        print("Se reemplazara para asegurar que este correcta.")

    backup = BASE.with_name("base.html.backup_botones_definitivo")

    if not backup.exists():
        shutil.copy2(BASE, backup)
        print()
        print("Backup creado:")
        print(backup)

    # Eliminar antiguos bloques conocidos.
    inicio = contenido.find('<style id="EDUTURNOS_BOTONES_GLOBALES">')
    if inicio != -1:
        fin = contenido.find("</style>", inicio)
        if fin != -1:
            contenido = contenido[:inicio] + contenido[fin + len("</style>"):]

    inicio = contenido.find('<style id="EDUTURNOS_ESTILO_BOTONES_DEFINITIVO">')
    if inicio != -1:
        fin = contenido.find("</style>", inicio)
        if fin != -1:
            contenido = contenido[:inicio] + contenido[fin + len("</style>"):]

    inicio = contenido.find('<script id="EDUTURNOS_JS_BOTONES_DEFINITIVO">')
    if inicio != -1:
        fin = contenido.find("</script>", inicio)
        if fin != -1:
            contenido = contenido[:inicio] + contenido[fin + len("</script>"):]

    # Insertar antes del cierre de body.
    posicion = contenido.lower().rfind("</body>")

    bloque = "\n" + ESTILO + "\n" + JAVASCRIPT + "\n"

    if posicion != -1:
        contenido = (
            contenido[:posicion]
            + bloque
            + contenido[posicion:]
        )
    else:
        contenido += bloque

    BASE.write_text(contenido, encoding="utf-8")

    print()
    print("CONFIGURACION APLICADA CORRECTAMENTE")
    print()
    print("Fondo normal : #1769aa")
    print("Letra        : #ffffff")
    print("Hover        : #145b91")
    print()
    print("Se aplicara de forma global a:")
    print(" - Dashboard")
    print(" - Citas")
    print(" - Calendario")
    print(" - Formularios")
    print(" - Boton Atras")
    print(" - Nueva cita")
    print(" - Ver citas")
    print(" - Filtrar")
    print(" - Limpiar")
    print(" - Acciones")
    print(" - Botones similares")
    print()
    print("El calendario NO fue modificado.")
    print()
    print("Ahora reinicia Flask y presiona Ctrl + F5.")
    print("=" * 65)
    print()

if __name__ == "__main__":
    main()
