import re
from pathlib import Path

base = Path(r"D:\edu_Final\sql")

archivos = [
    "eduturnos.sql",
    "auth_migration.sql",
    "auto_auth_migration.sql",
    "security_migration.sql",
    "staff_identity_migration.sql"
]

print("=" * 70)
print("ANALISIS FINAL DEL ESQUEMA EDUTURNOS")
print("=" * 70)

for nombre in archivos:
    ruta = base / nombre
    texto = ruta.read_text(encoding="utf-8")

    print("\n" + "=" * 70)
    print(nombre)
    print("=" * 70)

    tablas = re.findall(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?([A-Za-z0-9_]+)`?',
        texto,
        re.I
    )

    columnas = re.findall(
        r'ALTER\s+TABLE\s+`?([A-Za-z0-9_]+)`?\s+ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?`?([A-Za-z0-9_]+)`?',
        texto,
        re.I
    )

    print("TABLAS CREADAS:")
    if tablas:
        for tabla in tablas:
            print("  -", tabla)
    else:
        print("  Ninguna")

    print("\nCOLUMNAS AGREGADAS POR ALTER:")
    if columnas:
        for tabla, columna in columnas:
            print(f"  - {tabla}.{columna}")
    else:
        print("  Ninguna")

print("\n" + "=" * 70)
print("TABLAS QUE EL ESQUEMA PRINCIPAL DEBE TENER")
print("=" * 70)

principal = (base / "eduturnos.sql").read_text(encoding="utf-8")

tablas = re.findall(
    r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?([A-Za-z0-9_]+)`?',
    principal,
    re.I
)

for i, tabla in enumerate(tablas, 1):
    print(f"{i:02}. {tabla}")

print("\n" + "=" * 70)
print("ANALISIS TERMINADO")
print("=" * 70)