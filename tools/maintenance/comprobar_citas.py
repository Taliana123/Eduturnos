from flask import Flask
from database.db import consultar

app = Flask(__name__)

app.config.update(
    MYSQL_HOST="127.0.0.1",
    MYSQL_PORT=3306,
    MYSQL_USER="root",
    MYSQL_PASSWORD="",
    MYSQL_DATABASE="eduturnos",
    MYSQL_POOL_SIZE=5,
)

TABLAS = [
    "docentes",
    "usuarios",
    "motivos",
    "periodos_academicos",
    "estados_cita",
    "sedes",
    "jornadas",
    "grados",
    "grupos",
]

with app.app_context():

    print()
    print("========================================")
    print(" ESTRUCTURA DE TABLAS EDUTURNOS")
    print("========================================")

    for tabla in TABLAS:

        print()
        print(f"--- {tabla} ---")

        columnas = consultar(
            f"SHOW COLUMNS FROM `{tabla}`"
        )

        for columna in columnas:
            print(
                columna["Field"],
                "|",
                columna["Type"],
                "| Null=",
                columna["Null"],
                "| Default=",
                columna["Default"],
            )

    print()
    print("========================================")
    print(" FIN")
    print("========================================")