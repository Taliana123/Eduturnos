@'
import mysql.connector

print("=" * 60)
print("EDUTURNOS - VERIFICAR REGISTRO INSTITUCIONAL")
print("=" * 60)

servidor = input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"
puerto = input("Puerto [3306]: ").strip() or "3306"
usuario = input("Usuario [root]: ").strip() or "root"
password = input("Contraseña MySQL: ")

conexion = None
cursor = None

try:
    conexion = mysql.connector.connect(
        host=servidor,
        port=int(puerto),
        user=usuario,
        password=password,
        database="eduturnos"
    )

    cursor = conexion.cursor(dictionary=True)

    print("\n========================================")
    print("REGISTROS INSTITUCIONALES")
    print("========================================")

    cursor.execute("""
        SELECT
            id,
            id_usuario,
            id_rol,
            rol_nombre,
            tipo_documento,
            documento,
            nombres,
            apellidos,
            correo,
            estado,
            fecha_vinculacion
        FROM directorio_institucional
        ORDER BY id
    """)

    registros = cursor.fetchall()

    if not registros:
        print("\nNO HAY REGISTROS EN EL DIRECTORIO.")
    else:
        for r in registros:
            print("\n----------------------------------------")
            print("ID:             ", r["id"])
            print("ID usuario:     ", r["id_usuario"])
            print("Rol:            ", r["rol_nombre"])
            print("Tipo documento: ", r["tipo_documento"])
            print("Documento:      ", r["documento"])
            print("Nombres:        ", r["nombres"])
            print("Apellidos:      ", r["apellidos"])
            print("Correo:         ", r["correo"])
            print("Estado:         ", r["estado"])
            print("Fecha vínculo:  ", r["fecha_vinculacion"])

    print("\n========================================")
    print("TOTAL DE REGISTROS:", len(registros))
    print("========================================")

except mysql.connector.Error as e:
    print("\nERROR DE MYSQL:")
    print(e)

except Exception as e:
    print("\nERROR:")
    print(e)

finally:
    if cursor:
        cursor.close()

    if conexion and conexion.is_connected():
        conexion.close()

input("\nPresiona ENTER para cerrar...")