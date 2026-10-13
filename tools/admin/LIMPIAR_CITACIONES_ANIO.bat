import os
import sys
import logging
from datetime import datetime, timedelta
from database.db import get_db_connection
from servicios.email import enviar_correo_recordatorio

# Control de instancia única mediante archivo de bloqueo (lockfile)
LOCK_FILE = os.path.join(os.path.dirname(__file__), 'recordatorios.lock')

def obtener_bloqueo():
    if os.path.exists(LOCK_FILE):
        # Si el archivo tiene más de 10 minutos, lo consideramos huérfano y lo removemos
        mtime = datetime.fromtimestamp(os.path.getmtime(LOCK_FILE))
        if datetime.now() - mtime > timedelta(minutes=10):
            os.remove(LOCK_FILE)
        else:
            print("El proceso de recordatorios ya se encuentra en ejecución.")
            sys.exit(0)
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def liberar_bloqueo():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def procesar_recordatorios():
    obtener_bloqueo()
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Recordatorios de 24 horas
            query_24h = """
                SELECT c.id_citacion, c.fecha_citacion, c.hora_citacion, c.lugar,
                       e.nombres AS est_nombre, e.apellidos AS est_apellido,
                       a.correo AS acudiente_correo, u.correo_electronico AS docente_correo
                FROM citaciones c
                JOIN estudiantes e ON c.id_estudiante = e.id_estudiante
                JOIN acudientes a ON c.id_acudiente = a.id_acudiente
                JOIN docentes d ON c.id_docente = d.id_docente
                JOIN usuarios u ON d.id_usuario = u.id_usuario
                WHERE c.id_estado IN (1, 2)
                  AND CONCAT(c.fecha_citacion, ' ', c.hora_citacion) BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR)
                  AND c.id_citacion NOT IN (
                      SELECT id_citacion FROM recordatorios_enviados WHERE tipo_recordatorio = '24H'
                  )
            """
            cursor.execute(query_24h)
            citaciones_24h = cursor.fetchall()
            for cit in citaciones_24h:
                enviar_correo_recordatorio(cit, tipo='24H')
                cursor.execute(
                    "INSERT INTO recordatorios_enviados (id_citacion, tipo_recordatorio, fecha_envio) VALUES (%s, '24H', NOW())",
                    (cit['id_citacion'],)
                )

            # Recordatorios de 2 horas
            query_2h = """
                SELECT c.id_citacion, c.fecha_citacion, c.hora_citacion, c.lugar,
                       e.nombres AS est_nombre, e.apellidos AS est_apellido,
                       a.correo AS acudiente_correo, u.correo_electronico AS docente_correo
                FROM citaciones c
                JOIN estudiantes e ON c.id_estudiante = e.id_estudiante
                JOIN acudientes a ON c.id_acudiente = a.id_acudiente
                JOIN docentes d ON c.id_docente = d.id_docente
                JOIN usuarios u ON d.id_usuario = u.id_usuario
                WHERE c.id_estado IN (1, 2)
                  AND CONCAT(c.fecha_citacion, ' ', c.hora_citacion) BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 2 HOUR)
                  AND c.id_citacion NOT IN (
                      SELECT id_citacion FROM recordatorios_enviados WHERE tipo_recordatorio = '2H'
                  )
            """
            cursor.execute(query_2h)
            citaciones_2h = cursor.fetchall()
            for cit in citaciones_2h:
                enviar_correo_recordatorio(cit, tipo='2H')
                cursor.execute(
                    "INSERT INTO recordatorios_enviados (id_citacion, tipo_recordatorio, fecha_envio) VALUES (%s, '2H', NOW())",
                    (cit['id_citacion'],)
                )

        conn.commit()
        conn.close()
    finally:
        liberar_bloqueo()

if __name__ == '__main__':
    procesar_recordatorios()