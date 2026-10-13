from app import app

from datetime import date, timedelta

from database.db import consultar, ejecutar

from werkzeug.security import generate_password_hash


USUARIOS = [

    ("Super Admin", "10000001", "Super", "Admin", "admin@eduturnos.local", "3000000001"),

    ("Administrador / Coordinador", "10000002", "Ana", "Coordinadora", "coordinacion@eduturnos.local", "3000000002"),

    ("Docente", "10000003", "Carlos", "Docente", "docente@eduturnos.local", "3000000003"),

    ("Acudiente", "10000004", "Laura", "Acudiente", "acudiente@eduturnos.local", "3000000004"),

    ("Estudiante", "10000005", "Juan", "Estudiante", "estudiante@eduturnos.local", "3000000005"),

]



with app.app_context():

    for rol, documento, nombres, apellidos, correo, telefono in USUARIOS:

        existe = consultar(
            "SELECT id_usuario FROM usuarios WHERE documento=%s",
            (documento,),
            uno=True
        )

        if not existe:

            r = consultar(
                "SELECT id FROM roles WHERE nombre=%s",
                (rol,),
                uno=True
            )

            id_usuario = ejecutar(
                """
                INSERT INTO usuarios(
                    id_rol,
                    tipo_documento,
                    documento,
                    nombres,
                    apellidos,
                    correo,
                    telefono,
                    password_hash,
                    verificado
                )
                VALUES(
                    %s,
                    'CC',
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    1
                )
                """,
                (
                    r["id"],
                    documento,
                    nombres,
                    apellidos,
                    correo,
                    telefono,
                    generate_password_hash("123456")
                )
            )

            if rol == "Acudiente":

                ejecutar(
                    """
                    INSERT INTO acudientes(
                        id_usuario,
                        tipo_documento,
                        documento,
                        nombres,
                        apellidos,
                        telefono,
                        correo
                    )
                    VALUES(
                        %s,
                        'CC',
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        id_usuario,
                        documento,
                        nombres,
                        apellidos,
                        telefono,
                        correo
                    )
                )

            if rol == "Docente":

                sede = consultar(
                    "SELECT id FROM sedes LIMIT 1",
                    uno=True
                )

                jornada = consultar(
                    "SELECT id FROM jornadas LIMIT 1",
                    uno=True
                )

                ejecutar(
                    """
                    INSERT INTO docentes(
                        id_usuario,
                        tipo_documento,
                        documento,
                        nombres,
                        apellidos,
                        correo_institucional,
                        telefono,
                        id_sede,
                        id_jornada,
                        area,
                        asignatura
                    )
                    VALUES(
                        %s,
                        'CC',
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        'General',
                        'General'
                    )
                    """,
                    (
                        id_usuario,
                        documento,
                        nombres,
                        apellidos,
                        correo,
                        telefono,
                        sede["id"],
                        jornada["id"]
                    )
                )

    sede = consultar(
        "SELECT id FROM sedes WHERE estado = 1 ORDER BY id LIMIT 1",
        uno=True,
    )
    jornada = consultar(
        "SELECT id FROM jornadas WHERE estado = 1 ORDER BY id LIMIT 1",
        uno=True,
    )
    grado = consultar(
        "SELECT id FROM grados WHERE nombre = '8' AND estado = 1 LIMIT 1",
        uno=True,
    )
    grupo = consultar(
        "SELECT id FROM grupos WHERE id_grado = %s AND nombre = '1' AND estado = 1 LIMIT 1",
        (grado["id"],),
        uno=True,
    )
    periodo = consultar(
        """
        SELECT id, fecha_inicio, fecha_fin
        FROM periodos_academicos
        WHERE activo = 1 AND cerrado = 0
        ORDER BY fecha_fin DESC
        LIMIT 1
        """,
        uno=True,
    )

    if not all((sede, jornada, grado, grupo, periodo)):
        raise RuntimeError("Faltan catálogos académicos para crear el caso de demostración.")

    estudiante_usuario = consultar(
        "SELECT id_usuario FROM usuarios WHERE documento = '10000005'",
        uno=True,
    )
    estudiante = consultar(
        "SELECT id_estudiante FROM estudiantes WHERE documento = '10000005'",
        uno=True,
    )

    if not estudiante:
        estudiante_id = ejecutar(
            """
            INSERT INTO estudiantes (
                id_usuario, codigo_estudiantil, tipo_documento, documento,
                nombres, apellidos, curso, id_sede, id_jornada, id_grado,
                id_grupo, id_periodo, estado
            )
            VALUES (%s, 'EST-DEMO-001', 'TI', '10000005', 'Juan', 'Estudiante',
                    '8-1', %s, %s, %s, %s, %s, 'Activo')
            """,
            (
                estudiante_usuario["id_usuario"],
                sede["id"],
                jornada["id"],
                grado["id"],
                grupo["id"],
                periodo["id"],
            ),
        )
        estudiante = {"id_estudiante": estudiante_id}

    acudiente = consultar(
        "SELECT id_acudiente FROM acudientes WHERE documento = '10000004'",
        uno=True,
    )
    docente = consultar(
        "SELECT id_docente FROM docentes WHERE documento = '10000003'",
        uno=True,
    )
    coordinador = consultar(
        "SELECT id_usuario FROM usuarios WHERE documento = '10000002'",
        uno=True,
    )

    ejecutar(
        """
        INSERT INTO estudiante_acudiente (
            id_estudiante, id_acudiente, parentesco, principal, estado
        )
        VALUES (%s, %s, 'Madre', 1, 1)
        ON DUPLICATE KEY UPDATE parentesco = VALUES(parentesco), principal = 1, estado = 1
        """,
        (estudiante["id_estudiante"], acudiente["id_acudiente"]),
    )
    ejecutar(
        """
        INSERT INTO asignaciones_docentes (id_docente, id_estudiante, estado)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE estado = 1
        """,
        (docente["id_docente"], estudiante["id_estudiante"]),
    )

    caso_existente = consultar(
        "SELECT id FROM citas WHERE observaciones LIKE 'CASO-DEMO-COORDINACION:%' LIMIT 1",
        uno=True,
    )

    if not caso_existente:
        motivo = consultar(
            "SELECT id FROM motivos WHERE nombre = 'Convivencia' AND estado = 1 LIMIT 1",
            uno=True,
        )
        estado = consultar(
            "SELECT id FROM estados_cita WHERE nombre = 'Pendiente' AND estado = 1 LIMIT 1",
            uno=True,
        )
        fecha_cita = max(date.today() + timedelta(days=7), periodo["fecha_inicio"])

        if fecha_cita > periodo["fecha_fin"]:
            raise RuntimeError("El periodo académico activo no admite una citación futura.")

        ejecutar(
            """
            INSERT INTO citas (
                id_estudiante, id_acudiente, id_docente, id_motivo, id_estado,
                id_periodo, fecha, hora, lugar, observaciones, creado_por
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, '10:30', 'Coordinación', %s, %s)
            """,
            (
                estudiante["id_estudiante"],
                acudiente["id_acudiente"],
                docente["id_docente"],
                motivo["id"],
                estado["id"],
                periodo["id"],
                fecha_cita,
                (
                    "CASO-DEMO-COORDINACION: Citación al estudiante para revisar "
                    "una situación de convivencia y acordar compromisos con su acudiente."
                ),
                coordinador["id_usuario"],
            ),
        )

    print("Datos de prueba y caso de citación creados. Contraseña de todos: 123456")