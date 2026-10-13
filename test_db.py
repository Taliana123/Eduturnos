from app import app
from database.db import comprobar_conexion


with app.app_context():
    try:
        comprobar_conexion()
        print("====================================")
        print("CONEXION EXITOSA A MYSQL")
        print(f"BASE DE DATOS: {app.config['MYSQL_DATABASE']}")
        print("====================================")
    except Exception as exc:
        print("====================================")
        print("ERROR DE CONEXION A MYSQL")
        print(exc)
        print("====================================")
        raise SystemExit(1)
