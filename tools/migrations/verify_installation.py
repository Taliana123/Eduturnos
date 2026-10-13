from app import app
from database.db import comprobar_conexion, consultar
from routes.auth import _rol_id

REQUIRED_TABLES={'roles','permisos','rol_permiso','instituciones','sedes','jornadas','grados','grupos','periodos_academicos','usuarios','codigos_verificacion','estudiantes','acudientes','estudiante_acudiente','docentes','directorio_institucional','asignaciones_docentes','motivos','estados_cita','citas','seguimiento_citas','justificaciones','notificaciones','auditoria'}
with app.app_context():
    print('CONEXIÓN MYSQL:', 'OK' if comprobar_conexion() else 'ERROR')
    tables={r['Tables_in_eduturnos'] for r in consultar('SHOW TABLES')}
    missing=REQUIRED_TABLES-tables
    print('TABLAS ESPERADAS:',len(REQUIRED_TABLES)); print('TABLAS ENCONTRADAS:',len(tables)); print('ESTADO:', 'OK' if not missing else 'FALTAN: '+', '.join(sorted(missing)))
    print('ROLES CLAVE:', 'OK' if all(_rol_id(x) for x in ['Estudiante','Acudiente','Docente','Administrador / Coordinador','Rector']) else 'REVISAR')
