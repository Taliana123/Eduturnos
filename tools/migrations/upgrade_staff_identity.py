from pathlib import Path
import mysql.connector

ROOT = Path(__file__).resolve().parent


def main():
    print("=" * 60)
    print("EDUTURNOS - ACTUALIZAR IDENTIDAD DE PERSONAL")
    print("=" * 60)
    host = input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"
    port = int(input("Puerto [3306]: ").strip() or "3306")
    user = input("Usuario [root]: ").strip() or "root"
    password = input("Contraseña de MySQL (Enter si no tiene): ")
    cnx = mysql.connector.connect(host=host, port=port, user=user, password=password, database="eduturnos")
    try:
        cur = cnx.cursor()
        for raw in (ROOT / "sql" / "staff_identity_migration.sql").read_text(encoding="utf-8").split(";"):
            stmt = raw.strip()
            if stmt:
                try:
                    cur.execute(stmt)
                except mysql.connector.Error as exc:
                    # MySQL no siempre admite ADD COLUMN IF NOT EXISTS según versión.
                    if "Duplicate column" in str(exc):
                        continue
                    if "Duplicate key name" in str(exc):
                        continue
                    if "Duplicate foreign key constraint name" in str(exc):
                        continue
                    raise
        cnx.commit()
        print("\nOK: estructura de identidad del personal actualizada.")
        print("Ahora docentes, coordinadores y rectores pueden tener código institucional por sede.")
    finally:
        cur.close()
        cnx.close()


if __name__ == "__main__":
    main()
