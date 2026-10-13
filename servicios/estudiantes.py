# ============================================================
# SERVICIO DE ESTUDIANTES - EDUTURNOS
# ============================================================
#
# Funciones centrales para:
# - Validar grados permitidos.
# - Validar grupos visibles.
# - Obtener el grupo real de la BD.
# - Controlar el máximo de 40 estudiantes por grupo.
# - Evitar sobrepasar el cupo con registros simultáneos.
# - Generar códigos estudiantiles automáticamente.
#
# IMPORTANTE:
# El formulario muestra:
#
#   Grupo 1
#   Grupo 2
#   ...
#   Grupo 6
#
# Pero el ID real de la tabla grupos depende del grado.
#
# Ejemplo:
#   6.º Grupo 1 -> id_grupo = 31
#
# Por eso NUNCA se debe guardar directamente
# el número visible del grupo como id_grupo.
# ============================================================

from datetime import datetime
import uuid

from database.db import consultar


# ============================================================
# CONFIGURACIÓN
# ============================================================

# EDUTURNOS solamente permite registrar estudiantes
# desde sexto hasta undécimo.
GRADOS_PERMITIDOS = {6, 7, 8, 9, 10, 11}

# El formulario muestra siempre estos grupos.
GRUPOS_VISIBLES = {1, 2, 3, 4, 5, 6}

# Máximo de estudiantes activos permitidos
# en un mismo grupo.
MAX_ESTUDIANTES_GRUPO = 40


# ============================================================
# CONVERSIÓN SEGURA A ENTERO
# ============================================================

def _entero(valor):
    """
    Convierte un valor a entero de forma segura.

    Ejemplos:
        _entero("6")   -> 6
        _entero(6)     -> 6
        _entero("")    -> None
        _entero(None)  -> None
        _entero("abc") -> None
    """

    try:
        if valor is None:
            return None

        texto = str(valor).strip()

        if not texto:
            return None

        return int(texto)

    except (TypeError, ValueError):
        return None


# ============================================================
# VALIDAR GRADO
# ============================================================

def validar_grado(grado_id):
    """
    Verifica que el grado pertenezca a los grados
    permitidos para el registro de estudiantes.

    Permitidos:
        6, 7, 8, 9, 10, 11
    """

    grado = _entero(grado_id)

    return grado in GRADOS_PERMITIDOS


# ============================================================
# VALIDAR GRUPO VISIBLE
# ============================================================

def validar_grupo_visible(grupo_visible):
    """
    Valida el número de grupo que recibe el formulario.

    El formulario utiliza:
        Grupo 1
        Grupo 2
        Grupo 3
        Grupo 4
        Grupo 5
        Grupo 6

    Este número NO necesariamente coincide con el ID
    de la tabla grupos.
    """

    grupo = _entero(grupo_visible)

    return grupo in GRUPOS_VISIBLES


# ============================================================
# OBTENER GRUPO REAL DE LA BASE DE DATOS
# ============================================================

def obtener_grupo_real(grado_id, grupo_visible):
    """
    Busca el registro real de la tabla grupos.

    Recibe:
        grado_id      -> ID del grado.
        grupo_visible -> número visible 1..6.

    Devuelve un diccionario con:

        id
        nombre
        id_grado
        grado

    Ejemplo:

        grado_id = 6
        grupo_visible = 1

    Puede devolver:

        {
            "id": 31,
            "nombre": "1",
            "id_grado": 6,
            "grado": "6"
        }

    IMPORTANTE:
    No se utiliza grupo_visible como id_grupo.
    """

    grado = _entero(grado_id)
    grupo = _entero(grupo_visible)

    # Validar grado.
    if grado not in GRADOS_PERMITIDOS:
        return None

    # Validar grupo visible.
    if grupo not in GRUPOS_VISIBLES:
        return None

    return consultar(
        """
        SELECT
            g.id,
            g.nombre,
            g.id_grado,
            gr.nombre AS grado
        FROM grupos g
        INNER JOIN grados gr
            ON gr.id = g.id_grado
        WHERE
            g.id_grado = %s
            AND g.nombre = %s
            AND g.estado = 1
            AND gr.estado = 1
        LIMIT 1
        """,
        (
            grado,
            str(grupo),
        ),
        uno=True,
    )


# ============================================================
# OBTENER ID REAL DEL GRUPO
# ============================================================

def obtener_id_grupo_real(grado_id, grupo_visible):
    """
    Devuelve únicamente el ID real de la tabla grupos.

    Ejemplo:

        obtener_id_grupo_real(6, 1)

    podría devolver:

        31

    Si el grupo no existe, devuelve None.
    """

    grupo = obtener_grupo_real(
        grado_id,
        grupo_visible,
    )

    if not grupo:
        return None

    return grupo["id"]


# ============================================================
# VALIDAR RELACIÓN GRADO / GRUPO
# ============================================================

def validar_grupo_para_grado(grado_id, grupo_visible):
    """
    Comprueba que el grupo visible realmente exista
    para el grado seleccionado.

    Devuelve:
        True  -> existe
        False -> no existe
    """

    return obtener_grupo_real(
        grado_id,
        grupo_visible,
    ) is not None


# ============================================================
# BLOQUEAR GRUPO Y COMPROBAR CUPO
# ============================================================

def bloquear_y_comprobar_cupo(
    cnx,
    grado_id,
    grupo_visible,
    excluir_estudiante_id=None,
):
    """
    Bloquea temporalmente la fila real del grupo dentro
    de una transacción y comprueba el número de estudiantes
    activos.

    Esto es importante para evitar una situación como:

        Registro A -> ve 39 estudiantes.
        Registro B -> ve 39 estudiantes.
        Registro A -> registra.
        Registro B -> registra.

    Sin bloqueo podrían terminar existiendo 41.

    FOR UPDATE hace que los registros simultáneos que intenten
    modificar el mismo grupo esperen su turno.

    Parámetros:

        cnx:
            conexión MySQL perteneciente a una transacción.

        grado_id:
            ID del grado.

        grupo_visible:
            número visible del grupo (1..6).

        excluir_estudiante_id:
            ID del estudiante que se está editando.
            Sirve para no contarlo como estudiante adicional.

    Devuelve:

        Diccionario del grupo real.

    Lanza:

        ValueError
            Si el grado, grupo o cupo no son válidos.
    """

    grado = _entero(grado_id)
    grupo = _entero(grupo_visible)

    # --------------------------------------------------------
    # VALIDAR GRADO
    # --------------------------------------------------------

    if grado not in GRADOS_PERMITIDOS:
        raise ValueError(
            "Solo se permiten estudiantes de los grados "
            "6.º a 11.º."
        )

    # --------------------------------------------------------
    # VALIDAR GRUPO
    # --------------------------------------------------------

    if grupo not in GRUPOS_VISIBLES:
        raise ValueError(
            "El grupo seleccionado no es válido. "
            "Debe seleccionar un grupo del 1 al 6."
        )

    # --------------------------------------------------------
    # NORMALIZAR ID DEL ESTUDIANTE A EXCLUIR
    # --------------------------------------------------------

    excluir_id = None

    if excluir_estudiante_id is not None:
        excluir_id = _entero(excluir_estudiante_id)

        if excluir_id is None:
            raise ValueError(
                "El estudiante indicado para la actualización "
                "no es válido."
            )

    # --------------------------------------------------------
    # CREAR CURSOR
    # --------------------------------------------------------

    cur = cnx.cursor(dictionary=True)

    try:

        # ====================================================
        # BLOQUEAR LA FILA REAL DEL GRUPO
        # ====================================================

        cur.execute(
            """
            SELECT
                g.id,
                g.nombre,
                g.id_grado,
                gr.nombre AS grado
            FROM grupos g
            INNER JOIN grados gr
                ON gr.id = g.id_grado
            WHERE
                g.id_grado = %s
                AND g.nombre = %s
                AND g.estado = 1
                AND gr.estado = 1
            LIMIT 1
            FOR UPDATE
            """,
            (
                grado,
                str(grupo),
            ),
        )

        grupo_real = cur.fetchone()

        # ----------------------------------------------------
        # GRUPO NO EXISTE
        # ----------------------------------------------------

        if not grupo_real:
            raise ValueError(
                f"El Grupo {grupo} no existe para el "
                f"grado {grado}."
            )

        # ====================================================
        # CONTAR ESTUDIANTES ACTIVOS
        # ====================================================

        if excluir_id is not None:

            cur.execute(
                """
                SELECT
                    COUNT(*) AS total
                FROM estudiantes
                WHERE
                    id_grupo = %s
                    AND estado = 'Activo'
                    AND id_estudiante <> %s
                """,
                (
                    grupo_real["id"],
                    excluir_id,
                ),
            )

        else:

            cur.execute(
                """
                SELECT
                    COUNT(*) AS total
                FROM estudiantes
                WHERE
                    id_grupo = %s
                    AND estado = 'Activo'
                """,
                (
                    grupo_real["id"],
                ),
            )

        fila = cur.fetchone()

        total = int(
            fila["total"]
            if fila and fila.get("total") is not None
            else 0
        )

        # ====================================================
        # VALIDAR CUPO
        # ====================================================

        if total >= MAX_ESTUDIANTES_GRUPO:

            raise ValueError(
                f"El grado {grado} - Grupo {grupo} "
                f"ya tiene {MAX_ESTUDIANTES_GRUPO} "
                f"estudiantes activos. "
                f"No se pueden registrar más estudiantes "
                f"en este grupo."
            )

        # ====================================================
        # DEVOLVER GRUPO REAL
        # ====================================================

        return grupo_real

    finally:

        cur.close()


# ============================================================
# OBTENER CANTIDAD DE ESTUDIANTES DE UN GRUPO
# ============================================================

def contar_estudiantes_grupo(grupo_id):
    """
    Cuenta los estudiantes activos de un grupo utilizando
    el ID REAL de la tabla grupos.

    Parámetro:

        grupo_id:
            ID real de grupos.id.

    Devuelve:

        Número entero.
    """

    grupo = _entero(grupo_id)

    if grupo is None:
        return 0

    resultado = consultar(
        """
        SELECT
            COUNT(*) AS total
        FROM estudiantes
        WHERE
            id_grupo = %s
            AND estado = 'Activo'
        """,
        (grupo,),
        uno=True,
    )

    if not resultado:
        return 0

    return int(
        resultado.get("total", 0) or 0
    )


# ============================================================
# CONSULTAR CUPO DISPONIBLE
# ============================================================

def cupo_disponible(grupo_id):
    """
    Devuelve cuántos cupos quedan disponibles.

    Ejemplo:

        37 estudiantes -> 3 cupos disponibles.

    El resultado nunca será menor que cero.
    """

    total = contar_estudiantes_grupo(
        grupo_id
    )

    disponible = (
        MAX_ESTUDIANTES_GRUPO - total
    )

    return max(disponible, 0)


# ============================================================
# GENERAR CÓDIGO TEMPORAL
# ============================================================

def codigo_temporal():
    """
    Genera un código temporal único.

    Se utiliza antes de conocer el id_estudiante.

    Ejemplo:

        TMP-4f7b8c...
    """

    return (
        "TMP-"
        + uuid.uuid4().hex
    )


# ============================================================
# GENERAR CÓDIGO ESTUDIANTIL DEFINITIVO
# ============================================================

def codigo_final(id_estudiante):
    """
    Genera el código estudiantil definitivo.

    Formato:

        EDU-AAAA-00001

    Ejemplos:

        EDU-2026-00001
        EDU-2026-00002
        EDU-2026-00003

    El número final corresponde al ID interno del estudiante.

    Esto permite generar un código único sin pedirle
    al estudiante que lo escriba manualmente.
    """

    estudiante_id = _entero(
        id_estudiante
    )

    if estudiante_id is None or estudiante_id <= 0:
        raise ValueError(
            "No se puede generar el código estudiantil "
            "porque el ID del estudiante no es válido."
        )

    return (
        f"EDU-{datetime.now().year}-"
        f"{estudiante_id:05d}"
    )


# ============================================================
# VALIDAR CÓDIGO ESTUDIANTIL
# ============================================================

def validar_codigo_estudiantil(codigo):
    """
    Comprueba que un código estudiantil tenga el formato
    esperado.

    Formato:

        EDU-2026-00001

    Devuelve:

        True / False

    Esta función solamente valida el formato.
    No comprueba si el código existe en la BD.
    """

    if not codigo:
        return False

    codigo = str(codigo).strip().upper()

    partes = codigo.split("-")

    if len(partes) != 3:
        return False

    prefijo, anio, numero = partes

    if prefijo != "EDU":
        return False

    if len(anio) != 4 or not anio.isdigit():
        return False

    if len(numero) != 5 or not numero.isdigit():
        return False

    return True


# ============================================================
# BUSCAR ESTUDIANTE POR CÓDIGO
# ============================================================

def obtener_estudiante_por_codigo(codigo):
    """
    Busca un estudiante utilizando su código estudiantil.

    Devuelve:
        Diccionario del estudiante.
        None si no existe.
    """

    if not validar_codigo_estudiantil(codigo):
        return None

    codigo = str(codigo).strip().upper()

    return consultar(
        """
        SELECT
            e.id_estudiante,
            e.id_usuario,
            e.codigo_estudiantil,
            e.tipo_documento,
            e.documento,
            e.nombres,
            e.apellidos,
            e.curso,
            e.id_sede,
            e.id_jornada,
            e.id_grado,
            e.id_grupo,
            e.id_periodo,
            e.estado
        FROM estudiantes e
        WHERE e.codigo_estudiantil = %s
        LIMIT 1
        """,
        (codigo,),
        uno=True,
    )


# ============================================================
# BUSCAR ESTUDIANTE POR DOCUMENTO
# ============================================================

def obtener_estudiante_por_documento(documento):
    """
    Busca un estudiante por número de documento.
    """

    if not documento:
        return None

    documento = str(documento).strip()

    if not documento:
        return None

    return consultar(
        """
        SELECT
            e.id_estudiante,
            e.id_usuario,
            e.codigo_estudiantil,
            e.tipo_documento,
            e.documento,
            e.nombres,
            e.apellidos,
            e.curso,
            e.id_sede,
            e.id_jornada,
            e.id_grado,
            e.id_grupo,
            e.id_periodo,
            e.estado
        FROM estudiantes e
        WHERE e.documento = %s
        LIMIT 1
        """,
        (documento,),
        uno=True,
    )


# ============================================================
# BUSCAR ESTUDIANTE POR ID
# ============================================================

def obtener_estudiante(id_estudiante):
    """
    Busca un estudiante por su ID interno.
    """

    estudiante_id = _entero(
        id_estudiante
    )

    if estudiante_id is None:
        return None

    return consultar(
        """
        SELECT
            e.id_estudiante,
            e.id_usuario,
            e.codigo_estudiantil,
            e.tipo_documento,
            e.documento,
            e.nombres,
            e.apellidos,
            e.curso,
            e.id_sede,
            e.id_jornada,
            e.id_grado,
            e.id_grupo,
            e.id_periodo,
            e.estado
        FROM estudiantes e
        WHERE e.id_estudiante = %s
        LIMIT 1
        """,
        (estudiante_id,),
        uno=True,
    )


# ============================================================
# EXPORTAR FUNCIONES
# ============================================================

__all__ = [
    "GRADOS_PERMITIDOS",
    "GRUPOS_VISIBLES",
    "MAX_ESTUDIANTES_GRUPO",
    "_entero",
    "validar_grado",
    "validar_grupo_visible",
    "obtener_grupo_real",
    "obtener_id_grupo_real",
    "validar_grupo_para_grado",
    "bloquear_y_comprobar_cupo",
    "contar_estudiantes_grupo",
    "cupo_disponible",
    "codigo_temporal",
    "codigo_final",
    "validar_codigo_estudiantil",
    "obtener_estudiante_por_codigo",
    "obtener_estudiante_por_documento",
    "obtener_estudiante",
]