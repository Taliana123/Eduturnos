from pathlib import Path
import re
import shutil

BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / "templates"
BACKUP = BASE / "backup_listas_vacias_seguro"

# Textos que sí son placeholders.
# "Todos" NO se elimina porque es una opción real de filtro.
PLACEHOLDERS = [
    "selecciona",
    "seleccione",
    "seleccionar",
    "elige",
    "elegir",
    "ninguno",
    "no definido",
]


def limpiar_recursos_antiguos(texto):
    """Elimina únicamente referencias a los desplegables personalizados."""

    texto = re.sub(
        r'<script\b[^>]*src=["\'][^"\']*(?:selects\.js|listas_eduturnos\.js)[^"\']*["\'][^>]*>\s*</script>',
        "",
        texto,
        flags=re.IGNORECASE | re.DOTALL,
    )

    texto = re.sub(
        r'<link\b[^>]*href=["\'][^"\']*listas_eduturnos\.css[^"\']*["\'][^>]*>',
        "",
        texto,
        flags=re.IGNORECASE,
    )

    return texto


def limpiar_clase_antigua(attrs):
    """Quita solo las clases usadas por los sistemas anteriores."""

    patron = re.compile(
        r'(\bclass\s*=\s*["\'])([^"\']*)(["\'])',
        re.IGNORECASE,
    )

    def reemplazar(match):
        inicio = match.group(1)
        clases = match.group(2)
        final = match.group(3)

        nuevas = [
            clase
            for clase in clases.split()
            if clase not in {
                "eduturnos-lista",
                "eduturnos-select",
                "eduturnos-select-original",
            }
        ]

        if not nuevas:
            return ""

        return inicio + " ".join(nuevas) + final

    return patron.sub(reemplazar, attrs)


def limpiar_selects(texto):
    """
    Modifica SOLO las etiquetas de apertura <select>.
    No toca el contenido Jinja del select.
    """

    def reemplazar(match):
        attrs = limpiar_clase_antigua(match.group(1))
        return (
            '<select'
            + attrs
            + '>'
            + '\n<option value="" selected disabled hidden></option>\n'
        )

    return re.sub(
        r'<select\b([^>]*)>',
        reemplazar,
        texto,
        flags=re.IGNORECASE,
    )


def eliminar_opciones_vacias_antiguas(texto):
    """
    Elimina únicamente opciones vacías o placeholders.

    No toca opciones reales como:
    - Todos
    - Mañana
    - Tarde
    - Noche
    - nombres de sedes
    - estudiantes
    - docentes
    """

    def reemplazar(match):
        attrs = match.group(1)
        contenido = match.group(2)

        # Solo value=""
        if not re.search(
            r'\bvalue\s*=\s*["\']\s*["\']',
            attrs,
            flags=re.IGNORECASE,
        ):
            return match.group(0)

        texto = re.sub(
            r'\s+',
            ' ',
            contenido,
        ).strip().lower()

        # Opción vacía
        if texto == "":
            return ""

        # Placeholder
        for palabra in PLACEHOLDERS:
            if texto.startswith(palabra):
                return ""

        return match.group(0)

    return re.sub(
        r'<option\b([^>]*)>(.*?)</option>',
        reemplazar,
        texto,
        flags=re.IGNORECASE | re.DOTALL,
    )


def procesar_archivo(ruta):
    texto = ruta.read_text(encoding="utf-8")
    original = texto

    # 1. Quitar referencias a sistemas personalizados
    texto = limpiar_recursos_antiguos(texto)

    # 2. Eliminar opciones vacías/placeholders anteriores
    texto = eliminar_opciones_vacias_antiguas(texto)

    # 3. Restaurar select nativo y colocar el espacio vacío
    texto = limpiar_selects(texto)

    if texto != original:
        ruta.write_text(texto, encoding="utf-8")
        return True

    return False


def main():

    print()
    print("=" * 65)
    print("EDUTURNOS - LISTAS VACÍAS SEGURO")
    print("=" * 65)
    print()

    if not TEMPLATES.exists():
        print("[ERROR] No existe la carpeta templates.")
        return

    # Copia de seguridad
    if BACKUP.exists():
        shutil.rmtree(BACKUP)

    shutil.copytree(TEMPLATES, BACKUP)

    print(f"COPIA DE SEGURIDAD: {BACKUP}")
    print()

    modificados = 0

    for archivo in TEMPLATES.rglob("*.html"):

        try:
            if procesar_archivo(archivo):
                modificados += 1
                print(f"CORREGIDO: {archivo}")

        except Exception as exc:
            print(f"[ERROR] {archivo}: {exc}")

    print()
    print("=" * 65)
    print("PROCESO TERMINADO CORRECTAMENTE")
    print("=" * 65)
    print()
    print(f"Archivos modificados: {modificados}")
    print()
    print("COMPORTAMIENTO:")
    print()
    print("CUADRO INICIAL:")
    print("[                                      ]")
    print()
    print("AL ABRIR:")
    print("Solo aparecen las opciones reales.")
    print()
    print("DESPUÉS DE ELEGIR:")
    print("[ Opción seleccionada                  ]")
    print()
    print("No se crean listas duplicadas.")
    print("No se reconstruyen bloques Jinja.")
    print()


if __name__ == "__main__":
    main()