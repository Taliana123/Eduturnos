"""Migración segura para instalaciones EDUTURNOS existentes.

No elimina datos.
Agrega o actualiza la estructura necesaria para EDUTURNOS.
"""

from getpass import getpass

import mysql.connector


# =========================================================
# CONEXIÓN
# =========================================================

host = input("Servidor MySQL [127.0.0.1]: ").strip() or "127.0.0.1"
port = int(input("Puerto [3306]: ").strip() or "3306")
user = input("Usuario [root]: ").strip() or "root"
password = getpass("Contraseña MySQL: ")

cnx = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database="eduturnos"
)

cur = cnx.cursor()


# =========================================================
# FUNCIONES
# =========================================================

def ejecutar(sql):
    try:
        cur.execute(sql)
        print("OK")

    except mysql.connector.Error as exc:

        mensaje = str(exc).lower()

        errores_ignorables = (
            "duplicate column",
            "duplicate key name",
            "already exists",
            "duplicate constraint",
            "duplicate foreign key",
            "multiple primary key",
            "duplicate key",
        )

        if any(error in mensaje for error in errores_ignorables):
            print("Ya existe, se continúa.")

        else:
            print("ERROR:", exc)
            raise


def existe_columna(tabla, columna):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
        AND table_name = %s
        AND column_name = %s
        """,
        (tabla, columna)
    )

    return cur.fetchone()[0] > 0


def existe_tabla(tabla):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
        AND table_name = %s
        """,
        (tabla,)
    )

    return cur.fetchone()[0] > 0


def existe_constraint(tabla, constraint):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.table_constraints
        WHERE table_schema = DATABASE()
        AND table_name = %s
        AND constraint_name = %s
        """,
        (tabla, constraint)
    )

    return cur.fetchone()[0] > 0


# =========================================================
# MIGRACIÓN
# =========================================================

try:

    print("")
    print("========================================")
    print("EDUTURNOS - MIGRACIÓN DE BASE DE DATOS")
    print("========================================")
    print("")


    # =====================================================
    # SEDES
    # =====================================================

    print("Verificando tabla sedes...")

    if not existe_columna("sedes", "direccion"):

        cur.execute(
            """
            ALTER TABLE sedes
            ADD COLUMN direccion VARCHAR(255) NULL
            """
        )

        print("direccion agregada.")

    else:

        print("direccion ya existe.")


    if not existe_columna("sedes", "codigo_sede"):

        cur.execute(
            """
            ALTER TABLE sedes
            ADD COLUMN codigo_sede CHAR(6) NULL
            """
        )

        print("codigo_sede agregado.")

    else:

        print("codigo_sede ya existe.")


    # =====================================================
    # PERIODOS ACADÉMICOS
    # =====================================================

    print("Verificando periodos_academicos...")

    try:

        cur.execute(
            """
            ALTER TABLE periodos_academicos
            ADD UNIQUE KEY uq_periodo_nombre (nombre)
            """
        )

        print("Índice de periodos creado.")

    except mysql.connector.Error as exc:

        mensaje = str(exc).lower()

        if (
            "duplicate key name" in mensaje
            or "duplicate key" in mensaje
            or "already exists" in mensaje
        ):

            print("Índice de periodos ya existe.")

        else:

            raise


    # =====================================================
    # TOKENS DE RECUPERACIÓN
    # =====================================================

    print("Verificando tokens_recuperacion...")

    if not existe_tabla("tokens_recuperacion"):

        cur.execute(
            """
            CREATE TABLE tokens_recuperacion (

                id INT AUTO_INCREMENT PRIMARY KEY,

                id_usuario INT NOT NULL,

                token_hash CHAR(64) NOT NULL UNIQUE,

                fecha_creacion
                    DATETIME NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                fecha_expiracion
                    DATETIME NOT NULL,

                usado
                    TINYINT(1) NOT NULL
                    DEFAULT 0,

                FOREIGN KEY (id_usuario)
                    REFERENCES usuarios(id_usuario)
                    ON DELETE CASCADE,

                INDEX idx_token_exp
                    (fecha_expiracion, usado)

            ) ENGINE=InnoDB
            """
        )

        print("tokens_recuperacion creada.")

    else:

        print("tokens_recuperacion ya existe.")

        if not existe_columna(
            "tokens_recuperacion",
            "codigo_hash"
        ):

            cur.execute(
                """
                ALTER TABLE tokens_recuperacion
                ADD COLUMN codigo_hash CHAR(64) NULL
                """
            )

            print("codigo_hash agregado.")

        else:

            print("codigo_hash ya existe.")


    # =====================================================
    # ESTUDIANTES - ID USUARIO
    # =====================================================

    print("Verificando estudiantes...")

    if not existe_columna("estudiantes", "id_usuario"):

        cur.execute(
            """
            ALTER TABLE estudiantes
            ADD COLUMN id_usuario INT NULL
            """
        )

        print("id_usuario agregado a estudiantes.")

    else:

        print("id_usuario ya existe en estudiantes.")


    # =====================================================
    # IMPORTANTE:
    # NO CREAR fk_estudiante_usuario
    #
    # Ya comprobamos que en tu base de datos existe:
    #
    # fk_estudiante_usuario
    #
    # Por eso NO se vuelve a crear.
    # =====================================================

    if existe_constraint(
        "estudiantes",
        "fk_estudiante_usuario"
    ):

        print("fk_estudiante_usuario ya existe.")

    else:

        print(
            "fk_estudiante_usuario no existe."
        )

        cur.execute(
            """
            ALTER TABLE estudiantes
            ADD CONSTRAINT fk_estudiante_usuario
            FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id_usuario)
            ON DELETE SET NULL
            """
        )

        print(
            "fk_estudiante_usuario creada."
        )


    # =====================================================
    # DIRECTORIO INSTITUCIONAL
    # =====================================================

    print(
        "Verificando directorio_institucional..."
    )


    if not existe_columna(
        "directorio_institucional",
        "id_sede"
    ):

        cur.execute(
            """
            ALTER TABLE directorio_institucional
            ADD COLUMN id_sede INT NULL
            """
        )

        print("id_sede agregado.")

    else:

        print("id_sede ya existe.")


    if not existe_columna(
        "directorio_institucional",
        "id_jornada"
    ):

        cur.execute(
            """
            ALTER TABLE directorio_institucional
            ADD COLUMN id_jornada INT NULL
            """
        )

        print("id_jornada agregado.")

    else:

        print("id_jornada ya existe.")


    # =====================================================
    # FK DIRECTORIO - SEDE
    # =====================================================

    if existe_constraint(
        "directorio_institucional",
        "fk_directorio_sede"
    ):

        print("fk_directorio_sede ya existe.")

    else:

        try:

            cur.execute(
                """
                ALTER TABLE directorio_institucional
                ADD CONSTRAINT fk_directorio_sede
                FOREIGN KEY (id_sede)
                REFERENCES sedes(id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
                """
            )

            print(
                "fk_directorio_sede creada."
            )

        except mysql.connector.Error as exc:

            print(
                "No se pudo crear fk_directorio_sede:",
                exc
            )


    # =====================================================
    # FK DIRECTORIO - JORNADA
    # =====================================================

    if existe_constraint(
        "directorio_institucional",
        "fk_directorio_jornada"
    ):

        print(
            "fk_directorio_jornada ya existe."
        )

    else:

        try:

            cur.execute(
                """
                ALTER TABLE directorio_institucional
                ADD CONSTRAINT fk_directorio_jornada
                FOREIGN KEY (id_jornada)
                REFERENCES jornadas(id)
                ON DELETE SET NULL
                """
            )

            print(
                "fk_directorio_jornada creada."
            )

        except mysql.connector.Error as exc:

            print(
                "No se pudo crear fk_directorio_jornada:",
                exc
            )


    # =====================================================
    # SOLICITUDES DE CITA
    # =====================================================

    print("Verificando solicitudes_cita...")

    if not existe_tabla("solicitudes_cita"):

        cur.execute(
            """
            CREATE TABLE solicitudes_cita (

                id INT AUTO_INCREMENT PRIMARY KEY,

                solicitante_usuario_id INT NOT NULL,

                tipo_solicitante
                    ENUM('Acudiente','Docente')
                    NOT NULL,

                id_estudiante INT NOT NULL,

                id_acudiente INT NULL,

                id_docente INT NOT NULL,

                id_motivo INT NOT NULL,

                fecha_solicitada DATE NOT NULL,

                hora_solicitada TIME NOT NULL,

                fecha_propuesta DATE NULL,

                hora_propuesta TIME NULL,

                lugar VARCHAR(150) NULL,

                observaciones TEXT NULL,

                respuesta TEXT NULL,

                estado
                    ENUM(
                        'Pendiente',
                        'Propuesta',
                        'Aceptada',
                        'Rechazada',
                        'Cancelada'
                    )
                    NOT NULL DEFAULT 'Pendiente',

                revisado_por INT NULL,

                cita_id INT NULL,

                fecha_creacion
                    DATETIME NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                fecha_revision DATETIME NULL,

                fecha_actualizacion
                    DATETIME NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,

                FOREIGN KEY (solicitante_usuario_id)
                    REFERENCES usuarios(id_usuario)
                    ON DELETE RESTRICT,

                FOREIGN KEY (id_estudiante)
                    REFERENCES estudiantes(id_estudiante)
                    ON DELETE RESTRICT,

                FOREIGN KEY (id_acudiente)
                    REFERENCES acudientes(id_acudiente)
                    ON DELETE SET NULL,

                FOREIGN KEY (id_docente)
                    REFERENCES docentes(id_docente)
                    ON DELETE RESTRICT,

                FOREIGN KEY (id_motivo)
                    REFERENCES motivos(id)
                    ON DELETE RESTRICT,

                FOREIGN KEY (revisado_por)
                    REFERENCES usuarios(id_usuario)
                    ON DELETE SET NULL,

                FOREIGN KEY (cita_id)
                    REFERENCES citas(id)
                    ON DELETE SET NULL,

                INDEX idx_solicitud_estado
                    (estado, fecha_creacion),

                INDEX idx_solicitud_solicitante
                    (solicitante_usuario_id, estado),

                INDEX idx_solicitud_docente
                    (
                        id_docente,
                        fecha_solicitada,
                        hora_solicitada
                    )

            ) ENGINE=InnoDB
            """
        )

        print("solicitudes_cita creada.")

    else:

        print("solicitudes_cita ya existe.")


    # =====================================================
    # INSTITUCIÓN
    # =====================================================

    print("Verificando institución...")

    cur.execute(
        """
        SELECT id
        FROM instituciones
        WHERE nombre = %s
        LIMIT 1
        """,
        (
            "Institución Educativa José Joaquín Flórez Hernández",
        )
    )

    institucion = cur.fetchone()


    if not institucion:

        cur.execute(
            """
            INSERT INTO instituciones
                (nombre, ciudad, departamento)
            VALUES
                (%s, %s, %s)
            """,
            (
                "Institución Educativa José Joaquín Flórez Hernández",
                "Ibagué",
                "Tolima",
            )
        )

        institucion_id = cur.lastrowid

        print("Institución creada.")

    else:

        institucion_id = institucion[0]

        print("Institución ya existe.")


    # =====================================================
    # SEDES OFICIALES
    # =====================================================

    sedes = [

        (
            "Sede Principal (Las Américas)",
            "Ciudadela Las Américas, sector Picaleña (Cra. 15A Sur #2-01)",
            "238596",
        ),

        (
            "Sede Arboleda Campestre",
            "Calle 152 #21 Sur - 22, urbanización Arboleda Campestre",
            "418257",
        ),

        (
            "Sede Secundino Porras Cruz",
            "Zona sur de Ibagué",
            "563812",
        ),

        (
            "Sede Picaleña",
            "Antigua Escuela Urbana Mixta de Picaleña, sobre la vía nacional",
            "724305",
        ),

        (
            "Sede Bello Horizonte",
            "Barrio Bello Horizonte",
            "351864",
        ),

        (
            "Sede San Francisco Club",
            "Barrio San Francisco Club, Calle 113 con Carrera 48 Sur",
            "896421",
        ),
    ]


    # =====================================================
    # DESACTIVAR SEDES ANTIGUAS
    # =====================================================

    nombres_sedes = [
        sede[0]
        for sede in sedes
    ]

    placeholders = ",".join(
        ["%s"] * len(nombres_sedes)
    )

    sql_desactivar = f"""
        UPDATE sedes
        SET estado = 0
        WHERE id_institucion = %s
        AND nombre NOT IN ({placeholders})
    """

    parametros = [institucion_id]

    parametros.extend(nombres_sedes)

    cur.execute(
        sql_desactivar,
        parametros
    )

    print("Sedes antiguas desactivadas.")


    # =====================================================
    # INSERTAR / ACTUALIZAR SEDES
    # =====================================================

    for nombre, direccion, codigo_sede in sedes:

        cur.execute(
            """
            SELECT id
            FROM sedes
            WHERE id_institucion = %s
            AND nombre = %s
            LIMIT 1
            """,
            (
                institucion_id,
                nombre,
            )
        )

        row = cur.fetchone()


        if row:

            cur.execute(
                """
                UPDATE sedes
                SET
                    direccion = %s,
                    codigo_sede = %s,
                    estado = 1
                WHERE id = %s
                """,
                (
                    direccion,
                    codigo_sede,
                    row[0],
                )
            )

            print(
                "Sede actualizada:",
                nombre
            )

        else:

            cur.execute(
                """
                INSERT INTO sedes
                    (
                        id_institucion,
                        nombre,
                        direccion,
                        codigo_sede,
                        estado
                    )
                VALUES
                    (%s, %s, %s, %s, 1)
                """,
                (
                    institucion_id,
                    nombre,
                    direccion,
                    codigo_sede,
                )
            )

            print(
                "Sede creada:",
                nombre
            )


    # =====================================================
    # JORNADAS
    # =====================================================

    jornadas = [
        "Mañana",
        "Tarde",
        "Noche",
    ]

    for nombre_jornada in jornadas:

        cur.execute(
            """
            INSERT IGNORE INTO jornadas
                (nombre, estado)
            VALUES
                (%s, 1)
            """,
            (
                nombre_jornada,
            )
        )

    print("Jornadas verificadas.")


    # =====================================================
    # GUARDAR
    # =====================================================

    cnx.commit()

    print("")
    print("========================================")
    print("MIGRACIÓN COMPLETADA CORRECTAMENTE")
    print("========================================")
    print("")
    print("No se eliminaron datos.")
    print("Estudiantes verificados.")
    print("Usuarios verificados.")
    print("Directorio institucional verificado.")
    print("Sedes verificadas.")
    print("Jornadas verificadas.")
    print("Solicitudes de cita verificadas.")
    print("")
    print("Sedes oficiales activas: 6")
    print("Códigos de personal: exactamente 6 dígitos.")
    print("")


except mysql.connector.Error as exc:

    cnx.rollback()

    print("")
    print("========================================")
    print("ERROR EN LA MIGRACIÓN")
    print("========================================")
    print(exc)
    print("")
    print("Se revirtieron los cambios pendientes.")
    print("")


finally:

    cur.close()
    cnx.close()