from pathlib import Path
import re

archivo = Path("instalar_calendario_fullcalendar.py")

if not archivo.exists():
    print("ERROR: no existe instalar_calendario_fullcalendar.py")
    raise SystemExit(1)

texto = archivo.read_text(encoding="utf-8")

# Reemplazar directamente la definición de URL_LOCALE
patron = r'URL_LOCALE\s*=\s*[^\r\n]+'

reemplazo = (
    'URL_LOCALE = '
    '"https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/locales/es/global.js"'
)

nuevo, cantidad = re.subn(patron, reemplazo, texto, count=1)

if cantidad == 0:
    print("ERROR: no se encontró URL_LOCALE")
    raise SystemExit(1)

archivo.write_text(nuevo, encoding="utf-8")

print("=" * 70)
print("FULLCALENDAR CORREGIDO")
print("=" * 70)
print()
print("URL_LOCALE:")
print("https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/locales/es/global.js")
print()
print("CORRECTO")