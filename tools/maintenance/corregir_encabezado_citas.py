from pathlib import Path
import re

ruta = Path("templates/citas/index.html")

if not ruta.exists():
    print("[ERROR] No existe templates/citas/index.html")
    raise SystemExit(1)

texto = ruta.read_text(encoding="utf-8")

original = texto

# Cambiar únicamente el encabezado de columna "Acciones"
# por "Observaciones".
texto = re.sub(
    r'(<th\b[^>]*>\s*)(?:\*\*)?\s*Acciones\s*(?:\*\*)?\s*(</th>)',
    r'\1Observaciones\2',
    texto,
    flags=re.IGNORECASE
)

if texto == original:
    # Segunda posibilidad: encabezado sin <th> separado
    texto = re.sub(
        r'(\|\s*)(?:\*\*)?\s*Acciones\s*(?:\*\*)?(\s*\|)',
        r'\1Observaciones\2',
        texto,
        flags=re.IGNORECASE
    )

if texto != original:
    ruta.write_text(texto, encoding="utf-8")
    print("CORRECTO: el encabezado cambió de Acciones a Observaciones.")
else:
    print("[AVISO] No se encontró el encabezado 'Acciones'.")
    print("No se hizo ningún cambio.")