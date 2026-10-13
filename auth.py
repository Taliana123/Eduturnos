from datetime import datetime, timedelta
import time

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from werkzeug.security import generate_password_hash, check_password_hash

from database.db import consultar, ejecutar
from roles import (
    PORTALES,
    es_correo_institucional,
    es_codigo_institucional_valido,
)
from routes.helpers import usuario_actual


auth_bp = Blueprint("auth", __name__)


MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 15


# ============================================================
# UTILIDADES
# ============================================================

def _texto(valor):
    return (valor or "").strip()


def _normalizar_correo(correo):
    return _texto(correo).lower()


def _normalizar_documento(documento):
    return "".join(ch for ch in _texto(documento) if ch.isalnum())


def _sedes():
    """
    Obtiene las sedes directamente de MySQL.
    """
    try:
        return consultar(
            """
            SELECT id, nombre, direccion, codigo_sede
            FROM sedes
            WHERE estado = 1
            ORDER BY id
            """
        )
    except Exception:
        return []


def _jornadas():
    """
    Obtiene las jornadas directamente de MySQL.
    """
    try:
        return consultar(
            """
            SELECT id, nombre
            FROM jornadas
            WHERE estado = 1
            ORDER BY id
            """
        )
    except Exception:
        return []


def _buscar_usuario(identificador):
    """
    Busca un usuario por documento o correo.
    """
    identificador = _texto(identificador)

    if not identificador:
        return None

    filas = consultar(
        """
        SELECT
            u.*,
            r.nombre AS rol_nombre
        FROM usuarios u
        INNER JOIN roles r
            ON r.id = u.id_rol
        WHERE u.documento = %s
           OR LOWER(u.correo) = LOWER(%s)
        LIMIT 1
        """,
        (identificador, identificador),
    )

    return filas[0] if filas else None


def _obtener_rol(nombre):
    filas = consultar(
        """
        SELECT id, nombre
        FROM roles
        WHERE nombre = %s
        LIMIT 1
        """,
        (nombre,),
    )

    return filas[0] if filas else None


def _codigo_correcto(codigo, codigo_hash):
    """
    Comprueba el código institucional.

    Los registros nuevos deben utilizar hashes generados con
    generate_password_hash().

    Para permitir migrar el registro de prueba antiguo, si el
    valor existente está en texto plano se compara una sola vez
    y posteriormente se convierte a hash.
    """
    codigo = _texto(codigo)
    codigo_hash = _texto(codigo_hash)

    if not codigo or not codigo_hash:
        return False

    # Registro antiguo de prueba / migración.
    if codigo_hash == codigo:
        return True

    try:
        return check_password_hash(codigo_hash, codigo)
    except (ValueError, TypeError):
        return False


def _buscar_personal(
    documento,
    nombres,
    apellidos,
    correo,
    rol_nombre,
    sede_id,
    jornada_id,
    codigo,
):
    """
    Verifica que el funcionario exista en
    directorio_institucional y que corresponda al rol,
    sede, jornada y código suministrados.
    """

    rol = _obtener_rol(rol_nombre)

    if not rol:
        return None, "El rol seleccionado no existe en la base de datos."

    documento = _normalizar_documento(documento)
    nombres = _texto(nombres)
    apellidos = _texto(apellidos)
    correo = _normalizar_correo(correo)

    try:
        sede_id = int(sede_id)
    except (TypeError, ValueError):
        return None, "La sede seleccionada no es válida."

    try:
        jornada_id = int(jornada_id)
    except (TypeError, ValueError):
        return None, "La jornada seleccionada no es válida."

    filas = consultar(
        """
        SELECT
            d.id,
            d.id_usuario,
            d.id_rol,
            d.tipo_documento,
            d.documento,
            d.nombres,
            d.apellidos,
            d.correo_institucional,
            d.id_sede,
            d.id_jornada,
            d.codigo_institucional_hash,
            d.estado,
            d.fecha_vinculacion
        FROM directorio_institucional d
        WHERE d.documento = %s
          AND LOWER(d.correo_institucional) = LOWER(%s)
          AND d.id_rol = %s
          AND d.id_sede = %s
          AND (
                d.id_jornada = %s
                OR d.id_jornada IS NULL
              )
        LIMIT 1
        """,
        (
            documento,
            correo,
            rol["id"],
            sede_id,
            jornada_id,
        ),
    )

    if not filas:
        return None, (
            "No encontramos un registro institucional que coincida "
            "con los datos, rol, sede y jornada seleccionados."
        )

    personal = filas[0]

    if not personal["estado"]:
        return None, (
            "El registro institucional está inactivo. "
            "Debes utilizar un registro activo."
        )

    if not _codigo_correcto(
        codigo,
        personal["codigo_institucional_hash"],
    ):
        return None, "El código institucional no es correcto."

    # Si el registro todavía tenía el código antiguo en texto plano,
    # lo migramos automáticamente a un hash seguro.
    if personal["codigo_institucional_hash"] == _texto(codigo):
        nuevo_hash = generate_password_hash(codigo)

        ejecutar(
            """
            UPDATE directorio_institucional
            SET codigo_institucional_hash = %s
            WHERE id = %s
            """,
            (nuevo_hash, personal["id"]),
        )

        personal["codigo_institucional_hash"] = nuevo_hash

    return personal, None


def _relacionar_usuario(
    portal,
    usuario_id,
    personal=None,
    documento=None,
):
    """
    Relaciona el usuario creado con su registro académico/institucional.
    """

    if portal == "estudiante":
        if not documento:
            return

        ejecutar(
            """
            UPDATE estudiantes
            SET id_usuario = %s
            WHERE documento = %s
            LIMIT 1
            """,
            (usuario_id, _normalizar_documento(documento)),
        )

    elif portal == "acudiente":
        if not documento:
            return

        ejecutar(
            """
            UPDATE acudientes
            SET id_usuario = %s
            WHERE documento = %s
            LIMIT 1
            """,
            (usuario_id, _normalizar_documento(documento)),
        )

    elif personal:
        personal_id = personal["id"]

        # Vinculación principal con el directorio institucional.
        ejecutar(
            """
            UPDATE directorio_institucional
            SET
                id_usuario = %s,
                fecha_vinculacion = COALESCE(
                    fecha_vinculacion,
                    NOW()
                )
            WHERE id = %s
            """,
            (usuario_id, personal_id),
        )

        # Si es docente, también vinculamos el registro de docentes.
        if portal == "docente":
            ejecutar(
                """
                UPDATE docentes
                SET id_usuario = %s
                WHERE documento = %s
                LIMIT 1
                """,
                (
                    usuario_id,
                    _normalizar_documento(documento),
                ),
            )


def _crear_o_actualizar_usuario(
    rol_id,
    documento,
    tipo_documento,
    nombres,
    apellidos,
    correo,
    telefono,
    password,
):
    """
    Crea el usuario o actualiza uno existente.
    """

    documento = _normalizar_documento(documento)
    correo = _normalizar_correo(correo)

    existente = consultar(
        """
        SELECT id_usuario
        FROM usuarios
        WHERE documento = %s
           OR LOWER(correo) = LOWER(%s)
        LIMIT 1
        """,
        (documento, correo),
    )

    password_hash = generate_password_hash(password)

    if existente:
        usuario_id = existente[0]["id_usuario"]

        ejecutar(
            """
            UPDATE usuarios
            SET
                id_rol = %s,
                tipo_documento = %s,
                documento = %s,
                nombres = %s,
                apellidos = %s,
                correo = %s,
                telefono = %s,
                password_hash = %s,
                verificado = 1,
                estado = 1,
                intentos_fallidos = 0,
                bloqueado_hasta = NULL
            WHERE id_usuario = %s
            """,
            (
                rol_id,
                tipo_documento,
                documento,
                nombres,
                apellidos,
                correo,
                telefono,
                password_hash,
                usuario_id,
            ),
        )

        return usuario_id

    ejecutar(
        """
        INSERT INTO usuarios (
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
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s,
            1, 1, 0, NULL
        )
        """,
        (
            rol_id,
            tipo_documento,
            documento,
            nombres,
            apellidos,
            correo,
            telefono,
            password_hash,
        ),
    )

    fila = consultar(
        """
        SELECT id_usuario
        FROM usuarios
        WHERE documento = %s
        LIMIT 1
        """,
        (documento,),
    )

    if not fila:
        raise RuntimeError(
            "El usuario fue creado pero no se pudo recuperar su ID."
        )

    return fila[0]["id_usuario"]


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        identificador = _texto(
            request.form.get("identificador")
            or request.form.get("correo")
            or request.form.get("documento")
        )

        password = request.form.get("password", "")

        rol_portal = _texto(
            request.form.get("portal")
            or request.form.get("rol")
        ).lower()

        sede_id = request.form.get("sede_id")
        jornada_id = request.form.get("jornada_id")
        codigo = request.form.get("codigo")

        if not identificador or not password:
            flash(
                "Ingresa tu correo o documento y tu contraseña.",
                "danger",
            )
            return render_template(
                "auth/login.html",
                portales=PORTALES,
                sedes=_sedes(),
                jornadas=_jornadas(),
            )

        usuario = _buscar_usuario(identificador)

        if not usuario:
            flash("Los datos de acceso no son correctos.", "danger")
            return render_template(
                "auth/login.html",
                portales=PORTALES,
                sedes=_sedes(),
                jornadas=_jornadas(),
            )

        # Estado general del usuario.
        if not usuario["estado"]:
            flash("Tu cuenta está desactivada.", "danger")
            return render_template(
                "auth/login.html",
                portales=PORTALES,
                sedes=_sedes(),
                jornadas=_jornadas(),
            )

        # Bloqueo temporal.
        bloqueado_hasta = usuario.get("bloqueado_hasta")

        if bloqueado_hasta:
            if bloqueado_hasta > datetime.now():
                restantes = int(
                    (
                        bloqueado_hasta - datetime.now()
                    ).total_seconds() / 60
                ) + 1

                flash(
                    f"Cuenta bloqueada temporalmente. "
                    f"Intenta nuevamente en aproximadamente "
                    f"{restantes} minuto(s).",
                    "danger",
                )

                return render_template(
                    "auth/login.html",
                    portales=PORTALES,
                    sedes=_sedes(),
                    jornadas=_jornadas(),
                )

            ejecutar(
                """
                UPDATE usuarios
                SET
                    intentos_fallidos = 0,
                    bloqueado_hasta = NULL
                WHERE id_usuario = %s
                """,
                (usuario["id_usuario"],),
            )

            usuario["intentos_fallidos"] = 0

        # Si seleccionó un portal, verificamos que corresponda
        # con el rol real de la cuenta.
        if rol_portal in PORTALES:

            rol_esperado = PORTALES[rol_portal]["rol"]

            if usuario["rol_nombre"] != rol_esperado:
                flash(
                    "El rol seleccionado no corresponde a esta cuenta.",
                    "danger",
                )
                return render_template(
                    "auth/login.html",
                    portales=PORTALES,
                    sedes=_sedes(),
                    jornadas=_jornadas(),
                )

        # Contraseña.
        try:
            password_correcta = check_password_hash(
                usuario["password_hash"],
                password,
            )
        except (ValueError, TypeError):
            password_correcta = False

        if not password_correcta:

            intentos = int(
                usuario.get("intentos_fallidos") or 0
            ) + 1

            if intentos >= MAX_INTENTOS:

                bloqueo = datetime.now() + timedelta(
                    minutes=MINUTOS_BLOQUEO
                )

                ejecutar(
                    """
                    UPDATE usuarios
                    SET
                        intentos_fallidos = %s,
                        bloqueado_hasta = %s
                    WHERE id_usuario = %s
                    """,
                    (
                        intentos,
                        bloqueo,
                        usuario["id_usuario"],
                    ),
                )

                flash(
                    "Se alcanzó el máximo de intentos. "
                    "La cuenta quedó bloqueada temporalmente.",
                    "danger",
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
                    "Contraseña incorrecta.",
                    "danger",
                )

            return render_template(
                "auth/login.html",
                portales=PORTALES,
                sedes=_sedes(),
                jornadas=_jornadas(),
            )

        # Para personal institucional verificamos adicionalmente
        # correo, sede, jornada y código.
        if usuario["rol_nombre"] in (
            "Docente",
            "Administrador / Coordinador",
            "Rector",
        ):

            correo_usuario = _normalizar_correo(
                usuario["correo"]
            )

            if not es_correo_institucional(correo_usuario):
                flash(
                    "El acceso del personal requiere un correo "
                    "institucional @jjfh.edu.co.",
                    "danger",
                )
                return render_template(
                    "auth/login.html",
                    portales=PORTALES,
                    sedes=_sedes(),
                    jornadas=_jornadas(),
                )

            if not sede_id or not jornada_id or not codigo:
                flash(
                    "Para acceder como personal institucional "
                    "debes indicar sede, jornada y código.",
                    "danger",
                )
                return render_template(
                    "auth/login.html",
                    portales=PORTALES,
                    sedes=_sedes(),
                    jornadas=_jornadas(),
                )

            if not es_codigo_institucional_valido(codigo):
                flash(
                    "El código institucional debe tener 6 dígitos.",
                    "danger",
                )
                return render_template(
                    "auth/login.html",
                    portales=PORTALES,
                    sedes=_sedes(),
                    jornadas=_jornadas(),
                )

            personal = consultar(
                """
                SELECT
                    d.*,
                    r.nombre AS rol_nombre
                FROM directorio_institucional d
                INNER JOIN roles r
                    ON r.id = d.id_rol
                WHERE d.id_usuario = %s
                  AND d.id_sede = %s
                  AND (
                        d.id_jornada = %s
                        OR d.id_jornada IS NULL
                      )
                  AND d.estado = 1
                LIMIT 1
                """,
                (
                    usuario["id_usuario"],
                    sede_id,
                    jornada_id,
                ),
            )

            if not personal:
                flash(
                    "La cuenta no está vinculada a la sede o jornada "
                    "seleccionada.",
                    "danger",
                )
                return render_template(
                    "auth/login.html",
                    portales=PORTALES,
                    sedes=_sedes(),
                    jornadas=_jornadas(),
                )

            if not _codigo_correcto(
                codigo,
                personal[0]["codigo_institucional_hash"],
            ):
                flash(
                    "El código institucional no es correcto.",
                    "danger",
                )
                return render_template(
                    "auth/login.html",
                    portales=PORTALES,
                    sedes=_sedes(),
                    jornadas=_jornadas(),
                )

        # Login correcto.
        ejecutar(
            """
            UPDATE usuarios
            SET
                intentos_fallidos = 0,
                bloqueado_hasta = NULL,
                ultimo_acceso = NOW()
            WHERE id_usuario = %s
            """,
            (usuario["id_usuario"],),
        )

        session.clear()

        session["usuario_id"] = usuario["id_usuario"]
        session["id_usuario"] = usuario["id_usuario"]
        session["rol"] = usuario["rol_nombre"]
        session["nombres"] = usuario["nombres"]
        session["apellidos"] = usuario["apellidos"]
        session["correo"] = usuario["correo"]

        # Redirección según rol.
        if usuario["rol_nombre"] == "Docente":
            return redirect(
                url_for("docente.index")
            )

        if usuario["rol_nombre"] == "Administrador / Coordinador":
            return redirect(
                url_for("coordinador.index")
            )

        if usuario["rol_nombre"] == "Rector":
            return redirect(
                url_for("rector.index")
            )

        if usuario["rol_nombre"] == "Estudiante":
            return redirect(
                url_for("estudiante.index")
            )

        if usuario["rol_nombre"] == "Acudiente":
            return redirect(
                url_for("acudiente.index")
            )

        return redirect(url_for("dashboard"))

    return render_template(
        "auth/login.html",
        portales=PORTALES,
        sedes=_sedes(),
        jornadas=_jornadas(),
    )


# ============================================================
# REGISTRO
# ============================================================

@auth_bp.route("/registro/<portal>", methods=["GET", "POST"])
def registro(portal):

    portal = _texto(portal).lower()
    info = PORTALES.get(portal)

    if not info:
        flash("El tipo de registro no es válido.", "danger")
        return redirect(url_for("auth.login"))

    sedes = _sedes()
    jornadas = _jornadas()

    if request.method == "POST":

        tipo_documento = _texto(
            request.form.get("tipo_documento") or "CC"
        )

        documento = _normalizar_documento(
            request.form.get("documento")
        )

        nombres = _texto(
            request.form.get("nombres")
        )

        apellidos = _texto(
            request.form.get("apellidos")
        )

        correo = _normalizar_correo(
            request.form.get("correo")
        )

        telefono = _texto(
            request.form.get("telefono")
        )

        password = request.form.get("password", "")
        password_confirmacion = request.form.get(
            "password_confirmacion"
            or "confirm_password",
            "",
        )

        sede_id = request.form.get("sede_id")
        jornada_id = request.form.get("jornada_id")

        codigo = _texto(
            request.form.get("codigo")
        )

        # --------------------------------------------------------
        # CAMPOS BÁSICOS
        # --------------------------------------------------------

        if not documento:
            flash("El documento es obligatorio.", "danger")
            return render_template(
                "auth/registro.html",
                portal=portal,
                info=info,
                sedes=sedes,
                jornadas=jornadas,
            )

        if not nombres:
            flash("Los nombres son obligatorios.", "danger")
            return render_template(
                "auth/registro.html",
                portal=portal,
                info=info,
                sedes=sedes,
                jornadas=jornadas,
            )

        if not apellidos:
            flash("Los apellidos son obligatorios.", "danger")
            return render_template(
                "auth/registro.html",
                portal=portal,
                info=info,
                sedes=sedes,
                jornadas=jornadas,
            )

        if not correo:
            flash("El correo es obligatorio.", "danger")
            return render_template(
                "auth/registro.html",
                portal=portal,
                info=info,
                sedes=sedes,
                jornadas=jornadas,
            )

        if not password:
            flash("La contraseña es obligatoria.", "danger")
            return render_template(
                "auth/registro.html",
                portal=portal,
                info=info,
                sedes=sedes,
                jornadas=jornadas,
            )

        if len(password) < 12:
            flash(
                "La contraseña debe tener al menos 12 caracteres.",
                "danger",
            )
            return render_template(
                "auth/registro.html",
                portal=portal,
                info=info,
                sedes=sedes,
                jornadas=jornadas,
            )

        if (
            password_confirmacion
            and password != password_confirmacion
        ):
            flash("Las contraseñas no coinciden.", "danger")
            return render_template(
                "auth/registro.html",
                portal=portal,
                info=info,
                sedes=sedes,
                jornadas=jornadas,
            )

        # --------------------------------------------------------
        # PERSONAL INSTITUCIONAL
        # --------------------------------------------------------

        personal = None

        if info["requiere_codigo"]:

            if not es_correo_institucional(correo):
                flash(
                    "Para este registro debes utilizar un correo "
                    "institucional que termine en @jjfh.edu.co.",
                    "danger",
                )
                return render_template(
                    "auth/registro.html",
                    portal=portal,
                    info=info,
                    sedes=sedes,
                    jornadas=jornadas,
                )

            if not sede_id:
                flash("Debes seleccionar una sede.", "danger")
                return render_template(
                    "auth/registro.html",
                    portal=portal,
                    info=info,
                    sedes=sedes,
                    jornadas=jornadas,
                )

            if not jornada_id:
                flash("Debes seleccionar una jornada.", "danger")
                return render_template(
                    "auth/registro.html",
                    portal=portal,
                    info=info,
                    sedes=sedes,
                    jornadas=jornadas,
                )

            if not es_codigo_institucional_valido(codigo):
                flash(
                    "El código institucional debe tener exactamente "
                    "6 dígitos.",
                    "danger",
                )
                return render_template(
                    "auth/registro.html",
                    portal=portal,
                    info=info,
                    sedes=sedes,
                    jornadas=jornadas,
                )

            personal, error = _buscar_personal(
                documento=documento,
                nombres=nombres,
                apellidos=apellidos,
                correo=correo,
                rol_nombre=info["rol"],
                sede_id=sede_id,
                jornada_id=jornada_id,
                codigo=codigo,
            )

            if not personal:
                flash(error, "danger")
                return render_template(
                    "auth/registro.html",
                    portal=portal,
                    info=info,
                    sedes=sedes,
                    jornadas=jornadas,
                )

        # --------------------------------------------------------
        # ESTUDIANTE
        # --------------------------------------------------------

        if portal == "estudiante":

            estudiantes = consultar(
                """
                SELECT *
                FROM estudiantes
                WHERE documento = %s
                  AND estado = 1
                LIMIT 1
                """,
                (documento,),
            )

            if not estudiantes:
                flash(
                    "No encontramos un estudiante activo con "
                    "ese documento.",
                    "danger",
                )
                return render_template(
                    "auth/registro.html",
                    portal=portal,
                    info=info,
                    sedes=sedes,
                    jornadas=jornadas,
                )

        # --------------------------------------------------------
        # ACUDIENTE
        # --------------------------------------------------------

        if portal == "acudiente":

            acudientes = consultar(
                """
                SELECT *
                FROM acudientes
                WHERE documento = %s
                LIMIT 1
                """,
                (documento,),
            )

            if not acudientes:
                flash(
                    "No encontramos un acudiente registrado "
                    "con ese documento.",
                    "danger",
                )
                return render_template(
                    "auth/registro.html",
                    portal=portal,
                    info=info,
                    sedes=sedes,
                    jornadas=jornadas,
                )

        # --------------------------------------------------------
        # ROL
        # --------------------------------------------------------

        rol = _obtener_rol(info["rol"])

        if not rol:
            flash(
                "El rol configurado para este portal no existe.",
                "danger",
            )
            return render_template(
                "auth/registro.html",
                portal=portal,
                info=info,
                sedes=sedes,
                jornadas=jornadas,
            )

        # --------------------------------------------------------
        # COMPROBAR SI YA EXISTE CUENTA
        # --------------------------------------------------------

        existente = consultar(
            """
            SELECT
                id_usuario,
                id_rol,
                documento,
                correo,
                estado
            FROM usuarios
            WHERE documento = %s
               OR LOWER(correo) = LOWER(%s)
            LIMIT 1
            """,
            (documento, correo),
        )

        # Si existe una cuenta vinculada a otro rol, no la
        # reemplazamos silenciosamente.
        if existente:

            cuenta = existente[0]

            if cuenta["id_rol"] != rol["id"]:
                flash(
                    "Ya existe una cuenta con esos datos asociada "
                    "a otro rol.",
                    "danger",
                )
                return render_template(
                    "auth/registro.html",
                    portal=portal,
                    info=info,
                    sedes=sedes,
                    jornadas=jornadas,
                )

        # --------------------------------------------------------
        # CREAR / ACTUALIZAR
        # --------------------------------------------------------

        try:

            usuario_id = _crear_o_actualizar_usuario(
                rol_id=rol["id"],
                documento=documento,
                tipo_documento=tipo_documento,
                nombres=nombres,
                apellidos=apellidos,
                correo=correo,
                telefono=telefono,
                password=password,
            )

            _relacionar_usuario(
                portal=portal,
                usuario_id=usuario_id,
                personal=personal,
                documento=documento,
            )

        except Exception as exc:

            print(
                "ERROR REGISTRO EDUTURNOS:",
                repr(exc),
            )

            flash(
                "No fue posible completar el registro. "
                "Revisa los datos e inténtalo nuevamente.",
                "danger",
            )

            return render_template(
                "auth/registro.html",
                portal=portal,
                info=info,
                sedes=sedes,
                jornadas=jornadas,
            )

        flash(
            "Registro completado correctamente. "
            "Ya puedes iniciar sesión.",
            "success",
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/registro.html",
        portal=portal,
        info=info,
        sedes=sedes,
        jornadas=jornadas,
    )


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    flash(
        "Sesión cerrada correctamente.",
        "success",
    )

    return redirect(url_for("auth.login"))


# ============================================================
# DASHBOARD
# ============================================================

@auth_bp.route("/dashboard")
def dashboard():

    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        usuario=usuario,
    )