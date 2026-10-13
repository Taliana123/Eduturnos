from getpass import getpass
from pathlib import Path
import argparse
import mysql.connector
from mysql.connector import Error

ROOT=Path(__file__).resolve().parents[2]
SQL_FILE=ROOT/"database"/"eduturnos.sql"

def statements(text):
    out=[]; cur=[]
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("--"): continue
        cur.append(line)
        if line.strip().endswith(";"):
            out.append("\n".join(cur)); cur=[]
    if cur: out.append("\n".join(cur))
    return out

p=argparse.ArgumentParser(description="Configura EDUTURNOS en MySQL")
p.add_argument("--recrear",action="store_true",help="Elimina y recrea eduturnos. Solo para instalaciones de prueba.")
args=p.parse_args()
print("="*64); print("EDUTURNOS - CONFIGURACIÓN DE BASE DE DATOS"); print("="*64)
print("Modo seguro: no se borrarán datos existentes." if not args.recrear else "MODO RECREAR: se borrará la base eduturnos.")
host=input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"; port=int(input("Puerto [3306]: ").strip() or "3306"); user=input("Usuario [root]: ").strip() or "root"; password=getpass("Contraseña MySQL (Enter si no tiene): ")
cnx=cur=None
try:
    cnx=mysql.connector.connect(host=host,port=port,user=user,password=password,connection_timeout=8); cur=cnx.cursor()
    if args.recrear: cur.execute("DROP DATABASE IF EXISTS eduturnos")
    cur.execute("CREATE DATABASE IF NOT EXISTS eduturnos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"); cur.execute("USE eduturnos")
    for st in statements(SQL_FILE.read_text(encoding="utf-8")):
        up=st.strip().upper()
        if up.startswith("CREATE DATABASE") or up.startswith("USE EDUTURNOS"): continue
        try: cur.execute(st)
        except mysql.connector.Error as exc:
            # Idempotency: duplicate seed rows are ignored by the schema; only fail on real DDL/data errors.
            raise RuntimeError(f"SQL inválido o incompatible: {exc}\n\n{st[:500]}") from exc
    cnx.commit(); cur.execute("SHOW TABLES"); tables=[r[0] for r in cur.fetchall()]
    print(f"\nBase eduturnos lista. Tablas encontradas: {len(tables)}")
    return_code=0
except (Error,ValueError,RuntimeError) as exc:
    if cnx: cnx.rollback()
    print(f"\nERROR: {exc}"); return_code=1
finally:
    if cur: cur.close()
    if cnx and cnx.is_connected(): cnx.close()
raise SystemExit(return_code)
