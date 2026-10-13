from getpass import getpass
from werkzeug.security import generate_password_hash
import mysql.connector

host=input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"
port=int(input("Puerto [3306]: ").strip() or "3306")
user=input("Usuario [root]: ").strip() or "root"
password_db=getpass("Contraseña MySQL: ")
rol=input("Rol (Docente/Administrador / Coordinador/Rector): ").strip()
documento=input("Documento: ").strip()
codigo=getpass("Código individual de 6 dígitos asignado por la institución: ").strip()
if not (len(codigo)==6 and codigo.isdigit()):
    raise SystemExit("El código debe tener exactamente 6 dígitos.")
cnx=mysql.connector.connect(host=host,port=port,user=user,password=password_db,database="eduturnos")
cur=cnx.cursor()
try:
    cur.execute("SELECT id FROM roles WHERE nombre=%s", (rol,)); r=cur.fetchone()
    if not r: raise SystemExit("Rol no encontrado")
    cur.execute("SELECT id FROM directorio_institucional WHERE documento=%s AND id_rol=%s", (documento,r[0])); d=cur.fetchone()
    if not d: raise SystemExit("Persona no encontrada en directorio institucional")
    cur.execute("UPDATE directorio_institucional SET codigo_institucional_hash=%s WHERE id=%s", (generate_password_hash(codigo),d[0]))
    cnx.commit(); print("Código guardado: solo queda almacenado su hash.")
finally:
    cur.close(); cnx.close()
