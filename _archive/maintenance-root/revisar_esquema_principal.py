from pathlib import Path
import re

ruta = Path(r"D:\edu_Final\sql\eduturnos.sql")
sql = ruta.read_text(encoding="utf-8")

def mostrar_tabla(nombre):
    patron = rf'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?{nombre}`?\s*\((.*?)\)\s*ENGINE'
    m = re.search(patron, sql, re.I | re.S)

    if not m:
        print(f"\nNO SE ENCONTRO: {nombre}")
        return

    print("\n" + "=" * 70)
    print(f"TABLA: {nombre}")
    print("=" * 70)

    cuerpo = m.group(1)

    for linea in cuerpo.splitlines():
        linea = linea.strip()

        if not linea:
            continue

        if linea.upper().startswith(("PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "INDEX", "CONSTRAINT", "KEY ")):
            continue

        print(linea)

mostrar_tabla("usuarios")
mostrar_tabla("docentes")
mostrar_tabla("estudiantes")
mostrar_tabla("citas")

print("\n" + "=" * 70)
print("COMPROBACION TERMINADA")
print("=" * 70)