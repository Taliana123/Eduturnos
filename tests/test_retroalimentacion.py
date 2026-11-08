import pytest

import app as app_module
from routes import helpers, retroalimentacion
from servicios.avatar import avatar_inicial


def _client(monkeypatch, usuario):
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(retroalimentacion, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(
        app_module,
        "obtener_o_crear_avatar",
        lambda id_usuario: avatar_inicial(id_usuario),
    )
    client = app_module.app.test_client()
    with client.session_transaction() as sesion:
        sesion["usuario_id"] = usuario["id_usuario"]
        sesion["_csrf_token"] = "retro-csrf"
    return client


@pytest.mark.parametrize("rol", ["Docente", "Estudiante", "Acudiente"])
def test_usuarios_autorizados_ven_el_formulario_y_el_acceso_bajo_compartir(
    monkeypatch, rol
):
    usuario = {
        "id_usuario": 42,
        "id_institucion": 8,
        "rol_nombre": rol,
        "nombres": "Ana",
        "apellidos": "Pérez",
    }
    monkeypatch.setattr(retroalimentacion, "consultar", lambda *args, **kwargs: [])

    respuesta = _client(monkeypatch, usuario).get("/retroalimentacion/")

    assert respuesta.status_code == 200
    html = respuesta.get_data(as_text=True)
    assert "Quejas, reseñas y mejoras" in html
    assert "Tu comentario lo recibirán Rectoría y Coordinación" in html
    navegacion = html.split('<nav aria-label="Funciones de', 1)[1].split("</nav>", 1)[0]
    assert navegacion.index('href="/compartir"') < navegacion.index(
        'href="/retroalimentacion/"'
    )


def test_envio_guarda_categoria_y_contenido_con_la_institucion(monkeypatch):
    usuario = {
        "id_usuario": 42,
        "id_institucion": 8,
        "rol_nombre": "Estudiante",
        "nombres": "Ana",
        "apellidos": "Pérez",
    }
    inserciones = []
    monkeypatch.setattr(
        retroalimentacion,
        "ejecutar",
        lambda sql, params: inserciones.append((sql, params)),
    )

    respuesta = _client(monkeypatch, usuario).post(
        "/retroalimentacion/",
        data={
            "csrf_token": "retro-csrf",
            "tipo": "Idea de mejora",
            "asunto": "Mejorar el calendario",
            "comentario": "Sería útil ver la semana completa.",
        },
    )

    assert respuesta.status_code == 302
    assert respuesta.location.endswith("/retroalimentacion/")
    assert inserciones[0][1] == (
        42,
        8,
        "Idea de mejora",
        "Mejorar el calendario",
        "Sería útil ver la semana completa.",
    )


def test_envio_rechaza_datos_invalidos_sin_escribir(monkeypatch):
    usuario = {
        "id_usuario": 42,
        "id_institucion": 8,
        "rol_nombre": "Docente",
        "nombres": "Ana",
        "apellidos": "Pérez",
    }
    monkeypatch.setattr(
        retroalimentacion,
        "ejecutar",
        lambda *args: pytest.fail("No debe guardar una categoría inválida."),
    )
    monkeypatch.setattr(retroalimentacion, "consultar", lambda *args, **kwargs: [])

    respuesta = _client(monkeypatch, usuario).post(
        "/retroalimentacion/",
        data={
            "csrf_token": "retro-csrf",
            "tipo": "Otra categoría",
            "asunto": "Asunto",
            "comentario": "Comentario",
        },
    )

    assert respuesta.status_code == 200
    assert "Selecciona una categoría válida" in respuesta.get_data(as_text=True)


def test_envio_exige_csrf(monkeypatch):
    usuario = {
        "id_usuario": 42,
        "id_institucion": 8,
        "rol_nombre": "Docente",
        "nombres": "Ana",
        "apellidos": "Pérez",
    }
    monkeypatch.setattr(
        retroalimentacion,
        "ejecutar",
        lambda *args: pytest.fail("No debe guardar un POST sin CSRF."),
    )

    respuesta = _client(monkeypatch, usuario).post(
        "/retroalimentacion/",
        data={"tipo": "Queja", "asunto": "Asunto", "comentario": "Comentario"},
    )

    assert respuesta.status_code == 400


def test_inbox_solo_es_visible_para_rector_y_coordinacion(monkeypatch):
    usuario = {
        "id_usuario": 42,
        "id_institucion": 8,
        "rol_nombre": "Estudiante",
        "nombres": "Ana",
        "apellidos": "Pérez",
    }

    respuesta = _client(monkeypatch, usuario).get(
        "/retroalimentacion/administrar"
    )

    assert respuesta.status_code == 403


def test_actualizacion_de_estado_se_limita_a_la_institucion(monkeypatch):
    usuario = {
        "id_usuario": 7,
        "id_institucion": 8,
        "rol_nombre": "Rector",
        "nombres": "Rosa",
        "apellidos": "López",
    }
    consultas = []
    escrituras = []

    def consultar(sql, params, uno=False):
        consultas.append((sql, params, uno))
        return {"id": 15}

    monkeypatch.setattr(retroalimentacion, "consultar", consultar)
    monkeypatch.setattr(
        retroalimentacion,
        "ejecutar",
        lambda sql, params: escrituras.append((sql, params)),
    )

    respuesta = _client(monkeypatch, usuario).post(
        "/retroalimentacion/administrar",
        data={
            "csrf_token": "retro-csrf",
            "id_comentario": "15",
            "estado": "En revisión",
        },
    )

    assert respuesta.status_code == 302
    assert consultas[0][1] == (15, 8)
    assert "id_institucion=%s" in consultas[0][0]
    assert escrituras[0][1] == ("En revisión", 15, 8)
    assert "id_institucion=%s" in escrituras[0][0]
