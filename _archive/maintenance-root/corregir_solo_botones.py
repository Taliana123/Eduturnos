from pathlib import Path
import shutil
import re

BASE = Path(r"F:\edu_Final\templates\base.html")
BACKUP = Path(r"F:\edu_Final\templates\base.html.backup_botones")

MARCADOR = "EDUTURNOS_SOLO_BOTONES_V3"

CSS = r"""
<style id="EDUTURNOS_SOLO_BOTONES_V3">

/* =========================================================
   EDUTURNOS
   SOLO BOTONES
   Mismo estilo del botón "+ Nueva citación" de Citas
   ========================================================= */

/* BOTONES DE ACCIÓN */
button,
input[type="submit"],
input[type="button"],
input[type="reset"],
.boton,
a.boton,
button.boton,
.link-back,
a.link-back,
.edc-back,
a.edc-back {
    background: #1769aa !important;
    background-color: #1769aa !important;
    color: #ffffff !important;
    border: 1px solid #1769aa !important;
    border-radius: 7px !important;
    text-decoration: none !important;
    box-shadow: none !important;
    opacity: 1 !important;
    cursor: pointer !important;
}

/* TEXTO DENTRO DE LOS BOTONES */
button,
button *,
input[type="submit"],
input[type="submit"] *,
input[type="button"],
input[type="button"] *,
input[type="reset"],
input[type="reset"] *,
.boton,
.boton *,
a.boton,
a.boton *,
.link-back,
.link-back *,
.edc-back,
.edc-back * {
    color: #ffffff !important;
}

/* TAMAÑO DEL BOTÓN ATRÁS, CONSERVANDO EL RESTO IGUAL */
.link-back,
a.link-back,
.edc-back,
a.edc-back {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 34px !important;
    padding: 7px 12px !important;
    font-weight: 600 !important;
}

/* HOVER */
button:hover,
input[type="submit"]:hover,
input[type="button"]:hover,
input[type="reset"]:hover,
.boton:hover,
a.boton:hover,
button.boton:hover,
.link-back:hover,
a.link-back:hover,
.edc-back:hover,
a.edc-back:hover {
    background: #145b91 !important;
    background-color: #145b91 !important;
    color: #ffffff !important;
    border-color: #145b91 !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

/* BOTONES DEL CALENDARIO */
.edc-header-actions .boton,
.edc-header-actions a.boton,
.edc-buttons .boton,
.edc-buttons a.boton,
.edc-month-toolbar .boton,
.edc-month-toolbar a.boton {
    background: #1769aa !important;
    background-color: #1769aa !important;
    color: #ffffff !important;
    border-color: #1769aa !important;
}

/* BOTONES DE CITAS */
.citas-actions .boton,
.citas-actions a.boton,
.citas-actions button {
    background: #1769aa !important;
    background-color: #1769aa !important;
    color: #ffffff !important;
    border-color: #1769aa !important;
}

/* BOTONES DE DASHBOARD QUE YA USAN .boton */
.dashboard-card .boton,
.dashboard-card a.boton,
.quick-card .boton,
.quick-card a.boton,
.account-actions .boton,
.account-actions a.boton {
    background: #1769aa !important;
    background-color: #1769aa !important;
    color: #ffffff !important;
    border-color: #1769aa !important;
}

.dashboard-card .boton:hover,
.dashboard-card a.boton:hover,
.quick-card .boton:hover,
.quick-card a.boton:hover,
.account-actions .boton:hover,
.account-actions a.boton:hover {
    background: #145b91 !important;
    background-color: #145b91 !important;
    color: #ffffff !important;
    border-color: #145b91 !important;
}

</style>
"""

def quitar_bloques_inyectados(texto):
    marcadores = [
        r'<style id="EDUTURNOS_BOTONES_GLOBALES">.*?</style>',
        r'<style id="EDUTURNOS_ESTILO_BOTONES_DEFINITIVO">.*?</style>',
        r'<script id="EDUTURNOS_JS_BOTONES_DEFINITIVO">.*?</script>',
        r'<style id="EDUTURNOS_SOLO_BOTONES_V3">.*?</style>',
    ]

    for patron in marcadores:
        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    return texto


def main():
    print()
    print("=" * 68)
    print("EDUTURNOS - RESTAURAR TODO Y CAMBIAR SOLO BOTONES")
    print("=" * 68)

    if not BASE.exists():
        print()
        print("ERROR: no existe:")
        print(BASE)
        return

    # ---------------------------------------------------------
    # 1. Recuperar base.html anterior al cambio de botones.
    # ---------------------------------------------------------
    if BACKUP.exists():
        print()
        print("Restaurando base.html anterior...")
        shutil.copy2(BACKUP, BASE)
        print("OK: se recupero la version anterior de base.html")
    else:
        print()
        print("No existe el backup anterior.")
        print("Se eliminaran solamente los bloques de botones")
        print("que fueron agregados por los scripts anteriores.")

        contenido_actual = BASE.read_text(encoding="utf-8")
        contenido_actual = quitar_bloques_inyectados(contenido_actual)
        BASE.write_text(contenido_actual, encoding="utf-8")

    # ---------------------------------------------------------
    # 2. Leer base restaurada.
    # ---------------------------------------------------------
    contenido = BASE.read_text(encoding="utf-8")

    # Por seguridad, eliminar versiones anteriores.
    contenido = quitar_bloques_inyectados(contenido)

    # ---------------------------------------------------------
    # 3. Insertar SOLO estilos de botones.
    # ---------------------------------------------------------
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

    BASE.write_text(contenido, encoding="utf-8")

    print()
    print("=" * 68)
    print("CAMBIO TERMINADO")
    print("=" * 68)
    print()
    print("Se restauró el aspecto anterior de la página.")
    print("Ahora SOLO se modifican los botones.")
    print()
    print("Botón de referencia:")
    print("+ Nueva citación")
    print()
    print("Fondo normal : #1769aa")
    print("Letra        : #ffffff")
    print("Fondo hover  : #145b91")
    print()
    print("NO se modificaron:")
    print("- títulos")
    print("- textos")
    print("- filtros")
    print("- calendario")
    print("- tablas")
    print("- tarjetas")
    print("- campos")
    print("- estructura de la página")
    print()
    print("=" * 68)


if __name__ == "__main__":
    main()
