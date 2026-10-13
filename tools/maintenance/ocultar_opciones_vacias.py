from pathlib import Path
import re

for ruta in Path("templates").rglob("*.html"):
    texto = ruta.read_text(encoding="utf-8")
    original = texto

    texto = re.sub(
        r'<option\s+value=["\']\s*["\']\s*>\s*</option>',
        '<option value="" selected disabled hidden></option>',
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
        r'<option\s+value=["\']\s*["\']\s*>Ninguno</option>',
        '<option value="" selected disabled hidden></option>',
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
        r'<option\s+value=["\']\s*["\']\s*>No definido</option>',
        '<option value="" selected disabled hidden></option>',
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
        r'<option\s+value=["\']\s*["\']\s*>Todos</option>',
        '<option value="" selected disabled hidden></option>',
        texto,
        flags=re.IGNORECASE
    )

    if texto != original:
        ruta.write_text(texto, encoding="utf-8")
        print("CORREGIDO:", ruta)

print("PROCESO TERMINADO")
