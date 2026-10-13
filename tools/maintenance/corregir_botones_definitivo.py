from pathlib import Path
import shutil
import re

ROOT = Path(r"F:\edu_Final")
TEMPLATES = ROOT / "templates"
BASE = TEMPLATES / "base.html"
BASE_BACKUP = TEMPLATES / "base.html.backup_botones"

MARKER = "EDUTURNOS_BOTONES_V4"

STYLE = r'''
<style id="EDUTURNOS_BOTONES_V4">
/* =========================================================
   EDUTURNOS
   SOLO BOTONES
   Mismo azul y letra que "+ Nueva citación" de Citas
   ========================================================= */

button,
input[type="submit"],
input[type="button"],
input[type="reset"],
a.boton,
a[class*="boton"],
a.btn,
a[class*="btn-"],
a.link-back,
a.edc-back,
.boton,
.btn,
[class*="boton-"],
[class*="btn-"],
.link-back,
.edc-back {

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border-color: #1769aa !important;

    text-decoration: none !important;
}

/* Texto dentro de botones */
button *,
input[type="submit"] *,
input[type="button"] *,
input[type="reset"] *,
a.boton *,
a[class*="boton"] *,
a.btn *,
a[class*="btn-"] *,
.link-back *,
.edc-back * {
    color: #ffffff !important;
}

/* Hover */
button:hover,
input[type="submit"]:hover,
input[type="button"]:hover,
input[type="reset"]:hover,
a.boton:hover,
a[class*="boton"]:hover,
a.btn:hover,
a[class*="btn-"]:hover,
a.link-back:hover,
a.edc-back:hover,
.boton:hover,
.btn:hover,
[class*="boton-"]:hover,
[class*="btn-"]:hover,
.link-back:hover,
.edc-back:hover {

    background: #145b91 !important;
    background-color: #145b91 !important;

    color: #ffffff !important;

    border-color: #145b91 !important;

    text-decoration: none !important;
}

/* Elementos hijos durante hover */
button:hover *,
a.boton:hover *,
a[class*="boton"]:hover *,
a.btn:hover *,
a[class*="btn-"]:hover *,
.link-back:hover *,
.edc-back:hover * {
    color: #ffffff !important;
}
</style>
'''


def restaurar_base():
    if BASE.exists() and BASE_BACKUP.exists():
        shutil.copy2(BASE_BACKUP, BASE)
        print("OK - base.html restaurado al estado anterior.")
        return True

    if BASE.exists():
        texto = BASE.read_text(encoding="utf-8")

        # Elimina únicamente bloques de botones instalados anteriormente.
        patrones = [
            r'<style[^>]*id=["\']EDUTURNOS_BOTONES_GLOBALES["\'][^>]*>.*?</style>',
            r'<style[^>]*id=["\']EDUTURNOS_ESTILO_BOTONES_DEFINITIVO["\'][^>]*>.*?</style>',
            r'<style[^>]*id=["\']EDUTURNOS_SOLO_BOTONES_V3["\'][^>]*>.*?</style>',
            r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V4["\'][^>]*>.*?</style>',
            r'<script[^>]*id=["\']EDUTURNOS_JS_BOTONES_DEFINITIVO["\'][^>]*>.*?</script>',
        ]

        for patron in patrones:
            texto = re.sub(
                patron,
                "",
                texto,
                flags=re.IGNORECASE | re.DOTALL
            )

        BASE.write_text(texto, encoding="utf-8")
        print("OK - se limpiaron cambios anteriores de botones.")
        return True

    print("ERROR - no existe templates/base.html")
    return False


def quitar_marker(texto):
    patron = (
        r'\s*<style[^>]*id=["\']EDUTURNOS_BOTONES_V4["\'][^>]*>'
        r'.*?</style>\s*'
    )

    return re.sub(
        patron,
        "\n",
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )


def insertar_estilo(texto):
    texto = quitar_marker(texto)

    # Preferimos colocarlo dentro del último block de la plantilla.
    posiciones = list(re.finditer(r'{%\s*endblock\s*%}', texto, re.IGNORECASE))

    if posiciones:
        posicion = posiciones[-1].start()

        return (
            texto[:posicion]
            + "\n"
            + STYLE
            + "\n"
            + texto[posicion:]
        )

    return texto + "\n" + STYLE + "\n"


def procesar_plantillas():
    if not TEMPLATES.exists():
        print("ERROR - no existe la carpeta templates.")
        return

    archivos = list(TEMPLATES.rglob("*.html"))

    modificados = 0
    omitidos = 0

    for archivo in archivos:

        # No tocar backups.
        if ".backup" in archivo.name.lower():
            omitidos += 1
            continue

        # base.html ya fue restaurado y no necesita el CSS duplicado.
        if archivo.resolve() == BASE.resolve():
            omitidos += 1
            continue

        try:
            texto_original = archivo.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                texto_original = archivo.read_text(encoding="utf-8-sig")
            except Exception:
                omitidos += 1
                continue

        texto_nuevo = insertar_estilo(texto_original)

        if texto_nuevo != texto_original:
            backup = archivo.with_name(
                archivo.name + ".backup_botones_v4"
            )

            if not backup.exists():
                shutil.copy2(archivo, backup)

            archivo.write_text(
                texto_nuevo,
                encoding="utf-8"
            )

            modificados += 1

    print()
    print(f"Plantillas modificadas: {modificados}")
    print(f"Archivos omitidos:       {omitidos}")


def main():
    print()
    print("=" * 70)
    print("EDUTURNOS - CORRECCION DEFINITIVA: SOLO BOTONES")
    print("=" * 70)
    print()

    if not restaurar_base():
        return

    procesar_plantillas()

    print()
    print("=" * 70)
    print("CAMBIO TERMINADO")
    print("=" * 70)
    print()
    print("SOLO se modifico el estilo de los botones.")
    print()
    print("Color de fondo : #1769aa")
    print("Color de letra : #ffffff")
    print("Hover          : #145b91")
    print()
    print("Referencia:")
    print("+ Nueva citación de Citas")
    print()
    print("NO se cambiaron:")
    print("- textos")
    print("- titulos")
    print("- calendario")
    print("- filtros")
    print("- tarjetas")
    print("- campos")
    print("- tablas")
    print("- rutas")
    print("- MySQL")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
