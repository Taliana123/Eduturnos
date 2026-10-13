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
print("VERIFICACION FINAL DE LA BASE DE DATOS EDUTURNOS")
print("=" * 70)

tablas_necesarias = [
    "roles",
    "permisos",
    "rol_permiso",
    "instituciones",
    "sedes",
    "jornadas",
    "grados",
    "grupos",
    "periodos_academicos",
    "usuarios",
    "estudiantes",
    "acudientes",
    "estudiante_acudiente",
    "docentes",
    "asignaciones_docentes",
    "motivos",
    "estados_cita",
    "directorio_institucional",
    "citas",
    "solicitudes_cita",
    "seguimiento_citas",
    "justificaciones",
    "notificaciones",
    "codigos_verificacion",
    "control_acceso",
    "tokens_recuperacion",
    "auditoria",
    "codigos_acceso"
]

def existe(tabla):
    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = 'eduturnos'
          AND TABLE_NAME = %s
    """, (tabla,))
    return cur.fetchone()[0] == 1

faltantes = []

print("\n[1] TABLAS")
for tabla in tablas_necesarias:
    if existe(tabla):
        print(f"[OK]     {tabla}")
    else:
        print(f"[FALTA]  {tabla}")
        faltantes.append(tabla)

print("\n[2] CANTIDAD DE REGISTROS INICIALES")
for tabla in [
    "roles",
    "permisos",
    "instituciones",
    "sedes",
    "jornadas",
    "grados",
    "grupos",
    "periodos_academicos",
    "motivos",
    "estados_cita",
    "usuarios",
    "estudiantes",
    "acudientes",
    "docentes",
    "citas",
    "notificaciones"
]:
    try:
        cur.execute(f"SELECT COUNT(*) FROM `{tabla}`")
        cantidad = cur.fetchone()[0]
        print(f"{tabla:30} {cantidad}")
    except Exception as e:
        print(f"{tabla:30} ERROR: {e}")

print("\n[3] COLUMNAS CRITICAS")

columnas = [
    ("usuarios", "id_rol"),
    ("usuarios", "password_hash"),
    ("usuarios", "verificado"),
    ("usuarios", "intentos_fallidos"),
    ("usuarios", "bloqueado_hasta"),
    ("usuarios", "ultimo_acceso"),

    ("docentes", "id_usuario"),
    ("docentes", "codigo_institucional_hash"),

    ("estudiantes", "id_usuario"),

    ("directorio_institucional", "id_usuario"),
    ("directorio_institucional", "id_rol"),
    ("directorio_institucional", "id_sede"),
    ("directorio_institucional", "codigo_institucional_hash"),

    ("citas", "recordatorio_24h_enviado"),
    ("citas", "recordatorio_2h_enviado"),

    ("codigos_acceso", "codigo_hash"),
    ("codigos_acceso", "fecha_expiracion"),
    ("codigos_acceso", "usado")
]

for tabla, columna in columnas:
    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'eduturnos'
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
    """, (tabla, columna))

    if cur.fetchone()[0] == 1:
        print(f"[OK]     {tabla}.{columna}")
    else:
        print(f"[FALTA]  {tabla}.{columna}")
        faltantes.append(f"{tabla}.{columna}")

print("\n[4] FOREIGN KEYS DE directorio_institucional")

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
    ORDER BY CONSTRAINT_NAME
""")

for fila in cur.fetchall():
    print(
        f"[OK] {fila[0]}: "
        f"{fila[1]} -> {fila[2]}.{fila[3]}"
    )

print("\n[5] FOREIGN KEY id_sede")

cur.execute("""
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'eduturnos'
      AND TABLE_NAME = 'directorio_institucional'
      AND COLUMN_NAME = 'id_sede'
      AND REFERENCED_TABLE_NAME = 'sedes'
      AND REFERENCED_COLUMN_NAME = 'id'
""")

if cur.fetchone()[0] == 1:
    print("[OK] directorio_institucional.id_sede -> sedes.id")
else:
    print("[FALTA] directorio_institucional.id_sede -> sedes.id")
    faltantes.append("FK directorio_institucional.id_sede -> sedes.id")

print("\n[6] ESTRUCTURA GENERAL DE TABLAS")

cur.execute("""
    SELECT COUNT(*)
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = 'eduturnos'
      AND TABLE_TYPE = 'BASE TABLE'
""")

total = cur.fetchone()[0]
print("Total de tablas encontradas:", total)

print("\n" + "=" * 70)

if faltantes:
    print("VERIFICACION CON ELEMENTOS FALTANTES")
    print("=" * 70)

    for elemento in faltantes:
        print("-", elemento)

    raise SystemExit(3)

print("EDUTURNOS: BASE DE DATOS VERIFICADA CORRECTAMENTE")
print("=" * 70)
print("Esquema principal instalado")
print("Autenticacion preparada")
print("Seguridad preparada")
print("Identidad institucional preparada")
print("Recordatorios de citas preparados")
print("FK de sede verificada")
print("=" * 70)

cur.close()
conn.close()