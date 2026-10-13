from pathlib import Path

ruta = Path("templates/auth/registro_portal.html")

texto = ruta.read_text(encoding="utf-8")

# Quitar únicamente el texto de ejemplo del campo
texto = texto.replace(
    'placeholder="Código de 6 dígitos"',
    'placeholder=""'
)

texto = texto.replace(
    'placeholder="Código institucional"',
    'placeholder=""'
)

texto = texto.replace(
    'placeholder="6 dígitos"',
    'placeholder=""'
)

ruta.write_text(texto, encoding="utf-8")

print("CORRECTO: el campo Código institucional quedó sin texto de ejemplo.")