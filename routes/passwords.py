from datetime import datetime, timedelta
import secrets
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash
from database.db import consultar, ejecutar
from routes.helpers import login_requerido, usuario_actual, auditoria
from security import csrf_protegido

passwords_bp = Blueprint("passwords", __name__, url_prefix="/auth")


def _password_valida(p):
    return len(p) >= 12 and any(c.isupper() for c in p) and any(c.islower() for c in p) and any(c.isdigit() for c in p)


@passwords_bp.route("/cambiar-password", methods=["GET", "POST"])
@login_requerido
@csrf_protegido
def cambiar_password():
    u = usuario_actual()
    if request.method == "POST":
        actual = request.form.get("password_actual", "")
        nueva = request.form.get("password_nueva", "")
        confirmacion = request.form.get("password_confirmacion", "")
        from werkzeug.security import check_password_hash
        if not check_password_hash(u["password_hash"], actual):
            flash("La contraseña actual no es correcta.", "error")
        elif nueva != confirmacion or not _password_valida(nueva):
            flash("La nueva contraseña debe tener mínimo 12 caracteres e incluir mayúsculas, minúsculas y números.", "error")
        else:
            ejecutar("UPDATE usuarios SET password_hash=%s WHERE id_usuario=%s", (generate_password_hash(nueva), u["id_usuario"]))
            auditoria("CAMBIAR_PASSWORD", "Autenticación", u["id_usuario"])
            session.clear()
            flash("Contraseña actualizada. Inicia sesión nuevamente.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/cambiar_password.html")


@passwords_bp.route("/recuperar", methods=["GET", "POST"])
@csrf_protegido
def recuperar():
    if request.method == "POST":
        correo = (request.form.get("correo") or "").strip().lower()
        # Respuesta genérica para evitar enumeración de cuentas.
        try:
            usuario = consultar("SELECT id_usuario, correo FROM usuarios WHERE LOWER(correo)=%s AND estado=1", (correo,), uno=True)
        except Exception:
            flash("No fue posible conectar con la base de datos. Inténtalo nuevamente.", "error")
            return render_template("auth/recuperar.html")
        if usuario:
            try:
                # Asegura la estructura de recuperación incluso en instalaciones
                # antiguas que no ejecutaron la migración correspondiente.
                ejecutar("""CREATE TABLE IF NOT EXISTS tokens_recuperacion (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL,
                    token_hash CHAR(64) NOT NULL UNIQUE,
                    codigo_hash CHAR(64) NULL,
                    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    fecha_expiracion DATETIME NOT NULL,
                    usado TINYINT(1) NOT NULL DEFAULT 0,
                    intentos INT NOT NULL DEFAULT 0,
                    CONSTRAINT fk_tokens_rec_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
                    INDEX idx_token_exp (fecha_expiracion, usado),
                    INDEX idx_token_usuario (id_usuario, usado, fecha_expiracion)
                ) ENGINE=InnoDB""")

                # Compatibilidad con instalaciones antiguas:
                # algunas ya tienen tokens_recuperacion pero no la columna intentos.
                try:
                    existe_intentos = consultar(
                        "SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='tokens_recuperacion' AND column_name='intentos' LIMIT 1",
                        (current_app.config.get('MYSQL_DATABASE'),),
                        uno=True
                    )
                    if not existe_intentos:
                        ejecutar(
                            "ALTER TABLE tokens_recuperacion ADD COLUMN intentos INT NOT NULL DEFAULT 0"
                        )
                except Exception:
                    # Si otro proceso ya agregó la columna, continuamos.
                    pass
                # Algunas instalaciones antiguas tienen la tabla pero no el código.
                try:
                    existe_codigo = consultar("SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='tokens_recuperacion' AND column_name='codigo_hash' LIMIT 1", (current_app.config.get('MYSQL_DATABASE'),), uno=True)
                    if not existe_codigo:
                        ejecutar("ALTER TABLE tokens_recuperacion ADD COLUMN codigo_hash CHAR(64) NULL AFTER token_hash")
                except Exception:
                    # Si otro proceso ya agregó la columna, continuamos.
                    pass
                token = secrets.token_urlsafe(32)
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                codigo = f"{secrets.randbelow(1000000):06d}"
                codigo_hash = hashlib.sha256(codigo.encode()).hexdigest()
                ejecutar("UPDATE tokens_recuperacion SET usado=1 WHERE id_usuario=%s AND usado=0", (usuario["id_usuario"],))
                ejecutar("INSERT INTO tokens_recuperacion(id_usuario,token_hash,codigo_hash,intentos,fecha_expiracion) VALUES(%s,%s,%s,0,DATE_ADD(NOW(),INTERVAL 10 MINUTE))", (usuario["id_usuario"], token_hash, codigo_hash))
                try:
                    from servicios.email import enviar_correo_recuperacion
                    enviado = enviar_correo_recuperacion(usuario["correo"], codigo)
                    if not enviado:
                        raise RuntimeError("El proveedor de correo no confirmó el envío.")
                except Exception as exc:
                    # No dejamos un token activo que el usuario nunca recibió.
                    try:
                        ejecutar("DELETE FROM tokens_recuperacion WHERE token_hash=%s", (token_hash,))
                    except Exception:
                        current_app.logger.exception("No se pudo limpiar el token de recuperación tras fallar el correo")
                    current_app.logger.exception("No se pudo enviar recuperación: %s", exc)
                    flash("No fue posible enviar el correo de recuperación. Revisa la configuración de correo del sistema e inténtalo nuevamente.", "error")
                    return render_template("auth/recuperar.html")
            except Exception as exc:
                current_app.logger.exception("No se pudo preparar la recuperación: %s", exc)
                flash("No se pudo preparar la recuperación en este momento. Verifica la base de datos e inténtalo nuevamente.", "error")
                return render_template("auth/recuperar.html")
        flash("Si el correo existe, recibirás instrucciones para restablecer la contraseña.", "success")
        return redirect(url_for("passwords.verificar_codigo", correo=correo))
    return render_template("auth/recuperar.html")




@passwords_bp.route("/verificar-codigo", methods=["GET", "POST"])
@csrf_protegido
def verificar_codigo():
    correo = (request.values.get("correo") or "").strip().lower()
    if request.method == "POST":
        codigo = (request.form.get("codigo") or "").strip()
        if not correo or len(codigo) != 6 or not codigo.isdigit():
            flash("Ingresa el correo y el código de 6 dígitos recibido.", "error")
            return render_template("auth/verificar_codigo.html", correo=correo)
        usuario = consultar("SELECT id_usuario,correo FROM usuarios WHERE LOWER(correo)=%s AND estado=1", (correo,), uno=True)
        if not usuario:
            flash("El código no es válido o ya expiró.", "error")
            return render_template("auth/verificar_codigo.html", correo=correo)
        codigo_hash=hashlib.sha256(codigo.encode()).hexdigest()
        fila=consultar("SELECT id,token_hash,intentos FROM tokens_recuperacion WHERE id_usuario=%s AND usado=0 AND fecha_expiracion>NOW() ORDER BY id DESC LIMIT 1", (usuario["id_usuario"],), uno=True)
        if not fila:
            flash("El código no es válido o ya expiró.", "error")
            return render_template("auth/verificar_codigo.html", correo=correo)
        if int(fila.get("intentos") or 0) >= 5:
            ejecutar("UPDATE tokens_recuperacion SET usado=1 WHERE id=%s", (fila["id"],))
            flash("Se superó el número de intentos permitidos. Solicita un nuevo código.", "error")
            return render_template("auth/verificar_codigo.html", correo=correo)
        candidato=consultar("SELECT id FROM tokens_recuperacion WHERE id=%s AND codigo_hash=%s AND usado=0 AND fecha_expiracion>NOW() LIMIT 1", (fila["id"],codigo_hash), uno=True)
        if not candidato:
            ejecutar("UPDATE tokens_recuperacion SET intentos=intentos+1 WHERE id=%s", (fila["id"],))
            flash("El código no es válido o ya expiró.", "error")
            return render_template("auth/verificar_codigo.html", correo=correo)
        session["recovery_user_id"] = usuario["id_usuario"]
        session["recovery_token_hash"] = fila["token_hash"]
        session["recovery_verified_at"] = datetime.now().timestamp()
        return redirect(url_for("passwords.restablecer"))
    return render_template("auth/verificar_codigo.html", correo=correo)


@passwords_bp.route("/restablecer", methods=["GET", "POST"])
@csrf_protegido
def restablecer():
    fila = None

    # El acceso al cambio de contraseña se autoriza únicamente
    # mediante la sesión creada después de verificar el código.
    uid = session.get("recovery_user_id")
    verified_at = session.get("recovery_verified_at", 0)

    if uid and verified_at:
        try:
            vigente = datetime.now().timestamp() - float(verified_at) <= 600
        except (TypeError, ValueError):
            vigente = False

        if vigente:
            fila = {
                "id_usuario": uid,
                "token_hash": session.get("recovery_token_hash")
            }
    if not fila:
        flash("El código no es válido o ya expiró.", "error")
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        nueva = request.form.get("password_nueva", "")
        conf = request.form.get("password_confirmacion", "")
        if nueva != conf or not _password_valida(nueva):
            flash("La contraseña debe tener mínimo 12 caracteres e incluir mayúsculas, minúsculas y números.", "error")
        else:
            ejecutar("UPDATE usuarios SET password_hash=%s,intentos_fallidos=0,bloqueado_hasta=NULL WHERE id_usuario=%s", (generate_password_hash(nueva), fila["id_usuario"]))
            if fila.get("token_hash"):
                ejecutar("UPDATE tokens_recuperacion SET usado=1 WHERE token_hash=%s", (fila["token_hash"],))
            auditoria("RESTABLECER_PASSWORD", "Autenticación", fila["id_usuario"])
            session.pop("recovery_user_id", None); session.pop("recovery_token_hash", None); session.pop("recovery_verified_at", None)
            flash("Contraseña restablecida correctamente. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/restablecer.html")

