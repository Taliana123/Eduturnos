from pathlib import Path
import re
import shutil

# ============================================================
# EDUTURNOS - ESPACIO EN BLANCO EN DESPLEGABLES
# ============================================================

BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / "templates"

BACKUP = BASE / "backup_listas_antes_de_cambio"


def limpiar_clases_personalizadas(attrs):
    """
    Elimina únicamente las clases de los intentos anteriores
    de desplegables personalizados.
    No toca ninguna estructura Jinja.
    """

    patron = re.compile(
        r'(\bclass\s*=\s*["\'])([^"\']*)(["\'])',
        re.IGNORECASE
    )

    def reemplazar(match):
        inicio = match.group(1)
        clases = match.group(2)
        final = match.group(3)

        clases_nuevas = []

        for clase in clases.split():
            if clase not in {
                "eduturnos-lista",
                "eduturnos-select",
                "eduturnos-select-original",
            }:
                clases_nuevas.append(clase)

        if not clases_nuevas:
            return ""

        return inicio + " ".join(clases_nuevas) + final

    return patron.sub(reemplazar, attrs)


def quitar_recursos_personalizados(texto):
    """
    Quita los archivos CSS/JS que podían generar una segunda
    interfaz. No modifica HTML interno de formularios.
    """

    texto = re.sub(
        r'<script\b[^>]*src=["\'][^"\']*(?:selects\.js|listas_eduturnos\.js)[^"\']*["\'][^>]*>\s*</script>',
        "",
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )

    texto = re.sub(
        r'<link\b[^>]*href=["\'][^"\']*listas_eduturnos\.css[^"\']*["\'][^>]*>',
        "",
        texto,
        flags=re.IGNORECASE
    )

    return texto


def convertir_opciones_vacias(texto):
    """
    MODIFICA SOLO etiquetas <option>.

    No modifica:
    - {% for %}
    - {% if %}
    - variables Jinja
    - nombres de campos
    - rutas
    - formularios
    - etiquetas <select>
    """

    patron = re.compile(
        r'<option\b([^>]*)>(.*?)</option>',
        re.IGNORECASE | re.DOTALL
    )

    patrones_placeholder = [
        r'^selecciona\b',
        r'^seleccione\b',
        r'^seleccionar\b',
        r'^elige\b',
        r'^elegir\b',
        r'^no definido$',
        r'^ninguno$',
    ]

    cambios = 0

    def reemplazar(match):
        nonlocal cambios

        atributos = match.group(1)
        contenido = match.group(2).strip()

        # Detectar value vacío
        value_vacio = re.search(
            r'\bvalue\s*=\s*["\']\s*["\']',
            atributos,
            flags=re.IGNORECASE
        )

        if not value_vacio:
            return match.group(0)

        texto_limpio = re.sub(
            r'\s+',
            ' ',
            contenido
        ).strip().lower()

        # Ya es una opción vacía
        if texto_limpio == "":
            cambios += 1
            return (
                '<option value="" '
                'selected disabled hidden></option>'
            )

        # Es un placeholder
        es_placeholder = any(
            re.match(patron, texto_limpio)
            for patron in patrones_placeholder
        )

        if es_placeholder:
            cambios += 1
            return (
                '<option value="" '
                'selected disabled hidden></option>'
            )

        return match.group(0)

    nuevo = patron.sub(reemplazar, texto)

    return nuevo, cambios


def quitar_clases_select(texto):
    """
    Solo limpia las clases antiguas de los <select>.
    """

    patron = re.compile(
        r'<select\b([^>]*)>',
        re.IGNORECASE
    )

    def reemplazar(match):
        atributos = limpiar_clases_personalizadas(
            match.group(1)
        )
        return "<select" + atributos + ">"

    return patron.sub(reemplazar, texto)


def procesar_archivo(ruta):
    try:
        texto = ruta.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"[AVISO] No se pudo leer: {ruta}")
        return 0

    original = texto

    texto = quitar_recursos_personalizados(texto)
    texto = quitar_clases_select(texto)

    texto, cambios = convertir_opciones_vacias(texto)

    if texto != original:
        ruta.write_text(
            texto,
            encoding="utf-8"
        )
        print(
            f"CORREGIDO: {ruta} "
            f"({cambios} opciones)"
        )

    return cambios


def main():

    print()
    print("=" * 65)
    print("EDUTURNOS - ESPACIO EN BLANCO EN LISTAS")
    print("=" * 65)
    print()

    if not TEMPLATES.exists():
        print("[ERROR] No existe la carpeta templates.")
        return

    # --------------------------------------------------------
    # Copia de seguridad del estado actual
    # --------------------------------------------------------

    if BACKUP.exists():
        shutil.rmtree(BACKUP)

    shutil.copytree(
        TEMPLATES,
        BACKUP
    )

    print(
        f"COPIA DE SEGURIDAD: {BACKUP}"
    )
    print()

    archivos = 0
    opciones = 0

    # --------------------------------------------------------
    # Procesar todos los HTML
    # --------------------------------------------------------

    for archivo in TEMPLATES.rglob("*.html"):

        cambios = procesar_archivo(archivo)

        if cambios > 0:
            archivos += 1
            opciones += cambios

    print()
    print("=" * 65)
    print("PROCESO TERMINADO CORRECTAMENTE")
    print("=" * 65)
    print()
    print(f"Archivos modificados: {archivos}")
    print(f"Opciones corregidas: {opciones}")
    print()
    print("Resultado esperado:")
    print("1. El cuadro cerrado queda completamente blanco.")
    print("2. La opción vacía NO aparece en la lista abierta.")
    print("3. Al abrir aparecen solamente opciones reales.")
    print("4. Al seleccionar una opción, aparece en el cuadro.")
    print("5. No se crean listas duplicadas.")
    print("6. No se modifica la estructura Jinja.")
    print()


if __name__ == "__main__":
    main()