import mysql.connector

password = input("Contraseña MySQL: ")

conexion = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=password,
    database="eduturnos"
)

cursor = conexion.cursor()

print("Agregando id_sede...")

cursor.execute("""
ALTER TABLE directorio_institucional
ADD COLUMN id_sede INT NULL AFTER id_rol
""")

print("Agregando índice...")

cursor.execute("""
ALTER TABLE directorio_institucional
ADD INDEX idx_directorio_sede (id_sede)
""")

print("Agregando relación con sedes...")

cursor.execute("""
ALTER TABLE directorio_institucional
ADD CONSTRAINT fk_directorio_sede
FOREIGN KEY (id_sede)
REFERENCES sedes(id)
ON DELETE RESTRICT
ON UPDATE CASCADE
""")

conexion.commit()

print()
print("========================================")
print("CORREGIDO CORRECTAMENTE")
print("Se agregó id_sede a directorio_institucional")
print("========================================")

cursor.close()
conexion.close()