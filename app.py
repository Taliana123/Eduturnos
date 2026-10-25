from flask import Flask, flash, jsonify, redirect, render_template, request, current_app, send_from_directory, session, url_for
from mysql.connector import Error as MySQLError
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import BadRequest
from urllib.parse import quote

from config import Config
from database.bootstrap import ensure_database

from routes.acudientes import acudientes_bp
from routes.auth import auth_bp
from routes.calendario import calendario_bp
from routes.citaciones import citaciones_bp
from routes.citas import citas_bp
from routes.configuracion import configuracion_bp
from routes.cuenta import cuenta_bp
from routes.integraciones_google import integraciones_google_bp
from routes.asistente import asistente_bp
from routes.docentes import docentes_bp
from routes.estudiantes import estudiantes_bp
from routes.importacion import importacion_bp
from routes.justificaciones import justificaciones_bp
from routes.notificaciones import notificaciones_bp
from routes.passwords import passwords_bp
from routes.reportes import reportes_bp
from routes.seguimiento import seguimiento_bp
from routes.solicitudes import solicitudes_bp
from routes.soporte import soporte_bp
from roles import SEDES_INSTITUCIONALES

from security import csrf_token, require_configured_secret, validar_csrf
from servicios.mail import mail
from servicios.reuniones import HORARIOS_CITAS, formatear_hora


def _beepy_home_enabled():
    if not current_app.config.get("BEEPY_ENABLED", False) or request.endpoint != "inicio":
        return False
    domains = current_app.config.get("BEEPY_DOMAINS")
    if domains is None:
        domains = (current_app.config.get("BEEPY_DOMAIN", ""),)
    if isinstance(domains, str):
        domains = domains.split(",")
    allowed_domains = {str(domain).strip().lower() for domain in domains if str(domain).strip()}
    return request.host.split(":")[0].lower() in allowed_domains


def create_app():
    app = Flask(__name__)

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1
    )

    app.config.from_object(Config)

    # ConfiguraciÃ³n de correo mediante Flask-Mail.
    app.config["MAIL_SERVER"] = app.config.get("MAIL_HOST")
    app.config["MAIL_PORT"] = app.config.get("MAIL_PORT", 587)
    app.config["MAIL_USERNAME"] = app.config.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = app.config.get("MAIL_PASSWORD")
    app.config["MAIL_USE_TLS"] = app.config.get("MAIL_USE_TLS", True)
    app.config["MAIL_USE_SSL"] = app.config.get("MAIL_USE_SSL", False)
    app.config["MAIL_DEFAULT_SENDER"] = app.config.get("MAIL_FROM")

    mail.init_app(app)

    require_configured_secret(app.config)

    # Verificar/configurar la base de datos
    db_ok, db_msg = ensure_database(app.config)

    app.config["DB_BOOTSTRAP_OK"] = db_ok

    if not db_ok:
        app.logger.warning(
            "Base de datos no disponible durante el arranque: %s",
            db_msg
        )

    # CSRF
    app.jinja_env.globals["csrf_token"] = csrf_token
    app.jinja_env.globals["csrf_field"] = (
        lambda: f'<input type="hidden" name="csrf_token" value="{csrf_token()}">'
    )
    app.jinja_env.filters["hora_ampm"] = formatear_hora
    app.jinja_env.globals["horarios_citas"] = {
        jornada: [(f"{total // 60:02d}:{total % 60:02d}", formatear_hora(f"{total // 60:02d}:{total % 60:02d}"))
                  for total in HORARIOS_CITAS
              if (total < 12 * 60) == es_manana]
        for jornada, es_manana in (("Mañana", True), ("Tarde", False))
    }

    @app.context_processor
    def disponibilidad_asistente():
        return {
            "asistente_disponible": bool(current_app.config.get("GROQ_API_KEY")),
            "beepy_disponible": current_app.config.get("BEEPY_ENABLED", False),
            "beepy_inicio": _beepy_home_enabled(),
        }

    @app.context_processor
    def navegacion_institucional():
        from routes.helpers import usuario_actual
        endpoint = request.endpoint or ""
        publica = endpoint.startswith("auth.") and endpoint != "auth.dashboard"
        usuario = usuario_actual() if session.get("usuario_id") and not publica else None
        return {"usuario_navegacion": usuario}

    # Blueprint de autenticaciÃ³n
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Resto de mÃ³dulos
    for bp in (
        citas_bp,
        citaciones_bp,
        calendario_bp,
        notificaciones_bp,
        reportes_bp,
        estudiantes_bp,
        acudientes_bp,
        docentes_bp,
        seguimiento_bp,
        configuracion_bp,
        cuenta_bp,
        integraciones_google_bp,
        asistente_bp,
        passwords_bp,
        justificaciones_bp,
        solicitudes_bp,
        soporte_bp,
        importacion_bp,
    ):
        app.register_blueprint(bp)

    # ProtecciÃ³n CSRF para operaciones que modifican datos
    @app.before_request
    def security_checks():
        if request.args.get("mobile") == "1":
            session["mobile_mode"] = True

        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            try:
                validar_csrf()
            except BadRequest:
                current_app.logger.warning(
                    "Validación CSRF rechazada: método=%s endpoint=%s",
                    request.method,
                    request.endpoint,
                )
                if request.method == "POST" and request.endpoint == "auth.login":
                    flash(
                        "El formulario de acceso venció o quedó desactualizado. "
                        "Vuelve a ingresar tus datos.",
                        "error",
                    )
                    return redirect(url_for("auth.login"))
                raise

    # Encabezados de seguridad
    @app.after_request
    def headers(response):
        beepy_home = _beepy_home_enabled()
        beepy_origin = " https://www.beepychatbot.com" if current_app.config.get("BEEPY_ENABLED", False) else ""
        response.headers.setdefault(
            "X-Content-Type-Options",
            "nosniff"
        )

        response.headers.setdefault(
            "X-Frame-Options",
            "SAMEORIGIN"
        )

        response.headers.setdefault(
            "Referrer-Policy",
            "strict-origin-when-cross-origin"
        )

        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()"
        )

        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "img-src 'self' data:" + (beepy_origin + " https://s3-eu-west-1.amazonaws.com/livebeep/" if beepy_home else "") + "; "
            "media-src 'self'" + (beepy_origin if beepy_home else "") + "; "
            "frame-src 'self' https://maps.google.com https://www.google.com" + beepy_origin + "; "
            "style-src 'self' 'unsafe-inline'" + (beepy_origin if beepy_home else "") + "; "
            "font-src 'self' data:; "
            "script-src 'self' 'sha256-62/dacoeWnOfkToAKl3FGOLvpTyGZeCV/L/BoJUygnQ=' "
            "'sha256-Ob9XMylXxoM1xB3YQRjyJ+SzKYw5tIGjuDixpXDlHwc='" + (beepy_origin if beepy_home else "") + "; "
            "connect-src 'self'" + (beepy_origin if beepy_home else "") + "; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'self'; "
            "form-action 'self'"
        )

        if current_app.config.get("SESSION_COOKIE_SECURE"):
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains"
            )

        return response

    # PÃ¡gina principal
    @app.route("/")
    def inicio():
        respuesta = current_app.make_response(render_template("index.html"))
        respuesta.headers["Cache-Control"] = "no-store"
        return respuesta

    # Páginas públicas adicionales
    @app.route("/como-funciona")
    def como_funciona():
        return render_template("publico/como_funciona.html")

    @app.route("/beneficios")
    def beneficios():
        return render_template("publico/beneficios.html")

    @app.route("/privacidad")
    def privacidad():
        return render_template("publico/privacidad.html")

    @app.route("/terminos")
    def terminos():
        return render_template("publico/terminos.html")

    @app.route("/institucion")
    def institucion():
        sedes = [
            {"nombre": nombre, "direccion": direccion}
            for _, nombre, direccion, _ in SEDES_INSTITUCIONALES
        ]
        for sede in sedes:
            sede["mapa"] = (
                "https://maps.google.com/maps?q="
                + quote(sede["direccion"] + ", Ibagué, Tolima")
                + "&output=embed"
            )
        informacion = {
            "nombre": "Institución Educativa José Joaquín Flórez Hernández",
            "codigo": "173001010508",
            "secretaria": "Ibagué",
            "direccion": "Ciudadela Las Américas, sector Picaleña, Ibagué, Tolima",
            "telefono": "(608) 2697083",
            "correos": ("coliejjfh@hotmail.com", "orlandoorjuela28@yahoo.es"),
            "municipio": "Ibagué",
            "codigo_municipio": "73001",
            "departamento": "Tolima",
            "codigo_departamento": "73",
            "tipo": "Institución educativa",
            "genero": "Mixto",
            "zona": "Urbana y rural",
            "niveles": "Preescolar, básica primaria, básica secundaria y media",
            "jornadas": "Mañana, completa, tarde, nocturna y fin de semana",
            "grados": "0 a 11 y ciclos 21 a 26",
            "modelos": (
                "Educación tradicional, Escuela Nueva, Aceleración del Aprendizaje, "
                "A Crecer, CAFAM y programa para jóvenes en extraedad y adultos"
            ),
        }
        return render_template("institucion.html", informacion=informacion, sedes=sedes)
    # robots.txt
    @app.get("/robots.txt")
    def robots():
        return send_from_directory(
            app.static_folder,
            "robots.txt"
        )

    @app.get("/service-worker.js")
    def service_worker():
        response = send_from_directory(
            app.static_folder,
            "service-worker.js"
        )
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Service-Worker-Allowed"] = "/"
        return response

    # security.txt
    @app.get("/seguridad.txt")
    def seguridad_txt():
        return send_from_directory(
            app.static_folder,
            "security.txt"
        )

    # InformaciÃ³n de versiÃ³n
    @app.get("/version")
    def version():
        return jsonify({
            "name": "EDUTURNOS",
            "version": "1.0.0",
            "environment": current_app.config.get("APP_ENV")
        })

    # Estado de la base de datos
    @app.get("/estado")
    def estado():
        from database.db import comprobar_conexion

        try:
            ok = comprobar_conexion()
        except Exception:
            current_app.logger.exception(
                "Error comprobando conexiÃ³n con MySQL"
            )
            ok = False

        return render_template(
            "estado.html",
            db_ok=ok,
            db_host=current_app.config.get("MYSQL_HOST"),
            db_port=current_app.config.get("MYSQL_PORT")
        ), 200

    # Health check bÃ¡sico
    @app.get("/health/live")
    def health_live():
        return jsonify({
            "status": "ok",
            "service": "eduturnos"
        }), 200

    # Health check incluyendo base de datos
    @app.get("/health/ready")
    def health_ready():
        from database.db import comprobar_conexion

        try:
            ok = comprobar_conexion()
        except Exception:
            current_app.logger.exception(
                "Health check de base de datos fallÃ³"
            )

            return jsonify({
                "status": "degraded",
                "database": "unavailable"
            }), 503

        return jsonify({
            "status": "ok",
            "database": "ok"
        }), 200 if ok else 503

    # Health general
    @app.get("/health")
    def health():
        from database.db import comprobar_conexion

        try:
            ok = comprobar_conexion()
        except Exception:
            current_app.logger.exception(
                "Health check fallÃ³"
            )
            ok = False

        return jsonify({
            "status": "ok" if ok else "degraded",
            "database": "ok" if ok else "unavailable"
        }), 200

    # ==========================================================
    # MANEJO DE ERRORES MYSQL
    # ==========================================================
    #
    # Durante desarrollo mostramos el error real para poder
    # corregir exactamente el problema.
    #
    @app.errorhandler(MySQLError)
    def error_mysql(exc):
        current_app.logger.exception(
            "ERROR DE MYSQL EN EDUTURNOS"
        )

        if current_app.debug:
            return (
                f"""
                <html>
                    <head>
                        <title>Error de MySQL - EDUTURNOS</title>
                    </head>
                    <body>
                        <h1>Error de MySQL</h1>
                        <pre>{exc}</pre>
                    </body>
                </html>
                """,
                500
            )

        errno = getattr(exc, "errno", None)

        if errno in {2003, 2005, 2006, 2013}:
            mensaje = (
                "La base de datos no estÃ¡ disponible en este momento. "
                "Revisa MySQL e intÃ©ntalo nuevamente."
            )
            status = 503
        else:
            mensaje = (
                "No fue posible completar la operaciÃ³n con la "
                "base de datos. El error quedÃ³ registrado para "
                "su revisiÃ³n."
            )
            status = 500

        return render_template(
            "error.html",
            codigo=status,
            mensaje=mensaje
        ), status

    # ==========================================================
    # ERROR 403
    # ==========================================================

    @app.errorhandler(403)
    def prohibido(_):
        return render_template(
            "error.html",
            codigo=403,
            mensaje="No tienes permiso para entrar a esta secciÃ³n."
        ), 403

    # ==========================================================
    # ERROR 400
    # ==========================================================

    @app.errorhandler(400)
    def solicitud_invalida(_):
        return render_template(
            "error.html",
            codigo=400,
            mensaje=(
                "La solicitud no es vÃ¡lida. "
                "Actualiza la pÃ¡gina e intÃ©ntalo de nuevo."
            )
        ), 400

    # ==========================================================
    # ERROR 404
    # ==========================================================

    @app.errorhandler(404)
    def no_encontrado(_):
        return render_template(
            "error.html",
            codigo=404,
            mensaje="La pÃ¡gina que buscas no existe."
        ), 404

    # ==========================================================
    # ERROR 500
    # ==========================================================

    @app.errorhandler(500)
    def error_interno(exc):
        current_app.logger.exception(
            "ERROR 500 EN EDUTURNOS",
            exc_info=exc
        )

        # IMPORTANTE:
        # Durante desarrollo mostramos el error real.
        if current_app.debug:
            return (
                f"""
                <html>
                    <head>
                        <title>Error 500 - EDUTURNOS</title>
                    </head>
                    <body>
                        <h1>Error 500</h1>
                        <pre>{exc}</pre>
                        <hr>
                        <p>
                            Este detalle solo se muestra porque
                            EDUTURNOS estÃ¡ ejecutÃ¡ndose en modo desarrollo.
                        </p>
                    </body>
                </html>
                """,
                500
            )

        return render_template(
            "error.html",
            codigo=500,
            mensaje=(
                "OcurriÃ³ un error interno. "
                "Revisa el registro del servidor."
            )
        ), 500

    return app


app = create_app()


if __name__ == "__main__":
    debug = bool(app.config.get("DEV_MODE")) and app.config.get("APP_ENV") != "production"
    app.run(
        debug=debug,
        host="127.0.0.1",
        port=5000,
        use_reloader=debug,
    )
