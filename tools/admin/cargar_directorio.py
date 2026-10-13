import csv
from pathlib import Path
import mysql.connector

print("=" * 50)
print("EDUTURNOS - CARGAR DIRECTORIO INSTITUCIONAL")
print("=" * 50)

servidor = input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"
puerto = input("Puerto [3306]: ").strip() or "3306"
usuario = input("Usuario [root]: ").strip() or "root"
password = input("Contraseña MySQL: ")

CSV_FILE = Path(__file__).resolve().parents[2] / "data" / "directorio_institucional.csv"

if not CSV_FILE.exists():
    raise SystemExit(
        "\nERROR: No existe:\n"
        + str(CSV_FILE)
        + "\n"
    )

conexion = None
cursor = None

try:

    conexion = mysql.connector.connect(
        host=servidor,
        port=int(puerto),
        user=usuario,
        password=password,
        database="eduturnos",
        connection_timeout=10
    )

    cursor = conexion.cursor(dictionary=True)

    print("\nConexión a MySQL correcta.")

    print("\nArchivo encontrado:")
    print(CSV_FILE)

    cursor.execute("SHOW COLUMNS FROM directorio_institucional")
    columnas = [fila["Field"] for fila in cursor.fetchall()]

    print("\nColumnas encontradas en directorio_institucional:")
    print(", ".join(columnas))

    columnas_necesarias = [
        "id_rol",
        "documento",
        "nombres",
        "apellidos",
        "correo_institucional",
        "id_sede",
        "id_jornada",
        "estado"
    ]

    faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in columnas
    ]

    if faltantes:
        raise SystemExit(
            "\nFALTAN COLUMNAS EN directorio_institucional:\n"
            + ", ".join(faltantes)
        )

    with CSV_FILE.open(
        encoding="utf-8-sig",
        newline=""
    ) as archivo:

        lector = csv.DictReader(archivo)

        print("\nColumnas del CSV:")
        print(", ".join(lector.fieldnames or []))

        requeridas_csv = [
            "rol",
            "documento",
            "nombres",
            "apellidos",
            "correo",
            "sede",
            "jornada"
        ]

        faltantes_csv = [
            columna
            for columna in requeridas_csv
            if columna not in (lector.fieldnames or [])
        ]

        if faltantes_csv:
            raise SystemExit(
                "\nFALTAN COLUMNAS EN EL CSV:\n"
                + ", ".join(faltantes_csv)
            )

        insertados = 0
        actualizados = 0

        for row in lector:

            rol_csv = row["rol"].strip()
            documento = row["documento"].strip()
            nombres = row["nombres"].strip()
            apellidos = row["apellidos"].strip()
            correo = row["correo"].strip().lower()
            sede = row["sede"].strip()
            jornada = row["jornada"].strip()

            print("\n----------------------------------------")
            print("Procesando:", nombres, apellidos)
            print("Documento:", documento)
            print("Rol:", rol_csv)
            print("Correo:", correo)
            print("Sede:", sede)
            print("Jornada:", jornada)

            roles = {
                "Docente": "Docente",
                "Coordinador": "Administrador / Coordinador",
                "Rector": "Rector"
            }

            rol = roles.get(rol_csv)

            if not rol:
                raise ValueError(
                    "Rol no válido: " + rol_csv
                )

            cursor.execute(
                """
                SELECT id
                FROM roles
                WHERE nombre=%s
                LIMIT 1
                """,
                (rol,)
            )

            r = cursor.fetchone()

            if not r:
                raise ValueError(
                    "No existe el rol en la base de datos: " + rol
                )

            cursor.execute(
                """
                SELECT id
                FROM sedes
                WHERE LOWER(nombre)=LOWER(%s)
                LIMIT 1
                """,
                (sede,)
            )

            s = cursor.fetchone()

            if not s:
                raise ValueError(
                    "No existe la sede: " + sede
                )

            cursor.execute(
                """
                SELECT id
                FROM jornadas
                WHERE LOWER(nombre)=LOWER(%s)
                LIMIT 1
                """,
                (jornada,)
            )

            j = cursor.fetchone()

            if not j:
                raise ValueError(
                    "No existe la jornada: " + jornada
                )

            cursor.execute(
                """
                SELECT id
                FROM directorio_institucional
                WHERE documento=%s
                LIMIT 1
                """,
                (documento,)
            )

            existente = cursor.fetchone()

            if existente:

                cursor.execute(
                    """
                    UPDATE directorio_institucional
                    SET
                        id_rol=%s,
                        nombres=%s,
                        apellidos=%s,
                        correo_institucional=%s,
                        id_sede=%s,
                        id_jornada=%s,
                        estado=1
                    WHERE id=%s
                    """,
                    (
                        r["id"],
                        nombres,
                        apellidos,
                        correo,
                        s["id"],
                        j["id"],
                        existente["id"]
                    )
                )

                actualizados += 1

                print("ACTUALIZADO correctamente.")

            else:

                cursor.execute(
                    """
                    INSERT INTO directorio_institucional
                    (
                        id_rol,
                        tipo_documento,
                        documento,
                        nombres,
                        apellidos,
                        correo_institucional,
                        id_sede,
                        id_jornada,
                        estado
                    )
                    VALUES
                    (
                        %s,
                        'CC',
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        1
                    )
                    """,
                    (
                        r["id"],
                        documento,
                        nombres,
                        apellidos,
                        correo,
                        s["id"],
                        j["id"]
                    )
                )

                insertados += 1

                print("INSERTADO correctamente.")

    conexion.commit()

    print("\n" + "=" * 50)
    print("DIRECTORIO CARGADO CORRECTAMENTE")
    print("=" * 50)
    print("Registros insertados:", insertados)
    print("Registros actualizados:", actualizados)
    print("=" * 50)

except mysql.connector.Error as e:

    print("\n" + "=" * 50)
    print("ERROR DE MYSQL")
    print("=" * 50)
    print(e)

    if conexion and conexion.is_connected():
        conexion.rollback()

except Exception as e:

    print("\n" + "=" * 50)
    print("ERROR")
    print("=" * 50)
    print(e)

    if conexion and conexion.is_connected():
        conexion.rollback()

finally:

    if cursor:
        cursor.close()

    if conexion and conexion.is_connected():
        conexion.close()

input("\nPresiona ENTER para cerrar...")