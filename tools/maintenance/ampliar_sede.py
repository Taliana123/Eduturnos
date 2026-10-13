from pathlib import Path

ruta = Path("templates/base.html")

if not ruta.exists():
    print("[ERROR] No existe templates/base.html")
    raise SystemExit(1)

texto = ruta.read_text(encoding="utf-8")

anterior = """
grid-template-columns:
        repeat(3, minmax(0, 1fr)) !important;

    column-gap: 20px !important;
"""

nuevo = """
grid-template-columns:
        220px minmax(300px, 1.6fr) 200px !important;

    column-gap: 20px !important;
"""

if anterior not in texto:
    print("[AVISO] No se encontró la configuración anterior.")
    print("No se hizo ningún cambio.")
    raise SystemExit(0)

texto = texto.replace(anterior, nuevo, 1)

ruta.write_text(texto, encoding="utf-8")

print()
print("=" * 60)
print("ANCHO DE SEDE ACTUALIZADO")
print("=" * 60)
print()
print("Código: 220 px")
print("Sede: más ancha")
print("Jornada: 200 px")
print()
print("Los nombres largos de las sedes tendrán más espacio.")