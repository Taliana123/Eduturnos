from pathlib import Path
import shutil

BASE = Path(r"F:\edu_Final\templates\base.html")

CSS = r"""
<style id="EDUTURNOS_BOTONES_GLOBALES">
/* =========================================================
   EDUTURNOS - BOTONES UNIFICADOS
   Mismo estilo del boton "← Atrás" del calendario
   ========================================================= */

button,
input[type="submit"],
input[type="button"],
input[type="reset"],
.boton,
a.boton,
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
.edc-back {
    background-color: #1769aa !important;
    color: #ffffff !important;
    border: 1px solid #1769aa !important;
    border-radius: 7px !important;
    box-shadow: none !important;
    text-decoration: none !important;
    opacity: 1 !important;
    cursor: pointer !important;
}

/* BOTON ATRAS */
.link-back,
.edc-back,
.page-navigation .link-back {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 34px !important;
    height: 34px !important;
    padding: 7px 12px !important;
    margin: 0 !important;
    background-color: #1769aa !important;
    color: #ffffff !important;
    border: 1px solid #1769aa !important;
    border-radius: 7px !important;
    font-family: inherit !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    line-height: 1 !important;
    text-decoration: none !important;
}

/* HOVER */
button:hover,
input[type="submit"]:hover,
input[type="button"]:hover,
input[type="reset"]:hover,
.boton:hover,
a.boton:hover,
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
.page-navigation .link-back:hover {
    background-color: #145b91 !important;
    color: #ffffff !important;
    border-color: #145b91 !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

/* TEXTO E ICONOS DENTRO */
button *,
.boton *,
a.boton *,
.btn *,
.link-back *,
.edc-back * {
    color: #ffffff !important;
}

/* DASHBOARD */
.dashboard-card button,
.dashboard-card .boton,
.dashboard-card a.boton,
.dashboard-card .btn,
.quick-card button,
.quick-card .boton,
.quick-card a.boton,
.quick-card .btn,
.account-actions button,
.account-actions .boton,
.account-actions a.boton,
.account-actions .btn {
    background-color: #1769aa !important;
    color: #ffffff !important;
    border-color: #1769aa !important;
}

.dashboard-card button:hover,
.dashboard-card .boton:hover,
.dashboard-card a.boton:hover,
.dashboard-card .btn:hover,
.quick-card button:hover,
.quick-card .boton:hover,
.quick-card a.boton:hover,
.quick-card .btn:hover,
.account-actions button:hover,
.account-actions .boton:hover,
.account-actions a.boton:hover,
.account-actions .btn:hover {
    background-color: #145b91 !important;
    color: #ffffff !important;
    border-color: #145b91 !important;
}

/* FORMULARIOS */
form button,
form input[type="submit"],
form input[type="button"] {
    background-color: #1769aa !important;
    color: #ffffff !important;
    border: 1px solid #1769aa !important;
}

form button:hover,
form input[type="submit"]:hover,
form input[type="button"]:hover {
    background-color: #145b91 !important;
    color: #ffffff !important;
    border-color: #145b91 !important;
}

/* CITAS */
.citas-container button,
.citas-container .boton,
.citas-container a.boton,
.citas-actions button,
.citas-actions a,
.citas-actions .boton {
    background-color: #1769aa !important;
    color: #ffffff !important;
    border-color: #1769aa !important;
}

.citas-container button:hover,
.citas-container .boton:hover,
.citas-container a.boton:hover,
.citas-actions button:hover,
.citas-actions a:hover,
.citas-actions .boton:hover {
    background-color: #145b91 !important;
    color: #ffffff !important;
    border-color: #145b91 !important;
}

/* CALENDARIO */
.edc-header-actions button,
.edc-header-actions a,
.edc-header-actions .boton,
.edc-buttons button,
.edc-buttons a,
.edc-buttons .boton,
.edc-month-toolbar button,
.edc-month-toolbar a,
.edc-month-toolbar .boton {
    background-color: #1769aa !important;
    color: #ffffff !important;
    border-color: #1769aa !important;
}

.edc-header-actions button:hover,
.edc-header-actions a:hover,
.edc-header-actions .boton:hover,
.edc-buttons button:hover,
.edc-buttons a:hover,
.edc-buttons .boton:hover,
.edc-month-toolbar button:hover,
.edc-month-toolbar a:hover,
.edc-month-toolbar .boton:hover {
    background-color: #145b91 !important;
    color: #ffffff !important;
    border-color: #145b91 !important;
}

/* DESHABILITADOS */
button:disabled,
input[type="submit"]:disabled,
input[type="button"]:disabled {
    background-color: #1769aa !important;
    color: #ffffff !important;
    border-color: #1769aa !important;
    opacity: 0.55 !important;
    cursor: not-allowed !important;
}
</style>
"""

MARCADOR = 'id="EDUTURNOS_BOTONES_GLOBALES"'


def main():
    print()
    print("EDUTURNOS - CONFIGURANDO BOTONES")
    print("---------------------------------")

    if not BASE.exists():
        print()
        print("ERROR: No se encontro:")
        print(BASE)
        print()
        input("Presiona ENTER para cerrar...")
        return

    contenido = BASE.read_text(encoding="utf-8")

    if MARCADOR in contenido:
        print()
        print("Los botones ya estaban instalados.")
        print("No se modifico nuevamente el archivo.")
        print()
        input("Presiona ENTER para cerrar...")
        return

    backup = BASE.with_name("base.html.backup_botones")

    if not backup.exists():
        shutil.copy2(BASE, backup)
        print()
        print("Backup creado:")
        print(backup)

    posicion = contenido.lower().rfind("</body>")

    if posicion != -1:
        contenido_nuevo = (
            contenido[:posicion]
            + "\n"
            + CSS
            + "\n"
            + contenido[posicion:]
        )
    else:
        contenido_nuevo = contenido + "\n" + CSS

    BASE.write_text(contenido_nuevo, encoding="utf-8")

    print()
    print("========================================")
    print("BOTONES DE EDUTURNOS ACTUALIZADOS")
    print("========================================")
    print("Fondo: #1769aa")
    print("Letra: #ffffff")
    print("Hover: #145b91")
    print()
    print("Se aplicara a:")
    print("Dashboard")
    print("Citas")
    print("Calendario")
    print("Formularios")
    print("Botones de accion")
    print("Boton Atras")
    print()
    print("El calendario NO fue modificado.")
    print()
    input("Presiona ENTER para cerrar...")


if __name__ == "__main__":
    main()
