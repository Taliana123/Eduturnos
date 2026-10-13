from pathlib import Path
import re

# ============================================================
# EDUTURNOS - RESTAURAR LISTAS NATIVAS
# ============================================================

BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / "templates"
STATIC_JS = BASE / "static" / "js"
STATIC_CSS = BASE / "static" / "css"


def quitar_recursos_personalizados(texto):
    """
    Elimina completamente los CSS/JS que estaban creando
    una segunda interfaz para los desplegables.
    """

    # Quitar scripts antiguos
    patrones_script = [
        r'<script\b[^>]*src=["\'][^"\']*(?:selects\.js|listas_eduturnos\.js)[^"\']*["\'][^>]*>\s*</script>',
    ]

    for patron in patrones_script:
        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    # Quitar enlaces CSS personalizados
    texto = re.sub(
        r'<link\b[^>]*href=["\'][^"\']*listas_eduturnos\.css[^"\']*["\'][^>]*>',
        "",
        texto,
        flags=re.IGNORECASE
    )

    return texto


def limpiar_clases_select(attrs):
    """
    Elimina clases de los intentos anteriores de listas
    personalizadas, pero conserva las demás clases del proyecto.
    """

    def quitar_de_class(match):
        inicio = match.group(1)
        clases = match.group(2)
        fin = match.group(3)

        clases_nuevas = []

        for clase in clases.split():
            if clase not in {
                "eduturnos-lista",
                "eduturnos-select",
                "eduturnos-select-original",
            }:
                clases_nuevas.append(clase)

        if clases_nuevas:
            return inicio + " ".join(clases_nuevas) + fin

        return ""

    attrs = re.sub(
        r'(\bclass\s*=\s*["\'])([^"\']*)(["\'])',
        quitar_de_class,
        attrs,
        flags=re.IGNORECASE
    )

    return attrs


def option_es_vacia(option):
    """
    Determina si una opción tiene value vacío.
    """

    m = re.search(
        r'\bvalue\s*=\s*["\']\s*["\']',
        option,
        flags=re.IGNORECASE
    )

    if m:
        return True

    return False


def crear_option_vacia():
    """
    Esta opción sirve únicamente para que el cuadro cerrado
    aparezca vacío.

    hidden:
        No aparece como opción disponible al abrir.

    disabled:
        No se puede seleccionar manualmente.

    selected:
        Aparece inicialmente en el cuadro cuando no existe
        otra selección.
    """

    return '<option value="" disabled hidden selected></option>'


def procesar_select_completo(match):
    """
    Restaura un <select> nativo.

    Resultado:

    Cerrado:
        [                  ]

    Abierto:
        solo opciones reales

    Seleccionado:
        [Sede Picaleña    ]
    """

    attrs = match.group(1)
    contenido = match.group(2)

    # Quitar clases de las versiones anteriores
    attrs = limpiar_clases_select(attrs)

    # Buscar todas las opciones
    opciones = re.findall(
        r'<option\b[^>]*>.*?</option>',
        contenido,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not opciones:
        return "<select" + attrs + ">" + contenido + "</select>"

    opciones_reales = []
    hay_seleccion_real = False

    for opcion in opciones:

        # Opción vacía: NO debe entrar al menú
        if option_es_vacia(opcion):
            continue

        # Verificar si ya hay una opción real seleccionada
        if re.search(
            r'\bselected(?:\s*=\s*(?:"selected"|\'selected\'|selected))?\b',
            opcion,
            flags=re.IGNORECASE
        ):
            hay_seleccion_real = True

        opciones_reales.append(opcion)

    # Crear una sola opción vacía
    option_vacia = crear_option_vacia()

    # Si ya hay selección real, la opción vacía NO queda selected.
    if hay_seleccion_real:
        option_vacia = (
            '<option value="" disabled hidden></option>'
        )

    nuevo_contenido = option_vacia + "\n"

    if opciones_reales:
        nuevo_contenido += "\n".join(opciones_reales)

    return (
        "<select"
        + attrs
        + ">"
        + nuevo_contenido
        + "</select>"
    )


def procesar_archivo_html(ruta):
    try:
        texto = ruta.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"[AVISO] No se pudo leer: {ruta}")
        return False, 0

    original = texto

    # Primero eliminar JS/CSS anteriores
    texto = quitar_recursos_personalizados(texto)

    # Restaurar todos los select nativos
    coincidencias = len(
        re.findall(
            r"<select\b",
            texto,
            flags=re.IGNORECASE
        )
    )

    texto = re.sub(
        r"<select\b([^>]*)>(.*?)</select>",
        procesar_select_completo,
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )

    if texto != original:
        ruta.write_text(texto, encoding="utf-8")
        return True, coincidencias

    return False, coincidencias


def procesar_templates():
    if not TEMPLATES.exists():
        print("[ERROR] No existe la carpeta templates.")
        return

    archivos = 0
    listas = 0

    for archivo in TEMPLATES.rglob("*.html"):

        modificado, cantidad = procesar_archivo_html(archivo)

        if modificado:
            archivos += 1
            listas += cantidad
            print(f"RESTAURADO: {archivo}")

    print()
    print(f"ARCHIVOS MODIFICADOS: {archivos}")
    print(f"LISTAS PROCESADAS: {listas}")


def limpiar_archivos_personalizados():
    """
    Elimina los archivos que estaban provocando la segunda
    lista visual.
    """

    archivos = [
        STATIC_JS / "selects.js",
        STATIC_JS / "listas_eduturnos.js",
        STATIC_CSS / "listas_eduturnos.css",
    ]

    for archivo in archivos:

        if archivo.exists():
            try:
                archivo.unlink()
                print(f"ELIMINADO: {archivo}")
            except Exception as exc:
                print(
                    f"[AVISO] No se pudo eliminar "
                    f"{archivo}: {exc}"
                )


def limpiar_base():
    """
    Revisa base.html y elimina las referencias a los sistemas
    personalizados.
    """

    ruta = TEMPLATES / "base.html"

    if not ruta.exists():
        print("[AVISO] No existe templates/base.html")
        return

    texto = ruta.read_text(encoding="utf-8")
    original = texto

    texto = quitar_recursos_personalizados(texto)

    if texto != original:
        ruta.write_text(texto, encoding="utf-8")
        print("RESTAURADO: templates/base.html")
    else:
        print("base.html ya estaba sin esos recursos.")


def main():

    print()
    print("=" * 65)
    print("EDUTURNOS - RESTAURAR LISTAS NATIVAS")
    print("=" * 65)
    print()

    limpiar_archivos_personalizados()

    procesar_templates()

    limpiar_base()

    print()
    print("=" * 65)
    print("PROCESO TERMINADO")
    print("=" * 65)
    print()
    print("Las listas vuelven a ser nativas.")
    print("El cuadro cerrado comenzará vacío.")
    print("La opción vacía NO aparecerá al abrir la lista.")
    print("Solo aparecerán las opciones reales.")
    print("La opción elegida quedará visible en el cuadro.")
    print()


if __name__ == "__main__":
    main()