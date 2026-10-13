from pathlib import Path

ARCHIVO = Path("instalar_calendario_fullcalendar.py")

if not ARCHIVO.exists():
    print("[ERROR] No existe instalar_calendario_fullcalendar.py")
    raise SystemExit(1)

texto = ARCHIVO.read_text(encoding="utf-8")

# Corregir cualquier referencia al paquete antiguo de FullCalendar
texto = texto.replace(
    "@fullcalendar/core@7.1.0",
    "fullcalendar@7.1.0"
)

# En FullCalendar 7 la ruta del locale cambió:
# /locales/es.global.js  ->  /locales/es/global.js
texto = texto.replace(
    "locales/es.global.js",
    "locales/es/global.js"
)

ARCHIVO.write_text(texto, encoding="utf-8")

print()
print("=" * 70)
print("FULLCALENDAR CORREGIDO")
print("=" * 70)

if "@fullcalendar/core@7.1.0" in texto:
    print("[ERROR] Todavía existe una referencia antigua.")
else:
    print("[OK] Se eliminó la referencia a @fullcalendar/core.")

if "locales/es.global.js" in texto:
    print("[ERROR] Todavía existe la ruta antigua del locale.")
else:
    print("[OK] Se corrigió la ruta del locale español.")

print()
print("La URL que debe utilizarse es:")
print("https://cdn.jsdelivr.net/npm/fullcalendar@7.1.0/locales/es/global.js")
print()