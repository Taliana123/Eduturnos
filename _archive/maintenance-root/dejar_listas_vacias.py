from pathlib import Path
import re
import shutil

BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / "templates"
BACKUP = BASE / "backup_listas_vacias"


def quitar_selected(atributos):
    """
    Quita selected de una opción real para que ninguna
    aparezca seleccionada de forma automática.
    """
    atributos = re.sub(
        r'\s+selected(?:\s*=\s*(?:"selected"|\'selected\'|selected))?',
        '',
        atributos,
        flags=re.IGNORECASE
    )
    return atributos


def procesar_select(match):
    """
    Modifica únicamente el contenido de cada <select>.
    No modifica {% if %}, {% for %}, variables Jinja,
    nombres de campos ni atributos del select.
    """

    atributos = match.group(1)
    contenido = match.group(2)

    opciones = re.findall(
        r'<option\b([^>]*)>(.*?)</option>',
        contenido,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not opciones:
        return match.group(0)

    opciones_reales = []

    for attrs, texto in opciones:

        # Detectar opción value=""
        vacia = re.search(
            r'\bvalue\s*=\s*["\']\s*["\']',
            attrs,
            flags=re.IGNORECASE
        )

        if vacia:
            # Esta será la única opción inicial:
            # vacía, deshabilitada y oculta al abrir.
            continue

        # Quitar cualquier selección automática
        attrs = quitar_selected(attrs)

        # Detectar placeholders escritos
        texto_limpio = re.sub(
            r'\s+',
            ' ',
            texto
        ).strip().lower()

        placeholders = (
            texto_limpio.startswith("selecciona")
            or texto_limpio.startswith("seleccione")
            or texto_limpio.startswith("seleccionar")
            or texto_limpio.startswith("elige")
            or texto_limpio.startswith("elegir")
            or texto_limpio == "ninguno"
            or texto_limpio == "no definido"
        )

        if placeholders:
            continue

        opciones_reales.append(
            "<option" + attrs + ">" + texto + "</option>"
        )

    # Opción inicial completamente vacía.
    opcion_vacia = (
        '<option value="" selected disabled hidden></option>'
    )

    nuevo_contenido = opcion_vacia

    if opciones_reales:
        nuevo_contenido += "\n" + "\n".join(opciones_reales)

    return (
        "<select"
        + atributos
        + ">"
        + nuevo_contenido
        + "</select>"
    )


def procesar_archivo(ruta):
    texto = ruta.read_text(encoding="utf-8")
    original = texto

    texto = re.sub(
        r'<select\b([^>]*)>(.*?)</select>',
        procesar_select,
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )

    if texto != original:
        ruta.write_text(
            texto,
            encoding="utf-8"
        )
        return True

    return False


def main():

    print()
    print("=" * 65)
    print("EDUTURNOS - LISTAS VACÍAS AL INICIO")
    print("=" * 65)
    print()

    if not TEMPLATES.exists():
        print("[ERROR] No existe templates.")
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
    print("PROCESO TERMINADO")
    print("=" * 65)
    print()
    print(f"Archivos modificados: {modificados}")
    print()
    print("TODAS LAS LISTAS QUEDARÁN:")
    print()
    print("  CUADRO CERRADO:")
    print("  [                                      ]")
    print()
    print("  AL ABRIR:")
    print("  [ Sede Principal                     ]")
    print("  [ Sede Picaleña                      ]")
    print("  [ Sede San Martín                    ]")
    print()
    print("  DESPUÉS DE ELEGIR:")
    print("  [ Sede Picaleña                      ]")
    print()
    print("No se agregará una fila vacía al menú.")
    print("")


if __name__ == "__main__":
    main()