from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash
import mysql.connector

ROOT = Path(__file__).resolve().parent


def main():
    print("=" * 60)
    print("EDUTURNOS - ASIGNAR CÓDIGO INSTITUCIONAL A PERSONAL")
    print("=" * 60)
    host = input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"
    port = int(input("Puerto [3306]: ").strip() or "3306")
    user = input("Usuario [root]: ").strip() or "root"
    password_db = getpass("Contraseña de MySQL (Enter si no tiene): ")
    cnx = mysql.connector.connect(host=host, port=port, user=user, password=password_db, database="eduturnos")
    cur = cnx.cursor(dictionary=True)
    try:
        rol = input("Rol (Docente/Administrador / Coordinador/Rector): ").strip()
        documento = input("Documento del personal: ").strip()
        codigo = getpass("Código institucional de 6 dígitos que asignará el colegio: ").strip()
        if len(codigo) != 6 or not codigo.isdigit():
            raise SystemExit("El código debe tener exactamente 6 dígitos.")
        sede_nombre = input("Sede exacta: ").strip()
        if rol == "Docente":
            cur.execute("SELECT id FROM sedes WHERE LOWER(nombre)=LOWER(%s)", (sede_nombre,))
            sede = cur.fetchone()
            if not sede:
                raise SystemExit("La sede no existe en la tabla sedes.")
            cur.execute("SELECT id_docente FROM docentes WHERE documento=%s", (documento,))
            persona = cur.fetchone()
            if not persona:
                raise SystemExit("No existe ese docente en docentes.")
            cur.execute("UPDATE docentes SET codigo_institucional_hash=%s, id_sede=%s WHERE id_docente=%s", (generate_password_hash(codigo), sede["id"], persona["id_docente"]))
        else:
            cur.execute("SELECT id FROM roles WHERE nombre=%s", (rol,))
            rol_row = cur.fetchone()
            cur.execute("SELECT id FROM sedes WHERE LOWER(nombre)=LOWER(%s)", (sede_nombre,))
            sede = cur.fetchone()
            if not rol_row or not sede:
                raise SystemExit("Rol o sede no válidos.")
            cur.execute("SELECT id FROM directorio_institucional WHERE documento=%s AND id_rol=%s", (documento, rol_row["id"]))
            persona = cur.fetchone()
            if not persona:
                raise SystemExit("No existe esa persona en directorio_institucional con ese rol.")
            cur.execute("UPDATE directorio_institucional SET codigo_institucional_hash=%s, id_sede=%s WHERE id=%s", (generate_password_hash(codigo), sede["id"], persona["id"]))
        cnx.commit()
        print("\nOK: código guardado de forma segura para esa persona y sede.")
        print("El código original no se almacena en texto plano.")
    finally:
        cur.close()
        cnx.close()


if __name__ == "__main__":
    main()
