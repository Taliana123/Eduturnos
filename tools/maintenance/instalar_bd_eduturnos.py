import mysql.connector
from pathlib import Path
from datetime import datetime
import re

BASE = Path(r"D:\edu_Final")
SQL_DIR = BASE / "sql"

DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "eduturnos"

def conectar(database=None):
    config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD
    }

    if database:
        config["database"] = database

    return mysql.connector.connect(**config)

def ejecutar_script(conn, ruta):
    print(f"\nEjecutando: {ruta.name}")

    texto = ruta.read_text(encoding="utf-8")

    # Eliminar USE eduturnos porque ya estamos conectados a la BD.
    texto = re.sub(r'(?im)^\s*USE\s+`?eduturnos`?\s*;\s*', '', texto)

    # Separar sentencias SQL respetando ; dentro de textos simples.
    sentencias = []
    actual = []
    dentro_string = False
    escape = False

    for caracter in texto:
        if caracter == "\\" and dentro_string and not escape:
            escape = True
            actual.append(caracter)
            continue

        if caracter == "'" and not escape:
            dentro_string = not dentro_string

        if caracter == ";" and not dentro_string:
            sentencia = "".join(actual).strip()
            if sentencia:
                sentencias.append(sentencia)
            actual = []
        else:
            actual.append(caracter)

        escape = False

    ultimo = "".join(actual).strip()
    if ultimo:
        sentencias.append(ultimo)

    cur = conn.cursor()

    for i, sentencia in enumerate(sentencias, 1):
        try:
            cur.execute(sentencia)
            conn.commit()
        except Exception as e:
            print(f"ERROR en sentencia {i}:")
            print(str(e))
            print("Sentencia:")
            print(sentencia[:1000])
            cur.close()
            raise

    cur.close()

def tabla_existe(cur, tabla):
    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_name = %s
    """, (DB_NAME, tabla))
    return cur.fetchone()[0] == 1

def columna_existe(cur, tabla, columna):
    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
          AND column_name = %s
    """, (DB_NAME, tabla, columna))
    return cur.fetchone()[0] == 1

print("=" * 70)
print(" INSTALACION SEGURA DEL ESQUEMA EDUTURNOS")
print("=" * 70)

# ------------------------------------------------------------
# 1. CONEXION
# ------------------------------------------------------------

print("\n[1/8] Comprobando conexion a MySQL...")

try:
    conn = conectar(DB_NAME)
    cur = conn.cursor()
    print("CONEXION EXITOSA")
except Exception as e:
    print("NO SE PUDO CONECTAR A MYSQL")
    print(e)
    raise SystemExit(1)

# ------------------------------------------------------------
# 2. COMPROBAR QUE LA BASE ESTA VACIA
# ------------------------------------------------------------

print("\n[2/8] Comprobando datos existentes...")

cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = %s
    ORDER BY table_name
""", (DB_NAME,))

tablas_actuales = [fila[0] for fila in cur.fetchall()]

total_registros = 0

for tabla in tablas_actuales:
    try:
        cur.execute(f"SELECT COUNT(*) FROM `{tabla}`")
        cantidad = cur.fetchone()[0]
        total_registros += cantidad
        print(f"{tabla:30} {cantidad}")
    except Exception:
        pass

if total_registros != 0:
    print("\nABORTADO.")
    print("La base contiene registros y no se va a modificar automaticamente.")
    cur.close()
    conn.close()
    raise SystemExit(2)

print("\nLa base no contiene registros.")

# ------------------------------------------------------------
# 3. RESPALDO ESTRUCTURAL
# ------------------------------------------------------------

print("\n[3/8] Guardando respaldo de la estructura actual...")

respaldo = BASE / (
    "respaldo_estructura_eduturnos_" +
    datetime.now().strftime("%Y%m%d_%H%M%S") +
    ".sql"
)

with open(respaldo, "w", encoding="utf-8") as f:
    f.write("-- Respaldo estructural de EDUTURNOS\n")
    f.write("-- Fecha: " + datetime.now().isoformat() + "\n\n")
    f.write(f"-- Base de datos: {DB_NAME}\n\n")

    for tabla in tablas_actuales:
        cur.execute(f"SHOW CREATE TABLE `{tabla}`")
        fila = cur.fetchone()

        if fila:
            f.write(f"-- Tabla {tabla}\n")
            f.write(f"{fila[1]};\n\n")

print("Respaldo creado:")
print(respaldo)

# ------------------------------------------------------------
# 4. ELIMINAR SOLO LAS TABLAS VACIAS
# ------------------------------------------------------------

print("\n[4/8] Eliminando tablas antiguas vacias...")

cur.execute("SET FOREIGN_KEY_CHECKS = 0")

for tabla in tablas_actuales:
    print("Eliminando:", tabla)
    cur.execute(f"DROP TABLE IF EXISTS `{tabla}`")

cur.execute("SET FOREIGN_KEY_CHECKS = 1")
conn.commit()

print("Tablas antiguas eliminadas correctamente.")

# ------------------------------------------------------------
# 5. INSTALAR ESQUEMA PRINCIPAL
# ------------------------------------------------------------

print("\n[5/8] Instalando eduturnos.sql...")

ejecutar_script(conn, SQL_DIR / "eduturnos.sql")

print("Esquema principal instalado.")

# ------------------------------------------------------------
# 6. AUTENTICACION
# ------------------------------------------------------------

print("\n[6/8] Preparando autenticacion...")

ejecutar_script(conn, SQL_DIR / "auth_migration.sql")

print("Tabla codigos_acceso preparada.")

# ------------------------------------------------------------
# 7. IDENTIDAD INSTITUCIONAL
# ------------------------------------------------------------

print("\n[7/8] Preparando identidad institucional...")

cur = conn.cursor()

# docentes.codigo_institucional_hash
if not columna_existe(cur, "docentes", "codigo_institucional_hash"):
    print("Agregando docentes.codigo_institucional_hash...")
    cur.execute("""
        ALTER TABLE docentes
        ADD COLUMN codigo_institucional_hash VARCHAR(255) NULL
    """)
    conn.commit()
else:
    print("docentes.codigo_institucional_hash ya existe.")

# directorio_institucional.id_sede
if not columna_existe(cur, "directorio_institucional", "id_sede"):
    print("Agregando directorio_institucional.id_sede...")
    cur.execute("""
        ALTER TABLE directorio_institucional
        ADD COLUMN id_sede INT NULL
    """)
    conn.commit()
else:
    print("directorio_institucional.id_sede ya existe.")

# directorio_institucional.codigo_institucional_hash
if not columna_existe(cur, "directorio_institucional", "codigo_institucional_hash"):
    print("Agregando directorio_institucional.codigo_institucional_hash...")
    cur.execute("""
        ALTER TABLE directorio_institucional
        ADD COLUMN codigo_institucional_hash VARCHAR(255) NULL
    """)
    conn.commit()
else:
    print("directorio_institucional.codigo_institucional_hash ya existe.")

# Comprobar FK antes de crearla
cur.execute("""
    SELECT COUNT(*)
    FROM information_schema.table_constraints
    WHERE constraint_schema = %s
      AND table_name = 'directorio_institucional'
      AND constraint_name = 'fk_directorio_sede'
""", (DB_NAME,))

fk_existe = cur.fetchone()[0] == 1

if not fk_existe:
    print("Creando FK fk_directorio_sede...")
    cur.execute("""
        ALTER TABLE directorio_institucional
        ADD CONSTRAINT fk_directorio_sede
        FOREIGN KEY (id_sede)
        REFERENCES sedes(id)
        ON DELETE SET NULL
    """)
    conn.commit()
else:
    print("FK fk_directorio_sede ya existe.")

cur.close()

# ------------------------------------------------------------
# 8. VERIFICACION FINAL
# ------------------------------------------------------------

print("\n[8/8] Verificacion final...")

cur = conn.cursor()

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

faltantes = []

for tabla in tablas_necesarias:
    if tabla_existe(cur, tabla):
        print(f"[OK] {tabla}")
    else:
        print(f"[FALTA] {tabla}")
        faltantes.append(tabla)

print("\nDATOS INICIALES:")

for tabla in [
    "roles",
    "permisos",
    "instituciones",
    "sedes",
    "jornadas",
    "grados",
    "motivos",
    "estados_cita"
]:
    try:
        cur.execute(f"SELECT COUNT(*) FROM `{tabla}`")
        cantidad = cur.fetchone()[0]
        print(f"{tabla:30} {cantidad}")
    except Exception as e:
        print(f"{tabla:30} ERROR")

print("\nCOLUMNAS CRITICAS:")

for tabla, columna in [
    ("usuarios", "id_rol"),
    ("usuarios", "password_hash"),
    ("usuarios", "intentos_fallidos"),
    ("usuarios", "bloqueado_hasta"),
    ("usuarios", "ultimo_acceso"),
    ("docentes", "codigo_institucional_hash"),
    ("directorio_institucional", "id_sede"),
    ("directorio_institucional", "codigo_institucional_hash"),
    ("citas", "recordatorio_24h_enviado"),
    ("citas", "recordatorio_2h_enviado")
]:
    if columna_existe(cur, tabla, columna):
        print(f"[OK] {tabla}.{columna}")
    else:
        print(f"[FALTA] {tabla}.{columna}")
        faltantes.append(f"{tabla}.{columna}")

cur.close()
conn.close()

print("\n" + "=" * 70)

if faltantes:
    print("INSTALACION TERMINADA CON ELEMENTOS FALTANTES")
    print("=" * 70)
    for elemento in faltantes:
        print("-", elemento)
    raise SystemExit(3)

print("EDUTURNOS: BASE DE DATOS INSTALADA CORRECTAMENTE")
print("=" * 70)
print("27 tablas principales + codigos_acceso")
print("Autenticacion preparada")
print("Seguridad preparada")
print("Identidad institucional preparada")
print("Recordatorios de citas preparados")
print("")
print("Respaldo estructural:")
print(respaldo)
print("=" * 70)