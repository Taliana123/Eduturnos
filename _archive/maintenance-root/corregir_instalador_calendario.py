from pathlib import Path

ruta = Path("instalar_calendario_fullcalendar.py")

if not ruta.exists():
    print("[ERROR] No existe instalar_calendario_fullcalendar.py")
    raise SystemExit(1)

texto = ruta.read_text(encoding="utf-8")

vieja = (
    "https://cdn.jsdelivr.net/npm/"
    "@fullcalendar/core@7.1.0/locales/es.global.js"
)

nueva = (
    "https://cdn.jsdelivr.net/npm/"
    "fullcalendar@7.1.0/locales/es.global.js"
)

if vieja in texto:
    texto = texto.replace(vieja, nueva)
    ruta.write_text(texto, encoding="utf-8")
    print("CORREGIDO: dirección del idioma español.")
else:
    print("La dirección anterior no aparece.")
    print("Se revisará igualmente el instalador.")

print()
print("URL CORRECTA:")
print(nueva)