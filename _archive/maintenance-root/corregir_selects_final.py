from pathlib import Path
import re

archivos = [
    "templates/auth/registro_portal.html",
    "templates/citaciones/form.html",
    "templates/citas/nueva.html",
    "templates/docentes/asignaciones.html",
    "templates/estudiantes/form.html",
    "templates/reportes/index.html",
]

for archivo in archivos:
    ruta = Path(archivo)

    if not ruta.exists():
        continue

    texto = ruta.read_text(encoding="utf-8")
    original = texto

    # Corrige placeholders que quedaron solamente como "selected".
    texto = re.sub(
        r'<option\s+value=["\']\s*["\']\s+selected\s*>\s*</option>',
        '<option value="" selected disabled hidden></option>',
        texto,
        flags=re.IGNORECASE
    )

    # Corrige cualquier placeholder vacío sin atributos completos.
    texto = re.sub(
        r'<option\s+value=["\']\s*["\']\s*>\s*</option>',
        '<option value="" selected disabled hidden></option>',
        texto,
        flags=re.IGNORECASE
    )

    # En el formulario de estudiantes, Sede y Jornada deben iniciar vacíos.
    if archivo == "templates/estudiantes/form.html":
        texto = re.sub(
            r'(<select[^>]*name=["\']sede["\'][^>]*>)',
            r'\1<option value="" selected disabled hidden></option>',
            texto,
            count=1,
            flags=re.IGNORECASE
        )

        texto = re.sub(
            r'(<select[^>]*name=["\']jornada["\'][^>]*>)',
            r'\1<option value="" selected disabled hidden></option>',
            texto,
            count=1,
            flags=re.IGNORECASE
        )

        # Evita duplicar el placeholder si el archivo ya lo tenía.
        texto = texto.replace(
            '<option value="" selected disabled hidden></option><option value="" selected disabled hidden></option>',
            '<option value="" selected disabled hidden></option>'
        )

    if texto != original:
        ruta.write_text(texto, encoding="utf-8")
        print("CORREGIDO:", archivo)

print()
print("PROCESO TERMINADO")
