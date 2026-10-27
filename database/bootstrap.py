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

        # Admite citas dirigidas a personal sin inventar estudiante/acudiente.
        for columna, definicion in (
            ("destinatario_tipo", "ENUM('Estudiante','Docente','Rector','Administrador / Coordinador') NULL"),
            ("destinatario_usuario_id", "INT NULL"),
        ):
            cursor.execute(f"SHOW COLUMNS FROM citas LIKE '{columna}'")
            if cursor.fetchone() is None:
                cursor.execute(f"ALTER TABLE citas ADD COLUMN {columna} {definicion}")
        for columna in ("id_estudiante", "id_acudiente", "id_docente"):
            cursor.execute(f"SHOW COLUMNS FROM citas LIKE '{columna}'")
            definicion = cursor.fetchone()
            if definicion and str(definicion[2]).upper() == "NO":
                cursor.execute(f"ALTER TABLE citas MODIFY COLUMN {columna} INT NULL")
        cursor.execute("SHOW INDEX FROM citas WHERE Key_name='idx_cita_destinatario'")
        if cursor.fetchone() is None:
            cursor.execute("CREATE INDEX idx_cita_destinatario ON citas(destinatario_usuario_id,fecha,hora)")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cita_participantes (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_cita INT NOT NULL,
                id_usuario INT NOT NULL,
                tipo ENUM('Organizador','Destinatario','Participante') NOT NULL DEFAULT 'Participante',
                fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_cita_participante (id_cita,id_usuario),
                INDEX idx_cita_participante_usuario (id_usuario,id_cita),
                CONSTRAINT fk_cita_participante_cita FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE CASCADE,
                CONSTRAINT fk_cita_participante_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
            ) ENGINE=InnoDB
        """)

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

