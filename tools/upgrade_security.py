from getpass import getpass
import mysql.connector

print("="*60)
print("EDUTURNOS - SEGURIDAD DE AUTENTICACION")
print("="*60)
host = input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"
port = int(input("Puerto [3306]: ").strip() or "3306")
user = input("Usuario [root]: ").strip() or "root"
password = getpass("Contraseña de MySQL (Enter si no tiene): ")
cnx = mysql.connector.connect(host=host, port=port, user=user, password=password, database="eduturnos")
cur = cnx.cursor()
try:
    for stmt in [
        "ALTER TABLE usuarios ADD COLUMN intentos_fallidos INT NOT NULL DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN bloqueado_hasta DATETIME NULL",
        "ALTER TABLE usuarios ADD COLUMN ultimo_acceso DATETIME NULL",
    ]:
        try:
            cur.execute(stmt)
        except mysql.connector.Error as exc:
            if exc.errno != 1060:
                raise
    cnx.commit()
    print("OK. Seguridad de inicio de sesión preparada.")
finally:
    cur.close(); cnx.close()
