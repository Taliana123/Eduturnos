from pathlib import Path
import mysql.connector
from getpass import getpass

ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / "sql" / "auto_auth_migration.sql"


def split_sql(text):
    out, current = [], []
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("--"):
            continue
        current.append(line)
        if line.strip().endswith(";"):
            out.append("\n".join(current).strip())
            current = []
    if current:
        out.append("\n".join(current).strip())
    return out


print("=" * 60)
print("EDUTURNOS - AUTENTICACION AUTOMATICA")
print("=" * 60)
print("Crea el directorio institucional para validar automáticamente")
print("coordinadores y rectoría, sin códigos manuales al registrar usuarios.")
print()
host = input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"
port = int(input("Puerto [3306]: ").strip() or "3306")
user = input("Usuario [root]: ").strip() or "root"
password = getpass("Contraseña de MySQL (Enter si no tiene): ")

cnx = mysql.connector.connect(host=host, port=port, user=user, password=password, database="eduturnos")
cur = cnx.cursor()
try:
    for stmt in split_sql(SQL_FILE.read_text(encoding="utf-8")):
        cur.execute(stmt)
    cnx.commit()
    print("\nOK. Autenticación automática preparada.")
    print("Los registros de estudiantes, acudientes y docentes ya sirven como directorio.")
    print("Coordinación/Rectoría requieren una fila en directorio_institucional,")
    print("cargada una sola vez como parte del directorio oficial.")
finally:
    cur.close()
    cnx.close()
