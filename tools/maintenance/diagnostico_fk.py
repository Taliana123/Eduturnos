import mysql.connector

config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "eduturnos"
}

conn = mysql.connector.connect(**config)
cur = conn.cursor()

print("=" * 70)
print("DIAGNOSTICO DE FK: directorio_institucional -> sedes")
print("=" * 70)

print("\n[1] ESTRUCTURA DE sedes")
cur.execute("SHOW CREATE TABLE sedes")
fila = cur.fetchone()
print(fila[1])

print("\n[2] ESTRUCTURA DE directorio_institucional")
cur.execute("SHOW CREATE TABLE directorio_institucional")
fila = cur.fetchone()
print(fila[1])

print("\n[3] TIPO EXACTO DE sedes.id")
cur.execute("""
    SELECT
        COLUMN_NAME,
        COLUMN_TYPE,
        IS_NULLABLE,
        COLUMN_KEY,
        EXTRA
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'eduturnos'
      AND TABLE_NAME = 'sedes'
      AND COLUMN_NAME = 'id'
""")

for fila in cur.fetchall():
    print(fila)

print("\n[4] TIPO EXACTO DE directorio_institucional.id_sede")
cur.execute("""
    SELECT
        COLUMN_NAME,
        COLUMN_TYPE,
        IS_NULLABLE,
        COLUMN_KEY,
        EXTRA
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'eduturnos'
      AND TABLE_NAME = 'directorio_institucional'
      AND COLUMN_NAME = 'id_sede'
""")

for fila in cur.fetchall():
    print(fila)

print("\n[5] INDICES DE sedes")
cur.execute("SHOW INDEX FROM sedes")

for fila in cur.fetchall():
    print(fila)

print("\n[6] FOREIGN KEYS DE directorio_institucional")
cur.execute("""
    SELECT
        CONSTRAINT_NAME,
        COLUMN_NAME,
        REFERENCED_TABLE_NAME,
        REFERENCED_COLUMN_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'eduturnos'
      AND TABLE_NAME = 'directorio_institucional'
      AND REFERENCED_TABLE_NAME IS NOT NULL
""")

for fila in cur.fetchall():
    print(fila)

print("\n" + "=" * 70)
print("DIAGNOSTICO TERMINADO")
print("=" * 70)

cur.close()
conn.close()