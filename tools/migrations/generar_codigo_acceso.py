from datetime import datetime, timedelta
import secrets
from getpass import getpass
from werkzeug.security import generate_password_hash
import mysql.connector
from config import Config

PORTALES = {
    "estudiante": "Estudiante",
    "acudiente": "Acudiente",
    "docente": "Docente",
    "coordinador": "Administrador / Coordinador",
    "rector": "Rector",
}


def main():
    print("EDUTURNOS - GENERAR CÓDIGO INSTITUCIONAL")
    print("Usa este programa únicamente como institución/administrador para autorizar una cuenta.")
    for k, v in PORTALES.items():
        print(f"  {k}: {v}")
    portal = input("Portal: ").strip().lower()
    if portal not in PORTALES:
        print("Portal inválido.")
        return 1
    documento = input("Documento del usuario (opcional): ").strip() or None
    correo = input("Correo institucional (opcional): ").strip().lower() or None
    dias = input("Validez en días [1]: ").strip() or "1"
    codigo = f"{secrets.randbelow(1_000_000):06d}"

    cnx = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
    )
    try:
        cur = cnx.cursor()
        cur.execute("SELECT id FROM roles WHERE nombre=%s", (PORTALES[portal],))
        rol = cur.fetchone()
        if not rol:
            print("No existe el rol en la base de datos.")
            return 1
        cur.execute(
            """
            INSERT INTO codigos_acceso(id_rol, portal, documento, correo, codigo_hash, fecha_expiracion)
            VALUES(%s,%s,%s,%s,%s,%s)
            """,
            (rol[0], portal, documento, correo, generate_password_hash(codigo), datetime.now() + timedelta(days=int(dias))),
        )
        cnx.commit()
        print("\nCÓDIGO GENERADO (entregar al usuario una sola vez):")
        print(codigo)
        return 0
    finally:
        cur.close()
        cnx.close()


if __name__ == "__main__":
    raise SystemExit(main())
