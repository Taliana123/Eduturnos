from datetime import datetime, timedelta
from flask import Flask

from database.db import consultar, ejecutar


app = Flask(__name__)

app.config.update(
    MYSQL_HOST="127.0.0.1",
    MYSQL_PORT=3306,
    MYSQL_USER="root",
    MYSQL_PASSWORD="",
    MYSQL_DATABASE="eduturnos",
    MYSQL_POOL_SIZE=5,
)


# =========================================================
# BUSCAR DOCENTE
# =========================================================

def buscar_docente():

    return consultar(
        """
        SELECT
            d.id_docente,
            d.id_usuario,
            d.nombres,
            d.apellidos
        FROM docentes d
        JOIN usuarios u
            ON u.id_usuario = d.id_usuario
        WHERE d.estado = 1
          AND u.estado = 1
        ORDER BY d.id_docente
        LIMIT 1
        """,
        uno=True,
    )


# =========================================================
# BUSCAR USUARIO QUE CREARÁ LA CITA
# =========================================================

def buscar_creador():

    return consultar(
        """
        SELECT
            u.id_usuario,
            u.nombres,
            u.apellidos
        FROM usuarios u
        JOIN roles r
            ON r.id = u.id_rol
        WHERE u.estado = 1
          AND r.nombre IN (
              'Administrador / Coordinador',
              'Super Admin',
              'Rector'
          )
        ORDER BY u.id_usuario
        LIMIT 1
        """,
        uno=True,
    )


# =========================================================
# BUSCAR MOTIVO
# =========================================================

def buscar_motivo():

    return consultar(
        """
        SELECT
            id,
            nombre
        FROM motivos
        WHERE estado = 1
        ORDER BY id
        LIMIT 1
        """,
        uno=True,
    )


# =========================================================
# BUSCAR PERIODO ACTIVO
# =========================================================

def buscar_periodo():

    return consultar(
        """
        SELECT
            id,
            nombre
        FROM periodos_academicos
        WHERE activo = 1
          AND cerrado = 0
        ORDER BY id
        LIMIT 1
        """,
        uno=True,
    )


# =========================================================
# BUSCAR ESTADO PENDIENTE
# =========================================================

def buscar_estado_pendiente():

    return consultar(
        """
        SELECT
            id,
            nombre
        FROM estados_cita
        WHERE nombre = 'Pendiente'
          AND estado = 1
        LIMIT 1
        """,
        uno=True,
    )


# =========================================================
# BUSCAR SEDE
# =========================================================

def buscar_sede():

    return consultar(
        """
        SELECT
            id,
            nombre
        FROM sedes
        WHERE estado = 1
        ORDER BY id
        LIMIT 1
        """,
        uno=True,
    )


# =========================================================
# BUSCAR JORNADA
# =========================================================

def buscar_jornada():

    return consultar(
        """
        SELECT
            id,
            nombre
        FROM jornadas
        WHERE estado = 1
        ORDER BY id
        LIMIT 1
        """,
        uno=True,
    )


# =========================================================
# BUSCAR GRADO
# =========================================================

def buscar_grado():

    return consultar(
        """
        SELECT
            id,
            nombre
        FROM grados
        WHERE id >= 6
          AND estado = 1
        ORDER BY id
        LIMIT 1
        """,
        uno=True,
    )


# =========================================================
# BUSCAR GRUPO
# =========================================================

def buscar_grupo(grado_id):

    return consultar(
        """
        SELECT
            id,
            nombre
        FROM grupos
        WHERE id_grado = %s
          AND estado = 1
        ORDER BY id
        LIMIT 1
        """,
        (grado_id,),
        uno=True,
    )


# =========================================================
# CREAR ESTUDIANTE DE PRUEBA
# =========================================================

def crear_estudiante(
    sede_id,
    jornada_id,
    grado_id,
    grupo_id,
    periodo_id,
):

    codigo = "PRUEBA-EDUTURNOS"

    existente = consultar(
        """
        SELECT
            id_estudiante
        FROM estudiantes
        WHERE codigo_estudiantil = %s
        LIMIT 1
        """,
        (codigo,),
        uno=True,
    )

    if existente:
        return existente["id_estudiante"]

    documento = "999999991"

    existente = consultar(
        """
        SELECT
            id_estudiante
        FROM estudiantes
        WHERE documento = %s
        LIMIT 1
        """,
        (documento,),
        uno=True,
    )

    if existente:
        return existente["id_estudiante"]

    return ejecutar(
        """
        INSERT INTO estudiantes (
            id_usuario,
            codigo_estudiantil,
            tipo_documento,
            documento,
            nombres,
            apellidos,
            curso,
            id_sede,
            id_jornada,
            id_grado,
            id_grupo,
            id_periodo,
            estado
        )
        VALUES (
            NULL,
            %s,
            'TI',
            %s,
            'ESTUDIANTE',
            'PRUEBA EDUTURNOS',
            'PRUEBA',
            %s,
            %s,
            %s,
            %s,
            %s,
            'Activo'
        )
        """,
        (
            codigo,
            documento,
            sede_id,
            jornada_id,
            grado_id,
            grupo_id,
            periodo_id,
        ),
    )


# =========================================================
# CREAR ACUDIENTE DE PRUEBA
# =========================================================

def crear_acudiente():

    documento = "999999992"

    existente = consultar(
        """
        SELECT
            id_acudiente
        FROM acudientes
        WHERE documento = %s
        LIMIT 1
        """,
        (documento,),
        uno=True,
    )

    if existente:
        return existente["id_acudiente"]

    return ejecutar(
        """
        INSERT INTO acudientes (
            id_usuario,
            tipo_documento,
            documento,
            nombres,
            apellidos,
            telefono,
            correo,
            municipio,
            estado
        )
        VALUES (
            NULL,
            'CC',
            %s,
            'ACUDIENTE',
            'PRUEBA EDUTURNOS',
            '3000000000',
            'prueba@eduturnos.local',
            'Ibagué',
            1
        )
        """,
        (documento,),
    )


# =========================================================
# RELACIONAR ESTUDIANTE Y ACUDIENTE
# =========================================================

def relacionar_estudiante_acudiente(
    estudiante_id,
    acudiente_id,
):

    existente = consultar(
        """
        SELECT
            id
        FROM estudiante_acudiente
        WHERE id_estudiante = %s
          AND id_acudiente = %s
        LIMIT 1
        """,
        (
            estudiante_id,
            acudiente_id,
        ),
        uno=True,
    )

    if existente:
        return

    ejecutar(
        """
        INSERT INTO estudiante_acudiente (
            id_estudiante,
            id_acudiente,
            parentesco,
            principal,
            estado
        )
        VALUES (
            %s,
            %s,
            'Padre/Madre',
            1,
            1
        )
        """,
        (
            estudiante_id,
            acudiente_id,
        ),
    )


# =========================================================
# CREAR CITA DE PRUEBA
# =========================================================

def crear_cita(
    estudiante_id,
    acudiente_id,
    docente_id,
    motivo_id,
    estado_id,
    periodo_id,
    creador_id,
):

    # La cita queda aproximadamente 2 horas y 10 minutos
    # después del momento de ejecución.

    momento = datetime.now() + timedelta(
        hours=2,
        minutes=10,
    )

    fecha = momento.date()

    hora = momento.strftime(
        "%H:%M:%S"
    )

    cita_id = ejecutar(
        """
        INSERT INTO citas (
            id_estudiante,
            id_acudiente,
            id_docente,
            id_motivo,
            id_estado,
            id_periodo,
            fecha,
            hora,
            lugar,
            observaciones,
            creado_por,
            recordatorio_24h_enviado,
            recordatorio_2h_enviado
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            'Sala de reuniones - PRUEBA',
            'Cita de prueba automática de recordatorios EDUTURNOS.',
            %s,
            0,
            0
        )
        """,
        (
            estudiante_id,
            acudiente_id,
            docente_id,
            motivo_id,
            estado_id,
            periodo_id,
            fecha,
            hora,
            creador_id,
        ),
    )

    return cita_id, fecha, hora


# =========================================================
# EJECUCIÓN
# =========================================================

with app.app_context():

    print()
    print("==============================================")
    print(" PRUEBA AUTOMÁTICA DE RECORDATORIOS EDUTURNOS")
    print("==============================================")
    print()

    docente = buscar_docente()

    if not docente:
        raise RuntimeError(
            "No existe un docente activo vinculado a un usuario."
        )

    creador = buscar_creador()

    if not creador:
        raise RuntimeError(
            "No existe un usuario activo de coordinación, rectoría o administración."
        )

    motivo = buscar_motivo()

    if not motivo:
        raise RuntimeError(
            "No existe ningún motivo activo configurado."
        )

    periodo = buscar_periodo()

    if not periodo:
        raise RuntimeError(
            "No existe un periodo académico activo."
        )

    estado = buscar_estado_pendiente()

    if not estado:
        raise RuntimeError(
            "No existe el estado Pendiente activo."
        )

    sede = buscar_sede()
    jornada = buscar_jornada()
    grado = buscar_grado()

    if not sede:
        raise RuntimeError(
            "No existe ninguna sede activa."
        )

    if not jornada:
        raise RuntimeError(
            "No existe ninguna jornada activa."
        )

    if not grado:
        raise RuntimeError(
            "No existe ningún grado activo entre 6 y 11."
        )

    grupo = buscar_grupo(
        grado["id"]
    )

    if not grupo:
        raise RuntimeError(
            "No existe un grupo activo para el grado seleccionado."
        )

    estudiante_id = crear_estudiante(
        sede["id"],
        jornada["id"],
        grado["id"],
        grupo["id"],
        periodo["id"],
    )

    acudiente_id = crear_acudiente()

    relacionar_estudiante_acudiente(
        estudiante_id,
        acudiente_id,
    )

    cita_id, fecha, hora = crear_cita(
        estudiante_id,
        acudiente_id,
        docente["id_docente"],
        motivo["id"],
        estado["id"],
        periodo["id"],
        creador["id_usuario"],
    )

    print("CITA DE PRUEBA CREADA CORRECTAMENTE")
    print()
    print(f"ID de cita: {cita_id}")
    print(f"Fecha:      {fecha}")
    print(f"Hora:       {hora}")
    print(
        f"Docente:    {docente['nombres']} "
        f"{docente['apellidos']}"
    )
    print(
        f"Creador:    {creador['nombres']} "
        f"{creador['apellidos']}"
    )
    print()

    print(
        "Ejecutando el sistema de recordatorios..."
    )
    print()

    from tools.enviar_recordatorios import (
        procesar_recordatorios
    )

    procesar_recordatorios()

    print()
    print("==============================================")
    print(" PRUEBA FINALIZADA")
    print("==============================================")
    print()