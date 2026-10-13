import mysql.connector

config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "eduturnos"
}

try:
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()

    print("=" * 60)
    print("REVISION DE DATOS ACTUALES DE EDUTURNOS")
    print("=" * 60)

    tablas = [
        "usuarios",
        "estudiantes",
        "acudientes",
        "docentes",
        "coordinadores",
        "citas",
        "motivos",
        "notificaciones",
        "asistencias",
        "evidencias",
        "historial",
        "control_acceso",
        "disponibilidad",
        "estudiante_acudiente"
    ]

    for tabla in tablas:
        try:
            cur.execute(f"SELECT COUNT(*) FROM `{tabla}`")
            cantidad = cur.fetchone()[0]
            print(f"{tabla:25} {cantidad} registros")
        except Exception:
            print(f"{tabla:25} NO DISPONIBLE")

    print("=" * 60)
    print("REVISION TERMINADA")
    print("=" * 60)

    cur.close()
    conn.close()

except Exception as e:
    print("ERROR DE CONEXION:")
    print(e)