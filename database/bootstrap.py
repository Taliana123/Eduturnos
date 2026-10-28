import mysql.connector
from pathlib import Path
from flask import current_app


def ensure_database(config=None):
    """
    Comprueba que EDUTURNOS pueda conectarse a la base de datos.
    La configuración inicial de MySQL se realiza mediante
    PRIMERA_VEZ.bat / setup_database.py, no en cada arranque de Flask.
    """
    cfg = config or current_app.config

    cnx = None
    cursor = None

    try:
        cnx = mysql.connector.connect(
            host=cfg["MYSQL_HOST"],
            port=cfg["MYSQL_PORT"],
            user=cfg["MYSQL_USER"],
            password=cfg["MYSQL_PASSWORD"],
            database=cfg["MYSQL_DATABASE"],
            connection_timeout=8,
        )

        # Cursor con resultados almacenados para evitar
        # "Unread result found" entre consultas consecutivas.
        cursor = cnx.cursor(buffered=True)

        cursor.execute("SELECT 1")
        cursor.fetchone()

        # Migraciones pequeñas y seguras para instalaciones existentes.
        # Guarda la descripcion del motivo personalizado.
        cursor.execute("SHOW COLUMNS FROM citas LIKE 'motivo_otro'")
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE citas ADD COLUMN motivo_otro VARCHAR(255) NULL"
            )

        # La creación inicial completa sigue estando en database/eduturnos.sql.

        cursor.execute(
            "SHOW COLUMNS FROM citas LIKE 'recordatorio_24h_enviado'"
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE citas "
                "ADD COLUMN recordatorio_24h_enviado "
                "TINYINT(1) NOT NULL DEFAULT 0"
            )

        cursor.execute(
            "SHOW COLUMNS FROM citas LIKE 'recordatorio_2h_enviado'"
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE citas "
                "ADD COLUMN recordatorio_2h_enviado "
                "TINYINT(1) NOT NULL DEFAULT 0"
            )

        cursor.execute(
            "SHOW INDEX FROM citas WHERE Key_name = 'idx_cita_recordatorios'"
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "CREATE INDEX idx_cita_recordatorios "
                "ON citas "
                "(fecha, hora, recordatorio_24h_enviado, recordatorio_2h_enviado)"
            )

        migracion_escolar = Path(__file__).resolve().parents[1] / "sql" / "school_workflow.sql"
        cursor.execute(migracion_escolar.read_text(encoding="utf-8"))
        while cursor.nextset():
            pass
        migracion_google = Path(__file__).resolve().parents[1] / "sql" / "google_calendar_sync.sql"
        for sentencia in migracion_google.read_text(encoding="utf-8").split(";"):
            sentencia = sentencia.strip()
            if not sentencia:
                continue
            if sentencia.upper().startswith("ALTER TABLE INTEGRACIONES_GOOGLE"):
                cursor.execute("SHOW COLUMNS FROM integraciones_google LIKE 'fecha_prueba'")
                if cursor.fetchone() is not None:
                    continue
            if sentencia.upper().startswith("ALTER TABLE EVENTOS_GOOGLE"):
                cursor.execute("SHOW COLUMNS FROM eventos_google LIKE 'estado'")
                estado = cursor.fetchone()
                if estado and "Cancelado" in str(estado[1]):
                    continue
            cursor.execute(sentencia)
        cnx.commit()

        return True, "Base de datos verificada y migraciones compatibles aplicadas."

    except Exception as exc:
        if cnx is not None:
            try:
                cnx.rollback()
            except Exception:
                pass

        return False, f"No fue posible conectar con MySQL: {exc}"

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

        if cnx is not None:
            try:
                cnx.close()
            except Exception:
                pass


def inicializar_datos_base():
    """Alias para comprobación manual de la base de datos."""
    return ensure_database()


if __name__ == "__main__":
    ok, mensaje = inicializar_datos_base()
    print(mensaje)
