from datetime import date, timedelta
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
import time
from urllib.parse import parse_qs, urlsplit

import pytest
import re
from werkzeug.exceptions import Conflict, Forbidden, NotFound

from app import app
from routes.citas import _destino_cita_creada, _transicion_estado_permitida, _validar_cierre_cita, _validar_fecha_cita
from routes import citas as citas_routes
from routes import helpers
from routes import calendario as calendario_routes
from routes import auth as auth_routes
from routes import configuracion as configuracion_routes
from routes import helpers as session_helpers


def test_login_cookie_persists_for_30_days():
    from datetime import timedelta as datetime_timedelta

    assert app.permanent_session_lifetime == datetime_timedelta(days=30)

    client = app.test_client()
    with client.session_transaction() as stored_session:
        stored_session.permanent = True
        stored_session["usuario_id"] = 42
        stored_session["creado_en"] = time.time()

    response = client.get("/auth/login")

    expires = response.headers["Set-Cookie"].split("Expires=", 1)[1].split(";", 1)[0]
    remaining = parsedate_to_datetime(expires).timestamp() - time.time()
    assert 29 * 24 * 60 * 60 < remaining <= 30 * 24 * 60 * 60


def test_usuario_actual_no_expira_sesion_durante_su_periodo_configurado(monkeypatch):
    from datetime import timedelta as datetime_timedelta

    usuario = {"id_usuario": 42, "rol_nombre": "Estudiante"}
    now = 1_800_000_000
    monkeypatch.setattr(session_helpers, "time", lambda: now)
    monkeypatch.setattr(session_helpers, "consultar", lambda *args, **kwargs: usuario)

    with app.test_request_context("/"):
        session_helpers.session["usuario_id"] = 42
        session_helpers.session["creado_en"] = now - datetime_timedelta(days=29).total_seconds()
        assert session_helpers.usuario_actual() == usuario
        assert session_helpers.session["usuario_id"] == 42


def test_usuario_actual_expira_sesion_despues_de_30_dias(monkeypatch):
    from datetime import timedelta as datetime_timedelta

    now = 1_800_000_000
    monkeypatch.setattr(session_helpers, "time", lambda: now)
    monkeypatch.setattr(
        session_helpers,
        "consultar",
        lambda *args, **kwargs: pytest.fail("No debe consultar una sesión expirada."),
    )

    with app.test_request_context("/"):
        session_helpers.session["usuario_id"] = 42
        session_helpers.session["creado_en"] = now - datetime_timedelta(days=31).total_seconds()
        assert session_helpers.usuario_actual() is None
        assert not session_helpers.session


def test_sesion_activa_abre_dashboard_desde_inicio_y_login(monkeypatch):
    usuario = {"id_usuario": 42, "rol_nombre": "Docente"}
    monkeypatch.setattr(session_helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(auth_routes, "usuario_actual", lambda: usuario)
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["usuario_id"] = usuario["id_usuario"]
        sesion.permanent = True

    for path in ("/", "/auth/login"):
        respuesta = client.get(path)
        assert respuesta.status_code == 302
        assert urlsplit(respuesta.location).path == "/auth/dashboard"


def test_blueprints_principales_registrados():
    endpoints = {rule.endpoint for rule in app.url_map.iter_rules()}
    for endpoint in {
        'auth.login','auth.registro','auth.dashboard','citas.index','citas.nueva',
        'calendario.index','notificaciones.index','reportes.index','estudiantes.lista',
        'acudientes.lista','docentes.lista','seguimiento.lista','configuracion.index','institucion',
        'cuenta.index','integraciones_google.index','asistente.preguntar'
    }:
        assert endpoint in endpoints


def test_mi_cuenta_solicita_inicio_de_sesion_sin_consultar_base():
    respuesta = app.test_client().get("/cuenta/")

    assert respuesta.status_code == 302
    assert urlsplit(respuesta.location).path == "/auth/login"


@pytest.mark.parametrize(
    ("endpoint", "extra_data"),
    [
        ("/auth/recuperar", {}),
        ("/auth/verificar-codigo", {"accion": "reenviar", "codigo": ""}),
    ],
)
def test_recuperacion_envia_codigo_al_correo_que_se_ingreso(
    monkeypatch, endpoint, extra_data
):
    from routes import passwords as passwords_routes
    from servicios import email as email_service

    usuario = {
        "id_usuario": 42,
        "correo": "persona@gmail.com",
        "rol_nombre": "Acudiente",
    }
    envios = []

    def consultar_mock(sql, params=(), uno=False):
        if "FROM usuarios" in sql:
            assert params == ("persona@gmail.com",)
            return usuario
        if "information_schema.columns" in sql:
            return {"existe": 1}
        raise AssertionError(sql)

    monkeypatch.setattr(passwords_routes, "consultar", consultar_mock)
    monkeypatch.setattr(passwords_routes, "ejecutar", lambda *args, **kwargs: 1)
    monkeypatch.setattr(
        email_service.mail,
        "send",
        lambda mensaje: envios.append(mensaje),
    )
    for key, value in {
        "MAIL_SERVER": "smtp.example.com",
        "MAIL_USERNAME": "sender@example.com",
        "MAIL_PASSWORD": "smtp-test-password",
        "MAIL_DEFAULT_SENDER": "sender@example.com",
    }.items():
        monkeypatch.setitem(app.config, key, value)

    client = app.test_client()
    with client.session_transaction() as client_session:
        client_session["_csrf_token"] = "csrf-test"
    data = {"csrf_token": "csrf-test", "correo": "Persona@Gmail.com", **extra_data}

    respuesta = client.post(endpoint, data=data)

    assert respuesta.status_code == 302
    assert urlsplit(respuesta.location).path == "/auth/verificar-codigo"
    assert len(envios) == 1
    assert envios[0].recipients == ["persona@gmail.com"]
    assert 'src="cid:eduturnos-logo"' in envios[0].html


def test_recuperacion_no_envia_si_el_dominio_no_corresponde_al_rol(monkeypatch):
    from routes import passwords as passwords_routes
    from servicios import email as email_service

    usuario = {
        "id_usuario": 42,
        "correo": "persona@jjfh.edu.co",
        "rol_nombre": "Acudiente",
    }
    envios = []
    monkeypatch.setattr(passwords_routes, "consultar", lambda *args, **kwargs: usuario)
    monkeypatch.setattr(email_service.mail, "send", lambda mensaje: envios.append(mensaje))

    client = app.test_client()
    with client.session_transaction() as client_session:
        client_session["_csrf_token"] = "csrf-test"
    respuesta = client.post(
        "/auth/recuperar",
        data={"csrf_token": "csrf-test", "correo": "persona@jjfh.edu.co"},
    )

    assert respuesta.status_code == 302
    assert not envios


def test_correo_no_registrado_no_se_reporta_como_enviado(monkeypatch):
    from routes import passwords as passwords_routes
    from servicios import email as email_service

    monkeypatch.setattr(passwords_routes, "consultar", lambda *args, **kwargs: None)
    envios = []
    monkeypatch.setattr(email_service.mail, "send", lambda mensaje: envios.append(mensaje))

    client = app.test_client()
    with client.session_transaction() as client_session:
        client_session["_csrf_token"] = "csrf-test"

    respuesta = client.post(
        "/auth/recuperar",
        data={
            "csrf_token": "csrf-test",
            "correo": "no-registrado@gmail.com",
        },
    )

    assert respuesta.status_code == 302
    assert not envios
    with client.session_transaction() as client_session:
        mensajes = client_session["_flashes"]
    assert "asociado a una cuenta activa" in mensajes[0][1]


def test_recuperacion_rechaza_dominio_no_permitido_sin_buscar_cuenta(monkeypatch):
    from routes import passwords as passwords_routes

    monkeypatch.setattr(
        passwords_routes,
        "consultar",
        lambda *args, **kwargs: pytest.fail("No debe consultar cuentas con un dominio no permitido."),
    )
    client = app.test_client()
    with client.session_transaction() as client_session:
        client_session["_csrf_token"] = "csrf-test"

    respuesta = client.post(
        "/auth/recuperar",
        data={"csrf_token": "csrf-test", "correo": "persona@outlook.com"},
    )

    assert respuesta.status_code == 200
    assert "Gmail para estudiantes y acudientes" in respuesta.get_data(as_text=True)


@pytest.mark.parametrize(
    ("portal", "correo"),
    [
        ("estudiante", "estudiante@jjfh.edu.co"),
        ("acudiente", "acudiente@outlook.com"),
        ("docente", "docente@gmail.com"),
        ("coordinador", "coordinador@gmail.com"),
        ("rector", "rector@gmail.com"),
    ],
)
def test_registro_rechaza_correo_que_no_corresponde_al_portal(
    monkeypatch, portal, correo
):
    monkeypatch.setattr(auth_routes, "_sedes", lambda: [])
    monkeypatch.setattr(auth_routes, "_jornadas", lambda: [])
    monkeypatch.setattr(
        auth_routes,
        "_mostrar_registro",
        lambda *args: "blocked-by-domain-validation",
    )

    with app.test_request_context(
        f"/auth/registro/{portal}",
        method="POST",
        data={"correo": correo},
    ):
        respuesta = auth_routes.registro_portal(portal)

    assert respuesta == "blocked-by-domain-validation"


@pytest.mark.parametrize("portal", ["estudiante", "acudiente"])
def test_registro_crea_cuenta_con_grupo_bloqueado_como_diccionario(
    monkeypatch, portal
):
    class Cursor:
        def __init__(self):
            self.lastrowid = 100

        def execute(self, _sql, _params=None):
            self.lastrowid += 1

        def fetchone(self):
            return None

        def close(self):
            pass

    class Connection:
        def cursor(self, **_kwargs):
            return Cursor()

    @contextmanager
    def transaction():
        yield Connection()

    grupo = {"id": 18, "nombre": "1", "id_grado": 6}
    grupos_bloqueados = []

    monkeypatch.setattr(auth_routes, "_sedes", lambda: [])
    monkeypatch.setattr(auth_routes, "_jornadas", lambda: [])
    monkeypatch.setattr(auth_routes, "_rol_id", lambda _rol: 3)
    monkeypatch.setattr(
        auth_routes,
        "_grado_estudiante_valido",
        lambda _grado: {"id": 6},
    )
    monkeypatch.setattr(auth_routes, "_obtener_grupo_real", lambda *_args: grupo)
    monkeypatch.setattr(
        auth_routes,
        "_bloquear_grupo_y_comprobar_cupo",
        lambda *_args, **_kwargs: grupos_bloqueados.append(True) or grupo,
    )
    monkeypatch.setattr(
        auth_routes,
        "_asignar_codigo_estudiantil_tx",
        lambda *_args: "EST-TEST",
    )
    monkeypatch.setattr(auth_routes, "_codigo_estudiantil", lambda _id: "EST-TEST")
    monkeypatch.setattr(auth_routes, "transaccion", transaction)

    def consultar_mock(sql, *_args, **_kwargs):
        if "FROM periodos_academicos" in sql:
            return {"id": 1}
        if "SELECT codigo_estudiantil" in sql:
            return {"codigo_estudiantil": "EST-TEST"}
        return None

    monkeypatch.setattr(auth_routes, "consultar", consultar_mock)

    data = {
        "tipo_documento": "TI" if portal == "estudiante" else "CC",
        "documento": "123456789",
        "nombres": "Ana",
        "apellidos": "Perez",
        "correo": "persona@gmail.com",
        "telefono": "3001234567",
        "password": "ClaveSegura123",
        "id_sede": "1",
        "id_jornada": "1",
        "id_grado": "6",
        "id_grupo": "1",
    }
    if portal == "acudiente":
        data.pop("id_sede")
        data.pop("id_jornada")
        data.pop("id_grado")
        data.pop("id_grupo")
        data.update(
            {
                "estudiante_tipo_documento": "TI",
                "estudiante_documento": "987654321",
                "estudiante_nombres": "Luis",
                "estudiante_apellidos": "Perez",
                "estudiante_id_sede": "1",
                "estudiante_id_jornada": "1",
                "estudiante_id_grado": "6",
                "estudiante_id_grupo": "1",
                "parentesco": "Madre",
            }
        )

    with app.test_request_context(
        f"/auth/registro/{portal}",
        method="POST",
        data=data,
    ):
        respuesta = auth_routes.registro_portal(portal)

    assert respuesta.status_code == 302
    assert respuesta.location.endswith("/auth/login")
    assert grupos_bloqueados


def test_registro_invalido_redirige_y_preserva_datos_sin_contrasena(monkeypatch):
    monkeypatch.setattr(auth_routes, "consultar", lambda *args, **kwargs: [])
    monkeypatch.setattr(auth_routes, "_sedes", lambda: [])
    monkeypatch.setattr(auth_routes, "_jornadas", lambda: [])
    datos = {
        "nombres": "Ana",
        "correo": "ana@outlook.com",
        "password": "No guardar esta clave",
        "csrf_token": "token",
    }
    client = app.test_client()
    pagina = client.get("/auth/registro/estudiante").get_data(as_text=True)
    token = re.search(r'name="csrf_token"\s+value="([^"]+)"', pagina).group(1)
    respuesta = client.post(
        "/auth/registro/estudiante",
        data={**datos, "csrf_token": token},
    )
    assert respuesta.status_code == 302
    assert respuesta.location.endswith("/auth/registro/estudiante")

    respuesta = client.get(respuesta.location)
    html = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 200
    assert "data-form-values=" in html
    assert "Ana" in html
    assert "No guardar esta clave" not in html


def test_fallo_smtp_no_muestra_mensaje_de_envio_correcto(monkeypatch):
    from routes import passwords as passwords_routes
    from servicios import email as email_service

    usuario = {
        "id_usuario": 42,
        "correo": "persona@gmail.com",
        "rol_nombre": "Estudiante",
    }
    escrituras = []

    def consultar_mock(sql, params=(), uno=False):
        if "FROM usuarios" in sql:
            return usuario
        if "information_schema.columns" in sql:
            return {"existe": 1}
        raise AssertionError(sql)

    def fallar_envio(_mensaje):
        raise OSError("SMTP no disponible")

    monkeypatch.setattr(passwords_routes, "consultar", consultar_mock)
    monkeypatch.setattr(
        passwords_routes,
        "ejecutar",
        lambda sql, params=(): escrituras.append((sql, params)),
    )
    monkeypatch.setattr(email_service.mail, "send", fallar_envio)
    for key, value in {
        "MAIL_SERVER": "smtp.example.com",
        "MAIL_USERNAME": "sender@example.com",
        "MAIL_PASSWORD": "smtp-test-password",
        "MAIL_DEFAULT_SENDER": "sender@example.com",
    }.items():
        monkeypatch.setitem(app.config, key, value)

    client = app.test_client()
    with client.session_transaction() as client_session:
        client_session["_csrf_token"] = "csrf-test"

    respuesta = client.post(
        "/auth/recuperar",
        data={"csrf_token": "csrf-test", "correo": "persona@gmail.com"},
    )

    assert respuesta.status_code == 200
    assert b"No fue posible enviar el correo de recuperaci" in respuesta.data
    assert any(sql.startswith("DELETE FROM tokens_recuperacion") for sql, _ in escrituras)
    assert b"Si el correo ingresado est" not in respuesta.data


def test_login_con_csrf_vencido_regresa_al_formulario_sin_error_400(caplog):
    respuesta = app.test_client().post("/auth/login", data={"identificador": "", "password": ""})

    assert respuesta.status_code == 302
    assert urlsplit(respuesta.location).path == "/auth/login"
    assert "Validación CSRF rechazada: método=POST endpoint=auth.login" in caplog.text


def test_formulario_login_no_se_guarda_en_cache():
    respuesta = app.test_client().get("/auth/login")

    assert respuesta.status_code == 200
    assert respuesta.headers["Cache-Control"] == "no-store"


def test_soporte_muestra_solo_enlace_de_correo_a_acudiente(monkeypatch):
    from routes import soporte as soporte_routes

    usuario = {
        "id_usuario": 42,
        "nombres": "Ana",
        "apellidos": "Pérez",
        "correo": "ana@example.com",
        "rol_nombre": "Acudiente",
    }
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(soporte_routes, "usuario_actual", lambda: usuario)

    client = app.test_client()
    with client.session_transaction() as session:
        session["usuario_id"] = 42
    respuesta = client.get("/soporte/")

    assert respuesta.status_code == 200
    assert 'href="mailto:coliejjfh@hotmail.com' in respuesta.get_data(as_text=True)
    assert "Enviar solicitud" not in respuesta.get_data(as_text=True)


@pytest.mark.parametrize("scope,rol,permitido", [
    ("personal", "Docente", True),
    ("personal", "Rector", True),
    ("personal", "Estudiante", True),
    ("personal", "Acudiente", True),
    ("institucional", "Super Admin", True),
    ("institucional", "Rector", True),
    ("institucional", "Administrador / Coordinador", False),
])
def test_google_calendar_respeta_alcance_y_rol(scope, rol, permitido):
    from routes.integraciones_google import _permite

    assert _permite(scope, rol) is permitido


def test_callback_google_encola_citas_futuras_al_conectar_acudiente(monkeypatch):
    from routes import integraciones_google as google_routes

    usuario = {"id_usuario": 42, "rol_nombre": "Acudiente"}
    conexiones = []
    sincronizaciones = []
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(google_routes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(google_routes, "intercambiar_codigo", lambda code: {"access_token": "token"})
    monkeypatch.setattr(google_routes, "calendar_id_objetivo", lambda scope_key: "primary")
    monkeypatch.setattr(google_routes, "probar_conexion_calendario", lambda token, calendar_id: None)
    monkeypatch.setattr(google_routes, "correo_google", lambda token: "acudiente@example.com")
    monkeypatch.setattr(google_routes, "guardar_conexion", lambda *args: conexiones.append(args))
    monkeypatch.setattr(
        google_routes,
        "encolar_citas_futuras",
        lambda scope_key, user_id: sincronizaciones.append((scope_key, user_id)) or {"citas": 2, "encoladas": 2},
    )
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["google_oauth_state"] = "estado-prueba"
        sesion["google_oauth_scope"] = "personal"

    respuesta = client.get("/integraciones-google/callback?state=estado-prueba&code=codigo")

    assert respuesta.status_code == 302
    assert conexiones[0][0] == "usuario:42"
    assert sincronizaciones == [("usuario:42", 42)]


@pytest.mark.parametrize("rol,visible", [
    ("Super Admin", True),
    ("Rector", True),
    ("Administrador / Coordinador", True),
    ("Docente", True),
    ("Estudiante", True),
    ("Acudiente", True),
])
def test_widget_edubot_esta_disponible_para_todos_los_roles(rol, visible):
    from flask import render_template

    with app.test_request_context("/auth/dashboard"):
        contenido = render_template(
            "_asistente_widget.html",
            usuario_navegacion={"rol_nombre": rol, "nombres": "Ana"},
        )

    assert ('class="dashboard-help"' in contenido) is visible
    assert ('data-eduturnos-assistant' in contenido) is visible
    assert ('<iframe' in contenido) is False


def test_widget_edubot_no_aparece_sin_sesion():
    from flask import render_template

    with app.test_request_context("/auth/dashboard"):
        html = render_template(
            "_asistente_widget.html",
            usuario_navegacion=None,
        )
    assert html.strip() == ""


@pytest.mark.parametrize("rol", ["Super Admin", "Rector", "Administrador / Coordinador", "Docente", "Estudiante", "Acudiente"])
def test_asistente_responde_localmente_a_todos_los_roles(monkeypatch, rol):
    from routes import asistente as asistente_routes

    usuario = {"id_usuario": 12, "rol_nombre": rol}
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(asistente_routes, "usuario_actual", lambda: usuario)
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["_csrf_token"] = "chat-csrf"
    response = client.post(
        "/asistente/preguntar",
        json={"mensaje": "¿Cómo reviso el calendario?"},
        headers={"X-CSRFToken": "chat-csrf"},
    )

    assert response.status_code == 200
    assert "Calendario" in response.json["respuesta"]
    assert "citaciones" in response.json["respuesta"].lower()


def test_asistente_responde_pregunta_abierta_con_el_perfil_actual(monkeypatch):
    from routes import asistente as asistente_routes

    usuario = {"id_usuario": 12, "rol_nombre": "Docente"}
    respuestas = []
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(asistente_routes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(
        asistente_routes,
        "generar_respuesta",
        lambda pregunta, rol=None: respuestas.append((pregunta, rol)) or "Para cambiar una preferencia, abre Mi cuenta.",
    )
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["_csrf_token"] = "chat-csrf"
    response = client.post(
        "/asistente/preguntar",
        json={"mensaje": "¿Cómo puedo usar el sistema?"},
        headers={"X-CSRFToken": "chat-csrf"},
    )

    assert response.status_code == 200
    assert response.json["respuesta"] == "Para cambiar una preferencia, abre Mi cuenta."
    assert respuestas == [("¿Cómo puedo usar el sistema?", "Docente")]


def test_asistente_avisa_si_la_respuesta_abierta_no_esta_disponible(monkeypatch):
    from routes import asistente as asistente_routes

    usuario = {"id_usuario": 12, "rol_nombre": "Docente"}
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(asistente_routes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(
        asistente_routes,
        "generar_respuesta",
        lambda pregunta, rol=None: (_ for _ in ()).throw(RuntimeError("IA no disponible")),
    )
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["_csrf_token"] = "chat-csrf"

    response = client.post(
        "/asistente/preguntar",
        json={"mensaje": "¿Cómo configuro otro módulo?"},
        headers={"X-CSRFToken": "chat-csrf"},
    )

    assert response.status_code == 503
    assert response.json["error"] == "IA no disponible"


def test_asistente_muestra_error_si_falta_configurar_proveedor(monkeypatch):
    from routes import asistente as asistente_routes

    usuario = {"id_usuario": 12, "rol_nombre": "Docente"}
    monkeypatch.setitem(app.config, "GROQ_API_KEY", "")
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(asistente_routes, "usuario_actual", lambda: usuario)
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["_csrf_token"] = "chat-csrf"

    response = client.post(
        "/asistente/preguntar",
        json={"mensaje": "¿Cómo configuro un proceso institucional especial?"},
        headers={"X-CSRFToken": "chat-csrf"},
    )

    assert response.status_code == 503
    assert "respuestas abiertas no están activadas" in response.json["error"]


def test_asistente_rechaza_mensaje_no_textual(monkeypatch):
    from routes import asistente as asistente_routes

    usuario = {"id_usuario": 12, "rol_nombre": "Docente"}
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(asistente_routes, "usuario_actual", lambda: usuario)
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["_csrf_token"] = "chat-csrf"
    response = client.post(
        "/asistente/preguntar",
        json={"mensaje": ["valor inválido"]},
        headers={"X-CSRFToken": "chat-csrf"},
    )

    assert response.status_code == 400
    assert response.json["error"] == "El mensaje debe ser texto."


def test_informacion_institucional_publica_muestra_siete_sedes():
    response = app.test_client().get("/institucion")

    assert response.status_code == 200
    assert b"173001010508" in response.data
    assert b"Sede San Mart\xc3\xadn" in response.data
    assert b"Sede Sim\xc3\xb3n Bol\xc3\xadvar" not in response.data
    assert response.data.count(b"<iframe") == 7
    assert b"frame-src 'self' https://maps.google.com" in response.headers["Content-Security-Policy"].encode()


def test_dashboard_agenda_y_vencidos_respetan_filtros_del_rol(monkeypatch):
    from flask import render_template as render_template_real

    usuario = {"id_usuario": 8, "rol_nombre": "Docente"}
    consultas = []
    contexto = {}
    monkeypatch.setattr(auth_routes, "usuario_actual", lambda: usuario)

    def consultar(sql, params=(), uno=False):
        consultas.append((sql, params, uno))
        if "SELECT c.id, c.fecha" in sql:
            return [{"id": 5, "fecha": date.today(), "hora": "09:00", "estudiante": "Estudiante"}]
        if "GROUP BY c.fecha" in sql:
            return [{"dia": date.today().day, "total": 1}]
        if "COUNT(*) AS total" in sql:
            return {"total": 2}
        if "FROM compromisos_cita" in sql:
            return [{"id_cita": 5, "descripcion": "Entregar documento", "fecha_limite": date.today()}]
        return {"total": 0}

    monkeypatch.setattr(auth_routes, "consultar", consultar)
    def renderizar_dashboard(template, **kwargs):
        contexto.update(kwargs)
        return render_template_real(template, **kwargs)

    monkeypatch.setattr(auth_routes, "render_template", renderizar_dashboard)
    with app.test_request_context("/auth/dashboard"):
        response = auth_routes.dashboard()

    assert "metric-month" in response
    assert contexto["agenda_hoy"][0]["id"] == 5
    assert contexto["datos"]["por_atender"] == 6
    assert contexto["datos"]["atendidas"] == 2
    assert contexto["datos"]["incumplidas"] == 2
    assert contexto["citas_activas_mes"] == 1
    assert date.today().day in contexto["dias_con_citas"]
    assert contexto["compromisos_vencidos"][0]["id_cita"] == 5
    assert contexto["compromisos_vencidos_total"] == 2
    assert contexto["solicitudes_pendientes"] == 0
    assert "Pendientes que requieren atención" in response
    assert "Compromisos sin completar" in response
    assert "Solicitudes por revisar" not in response
    assert any("c.fecha >= CURDATE()" in sql for sql, _, _ in consultas)
    for sql, params, _ in consultas:
        if "FROM citas c" in sql or "FROM compromisos_cita" in sql:
            assert "c.id_docente" in sql
            assert params[0] == 8


def test_dashboard_cuenta_solicitudes_pendientes_para_rector(monkeypatch):
    usuario = {"id_usuario": 3, "rol_nombre": "Rector"}
    consultas = []
    contexto = {}
    monkeypatch.setattr(auth_routes, "usuario_actual", lambda: usuario)

    def consultar(sql, params=(), uno=False):
        consultas.append(sql)
        if "FROM solicitudes_cita" in sql:
            return {"total": 3}
        if "SELECT c.id, c.fecha" in sql or "GROUP BY c.fecha" in sql:
            return []
        if "FROM compromisos_cita" in sql and "COUNT(*)" not in sql:
            return []
        return {"total": 0}

    monkeypatch.setattr(auth_routes, "consultar", consultar)
    monkeypatch.setattr(
        auth_routes,
        "render_template",
        lambda template, **kwargs: contexto.update(kwargs) or "Dashboard",
    )
    with app.test_request_context("/auth/dashboard"):
        response = auth_routes.dashboard()

    assert response == "Dashboard"
    assert contexto["solicitudes_pendientes"] == 3
    assert any("FROM solicitudes_cita" in sql for sql in consultas)


def test_acciones_estado_catalogo_fijan_el_destino_solicitado(monkeypatch):
    consultas = []
    monkeypatch.setattr(configuracion_routes, "ejecutar", lambda sql, params=(): consultas.append((sql, params)))

    for estado_objetivo in ("1", "0"):
        with app.test_request_context(
            "/configuracion/sede/7/toggle",
            method="POST",
            data={"estado_objetivo": estado_objetivo},
        ):
            configuracion_routes._fijar_estado("sedes", "id", 7)

    assert consultas == [
        ("UPDATE sedes SET estado=%s WHERE id=%s", (1, 7)),
        ("UPDATE sedes SET estado=%s WHERE id=%s", (0, 7)),
    ]


def test_calendario_disponibilidad_docente_se_limita_a_su_usuario(monkeypatch):
    consultas = []
    contexto = {}
    usuario = {"id_usuario": 8, "rol_nombre": "Docente"}
    monkeypatch.setattr(calendario_routes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(calendario_routes, "citas_visibles", lambda actual: [])
    monkeypatch.setattr(calendario_routes, "_aplicar_filtros", lambda citas: citas)

    def consultar(sql, params=(), uno=False):
        consultas.append((sql, params))
        if "FROM docentes WHERE id_usuario=%s" in sql:
            return [{"id_docente": 8, "nombre": "Docente Prueba"}]
        if "FROM disponibilidad_docente" in sql:
            return [{"id": 3, "dia_semana": 0, "hora_inicio": "08:00", "hora_fin": "10:00"}]
        return []

    monkeypatch.setattr(calendario_routes, "consultar", consultar)
    monkeypatch.setattr(calendario_routes, "render_template", lambda template, **kwargs: contexto.update(kwargs) or "Calendario")
    with app.test_request_context("/calendario/?anio=2026&mes=10"):
        calendario_routes.index.__wrapped__()

    selector = next((consulta for consulta in consultas if "FROM docentes WHERE id_usuario=%s" in consulta[0]), None)
    assert selector is not None
    assert selector[1] == (8,)
    assert contexto["rol_usuario"] == "Docente"
    assert contexto["docentes_disponibilidad"] == [{"id_docente": 8, "nombre": "Docente Prueba"}]
    assert contexto["docente_disponibilidad_id"] == 8


def test_home_publico():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert b'EDUTURNOS' in response.data
    assert b'/privacidad' in response.data
    assert b'/terminos' in response.data


def test_politicas_google_calendar_son_publicas():
    client = app.test_client()
    privacidad = client.get('/privacidad')
    terminos = client.get('/terminos')

    assert privacidad.status_code == 200
    assert b'No se env' in privacidad.data
    assert b'cifradas' in privacidad.data
    assert terminos.status_code == 200
    assert b'Google Calendar es una copia adicional' in terminos.data


def test_login_publico():
    client = app.test_client()
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Iniciar sesi' in response.data


def test_cita_rechaza_fecha_anterior_a_hoy():
    ayer = (date.today() - timedelta(days=1)).isoformat()

    try:
        _validar_fecha_cita(ayer)
    except ValueError as exc:
        assert "no puede ser anterior a hoy" in str(exc)
    else:
        raise AssertionError("Se aceptó una cita en una fecha pasada.")


def test_cita_acepta_fecha_de_hoy():
    hoy = date.today()

    assert _validar_fecha_cita(hoy.isoformat()) == hoy


def test_resultados_finales_solo_se_aplican_con_cierre_formal():
    assert not _transicion_estado_permitida("Rector", "Confirmada", "Realizada")
    assert not _transicion_estado_permitida("Docente", "Confirmada", "No asistió")
    assert _transicion_estado_permitida("Acudiente", "Pendiente", "Confirmada")
    assert not _transicion_estado_permitida("Acudiente", "Pendiente", "Realizada")


def test_nota_cita_conserva_estado_y_registra_autor(monkeypatch):
    usuario = {"id_usuario": 7, "rol_nombre": "Rector"}
    escrituras = []
    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(citas_routes, "consultar", lambda *args, **kwargs: {"id": 5, "estado": "Confirmada"})
    monkeypatch.setattr(citas_routes, "ejecutar", lambda sql, params: escrituras.append((sql, params)))
    monkeypatch.setattr(citas_routes, "auditoria", lambda *args: None)
    with app.test_request_context("/citas/5/notas", method="POST", data={"nota": "  Acuerdo registrado  "}):
        response = citas_routes.guardar_nota.__wrapped__(5)
    assert response.status_code == 302
    assert response.location.endswith("/citas/#cita-dialog-5")
    assert len(escrituras) == 1
    assert escrituras[0][0].startswith("INSERT INTO seguimiento_citas")
    assert escrituras[0][1] == (5, "Confirmada", "Pendiente", "Acuerdo registrado", 7)


@pytest.mark.parametrize("nota", ["", "   ", "texto" * 2001])
def test_nota_cita_rechaza_texto_invalido(monkeypatch, nota):
    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: {"id_usuario": 7, "rol_nombre": "Rector"})
    monkeypatch.setattr(citas_routes, "consultar", lambda *args, **kwargs: {"id": 5, "estado": "Confirmada"})
    escrituras = []
    monkeypatch.setattr(citas_routes, "ejecutar", lambda *args: escrituras.append(args))
    with app.test_request_context("/citas/5/notas", method="POST", data={"nota": nota}):
        response = citas_routes.guardar_nota.__wrapped__(5)
    assert response.status_code == 302
    assert not escrituras


def test_nota_docente_restringe_cita_asignada(monkeypatch):
    consultas = []
    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: {"id_usuario": 8, "rol_nombre": "Docente"})
    def consultar(sql, params, **kwargs):
        consultas.append((sql, params))
        return None
    monkeypatch.setattr(citas_routes, "consultar", consultar)
    escrituras = []
    monkeypatch.setattr(citas_routes, "ejecutar", lambda *args: escrituras.append(args))
    with app.test_request_context("/citas/5/notas", method="POST", data={"nota": "Nota privada"}):
        with pytest.raises(NotFound):
            citas_routes.guardar_nota.__wrapped__(5)
    assert "c.id_docente" in consultas[0][0]
    assert consultas[0][1] == (8, 5)
    assert not escrituras


@pytest.mark.parametrize("rol", ["Estudiante", "Acudiente"])
def test_nota_cita_no_permite_escritura_a_otros_roles(monkeypatch, rol):
    monkeypatch.setattr(helpers, "usuario_actual", lambda: {"id_usuario": 9, "rol_nombre": rol})
    with app.test_request_context("/citas/5/notas", method="POST", data={"nota": "No autorizada"}):
        with pytest.raises(Forbidden):
            citas_routes.guardar_nota(5)


def test_nota_cita_exige_csrf(monkeypatch):
    usuario = {"id_usuario": 7, "rol_nombre": "Rector"}
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: usuario)
    escrituras = []
    monkeypatch.setattr(citas_routes, "ejecutar", lambda *args: escrituras.append(args))
    response = app.test_client().post("/citas/5/notas", data={"nota": "Nota sin token"})
    assert response.status_code == 400
    assert not escrituras


def test_nota_cita_post_con_token_valido(monkeypatch):
    usuario = {"id_usuario": 7, "rol_nombre": "Rector"}
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(citas_routes, "consultar", lambda *args, **kwargs: {"id": 5, "estado": "Confirmada"})
    escrituras = []
    monkeypatch.setattr(citas_routes, "ejecutar", lambda sql, params: escrituras.append(params))
    monkeypatch.setattr(citas_routes, "auditoria", lambda *args: None)
    client = app.test_client()
    with client.session_transaction() as session:
        session["_csrf_token"] = "token-de-prueba"
    response = client.post("/citas/5/notas", data={"nota": "Nota válida", "csrf_token": "token-de-prueba"})
    assert response.status_code == 302
    assert escrituras == [(5, "Confirmada", "Pendiente", "Nota válida", 7)]


def test_historial_notas_solo_consulta_citas_visibles(monkeypatch):
    nota = {"id_cita": 5, "observaciones": "Nota anterior", "autor": "Usuario Prueba"}
    consultas = []
    contexto = {}
    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: {"id_usuario": 8, "rol_nombre": "Docente"})
    monkeypatch.setattr(citas_routes, "consultar_citas", lambda usuario: [{"id": 5}])
    monkeypatch.setattr(citas_routes, "datos_escolares", lambda *args, **kwargs: {})
    def consultar(sql, params):
        consultas.append((sql, params))
        return [nota]
    def render_template(template, **kwargs):
        contexto.update(kwargs)
        return ""
    monkeypatch.setattr(citas_routes, "consultar", consultar)
    monkeypatch.setattr(citas_routes, "render_template", render_template)
    with app.test_request_context("/citas/"):
        citas_routes.index.__wrapped__()
    assert "WHERE s.id_cita IN (%s)" in consultas[0][0]
    assert consultas[0][1] == (5,)
    assert contexto["notas_por_cita"] == {5: [nota]}


@pytest.mark.parametrize("datos,agente", [
    ({"vista_movil": "1"}, "Chrome Windows"),
    ({}, "Chrome Android"),
    ({}, "Safari iPhone"),
])
def test_cita_movil_abre_calendario_en_fecha_creada(datos, agente):
    with app.test_request_context("/citas/nueva", method="POST", data=datos, headers={"User-Agent": agente}):
        destino = urlsplit(_destino_cita_creada("2027-02-18"))
    assert destino.path == "/calendario/"
    assert parse_qs(destino.query) == {"anio": ["2027"], "mes": ["2"], "dia": ["2027-02-18"]}


def test_cita_pc_conserva_destino_al_listado():
    with app.test_request_context("/citas/nueva", method="POST", headers={"User-Agent": "Chrome Windows"}):
        assert _destino_cita_creada("2027-02-18") == "/citas/"


def test_hora_agenda_calendario_no_incluye_segundos():
    plantilla = app.jinja_loader.get_source(app.jinja_env, "calendario/index.html")[0]
    assert "cita.hora|hora_ampm" in plantilla
    formato = app.jinja_env.from_string("{{ hora|hora_ampm }}")
    assert formato.render(hora="10:30:00") == "10:30 AM"
    assert formato.render(hora="13:00:00") == "1:00 PM"


@pytest.mark.parametrize("estado_actual", ["Pendiente", "Confirmada", "Reprogramada", "Realizada"])
def test_reprogramar_solo_realizada_conserva_cita_anterior(monkeypatch, estado_actual):
    usuario = {"id_usuario": 7, "rol_nombre": "Rector"}
    cita = {
        "id_docente": 1,
        "id_estudiante": 2,
        "id_acudiente": 3,
        "creado_por": 7,
    }
    escrituras = []
    avisos = []

    class CursorPrueba:
        lastrowid = 901

        def execute(self, sql, params=()):
            self.sql = sql
            escrituras.append((sql, params))

        def fetchone(self):
            if "FOR UPDATE" in self.sql:
                return {"fecha": date.today(), "hora": "10:30", "id_estado": 4, "estado": estado_actual}
            return {"id": 6}

        def fetchall(self):
            return []

        def close(self):
            pass

    class ConexionPrueba:
        def cursor(self, **kwargs):
            return CursorPrueba()

    @contextmanager
    def transaccion_prueba():
        yield ConexionPrueba()

    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(citas_routes, "_cita_autorizada", lambda *args: cita)
    monkeypatch.setattr(citas_routes, "transaccion", transaccion_prueba)
    monkeypatch.setattr(citas_routes, "validar_disponibilidad", lambda *args: None)
    monkeypatch.setattr(citas_routes, "bloquear_agenda", lambda *args: None)
    monkeypatch.setattr(citas_routes, "comprobar_hueco", lambda *args, **kwargs: None)
    monkeypatch.setattr(citas_routes, "auditoria", lambda *args: None)
    monkeypatch.setattr(citas_routes, "_notificar", lambda *args: avisos.append(args))
    datos = {"fecha": (date.today() + timedelta(days=1)).isoformat(), "hora": "11:30", "motivo": "Otra reunión"}
    with app.test_request_context("/citas/5/reprogramar", method="POST", data=datos):
        if estado_actual != "Realizada":
            with pytest.raises(Conflict):
                citas_routes.reprogramar_cita.__wrapped__(5)
            assert not any(sql.startswith(("INSERT", "UPDATE", "DELETE")) for sql, _ in escrituras)
            return
        response = citas_routes.reprogramar_cita.__wrapped__(5)
    assert response.status_code == 302
    assert any("INSERT INTO citas" in sql and "SELECT id_estudiante" in sql for sql, _ in escrituras)
    assert not any("UPDATE citas" in sql or "DELETE" in sql for sql, _ in escrituras)
    assert next(params[0] for sql, params in escrituras if "INSERT INTO reprogramaciones_cita" in sql) == 901
    assert avisos[0][0] == 901


def test_reprogramar_cita_rechaza_a_personal_que_no_es_creador(monkeypatch):
    monkeypatch.setattr(
        citas_routes,
        "usuario_actual",
        lambda: {"id_usuario": 7, "rol_nombre": "Rector"},
    )
    monkeypatch.setattr(
        citas_routes,
        "_cita_autorizada",
        lambda *args: {"creado_por": 42},
    )

    with app.test_request_context(
        "/citas/5/reprogramar",
        method="POST",
        data={"fecha": "2030-01-01", "hora": "11:30", "motivo": "Cambio"},
    ):
        with pytest.raises(Forbidden):
            citas_routes.reprogramar_cita.__wrapped__(5)


def test_acudiente_solicita_cambio_al_creador_original(monkeypatch):
    from datetime import date

    solicitud_cita = {
        "id": 5,
        "id_docente": 1,
        "id_estudiante": 2,
        "id_acudiente": 3,
        "creado_por": 42,
        "fecha": date.today() + timedelta(days=1),
        "hora": "10:30:00",
        "estado": "Confirmada",
        "creador_rol": "Rector",
    }
    escrituras = []

    class CursorPrueba:
        lastrowid = 61
        sql = ""

        def execute(self, sql, params=()):
            self.sql = sql
            escrituras.append((sql, params))

        def fetchone(self):
            if "SELECT c.id, c.id_estudiante" in self.sql:
                return solicitud_cita
            return None

        def close(self):
            pass

    class ConexionPrueba:
        def cursor(self, **_kwargs):
            return CursorPrueba()

    @contextmanager
    def transaccion_prueba():
        yield ConexionPrueba()

    avisos = []
    monkeypatch.setattr(
        citas_routes,
        "usuario_actual",
        lambda: {"id_usuario": 9, "rol_nombre": "Acudiente"},
    )
    monkeypatch.setattr(citas_routes, "transaccion", transaccion_prueba)
    monkeypatch.setattr(citas_routes, "validar_disponibilidad", lambda *args: None)
    monkeypatch.setattr(citas_routes, "bloquear_agenda", lambda *args: None)
    monkeypatch.setattr(citas_routes, "comprobar_hueco", lambda *args, **kwargs: None)
    monkeypatch.setattr(citas_routes, "notificar", lambda *args: avisos.append(args))
    monkeypatch.setattr(citas_routes, "auditoria", lambda *args: None)

    fecha_propuesta = (date.today() + timedelta(days=2)).isoformat()
    with app.test_request_context(
        "/citas/5/solicitar-reprogramacion",
        method="POST",
        data={"fecha": fecha_propuesta, "hora": "11:30", "motivo": "No podemos asistir"},
    ):
        respuesta = citas_routes.solicitar_reprogramacion_cita.__wrapped__(5)

    insert = next(
        (params for sql, params in escrituras if "INSERT INTO solicitudes_reprogramacion_cita" in sql),
        None,
    )
    assert respuesta.status_code == 302
    assert insert is not None
    assert insert[:3] == (5, 9, 42)
    assert insert[3:5] == (solicitud_cita["fecha"], solicitud_cita["hora"])
    assert avisos[0][0] == 42


def test_creador_acepta_solicitud_y_actualiza_cita(monkeypatch):
    from datetime import date

    fecha_anterior = date.today() + timedelta(days=1)
    fecha_solicitada = date.today() + timedelta(days=2)
    solicitud = {
        "id": 61,
        "id_cita": 5,
        "solicitante_usuario_id": 9,
        "creador_usuario_id": 7,
        "fecha_anterior": fecha_anterior,
        "hora_anterior": "10:30:00",
        "fecha_solicitada": fecha_solicitada,
        "hora_solicitada": "11:30:00",
        "motivo": "No podemos asistir",
        "estado": "Pendiente",
    }
    cita = {
        "id": 5,
        "id_docente": 1,
        "id_estudiante": 2,
        "id_acudiente": 3,
        "creado_por": 7,
        "estado": "Confirmada",
    }
    escrituras = []

    class CursorPrueba:
        rowcount = 1
        sql = ""

        def execute(self, sql, params=()):
            self.sql = sql
            escrituras.append((sql, params))

        def fetchone(self):
            if "FROM solicitudes_reprogramacion_cita" in self.sql and "FOR UPDATE" in self.sql:
                return solicitud
            if "FROM citas c" in self.sql and "FOR UPDATE" in self.sql:
                return cita
            if "SELECT id FROM estados_cita" in self.sql:
                return {"id": 4}
            return None

        def close(self):
            pass

    class ConexionPrueba:
        def cursor(self, **_kwargs):
            return CursorPrueba()

    @contextmanager
    def transaccion_prueba():
        yield ConexionPrueba()

    avisos = []
    monkeypatch.setattr(
        citas_routes,
        "usuario_actual",
        lambda: {"id_usuario": 7, "rol_nombre": "Rector"},
    )
    monkeypatch.setattr(citas_routes, "transaccion", transaccion_prueba)
    monkeypatch.setattr(citas_routes, "validar_disponibilidad", lambda *args: None)
    monkeypatch.setattr(citas_routes, "bloquear_agenda", lambda *args: None)
    monkeypatch.setattr(citas_routes, "comprobar_hueco", lambda *args, **kwargs: None)
    monkeypatch.setattr(citas_routes, "auditoria", lambda *args: None)
    monkeypatch.setattr(citas_routes, "_notificar", lambda *args: avisos.append(args))
    monkeypatch.setattr(
        "servicios.google_calendar.encolar_cita_cursor",
        lambda *args: None,
    )

    with app.test_request_context(
        "/citas/solicitudes-reprogramacion/61/resolver",
        method="POST",
        data={"accion": "aceptar"},
    ):
        respuesta = citas_routes.resolver_solicitud_reprogramacion.__wrapped__(61)

    actualizacion = next(
        params for sql, params in escrituras if "UPDATE citas" in sql
    )
    assert respuesta.status_code == 302
    assert actualizacion[0] == fecha_solicitada
    assert actualizacion[1].strftime("%H:%M") == "11:30"
    assert actualizacion[2:5] == (4, 5, 7)
    assert any("UPDATE solicitudes_reprogramacion_cita" in sql for sql, _ in escrituras)
    assert avisos[0][0] == 5


def test_crear_cita_movil_aparece_en_calendario_sin_segunda_creacion(monkeypatch):
    fecha = (date.today() + timedelta(days=40)).isoformat()
    usuario = {"id_usuario": 7, "rol_nombre": "Rector"}
    creadas = []
    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(citas_routes, "catalogos", lambda: {})
    monkeypatch.setattr(citas_routes, "consultar", lambda *args, **kwargs: {"id": 1, "id_usuario": 7})
    monkeypatch.setattr(citas_routes, "_cita_horario_ocupado", lambda *args: None)
    monkeypatch.setattr(citas_routes, "_notificar", lambda *args, **kwargs: None)
    monkeypatch.setattr(citas_routes, "auditoria", lambda *args: None)
    def ejecutar(sql, params):
        assert "INSERT INTO citas" in sql
        creadas.append({"id": 901, "fecha": params[6], "hora": params[7], "estudiante": "Prueba", "estado_nombre": "Pendiente"})
        return 901
    monkeypatch.setattr(citas_routes, "reservar_cita", ejecutar)
    monkeypatch.setattr(citas_routes, "validar_disponibilidad", lambda *args: None)
    datos = {"id_estudiante": "1", "id_docente": "1", "id_acudiente": "1", "id_motivo": "1", "id_periodo": "1", "fecha": fecha, "hora": "10:30", "vista_movil": "1"}
    with app.test_request_context("/citas/nueva", method="POST", data=datos):
        response = citas_routes.nueva.__wrapped__()
    assert response.status_code == 302
    assert len(creadas) == 1
    assert urlsplit(response.location).path == "/calendario/"
    monkeypatch.setattr(calendario_routes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(calendario_routes, "citas_visibles", lambda usuario: creadas)
    monkeypatch.setattr(calendario_routes, "consultar", lambda *args, **kwargs: [])
    contexto = {}
    def render_template(template, **kwargs):
        contexto.update(kwargs)
        return "Calendario"
    monkeypatch.setattr(calendario_routes, "render_template", render_template)
    with app.test_request_context(response.location):
        calendario_routes.index.__wrapped__()
    celda = next(dia for semana in contexto["semanas"] for dia in semana if dia["iso"] == fecha)
    assert celda["citas"][0]["id"] == 901
    assert contexto["citas_del_dia"][0]["id"] == 901


@pytest.mark.parametrize("asistencia,resultado", [("Pendiente", "Resultado"), ("Asistió", " "), ("No asistió", "x" * 10001)])
def test_cierre_exige_asistencia_y_resultado(asistencia, resultado):
    with pytest.raises(ValueError):
        _validar_cierre_cita(asistencia, resultado)


@pytest.mark.parametrize("asistencia,estado", [("Asistió", "Realizada"), ("No asistió", "No asistió")])
def test_cierre_usa_transaccion_y_estado_controlado(monkeypatch, asistencia, estado):
    class CursorPrueba:
        rowcount = 1
        def __init__(self):
            self.sql = []
            self.filas = iter([{"id": 5, "id_estado": 2, "estado": "Confirmada"}, {"id": 3}])
            self.cerrado = False
        def execute(self, sql, params):
            self.sql.append((sql, params))
        def fetchone(self):
            return next(self.filas)
        def close(self):
            self.cerrado = True
    cursor = CursorPrueba()
    class ConexionPrueba:
        def cursor(self, **kwargs):
            return cursor
    @contextmanager
    def transaccion_prueba():
        yield ConexionPrueba()
    monkeypatch.setattr(citas_routes, "transaccion", transaccion_prueba)
    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: {"id_usuario": 7, "rol_nombre": "Rector"})
    monkeypatch.setattr(citas_routes, "auditoria", lambda *args: None)
    monkeypatch.setattr(citas_routes, "_notificar", lambda *args: None)
    with app.test_request_context("/citas/5/cerrar", method="POST", data={"asistencia": asistencia, "resultado": "Resultado registrado"}):
        response = citas_routes.cerrar_cita.__wrapped__(5)
    assert response.status_code == 302
    assert "FOR UPDATE" in cursor.sql[0][0]
    assert cursor.sql[2][1] == (5, estado, asistencia, "Resultado registrado", 7)
    assert cursor.sql[3][0].startswith("INSERT INTO cierres_cita")
    assert cursor.sql[4][0].startswith("UPDATE citas")
    assert cursor.cerrado
