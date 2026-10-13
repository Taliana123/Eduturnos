# ============================================================
# AUTH - EDUTURNOS
# ============================================================

from calendar import monthcalendar
from datetime import date, datetime
import time
import hashlib

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from database.db import (
    consultar,
    ejecutar,
    transaccion,
)

from roles import (
    PORTALES,
    SEDES_INSTITUCIONALES,
    es_correo_institucional,
    es_codigo_institucional_valido,
    validar_codigo_sede,
    obtener_sede,
)

from routes.helpers import usuario_actual

# ------------------------------------------------------------
# SERVICIO DE ESTUDIANTES
# ------------------------------------------------------------

from servicios.estudiantes import (
    GRADOS_PERMITIDOS,
    GRUPOS_VISIBLES,
    MAX_ESTUDIANTES_GRUPO,
    validar_grado,
    validar_grupo_visible,
    obtener_grupo_real,
    bloquear_y_comprobar_cupo,
    codigo_temporal,
    codigo_final,
)


# ============================================================
# BLUEPRINT
# ============================================================

auth_bp = Blueprint("auth", __name__)


# ============================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================

MAX_INTENTOS = 5
BLOQUEO_MINUTOS = 15


# ============================================================
# REGLAS DE ESTUDIANTES
# ============================================================

GRADO_MINIMO_ESTUDIANTE = 6
GRADO_MAXIMO_ESTUDIANTE = 11

GRUPOS_VISIBLES_AUTH = {1, 2, 3, 4, 5, 6}

MAX_ESTUDIANTES_POR_GRUPO = 40


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def _sedes():
    try:
        filas = consultar(
            """
            SELECT
                id,
                nombre,
                direccion
            FROM sedes
            WHERE estado = 1
            ORDER BY id
            """
        )

        if filas:
            return [
                {
                    "id": int(fila["id"]),
                    "nombre": fila["nombre"],
                    "direccion": fila.get("direccion") or "",
                }
                for fila in filas
            ]

    except Exception as exc:
        print(
            "ERROR OBTENIENDO SEDES:",
            repr(exc),
            flush=True,
        )

    return [
        {
            "id": sede[0],
            "nombre": sede[1],
            "direccion": sede[2],
        }
        for sede in SEDES_INSTITUCIONALES
    ]


def _jornadas():
    try:
        filas = consultar(
            """
            SELECT
                id,
                nombre
            FROM jornadas
            WHERE estado = 1
            ORDER BY CASE nombre
                WHEN 'Mañana' THEN 1
                WHEN 'Tarde' THEN 2
                WHEN 'Noche' THEN 3
                ELSE 4
            END, nombre
            """
        )

        if filas:
            return [
                {
                    "id": int(fila["id"]),
                    "nombre": fila["nombre"],
                }
                for fila in filas
            ]

    except Exception as exc:
        print(
            "ERROR OBTENIENDO JORNADAS:",
            repr(exc),
            flush=True,
        )

    return [
        {
            "id": 1,
            "nombre": "Mañana",
        },
        {
            "id": 2,
            "nombre": "Tarde",
        },
        {
            "id": 3,
            "nombre": "Noche",
        },
    ]


def _mostrar_registro(
    portal,
    info,
    sedes,
    jornadas,
):
    try:
        grados = consultar(
            """
            SELECT
                id,
                nombre
            FROM grados
            WHERE estado = 1
            ORDER BY CAST(nombre AS UNSIGNED), nombre
            """
        )
    except Exception as exc:
        print(
            "ERROR OBTENIENDO GRADOS:",
            repr(exc),
            flush=True,
        )
        grados = []

    try:
        grupos = consultar(
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
                g.estado = 1
                AND gr.estado = 1
            ORDER BY
                CAST(gr.nombre AS UNSIGNED), gr.nombre,
                CAST(g.nombre AS UNSIGNED),
                g.nombre
            """
        )
    except Exception as exc:
        print(
            "ERROR OBTENIENDO GRUPOS:",
            repr(exc),
            flush=True,
        )
        grupos = []

    return render_template(
        "auth/registro_portal.html",
        portal=portal,
        info=info,
        sedes=sedes,
        jornadas=jornadas,
        grados=grados,
        grupos=grupos,
    )


def _mostrar_login():
    return render_template(
        "auth/login.html",
        sedes=_sedes(),
        jornadas=_jornadas(),
    )


def _correo(valor):
    return (valor or "").strip().lower()


def _rol_id(nombre):
    fila = consultar(
        """
        SELECT
            id
        FROM roles
        WHERE nombre = %s
        LIMIT 1
        """,
        (nombre,),
        uno=True,
    )

    if fila:
        return fila["id"]

    return None


# ============================================================
# OBTENER VALOR DEL FORMULARIO
#
# Permite que el HTML utilice cualquiera de estas variantes:
#
# id_sede / sede_id
# id_jornada / jornada_id
# id_grado / grado_id
# id_grupo / grupo_id
# ============================================================

def _form_value(*nombres):
    for nombre in nombres:
        valor = request.form.get(nombre)

        if valor is not None:
            valor = str(valor).strip()

            if valor:
                return valor

    return ""


# ============================================================
# VALIDACIONES DE GRADO
# ============================================================

def _grado_estudiante_valido(grado_id):
    try:
        grado = int(grado_id)
    except (TypeError, ValueError):
        return None

    if grado not in GRADOS_PERMITIDOS:
        return None

    if not (
        GRADO_MINIMO_ESTUDIANTE
        <= grado
        <= GRADO_MAXIMO_ESTUDIANTE
    ):
        return None

    return consultar(
        """
        SELECT
            id,
            nombre
        FROM grados
        WHERE
            id = %s
            AND estado = 1
        LIMIT 1
        """,
        (grado,),
        uno=True,
    )


# ============================================================
# GRUPO VISIBLE
# ============================================================

def _numero_grupo_visible(valor):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return None

    if numero not in GRUPOS_VISIBLES_AUTH:
        return None

    return numero


# ============================================================
# OBTENER GRUPO REAL
#
# Ejemplo:
#
# 6.º + Grupo 1
#
# puede corresponder a:
#
# id_grupo = 31
#
# El usuario nunca debe introducir el ID 31.
# ============================================================

def _obtener_grupo_real(
    grado_id,
    grupo_visible,
):
    grado = _grado_estudiante_valido(
        grado_id
    )

    if not grado:
        return None

    numero = _numero_grupo_visible(
        grupo_visible
    )

    if numero is None:
        return None

    return obtener_grupo_real(
        grado_id,
        numero,
    )


# ============================================================
# VALIDAR GRUPO
# ============================================================

def _validar_grupo_para_registro(
    grado_id,
    grupo_visible,
):
    grupo = _obtener_grupo_real(
        grado_id,
        grupo_visible,
    )

    if not grupo:
        return (
            None,
            "El grupo seleccionado no existe para "
            "el grado seleccionado.",
        )

    return grupo, None


# ============================================================
# CONTROL DE CUPO
# ============================================================

def _bloquear_grupo_y_comprobar_cupo(
    cnx,
    grado_id,
    grupo_visible,
    excluir_estudiante_id=None,
):
    return bloquear_y_comprobar_cupo(
        cnx,
        grado_id,
        grupo_visible,
        excluir_estudiante_id=excluir_estudiante_id,
    )


# ============================================================
# CÓDIGO ESTUDIANTIL
# ============================================================

def _codigo_estudiantil(id_estudiante):
    return codigo_final(
        id_estudiante
    )


def _asignar_codigo_estudiantil_tx(
    cnx,
    id_estudiante,
):
    codigo = codigo_final(
        id_estudiante
    )

    cur = cnx.cursor()

    try:
        cur.execute(
            """
            UPDATE estudiantes
            SET codigo_estudiantil = %s
            WHERE id_estudiante = %s
            """,
            (
                codigo,
                id_estudiante,
            ),
        )
    finally:
        cur.close()

    return codigo


# ============================================================
# CONTROL DE INTENTOS
# ============================================================

def _asegurar_control_acceso():
    try:
        ejecutar(
            """
            CREATE TABLE IF NOT EXISTS control_acceso (
                id INT AUTO_INCREMENT PRIMARY KEY,
                clave_hash CHAR(64) NOT NULL UNIQUE,
                intentos INT NOT NULL DEFAULT 0,
                bloqueado_hasta DATETIME NULL,
                fecha_actualizacion DATETIME NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_control_bloqueo (
                    bloqueado_hasta
                )
            ) ENGINE=InnoDB
            """
        )

        return True

    except Exception as exc:
        print(
            "ERROR CREANDO control_acceso:",
            repr(exc),
            flush=True,
        )

        return False


def _registrar_intento_fallido(clave_hash):
    try:
        if not _asegurar_control_acceso():
            return

        ejecutar(
            """
            INSERT INTO control_acceso
            (
                clave_hash,
                intentos,
                bloqueado_hasta
            )
            VALUES
            (
                %s,
                1,
                NULL
            )
            ON DUPLICATE KEY UPDATE
                intentos = intentos + 1,
                fecha_actualizacion = NOW()
            """,
            (clave_hash,),
        )

        fila = consultar(
            """
            SELECT
                intentos
            FROM control_acceso
            WHERE clave_hash = %s
            LIMIT 1
            """,
            (clave_hash,),
            uno=True,
        )

        if fila:
            intentos = int(
                fila.get("intentos") or 0
            )

            if intentos >= MAX_INTENTOS:
                ejecutar(
                    """
                    UPDATE control_acceso
                    SET bloqueado_hasta =
                        DATE_ADD(
                            NOW(),
                            INTERVAL %s MINUTE
                        )
                    WHERE clave_hash = %s
                    """,
                    (
                        BLOQUEO_MINUTOS,
                        clave_hash,
                    ),
                )

    except Exception as exc:
        print(
            "ERROR REGISTRANDO INTENTO:",
            repr(exc),
            flush=True,
        )


def _limpiar_intentos(clave_hash):
    try:
        if _asegurar_control_acceso():
            ejecutar(
                """
                DELETE FROM control_acceso
                WHERE clave_hash = %s
                """,
                (clave_hash,),
            )

    except Exception as exc:
        print(
            "ERROR LIMPIANDO INTENTOS:",
            repr(exc),
            flush=True,
        )


# ============================================================
# BUSCAR USUARIO
# ============================================================

def _buscar_usuario(identificador):
    valor = (identificador or "").strip()
    correo = _correo(valor)

    return consultar(
        """
        SELECT
            u.*,
            r.nombre AS rol_nombre
        FROM usuarios u
        INNER JOIN roles r
            ON r.id = u.id_rol
        WHERE
            u.documento = %s
            OR LOWER(TRIM(u.correo)) = %s
        LIMIT 1
        """,
        (
            valor,
            correo,
        ),
        uno=True,
    )


# ============================================================
# VALIDAR PERSONAL INSTITUCIONAL
# ============================================================

def _perfil_personal(
    portal,
    tipo_documento,
    documento,
    nombres,
    apellidos,
    correo,
    sede_id,
    jornada_id,
    codigo,
):
    if portal not in PORTALES:
        return None

    info = PORTALES[portal]
    rol = info["rol"]

    tipo_documento = (
        tipo_documento or "CC"
    ).strip().upper()

    documento = (
        documento or ""
    ).strip()

    nombres = (
        nombres or ""
    ).strip()

    apellidos = (
        apellidos or ""
    ).strip()

    correo = (
        correo or ""
    ).strip().lower()

    codigo = (
        codigo or ""
    ).strip()

    if tipo_documento not in (
        "CC",
        "TI",
        "CE",
    ):
        return None

    if not documento:
        return None

    if not nombres:
        return None

    if not apellidos:
        return None

    if not es_correo_institucional(correo):
        return None

    try:
        sede_id = int(sede_id)
    except (TypeError, ValueError):
        return None

    sede = obtener_sede(
        sede_id
    )

    if not sede:
        return None

    try:
        jornada_id = int(jornada_id)
    except (TypeError, ValueError):
        return None

    jornada = consultar(
        """
        SELECT
            id,
            nombre
        FROM jornadas
        WHERE
            id = %s
            AND estado = 1
        LIMIT 1
        """,
        (jornada_id,),
        uno=True,
    )

    if not jornada:
        return None

    if not es_codigo_institucional_valido(
        codigo
    ):
        return None

    if not validar_codigo_sede(
        sede_id,
        codigo,
    ):
        return None

    existente = consultar(
        """
        SELECT
            id_usuario
        FROM usuarios
        WHERE
            documento = %s
            OR LOWER(TRIM(correo)) = %s
        LIMIT 1
        """,
        (
            documento,
            correo,
        ),
        uno=True,
    )

    if existente:
        return None

    return {
        "id": None,
        "id_usuario": None,
        "tipo_documento": tipo_documento,
        "documento": documento,
        "nombres": nombres,
        "apellidos": apellidos,
        "correo_institucional": correo,
        "id_sede": sede_id,
        "id_jornada": jornada_id,
        "sede_nombre": sede["nombre"],
        "sede_direccion": sede["direccion"],
        "jornada_nombre": jornada["nombre"],
        "codigo_institucional": codigo,
        "rol_nombre": rol,
    }


# ============================================================
# CREAR DIRECTORIO PERSONAL
# ============================================================

def _crear_directorio_personal_tx(
    cnx,
    usuario_id,
    rol,
    perfil,
):
    rol_id = _rol_id(
        rol
    )

    if not rol_id:
        raise ValueError(
            f"No existe el rol '{rol}' en la tabla roles."
        )

    if not validar_codigo_sede(
        perfil["id_sede"],
        perfil["codigo_institucional"],
    ):
        raise ValueError(
            "El código institucional no corresponde "
            "a la sede seleccionada."
        )

    codigo_hash = generate_password_hash(
        perfil["codigo_institucional"]
    )

    cur = cnx.cursor(
        dictionary=True
    )

    try:
        cur.execute(
            """
            SELECT
                id
            FROM directorio_institucional
            WHERE
                documento = %s
                OR LOWER(TRIM(correo_institucional)) = %s
            LIMIT 1
            """,
            (
                perfil["documento"],
                perfil[
                    "correo_institucional"
                ].lower(),
            ),
        )

        directorio = cur.fetchone()

        if directorio:
            cur.execute(
                """
                UPDATE directorio_institucional
                SET
                    id_usuario = %s,
                    id_rol = %s,
                    tipo_documento = %s,
                    nombres = %s,
                    apellidos = %s,
                    correo_institucional = %s,
                    id_sede = %s,
                    id_jornada = %s,
                    codigo_institucional_hash = %s,
                    estado = 1,
                    fecha_vinculacion = NOW()
                WHERE id = %s
                """,
                (
                    usuario_id,
                    rol_id,
                    perfil["tipo_documento"],
                    perfil["nombres"],
                    perfil["apellidos"],
                    perfil[
                        "correo_institucional"
                    ],
                    perfil["id_sede"],
                    perfil["id_jornada"],
                    codigo_hash,
                    directorio["id"],
                ),
            )

        else:
            cur.execute(
                """
                INSERT INTO directorio_institucional
                (
                    id_usuario,
                    id_rol,
                    tipo_documento,
                    documento,
                    nombres,
                    apellidos,
                    correo_institucional,
                    id_sede,
                    id_jornada,
                    codigo_institucional_hash,
                    estado,
                    fecha_vinculacion
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    1,
                    NOW()
                )
                """,
                (
                    usuario_id,
                    rol_id,
                    perfil["tipo_documento"],
                    perfil["documento"],
                    perfil["nombres"],
                    perfil["apellidos"],
                    perfil[
                        "correo_institucional"
                    ],
                    perfil["id_sede"],
                    perfil["id_jornada"],
                    codigo_hash,
                ),
            )

    finally:
        cur.close()


# ============================================================
# RELACIONAR USUARIO CON PERFIL
# ============================================================

def _relacionar_tx(
    cnx,
    usuario_id,
    rol,
    perfil,
):
    cur = cnx.cursor(
        dictionary=True
    )

    try:

        if rol == "Estudiante":

            if "id_estudiante" not in perfil:
                raise ValueError(
                    "El perfil de estudiante no contiene "
                    "id_estudiante."
                )

            cur.execute(
                """
                UPDATE estudiantes
                SET id_usuario = %s
                WHERE id_estudiante = %s
                """,
                (
                    usuario_id,
                    perfil["id_estudiante"],
                ),
            )

            return

        if rol == "Acudiente":

            if "id_acudiente" not in perfil:
                raise ValueError(
                    "El perfil de acudiente no contiene "
                    "id_acudiente."
                )

            cur.execute(
                """
                UPDATE acudientes
                SET id_usuario = %s
                WHERE id_acudiente = %s
                """,
                (
                    usuario_id,
                    perfil["id_acudiente"],
                ),
            )

            return

        if rol == "Docente":

            cur.execute(
                """
                SELECT
                    id_docente
                FROM docentes
                WHERE documento = %s
                LIMIT 1
                """,
                (
                    perfil["documento"],
                ),
            )

            docente = cur.fetchone()

            if docente:
                cur.execute(
                    """
                    UPDATE docentes
                    SET
                        id_usuario = %s,
                        tipo_documento = %s,
                        nombres = %s,
                        apellidos = %s,
                        correo_institucional = %s,
                        id_sede = %s,
                        id_jornada = %s,
                        estado = 1
                    WHERE id_docente = %s
                    """,
                    (
                        usuario_id,
                        perfil["tipo_documento"],
                        perfil["nombres"],
                        perfil["apellidos"],
                        perfil[
                            "correo_institucional"
                        ],
                        perfil["id_sede"],
                        perfil["id_jornada"],
                        docente["id_docente"],
                    ),
                )

            else:
                cur.execute(
                    """
                    INSERT INTO docentes
                    (
                        id_usuario,
                        tipo_documento,
                        documento,
                        nombres,
                        apellidos,
                        correo_institucional,
                        telefono,
                        id_sede,
                        id_jornada,
                        estado
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        NULL,
                        %s,
                        %s,
                        1
                    )
                    """,
                    (
                        usuario_id,
                        perfil["tipo_documento"],
                        perfil["documento"],
                        perfil["nombres"],
                        perfil["apellidos"],
                        perfil[
                            "correo_institucional"
                        ],
                        perfil["id_sede"],
                        perfil["id_jornada"],
                    ),
                )

            _crear_directorio_personal_tx(
                cnx,
                usuario_id,
                rol,
                perfil,
            )

            return

        if rol == "Administrador / Coordinador":

            _crear_directorio_personal_tx(
                cnx,
                usuario_id,
                rol,
                perfil,
            )

            return

        if rol == "Rector":

            _crear_directorio_personal_tx(
                cnx,
                usuario_id,
                rol,
                perfil,
            )

            return

        raise ValueError(
            f"Rol no soportado: {rol}"
        )

    finally:
        cur.close()


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():

    if request.method == "GET":
        return _mostrar_login()

    identificador = request.form.get(
        "identificador",
        "",
    ).strip()

    password = request.form.get(
        "password",
        "",
    )

    codigo = request.form.get(
        "codigo_institucional",
        "",
    ).strip()

    sede_id = _form_value(
        "id_sede",
        "sede_id",
    )

    jornada_id = _form_value(
        "id_jornada",
        "jornada_id",
    )

    rate_key = hashlib.sha256(
        (
            identificador.lower()
            + "|"
            + (
                request.remote_addr
                or "unknown"
            )
        ).encode("utf-8")
    ).hexdigest()

    try:
        _asegurar_control_acceso()

        limite = consultar(
            """
            SELECT *
            FROM control_acceso
            WHERE
                clave_hash = %s
                AND bloqueado_hasta > NOW()
            LIMIT 1
            """,
            (
                rate_key,
            ),
            uno=True,
        )

    except Exception as exc:
        print(
            "ERROR CONTROL ACCESO:",
            repr(exc),
            flush=True,
        )

        limite = None

    if limite:
        flash(
            "Demasiados intentos. "
            "Espera unos minutos antes de volver a intentarlo.",
            "error",
        )

        return _mostrar_login()

    usuario = _buscar_usuario(
        identificador
    )

    if not usuario:

        _registrar_intento_fallido(
            rate_key
        )

        flash(
            "Credenciales incorrectas.",
            "error",
        )

        return _mostrar_login()

    bloqueado = usuario.get(
        "bloqueado_hasta"
    )

    if bloqueado and bloqueado > datetime.now():

        flash(
            "La cuenta está temporalmente bloqueada.",
            "error",
        )

        return _mostrar_login()

    password_hash = usuario.get(
        "password_hash",
        "",
    )

    try:
        password_correcta = check_password_hash(
            password_hash,
            password,
        )

    except Exception as exc:
        print(
            "ERROR VALIDANDO CONTRASEÑA:",
            repr(exc),
            flush=True,
        )

        password_correcta = False

    if not password_correcta:

        _registrar_intento_fallido(
            rate_key
        )

        intentos = (
            int(
                usuario.get(
                    "intentos_fallidos"
                )
                or 0
            )
            + 1
        )

        if intentos >= MAX_INTENTOS:

            ejecutar(
                """
                UPDATE usuarios
                SET
                    intentos_fallidos = %s,
                    bloqueado_hasta =
                        DATE_ADD(
                            NOW(),
                            INTERVAL %s MINUTE
                        )
                WHERE id_usuario = %s
                """,
                (
                    intentos,
                    BLOQUEO_MINUTOS,
                    usuario["id_usuario"],
                ),
            )

            flash(
                "Demasiados intentos. "
                "La cuenta quedó bloqueada durante "
                "15 minutos.",
                "error",
            )

        else:

            ejecutar(
                """
                UPDATE usuarios
                SET intentos_fallidos = %s
                WHERE id_usuario = %s
                """,
                (
                    intentos,
                    usuario["id_usuario"],
                ),
            )

            flash(
                "Credenciales incorrectas.",
                "error",
            )

        return _mostrar_login()

    if not usuario.get("estado"):

        flash(
            "La cuenta está inactiva.",
            "error",
        )

        return _mostrar_login()

    rol = usuario.get(
        "rol_nombre"
    )

    # ========================================================
    # VALIDACIÓN EXTRA DEL PERSONAL
    # ========================================================

    if rol in (
        "Docente",
        "Administrador / Coordinador",
        "Rector",
    ):

        if not es_correo_institucional(
            usuario.get("correo", "")
        ):

            flash(
                "El personal debe ingresar con "
                "su correo institucional @jjfh.edu.co.",
                "error",
            )

            return _mostrar_login()

        if not sede_id.isdigit():

            flash(
                "Selecciona una sede válida.",
                "error",
            )

            return _mostrar_login()

        if not jornada_id.isdigit():

            flash(
                "Selecciona una jornada válida.",
                "error",
            )

            return _mostrar_login()

        if not es_codigo_institucional_valido(
            codigo
        ):

            flash(
                "El código institucional debe "
                "tener exactamente 6 dígitos.",
                "error",
            )

            return _mostrar_login()

        perfil = consultar(
            """
            SELECT *
            FROM directorio_institucional
            WHERE
                id_usuario = %s
                AND id_sede = %s
                AND id_jornada = %s
                AND estado = 1
            LIMIT 1
            """,
            (
                usuario["id_usuario"],
                int(sede_id),
                int(jornada_id),
            ),
            uno=True,
        )

        if not perfil:

            flash(
                "La sede o jornada no corresponden "
                "a tu cuenta.",
                "error",
            )

            return _mostrar_login()

        codigo_hash = perfil.get(
            "codigo_institucional_hash"
        )

        try:
            codigo_correcto = (
                bool(codigo_hash)
                and check_password_hash(
                    codigo_hash,
                    codigo,
                )
            )

        except Exception as exc:

            print(
                "ERROR VALIDANDO CÓDIGO EN LOGIN:",
                repr(exc),
                flush=True,
            )

            codigo_correcto = False

        if not codigo_correcto:

            _registrar_intento_fallido(rate_key)

            flash(
                "El código institucional no es correcto.",
                "error",
            )

            return _mostrar_login()

    # ========================================================
    # LOGIN CORRECTO
    # ========================================================

    ejecutar(
        """
        UPDATE usuarios
        SET
            intentos_fallidos = 0,
            bloqueado_hasta = NULL,
            ultimo_acceso = NOW()
        WHERE id_usuario = %s
        """,
        (
            usuario["id_usuario"],
        ),
    )

    _limpiar_intentos(
        rate_key
    )

    session.clear()
    session.permanent = True

    session["usuario_id"] = (
        usuario["id_usuario"]
    )

    session["rol_nombre"] = usuario["rol_nombre"]

    session["creado_en"] = time.time()

    return redirect(
        url_for("auth.dashboard")
    )


# ============================================================
# REGISTRO
# ============================================================

@auth_bp.route("/registro")
def registro():

    return render_template(
        "auth/registro.html",
        portales=PORTALES,
    )


# ============================================================
# REGISTRO POR PORTAL
# ============================================================

@auth_bp.route(
    "/registro/<portal>",
    methods=["GET", "POST"],
)
def registro_portal(portal):

    info = PORTALES.get(
        portal
    )

    if not info:

        flash(
            "Tipo de cuenta no válido.",
            "error",
        )

        return redirect(
            url_for("auth.registro")
        )

    sedes = _sedes()
    jornadas = _jornadas()

    # ========================================================
    # MOSTRAR FORMULARIO
    # ========================================================

    if request.method == "GET":

        return _mostrar_registro(
            portal,
            info,
            sedes,
            jornadas,
        )

    # ========================================================
    # DATOS GENERALES
    # ========================================================

    tipo_documento = (
        request.form.get(
            "tipo_documento",
            "CC",
        )
        .strip()
        .upper()
        or "CC"
    )

    documento = request.form.get(
        "documento",
        "",
    ).strip()

    nombres = request.form.get(
        "nombres",
        "",
    ).strip()

    apellidos = request.form.get(
        "apellidos",
        "",
    ).strip()

    correo = _correo(
        request.form.get(
            "correo",
            "",
        )
    )

    telefono = request.form.get(
        "telefono",
        "",
    ).strip()

    password = request.form.get(
        "password",
        "",
    )

    # ========================================================
    # DATOS DEL ESTUDIANTE
    #
    # Acepta tanto:
    #
    # id_sede / sede_id
    # id_jornada / jornada_id
    # id_grado / grado_id
    # id_grupo / grupo_id
    # ========================================================

    curso = request.form.get(
        "curso",
        "",
    ).strip()

    sede_id = _form_value(
        "id_sede",
        "sede_id",
    )

    jornada_id = _form_value(
        "id_jornada",
        "jornada_id",
    )

    grado_id = _form_value(
        "id_grado",
        "grado_id",
    )

    grupo_id = _form_value(
        "id_grupo",
        "grupo_id",
    )

    # ========================================================
    # DATOS DEL ESTUDIANTE DEL ACUDIENTE
    # ========================================================

    estudiante_tipo_documento = (
        request.form.get(
            "estudiante_tipo_documento",
            "TI",
        )
        .strip()
        .upper()
        or "TI"
    )

    estudiante_documento = request.form.get(
        "estudiante_documento",
        "",
    ).strip()

    estudiante_nombres = request.form.get(
        "estudiante_nombres",
        "",
    ).strip()

    estudiante_apellidos = request.form.get(
        "estudiante_apellidos",
        "",
    ).strip()

    estudiante_sede_id = _form_value(
        "estudiante_id_sede",
        "estudiante_sede_id",
        "id_sede_estudiante",
    )

    estudiante_jornada_id = _form_value(
        "estudiante_id_jornada",
        "estudiante_jornada_id",
        "id_jornada_estudiante",
    )

    estudiante_grado_id = _form_value(
        "estudiante_id_grado",
        "estudiante_grado_id",
        "id_grado_estudiante",
    )

    estudiante_grupo_id = _form_value(
        "estudiante_id_grupo",
        "estudiante_grupo_id",
        "id_grupo_estudiante",
    )

    estudiante_curso = request.form.get(
        "estudiante_curso",
        "",
    ).strip()

    parentesco = request.form.get(
        "parentesco",
        "",
    ).strip()

    # ========================================================
    # VALIDACIONES GENERALES
    # ========================================================

    if tipo_documento not in (
        "CC",
        "TI",
        "CE",
    ):

        flash(
            "Selecciona un tipo de documento válido.",
            "error",
        )

        return _mostrar_registro(
            portal,
            info,
            sedes,
            jornadas,
        )

    if not documento:

        flash(
            "Escribe el número de documento.",
            "error",
        )

        return _mostrar_registro(
            portal,
            info,
            sedes,
            jornadas,
        )

    if not nombres:

        flash(
            "Escribe los nombres.",
            "error",
        )

        return _mostrar_registro(
            portal,
            info,
            sedes,
            jornadas,
        )

    if not apellidos:

        flash(
            "Escribe los apellidos.",
            "error",
        )

        return _mostrar_registro(
            portal,
            info,
            sedes,
            jornadas,
        )

    if not correo:

        flash(
            "Escribe un correo electrónico.",
            "error",
        )

        return _mostrar_registro(
            portal,
            info,
            sedes,
            jornadas,
        )

    if len(password) < 12:

        flash(
            "La contraseña debe tener mínimo "
            "12 caracteres.",
            "error",
        )

        return _mostrar_registro(
            portal,
            info,
            sedes,
            jornadas,
        )

    # ========================================================
    # VALIDACIÓN ESTUDIANTE
    # ========================================================

    grupo_estudiante_real = None

    if portal == "estudiante":

        if not sede_id.isdigit():

            flash(
                "Selecciona una sede.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not jornada_id.isdigit():

            flash(
                "Selecciona una jornada.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        grado = _grado_estudiante_valido(
            grado_id
        )

        if not grado:

            flash(
                "Los estudiantes solamente pueden "
                "registrarse de sexto a undécimo.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not validar_grupo_visible(
            grupo_id
        ):

            flash(
                "Selecciona un grupo válido "
                "(Grupo 1 a Grupo 6).",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        grupo_estudiante_real = _obtener_grupo_real(
            grado_id,
            grupo_id,
        )

        if not grupo_estudiante_real:

            flash(
                "El grupo seleccionado no existe "
                "para el grado seleccionado.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

    # ========================================================
    # VALIDACIÓN ACUDIENTE
    # ========================================================

    if portal == "acudiente":

        if estudiante_tipo_documento not in (
            "CC",
            "TI",
            "CE",
        ):

            flash(
                "El tipo de documento del estudiante "
                "no es válido.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not estudiante_documento:

            flash(
                "Escribe el documento del estudiante.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not estudiante_nombres:

            flash(
                "Escribe los nombres del estudiante.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not estudiante_apellidos:

            flash(
                "Escribe los apellidos del estudiante.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not estudiante_sede_id.isdigit():

            flash(
                "Selecciona la sede del estudiante.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not estudiante_jornada_id.isdigit():

            flash(
                "Selecciona la jornada del estudiante.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        grado_estudiante = (
            _grado_estudiante_valido(
                estudiante_grado_id
            )
        )

        if not grado_estudiante:

            flash(
                "Los estudiantes solamente pueden "
                "registrarse de sexto a undécimo.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not validar_grupo_visible(
            estudiante_grupo_id
        ):

            flash(
                "Selecciona un grupo válido "
                "(Grupo 1 a Grupo 6).",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        grupo_estudiante_real = (
            _obtener_grupo_real(
                estudiante_grado_id,
                estudiante_grupo_id,
            )
        )

        if not grupo_estudiante_real:

            flash(
                "El grupo del estudiante no corresponde "
                "al grado seleccionado.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not parentesco:

            flash(
                "Selecciona el parentesco.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

    # ========================================================
    # VALIDACIÓN PERSONAL
    # ========================================================

    if info.get("requiere_codigo"):

        if not es_correo_institucional(
            correo
        ):

            flash(
                "Para este tipo de cuenta debes utilizar "
                "un correo terminado en @jjfh.edu.co.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not sede_id.isdigit():

            flash(
                "Selecciona una sede institucional.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not jornada_id.isdigit():

            flash(
                "Selecciona una jornada.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        codigo = request.form.get(
            "codigo_institucional",
            "",
        ).strip()

        if not es_codigo_institucional_valido(
            codigo
        ):

            flash(
                "El código institucional debe "
                "tener exactamente 6 dígitos.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        if not validar_codigo_sede(
            int(sede_id),
            codigo,
        ):

            flash(
                "El código institucional no corresponde "
                "a la sede seleccionada.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

    else:
        codigo = ""

    # ========================================================
    # PROCESAR REGISTRO
    # ========================================================

    try:

        rol = info.get("rol")

        rol_id = _rol_id(
            rol
        )

        if not rol_id:

            flash(
                "El rol seleccionado no está configurado "
                "en la base de datos.",
                "error",
            )

            return _mostrar_registro(
                portal,
                info,
                sedes,
                jornadas,
            )

        # ====================================================
        # COMPROBAR CUENTA EXISTENTE
        # ====================================================

        existente = consultar(
            """
            SELECT
                id_usuario,
                estado
            FROM usuarios
            WHERE
                documento = %s
                OR LOWER(TRIM(correo)) = %s
            LIMIT 1
            """,
            (
                documento,
                correo,
            ),
            uno=True,
        )

        if existente:

            flash(
                "Ya existe una cuenta con ese documento "
                "o correo. Inicia sesión.",
                "error",
            )

            return redirect(
                url_for("auth.login")
            )

        # ====================================================
        # PERSONAL INSTITUCIONAL
        # ====================================================

        if info.get("requiere_codigo"):

            perfil = _perfil_personal(
                portal,
                tipo_documento,
                documento,
                nombres,
                apellidos,
                correo,
                int(sede_id),
                int(jornada_id),
                codigo,
            )

            if not perfil:

                flash(
                    "No fue posible validar los datos del "
                    "personal institucional. Revisa documento, "
                    "correo, sede, jornada y código.",
                    "error",
                )

                return _mostrar_registro(
                    portal,
                    info,
                    sedes,
                    jornadas,
                )

            password_hash = generate_password_hash(
                password
            )

            with transaccion() as cnx:

                cur = cnx.cursor()

                try:
                    cur.execute(
                        """
                        INSERT INTO usuarios
                        (
                            id_rol,
                            tipo_documento,
                            documento,
                            nombres,
                            apellidos,
                            correo,
                            telefono,
                            password_hash,
                            verificado,
                            estado,
                            intentos_fallidos,
                            bloqueado_hasta
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            1,
                            1,
                            0,
                            NULL
                        )
                        """,
                        (
                            rol_id,
                            tipo_documento,
                            documento,
                            nombres,
                            apellidos,
                            correo,
                            telefono or None,
                            password_hash,
                        ),
                    )

                    usuario_id = cur.lastrowid

                finally:
                    cur.close()

                _relacionar_tx(
                    cnx,
                    usuario_id,
                    rol,
                    perfil,
                )

            flash(
                "Registro completado correctamente. "
                "Ya puedes iniciar sesión.",
                "success",
            )

            return redirect(
                url_for("auth.login")
            )

        # ====================================================
        # ESTUDIANTE
        # ====================================================

        if portal == "estudiante":

            periodo = consultar(
                """
                SELECT
                    id
                FROM periodos_academicos
                WHERE estado = 1
                ORDER BY id DESC
                LIMIT 1
                """,
                uno=True,
            )

            if not periodo:

                flash(
                    "No existe un periodo académico activo.",
                    "error",
                )

                return _mostrar_registro(
                    portal,
                    info,
                    sedes,
                    jornadas,
                )

            estudiante_existente = consultar(
                """
                SELECT *
                FROM estudiantes
                WHERE documento = %s
                LIMIT 1
                """,
                (
                    documento,
                ),
                uno=True,
            )

            if (
                estudiante_existente
                and estudiante_existente.get("estado")
                != "Activo"
            ):

                flash(
                    "El estudiante encontrado está retirado "
                    "y no puede crear una cuenta activa.",
                    "error",
                )

                return _mostrar_registro(
                    portal,
                    info,
                    sedes,
                    jornadas,
                )

            if (
                estudiante_existente
                and estudiante_existente.get("id_usuario")
            ):

                flash(
                    "Este estudiante ya tiene una cuenta "
                    "registrada. Inicia sesión.",
                    "error",
                )

                return redirect(
                    url_for("auth.login")
                )

            password_hash = generate_password_hash(
                password
            )

            with transaccion() as cnx:

                cur = cnx.cursor(
                    dictionary=True
                )

                try:

                    # ----------------------------------------
                    # BLOQUEAR GRUPO Y COMPROBAR CUPO
                    # ----------------------------------------

                    grupo_real, total_grupo = (
                        _bloquear_grupo_y_comprobar_cupo(
                            cnx,
                            grado_id,
                            grupo_id,
                        )
                    )

                    # ----------------------------------------
                    # CREAR USUARIO
                    # ----------------------------------------

                    cur.execute(
                        """
                        INSERT INTO usuarios
                        (
                            id_rol,
                            tipo_documento,
                            documento,
                            nombres,
                            apellidos,
                            correo,
                            telefono,
                            password_hash,
                            verificado,
                            estado,
                            intentos_fallidos,
                            bloqueado_hasta
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            1,
                            1,
                            0,
                            NULL
                        )
                        """,
                        (
                            rol_id,
                            tipo_documento,
                            documento,
                            nombres,
                            apellidos,
                            correo,
                            telefono or None,
                            password_hash,
                        ),
                    )

                    usuario_id = cur.lastrowid

                    # ----------------------------------------
                    # ESTUDIANTE EXISTENTE
                    # ----------------------------------------

                    if estudiante_existente:

                        estudiante_id = (
                            estudiante_existente[
                                "id_estudiante"
                            ]
                        )

                        cur.execute(
                            """
                            UPDATE estudiantes
                            SET
                                id_usuario = %s,
                                tipo_documento = %s,
                                nombres = %s,
                                apellidos = %s,
                                id_sede = %s,
                                id_jornada = %s,
                                id_grado = %s,
                                id_grupo = %s,
                                curso = %s,
                                estado = 'Activo'
                            WHERE id_estudiante = %s
                            """,
                            (
                                usuario_id,
                                tipo_documento,
                                nombres,
                                apellidos,
                                int(sede_id),
                                int(jornada_id),
                                int(grado_id),
                                grupo_real["id"],
                                curso or None,
                                estudiante_id,
                            ),
                        )

                        # Si por alguna razón el registro
                        # existente no tiene un código válido,
                        # se conserva su código actual.

                    # ----------------------------------------
                    # ESTUDIANTE NUEVO
                    # ----------------------------------------

                    else:

                        codigo_tmp = codigo_temporal()

                        cur.execute(
                            """
                            INSERT INTO estudiantes
                            (
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
                            VALUES
                            (
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                'Activo'
                            )
                            """,
                            (
                                usuario_id,
                                codigo_tmp,
                                tipo_documento,
                                documento,
                                nombres,
                                apellidos,
                                curso or None,
                                int(sede_id),
                                int(jornada_id),
                                int(grado_id),
                                grupo_real["id"],
                                periodo["id"],
                            ),
                        )

                        estudiante_id = cur.lastrowid

                        # ------------------------------------
                        # CÓDIGO DEFINITIVO
                        # ------------------------------------

                        codigo_estudiantil = (
                            _asignar_codigo_estudiantil_tx(
                                cnx,
                                estudiante_id,
                            )
                        )

                finally:
                    cur.close()

            codigo_mostrar = (
                consultar(
                    """
                    SELECT codigo_estudiantil
                    FROM estudiantes
                    WHERE id_estudiante = %s
                    LIMIT 1
                    """,
                    (
                        estudiante_id,
                    ),
                    uno=True,
                )
            )

            codigo_mostrar = (
                codigo_mostrar[
                    "codigo_estudiantil"
                ]
                if codigo_mostrar
                else _codigo_estudiantil(
                    estudiante_id
                )
            )

            flash(
                "Cuenta de estudiante creada correctamente. "
                f"Tu código estudiantil es {codigo_mostrar}. "
                "Ya puedes iniciar sesión.",
                "success",
            )

            return redirect(
                url_for("auth.login")
            )

        # ====================================================
        # ACUDIENTE
        # ====================================================

        if portal == "acudiente":

            periodo = consultar(
                """
                SELECT
                    id
                FROM periodos_academicos
                WHERE estado = 1
                ORDER BY id DESC
                LIMIT 1
                """,
                uno=True,
            )

            if not periodo:

                flash(
                    "No existe un periodo académico activo.",
                    "error",
                )

                return _mostrar_registro(
                    portal,
                    info,
                    sedes,
                    jornadas,
                )

            acudiente_existente = consultar(
                """
                SELECT *
                FROM acudientes
                WHERE documento = %s
                LIMIT 1
                """,
                (
                    documento,
                ),
                uno=True,
            )

            if (
                acudiente_existente
                and int(
                    acudiente_existente.get(
                        "estado"
                    ) or 0
                ) != 1
            ):

                flash(
                    "El registro del acudiente está inactivo.",
                    "error",
                )

                return _mostrar_registro(
                    portal,
                    info,
                    sedes,
                    jornadas,
                )

            if (
                acudiente_existente
                and acudiente_existente.get(
                    "id_usuario"
                )
            ):

                flash(
                    "Este acudiente ya tiene una cuenta "
                    "registrada. Inicia sesión.",
                    "error",
                )

                return redirect(
                    url_for("auth.login")
                )

            estudiante_existente = consultar(
                """
                SELECT *
                FROM estudiantes
                WHERE documento = %s
                LIMIT 1
                """,
                (
                    estudiante_documento,
                ),
                uno=True,
            )

            if (
                estudiante_existente
                and estudiante_existente.get(
                    "estado"
                ) != "Activo"
            ):

                flash(
                    "El estudiante seleccionado está retirado.",
                    "error",
                )

                return _mostrar_registro(
                    portal,
                    info,
                    sedes,
                    jornadas,
                )

            password_hash = generate_password_hash(
                password
            )

            with transaccion() as cnx:

                cur = cnx.cursor(
                    dictionary=True
                )

                try:

                    # ----------------------------------------
                    # CREAR USUARIO ACUDIENTE
                    # ----------------------------------------

                    cur.execute(
                        """
                        INSERT INTO usuarios
                        (
                            id_rol,
                            tipo_documento,
                            documento,
                            nombres,
                            apellidos,
                            correo,
                            telefono,
                            password_hash,
                            verificado,
                            estado,
                            intentos_fallidos,
                            bloqueado_hasta
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            1,
                            1,
                            0,
                            NULL
                        )
                        """,
                        (
                            rol_id,
                            tipo_documento,
                            documento,
                            nombres,
                            apellidos,
                            correo,
                            telefono or None,
                            password_hash,
                        ),
                    )

                    usuario_id = cur.lastrowid

                    # ----------------------------------------
                    # CREAR / ACTUALIZAR ACUDIENTE
                    # ----------------------------------------

                    if acudiente_existente:

                        acudiente_id = (
                            acudiente_existente[
                                "id_acudiente"
                            ]
                        )

                        cur.execute(
                            """
                            UPDATE acudientes
                            SET
                                id_usuario = %s,
                                tipo_documento = %s,
                                nombres = %s,
                                apellidos = %s,
                                telefono = %s,
                                correo = %s,
                                estado = 1
                            WHERE id_acudiente = %s
                            """,
                            (
                                usuario_id,
                                tipo_documento,
                                nombres,
                                apellidos,
                                telefono or None,
                                correo,
                                acudiente_id,
                            ),
                        )

                    else:

                        cur.execute(
                            """
                            INSERT INTO acudientes
                            (
                                id_usuario,
                                tipo_documento,
                                documento,
                                nombres,
                                apellidos,
                                telefono,
                                correo,
                                direccion,
                                barrio,
                                municipio,
                                estado
                            )
                            VALUES
                            (
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                NULL,
                                NULL,
                                'Ibagué',
                                1
                            )
                            """,
                            (
                                usuario_id,
                                tipo_documento,
                                documento,
                                nombres,
                                apellidos,
                                telefono or None,
                                correo,
                            ),
                        )

                        acudiente_id = cur.lastrowid

                    # ----------------------------------------
                    # ESTUDIANTE
                    # ----------------------------------------

                    if estudiante_existente:

                        estudiante_id = (
                            estudiante_existente[
                                "id_estudiante"
                            ]
                        )

                    else:

                        # Bloqueo definitivo del grupo.
                        grupo_real, total_grupo = (
                            _bloquear_grupo_y_comprobar_cupo(
                                cnx,
                                estudiante_grado_id,
                                estudiante_grupo_id,
                            )
                        )

                        codigo_tmp = codigo_temporal()

                        cur.execute(
                            """
                            INSERT INTO estudiantes
                            (
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
                            VALUES
                            (
                                NULL,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                'Activo'
                            )
                            """,
                            (
                                codigo_tmp,
                                estudiante_tipo_documento,
                                estudiante_documento,
                                estudiante_nombres,
                                estudiante_apellidos,
                                estudiante_curso or None,
                                int(
                                    estudiante_sede_id
                                ),
                                int(
                                    estudiante_jornada_id
                                ),
                                int(
                                    estudiante_grado_id
                                ),
                                grupo_real["id"],
                                periodo["id"],
                            ),
                        )

                        estudiante_id = cur.lastrowid

                        # ------------------------------------
                        # CÓDIGO AUTOMÁTICO
                        # ------------------------------------

                        _asignar_codigo_estudiantil_tx(
                            cnx,
                            estudiante_id,
                        )

                    # ----------------------------------------
                    # RELACIÓN ESTUDIANTE - ACUDIENTE
                    # ----------------------------------------

                    cur.execute(
                        """
                        SELECT
                            id,
                            principal,
                            estado
                        FROM estudiante_acudiente
                        WHERE
                            id_estudiante = %s
                            AND id_acudiente = %s
                        LIMIT 1
                        """,
                        (
                            estudiante_id,
                            acudiente_id,
                        ),
                    )

                    relacion = cur.fetchone()

                    if relacion:

                        cur.execute(
                            """
                            UPDATE estudiante_acudiente
                            SET
                                parentesco = %s,
                                estado = 1
                            WHERE id = %s
                            """,
                            (
                                parentesco,
                                relacion["id"],
                            ),
                        )

                    else:

                        cur.execute(
                            """
                            SELECT
                                id
                            FROM estudiante_acudiente
                            WHERE
                                id_estudiante = %s
                                AND principal = 1
                                AND estado = 1
                            LIMIT 1
                            """,
                            (
                                estudiante_id,
                            ),
                        )

                        principal_existente = (
                            cur.fetchone()
                        )

                        principal = (
                            0
                            if principal_existente
                            else 1
                        )

                        cur.execute(
                            """
                            INSERT INTO estudiante_acudiente
                            (
                                id_estudiante,
                                id_acudiente,
                                parentesco,
                                principal,
                                estado
                            )
                            VALUES
                            (
                                %s,
                                %s,
                                %s,
                                %s,
                                1
                            )
                            """,
                            (
                                estudiante_id,
                                acudiente_id,
                                parentesco,
                                principal,
                            ),
                        )

                finally:
                    cur.close()

            flash(
                "Cuenta de acudiente creada correctamente. "
                "El estudiante quedó relacionado con tu cuenta.",
                "success",
            )

            return redirect(
                url_for("auth.login")
            )

        # ====================================================
        # PORTAL NO SOPORTADO
        # ====================================================

        raise ValueError(
            f"Portal no soportado: {portal}"
        )

    except Exception as exc:

        mensaje_error = (
            f"{type(exc).__name__}: {str(exc)}"
        )

        print(
            "ERROR EN REGISTRO EDUTURNOS:",
            mensaje_error,
            flush=True,
        )

        flash(
            "No se pudo completar el registro: "
            f"{mensaje_error}",
            "error",
        )

        return _mostrar_registro(
            portal,
            info,
            sedes,
            jornadas,
        )


# ============================================================
# DASHBOARD
# ============================================================

@auth_bp.route("/dashboard")
def dashboard():

    usuario = usuario_actual()

    if not usuario:

        flash(
            "Debes iniciar sesión.",
            "error",
        )

        return redirect(
            url_for("auth.login")
        )

    try:

        id_usuario = usuario["id_usuario"]
        rol = usuario["rol_nombre"]
        hoy = datetime.now().date()
        mes_explicito = bool(request.args.get("mes"))
        try:
            mes_inicio = datetime.strptime(request.args.get("mes", ""), "%Y-%m").date().replace(day=1)
        except ValueError:
            mes_inicio = hoy.replace(day=1)
        if mes_inicio.month == 12:
            mes_siguiente = date(mes_inicio.year + 1, 1, 1)
        else:
            mes_siguiente = date(mes_inicio.year, mes_inicio.month + 1, 1)
        if mes_inicio.month == 1:
            mes_anterior = date(mes_inicio.year - 1, 12, 1)
        else:
            mes_anterior = date(mes_inicio.year, mes_inicio.month - 1, 1)
        try:
            dia_solicitado = datetime.strptime(request.args.get("dia", ""), "%Y-%m-%d").date()
            dia_explicito = dia_solicitado.year == mes_inicio.year and dia_solicitado.month == mes_inicio.month
        except ValueError:
            dia_solicitado = None
            dia_explicito = False
        dia_seleccionado = dia_solicitado if dia_explicito else (
            hoy if hoy.year == mes_inicio.year and hoy.month == mes_inicio.month else mes_inicio
        )
        calendario_dias = monthcalendar(mes_inicio.year, mes_inicio.month)
        meses_espanol = (
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        )

        # ====================================================
        # CITAS VISIBLES
        # ====================================================

        if rol == "Docente":

            condicion = """
                c.id_docente IN (
                    SELECT
                        d.id_docente
                    FROM docentes d
                    WHERE
                        d.id_usuario = %s
                )
            """

            parametros = (
                id_usuario,
            )

        elif rol == "Estudiante":

            condicion = """
                c.id_estudiante IN (
                    SELECT
                        e.id_estudiante
                    FROM estudiantes e
                    WHERE
                        e.id_usuario = %s
                )
            """

            parametros = (
                id_usuario,
            )

        elif rol == "Acudiente":

            condicion = """
                c.id_acudiente IN (
                    SELECT
                        a.id_acudiente
                    FROM acudientes a
                    WHERE
                        a.id_usuario = %s
                )
            """

            parametros = (
                id_usuario,
            )

        elif rol in (
            "Administrador / Coordinador",
            "Rector",
            "Super Admin",
        ):

            condicion = "1 = 1"
            parametros = ()

        else:

            condicion = "1 = 0"
            parametros = ()

        # ====================================================
        # TOTAL CITAS
        # ====================================================

        fila_total = consultar(
            f"""
            SELECT
                COUNT(*) AS total
            FROM citas c
            WHERE {condicion}
            """,
            parametros,
            uno=True,
        )

        total_citas = int(
            fila_total["total"]
            if fila_total
            else 0
        )

        # ====================================================
        # CITAS PENDIENTES
        # ====================================================

        fila_pendientes = consultar(
            f"""
            SELECT
                COUNT(*) AS total
            FROM citas c
            INNER JOIN estados_cita ec
                ON ec.id = c.id_estado
            WHERE
                {condicion}
                AND LOWER(
                    TRIM(ec.nombre)
                ) = 'pendiente'
            """,
            parametros,
            uno=True,
        )

        pendientes = int(
            fila_pendientes["total"]
            if fila_pendientes
            else 0
        )

        # ====================================================
        # CITAS CONFIRMADAS
        # ====================================================

        fila_confirmadas = consultar(
            f"""
            SELECT
                COUNT(*) AS total
            FROM citas c
            INNER JOIN estados_cita ec
                ON ec.id = c.id_estado
            WHERE
                {condicion}
                AND LOWER(
                    TRIM(ec.nombre)
                ) = 'confirmada'
            """,
            parametros,
            uno=True,
        )

        confirmadas = int(
            fila_confirmadas["total"]
            if fila_confirmadas
            else 0
        )

        fila_reprogramadas = consultar(
                        f"""
                        SELECT COUNT(*) AS total
                        FROM citas c
                        INNER JOIN estados_cita ec ON ec.id = c.id_estado
                        WHERE {condicion}
                            AND LOWER(TRIM(ec.nombre)) = 'reprogramada'
                        """,
                        parametros,
                        uno=True,
                )
        fila_atendidas = consultar(
                        f"""
                        SELECT COUNT(*) AS total
                        FROM citas c
                        INNER JOIN estados_cita ec ON ec.id = c.id_estado
                        WHERE {condicion}
                            AND LOWER(TRIM(ec.nombre)) = 'realizada'
                        """,
                        parametros,
                        uno=True,
                )
        fila_incumplidas = consultar(
                        f"""
                        SELECT COUNT(*) AS total
                        FROM citas c
                        INNER JOIN estados_cita ec ON ec.id = c.id_estado
                        WHERE {condicion}
                            AND LOWER(TRIM(ec.nombre)) IN ('no asistió', 'no asistio', 'incumplida')
                        """,
                        parametros,
                        uno=True,
                )

        datos = {
            "total_citas": total_citas,
            "pendientes": pendientes,
            "confirmadas": confirmadas,
            "por_atender": int(fila_pendientes["total"] if fila_pendientes else 0)
            + int(fila_confirmadas["total"] if fila_confirmadas else 0)
            + int(fila_reprogramadas["total"] if fila_reprogramadas else 0),
            "atendidas": int(fila_atendidas["total"] if fila_atendidas else 0),
            "incumplidas": int(fila_incumplidas["total"] if fila_incumplidas else 0),
        }

        if dia_explicito:
            condicion_fecha = "c.fecha = %s"
            parametros_agenda = parametros + (dia_seleccionado,)
        elif mes_explicito:
            condicion_fecha = "c.fecha >= %s AND c.fecha < %s"
            parametros_agenda = parametros + (mes_inicio, mes_siguiente)
        else:
            condicion_fecha = "c.fecha >= CURDATE()"
            parametros_agenda = parametros
        agenda_hoy = consultar(
            f"""
            SELECT c.id, c.fecha, c.hora, c.lugar, ec.nombre AS estado,
                   CONCAT(e.nombres, ' ', e.apellidos) AS estudiante,
                   m.nombre AS motivo, gr.nombre AS grado, g.nombre AS grupo
            FROM citas c
            JOIN estados_cita ec ON ec.id = c.id_estado
            JOIN estudiantes e ON e.id_estudiante = c.id_estudiante
            LEFT JOIN motivos m ON m.id = c.id_motivo
            LEFT JOIN grados gr ON gr.id = e.id_grado
            LEFT JOIN grupos g ON g.id = e.id_grupo
            WHERE {condicion}
              AND {condicion_fecha}
              AND LOWER(TRIM(ec.nombre)) IN ('pendiente', 'confirmada', 'reprogramada')
            ORDER BY c.fecha, c.hora
            LIMIT 6
            """,
            parametros_agenda,
        )
        citas_del_mes = consultar(
            f"""
            SELECT DAY(c.fecha) AS dia, COUNT(*) AS total
            FROM citas c
            JOIN estados_cita ec ON ec.id = c.id_estado
            WHERE {condicion}
              AND c.fecha >= %s AND c.fecha < %s
              AND LOWER(TRIM(ec.nombre)) IN ('pendiente', 'confirmada', 'reprogramada')
            GROUP BY c.fecha
            """,
            parametros + (mes_inicio, mes_siguiente),
        )
        dias_con_citas = {int(fila["dia"]) for fila in citas_del_mes}
        citas_activas_mes = sum(int(fila["total"] or 0) for fila in citas_del_mes)

        solicitudes_pendientes = 0
        if rol in ("Super Admin", "Rector", "Administrador / Coordinador"):
            fila_solicitudes = consultar(
                "SELECT COUNT(*) AS total FROM solicitudes_cita WHERE estado='Pendiente'",
                uno=True,
            )
            solicitudes_pendientes = int(
                fila_solicitudes["total"] if fila_solicitudes else 0
            )

        compromisos_vencidos = []
        compromisos_vencidos_total = 0
        if rol in ("Super Admin", "Rector", "Administrador / Coordinador", "Docente"):
            fila_compromisos_vencidos = consultar(
                f"""
                SELECT COUNT(*) AS total
                FROM compromisos_cita cc
                JOIN citas c ON c.id = cc.id_cita
                WHERE {condicion}
                  AND cc.estado = 'Pendiente'
                  AND cc.fecha_limite < CURDATE()
                """,
                parametros,
                uno=True,
            )
            compromisos_vencidos_total = int(
                fila_compromisos_vencidos["total"]
                if fila_compromisos_vencidos
                else 0
            )
            compromisos_vencidos = consultar(
                f"""
                SELECT cc.id_cita, cc.descripcion, cc.responsable, cc.fecha_limite,
                       CONCAT(e.nombres, ' ', e.apellidos) AS estudiante
                FROM compromisos_cita cc
                JOIN citas c ON c.id = cc.id_cita
                JOIN estudiantes e ON e.id_estudiante = c.id_estudiante
                WHERE {condicion}
                  AND cc.estado = 'Pendiente'
                  AND cc.fecha_limite < CURDATE()
                ORDER BY cc.fecha_limite, cc.id
                LIMIT 5
                """,
                parametros,
            )

        # ====================================================
        # NOTIFICACIONES
        # ====================================================

        fila_notificaciones = consultar(
            """
            SELECT
                COUNT(*) AS total
            FROM notificaciones
            WHERE
                id_usuario = %s
                AND (
                    leida = 0
                    OR leida IS NULL
                )
            """,
            (
                id_usuario,
            ),
            uno=True,
        )

        notificaciones_no_leidas = int(
            fila_notificaciones["total"]
            if fila_notificaciones
            else 0
        )

        return render_template(
            "dashboard.html",
            usuario=usuario,
            datos=datos,
            citas_activas_mes=citas_activas_mes,
            agenda_hoy=agenda_hoy,
            calendario_dias=calendario_dias,
            dias_con_citas=dias_con_citas,
            dia_seleccionado=dia_seleccionado,
            mes_inicio=mes_inicio,
            mes_anterior=mes_anterior.strftime("%Y-%m"),
            mes_siguiente=mes_siguiente.strftime("%Y-%m"),
            nombre_mes=meses_espanol[mes_inicio.month - 1],
            compromisos_vencidos=compromisos_vencidos,
            compromisos_vencidos_total=compromisos_vencidos_total,
            solicitudes_pendientes=solicitudes_pendientes,
            notificaciones_no_leidas=(
                notificaciones_no_leidas
            ),
        )

    except Exception as exc:

        print(
            "ERROR CARGANDO DASHBOARD:",
            repr(exc),
            flush=True,
        )

        datos = {
            "total_citas": 0,
            "pendientes": 0,
            "confirmadas": 0,
            "por_atender": 0,
            "atendidas": 0,
            "incumplidas": 0,
        }

        notificaciones_no_leidas = 0

        flash(
            "El dashboard se abrió, pero algunos "
            "indicadores no pudieron cargarse.",
            "error",
        )

        return render_template(
            "dashboard.html",
            usuario=usuario,
            datos=datos,
            citas_activas_mes=0,
            agenda_hoy=[],
            calendario_dias=monthcalendar(datetime.now().year, datetime.now().month),
            dias_con_citas=set(),
            dia_seleccionado=datetime.now().date(),
            mes_inicio=datetime.now().date().replace(day=1),
            mes_anterior="",
            mes_siguiente="",
            nombre_mes="",
            compromisos_vencidos=[],
            compromisos_vencidos_total=0,
            solicitudes_pendientes=0,
            notificaciones_no_leidas=(
                notificaciones_no_leidas
            ),
        )


# ============================================================
# CERRAR SESIÓN
# ============================================================

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():

    session.clear()

    flash(
        "Sesión cerrada correctamente.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )
