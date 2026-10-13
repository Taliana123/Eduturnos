from __future__ import annotations
import argparse
import mysql.connector
from getpass import getpass

p=argparse.ArgumentParser()
p.add_argument('--anio', type=int, required=True)
p.add_argument('--confirmar', action='store_true')
a=p.parse_args()
if not a.confirmar:
    raise SystemExit('Operación cancelada. Usa --confirmar.')
host=input('Servidor MySQL [127.0.0.1]: ').strip() or '127.0.0.1'
port=int(input('Puerto [3306]: ').strip() or '3306')
user=input('Usuario [root]: ').strip() or 'root'
password=getpass('Contraseña MySQL: ')
cnx=cur=None
try:
    cnx=mysql.connector.connect(host=host,port=port,user=user,password=password,database='eduturnos')
    cur=cnx.cursor()
    cur.execute('SELECT id FROM periodos_academicos WHERE YEAR(fecha_fin)=%s',(a.anio,))
    ids=[r[0] for r in cur.fetchall()]
    if not ids: raise RuntimeError('No existe un periodo académico para ese año.')
    marks=','.join(['%s']*len(ids))
    cur.execute(f'SELECT COUNT(*) FROM citas WHERE id_periodo IN ({marks})',tuple(ids))
    total=cur.fetchone()[0]
    print(f'Se eliminarán {total} citaciones. No se borrarán estudiantes, acudientes, docentes ni usuarios.')
    cur.execute(f'DELETE FROM citas WHERE id_periodo IN ({marks})',tuple(ids))
    cnx.commit(); print('Limpieza completada.')
except Exception as exc:
    if cnx: cnx.rollback()
    raise SystemExit(f'ERROR: {exc}')
finally:
    if cur: cur.close()
    if cnx: cnx.close()
