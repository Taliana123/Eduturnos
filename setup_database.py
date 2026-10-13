from getpass import getpass
from pathlib import Path
import argparse

import mysql.connector
from mysql.connector import Error

ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / "database" / "eduturnos.sql"


def dividir_sql(texto: str):
    sentencias = []
    actual = []
    for linea in texto.splitlines():
        limpia = linea.strip()
        if not limpia or limpia.startswith("--"):
            continue
        actual.append(linea)
        if limpia.endswith(";"):
            sentencias.append("\n".join(actual).strip())
            actual = []
    if actual:
        sentencias.append("\n".join(actual).strip())
    return sentencias


def main():
    parser = argparse.ArgumentParser(description="Configura la base de datos EDUTURNOS")
    parser.add_argument(
        "--recrear",
        action="store_true",
        help="Elimina y recrea eduturnos. Solo para una instalación de prueba.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("EDUTURNOS - CONFIGURAR BASE DE DATOS")
    print("=" * 60)
    if args.recrear:
        print("MODO RECREAR: se eliminará la base eduturnos actual.")
    else:
        print("Modo seguro: se conservarán los datos de una base existente.")
    print()

    host = input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"
    port_text = input("Puerto [3306]: ").strip() or "3306"
    user = input("Usuario [root]: ").strip() or "root"
    password = getpass("Contraseña de MySQL (Enter si no tiene): ")

    try:
        port = int(port_text)
    except ValueError:
        print("El puerto debe ser un número, normalmente 3306.")
        return 1

    cnx = None
    cursor = None
    try:
        cnx = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connection_timeout=5,
        )
        if not cnx.is_connected():
            raise RuntimeError("MySQL no reportó una conexión activa.")

        cursor = cnx.cursor()
        if args.recrear:
            cursor.execute("DROP DATABASE IF EXISTS eduturnos")
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS eduturnos "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute("USE eduturnos")

        script = SQL_FILE.read_text(encoding="utf-8")
        for sentencia in dividir_sql(script):
            normalizada = sentencia.strip().upper()
            if normalizada.startswith("CREATE DATABASE"):
                continue
            if normalizada.startswith("USE EDUTURNOS"):
                continue
            if normalizada.startswith("SET FOREIGN_KEY_CHECKS"):
                continue
            if normalizada.startswith("DROP TABLE IF EXISTS"):
                # No se ejecutan instrucciones destructivas del esquema.
                continue
            cursor.execute(sentencia)

        cnx.commit()
        cursor.execute("SHOW TABLES")
        tablas = [fila[0] for fila in cursor.fetchall()]

        print("\nBASE DE DATOS CONFIGURADA CORRECTAMENTE.")
        print(f"Tablas creadas: {len(tablas)}")
        for tabla in tablas:
            print(f"  - {tabla}")
        print("\nLa conexión de EDUTURNOS a MySQL está lista.")
        return 0

    except Error as exc:
        if cnx is not None:
            try:
                cnx.rollback()
            except Exception:
                pass
        print("\nERROR AL CONFIGURAR LA BASE DE DATOS.")
        print(f"Código MySQL: {getattr(exc, 'errno', 'N/D')}")
        print(f"Detalle: {exc}")
        return 1
    except OSError as exc:
        print(f"\nNo se pudo leer {SQL_FILE}: {exc}")
        return 1
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


if __name__ == "__main__":
    raise SystemExit(main())
