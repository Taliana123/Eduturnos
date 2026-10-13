from pathlib import Path
import re

ruta = Path("instalar_calendario_fullcalendar.py")

if not ruta.exists():
    print("[ERROR] No existe instalar_calendario_fullcalendar.py")
    raise SystemExit(1)

texto = ruta.read_text(encoding="utf-8")

# Corrige cualquier URL de locale que esté usando @fullcalendar/core
texto = re.sub(
    r"https://cdn\.jsdelivr\.net/npm/@fullcalendar/core@7\.1\.0/locales/es\.global\.js",
    "https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/locales/es/global.js",
    texto
)

# También corrige variantes incorrectas por seguridad
texto = re.sub(
    r"https://cdn\.jsdelivr\.net/npm/fullcalendar@7\.1\.0/locales/es\.global\.js",
    "https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/locales/es/global.js",
    texto
)

# Por si el instalador construye la URL desde una variable
texto = re.sub(
    r'URL_LOCALE\s*=\s*["\'][^"\']+["\']',
    'URL_LOCALE = "https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/locales/es/global.js"',
    texto
)

ruta.write_text(texto, encoding="utf-8")

print()
print("=" * 70)
print("URL DE FULLCALENDAR CORREGIDA")
print("=" * 70)
print("https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/locales/es/global.js")
print()
print("El instalador ya está preparado para volver a ejecutarse.")