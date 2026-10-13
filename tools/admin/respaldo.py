import argparse
import base64
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import sys
import uuid

import mysql.connector

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from config import Config


def codificar(valor):
    if isinstance(valor, bytes):
        return {"tipo": "bytes", "valor": base64.b64encode(valor).decode("ascii")}
    if isinstance(valor, (datetime, date, time)):
        return {"tipo": type(valor).__name__, "valor": valor.isoformat()}
    if isinstance(valor, timedelta):
        return {"tipo": "timedelta", "valor": valor.total_seconds()}
    if isinstance(valor, Decimal):
        return {"tipo": "Decimal", "valor": str(valor)}
    raise TypeError(f"Tipo no soportado: {type(valor).__name__}")


def decodificar(valor):
    conversiones = {"datetime": datetime.fromisoformat, "date": date.fromisoformat, "time": time.fromisoformat, "Decimal": Decimal, "bytes": base64.b64decode, "timedelta": lambda segundos: timedelta(seconds=segundos)}
    if set(valor) == {"tipo", "valor"} and valor["tipo"] in conversiones:
        return conversiones[valor["tipo"]](valor["valor"])
    return valor


def configuracion():
    return dict(host=Config.MYSQL_HOST, port=Config.MYSQL_PORT, user=Config.MYSQL_USER, password=Config.MYSQL_PASSWORD, database=Config.MYSQL_DATABASE, connection_timeout=10)


def identificador(nombre):
    return "`" + nombre.replace("`", "``") + "`"


def crear_respaldo():
    destino = ROOT / "data" / "private" / "backups"
    destino.mkdir(parents=True, exist_ok=True)
    archivo = destino / f"eduturnos_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}.json.gz"
    cnx = mysql.connector.connect(**configuracion())
    cursor = cnx.cursor(buffered=True)
    contenido = {"version": 1, "creado": datetime.now().isoformat(), "database": Config.MYSQL_DATABASE, "tablas": []}
    try:
        cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        cursor.execute("START TRANSACTION WITH CONSISTENT SNAPSHOT")
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
        nombres = [fila[0] for fila in cursor.fetchall()]
        for nombre in nombres:
            cursor.execute(f"SHOW CREATE TABLE {identificador(nombre)}")
            esquema = cursor.fetchone()[1]
            cursor.execute(f"SELECT * FROM {identificador(nombre)}")
            columnas = list(cursor.column_names)
            contenido["tablas"].append({"nombre": nombre, "esquema": esquema, "columnas": columnas, "filas": cursor.fetchall()})
        cnx.rollback()
        temporal = archivo.with_suffix(".tmp")
        with gzip.open(temporal, "wt", encoding="utf-8") as salida:
            json.dump(contenido, salida, default=codificar, ensure_ascii=False)
        temporal.replace(archivo)
        archivo.with_suffix(archivo.suffix + ".sha256").write_text(hashlib.sha256(archivo.read_bytes()).hexdigest(), encoding="ascii")
        print(f"Respaldo creado: {archivo.name}; tablas: {len(nombres)}")
        return archivo
    finally:
        cursor.close()
        cnx.close()


def leer_respaldo(archivo):
    archivo = Path(archivo)
    esperado = archivo.with_suffix(archivo.suffix + ".sha256").read_text(encoding="ascii").strip()
    if hashlib.sha256(archivo.read_bytes()).hexdigest() != esperado:
        raise ValueError("La verificación de integridad del respaldo falló.")
    with gzip.open(archivo, "rt", encoding="utf-8") as entrada:
        contenido = json.load(entrada, object_hook=decodificar)
    if contenido.get("version") != 1 or not contenido.get("tablas"):
        raise ValueError("Formato de respaldo inválido.")
    return contenido


def probar_restauracion(archivo):
    contenido = leer_respaldo(archivo)
    nombre = "eduturnos_prueba_" + uuid.uuid4().hex[:16]
    cfg = configuracion()
    cfg.pop("database")
    cnx = mysql.connector.connect(**cfg)
    cursor = cnx.cursor(buffered=True)
    creada = False
    try:
        cursor.execute(f"CREATE DATABASE {identificador(nombre)} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        creada = True
        cursor.execute(f"USE {identificador(nombre)}")
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        for tabla in contenido["tablas"]:
            cursor.execute(tabla["esquema"])
        for tabla in contenido["tablas"]:
            if tabla["filas"]:
                columnas = ",".join(identificador(columna) for columna in tabla["columnas"])
                placeholders = ",".join(["%s"] * len(tabla["columnas"]))
                cursor.executemany(f"INSERT INTO {identificador(tabla['nombre'])} ({columnas}) VALUES ({placeholders})", tabla["filas"])
            cursor.execute(f"SELECT COUNT(*) FROM {identificador(tabla['nombre'])}")
            if cursor.fetchone()[0] != len(tabla["filas"]):
                raise ValueError("El conteo de registros restaurados no coincide.")
        cnx.commit()
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        print(f"Restauración verificada en una base temporal: {len(contenido['tablas'])} tablas.")
    finally:
        if creada:
            cursor.execute(f"DROP DATABASE {identificador(nombre)}")
        cursor.close()
        cnx.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verificar", type=Path)
    parser.add_argument("--probar-restauracion", action="store_true")
    args = parser.parse_args()
    archivo = args.verificar or crear_respaldo()
    leer_respaldo(archivo)
    print("Integridad verificada.")
    if args.probar_restauracion:
        probar_restauracion(archivo)


if __name__ == "__main__":
    main()