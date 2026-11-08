import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from app import app
from servicios import avatar


def test_avatar_inicial_es_estable_y_variado_por_usuario():
    first = avatar.avatar_inicial(1)

    assert first == avatar.avatar_inicial(1)
    assert first != avatar.avatar_inicial(2)
    assert set(first) == set(avatar.DEFAULT_AVATAR)


def test_normalizar_avatar_rechaza_opciones_no_permitidas():
    invalid = dict(avatar.DEFAULT_AVATAR, hairColor="url(https://example.invalid/evil.svg)")

    with pytest.raises(ValueError):
        avatar.normalizar_avatar(invalid)

    with pytest.raises(ValueError):
        avatar.normalizar_avatar({**avatar.DEFAULT_AVATAR, "extra": "value"})


def test_avatar_ofrece_mas_peinados_y_acepta_sus_capas():
    hairstyles = {
        option["value"] for option in avatar.AVATAR_CHOICES["hairstyle"]["options"]
    }

    assert {"afro", "braids", "bob", "side-swept"} <= hairstyles
    for hairstyle in hairstyles:
        assert avatar.normalizar_avatar(
            {**avatar.DEFAULT_AVATAR, "hairstyle": hairstyle}
        )["hairstyle"] == hairstyle


def test_obtener_avatar_persiste_una_combinacion_inicial(monkeypatch):
    stored = {}
    writes = []

    def fake_consultar(_sql, params, uno=False):
        assert uno is True
        assert params == (24,)
        return {"avatar_json": stored["avatar_json"]} if stored else None

    def fake_ejecutar(_sql, params):
        writes.append(params)
        stored["avatar_json"] = params[1]
        return 24

    monkeypatch.setattr(avatar, "consultar", fake_consultar)
    monkeypatch.setattr(avatar, "ejecutar", fake_ejecutar)

    first = avatar.obtener_o_crear_avatar(24)
    second = avatar.obtener_o_crear_avatar(24)

    assert first == second == avatar.avatar_inicial(24)
    assert len(writes) == 1
    assert json.loads(writes[0][1]) == first


def test_endpoint_guarda_solo_el_avatar_de_la_cuenta_autenticada(monkeypatch):
    import routes.cuenta as cuenta
    import routes.helpers as helpers
    import app as app_module

    user = {"id_usuario": 57, "rol_nombre": "Docente"}
    saved = []
    monkeypatch.setattr(helpers, "usuario_actual", lambda: user)
    monkeypatch.setattr(cuenta, "usuario_actual", lambda: user)
    monkeypatch.setattr(app_module, "obtener_o_crear_avatar", avatar.avatar_inicial)
    monkeypatch.setattr(
        cuenta,
        "guardar_avatar",
        lambda user_id, value: saved.append((user_id, value)) or value,
    )
    monkeypatch.setitem(app.config, "TESTING", True)
    client = app.test_client()
    token = "avatar-test-token"

    with client.session_transaction() as session:
        session["usuario_id"] = user["id_usuario"]
        session["_csrf_token"] = token

    payload = avatar.avatar_inicial(user["id_usuario"])
    response = client.post(
        "/cuenta/avatar",
        json=payload,
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 200
    assert response.json == {"ok": True, "avatar": payload}
    assert saved == [(user["id_usuario"], payload)]


def test_personalizador_usa_piezas_vectoriales_y_persistencia_de_cuenta():
    sidebar = Path("templates/_desktop_sidebar.html").read_text(encoding="utf-8")
    account = Path("templates/cuenta/index.html").read_text(encoding="utf-8")
    art = Path("templates/_avatar_art.html").read_text(encoding="utf-8")
    script = Path("static/js/avatar-customizer.js").read_text(encoding="utf-8")
    stylesheet = Path("static/css/desktop-sidebar.css").read_text(encoding="utf-8")
    schema = Path("sql/user_avatars.sql").read_text(encoding="utf-8")

    assert 'data-avatar-save-url="{{ url_for(\'cuenta.actualizar_avatar\') }}"' in sidebar
    assert 'data-avatar-choice data-field="{{ field }}"' in sidebar
    assert 'data-avatar-open' in account
    assert "data-avatar-hair" in art
    assert "data-avatar-outfit" in art
    assert "data-avatar-choice" in script
    assert 'method: "POST"' in script
    assert "X-CSRFToken" in script
    assert "avatares_usuario" in schema
    assert "FOREIGN KEY (id_usuario)" in schema
    assert "[data-hairstyle=" in stylesheet
    assert "background-image:url(" not in art
    assert 'data-hairstyle="{{ avatar.hairstyle }}"' in art
    assert 'data-avatar-hair="afro"' in art
    assert 'data-avatar-hair="braids"' in art
    assert 'data-avatar-hair="bob"' in art
    assert 'data-avatar-hair="side-swept"' in art
    assert ".user-avatar-drawing[data-hairstyle=\"afro\"]" in stylesheet


def test_menu_y_mi_cuenta_renderizan_el_avatar_con_sus_opciones():
    from flask import render_template

    user = {
        "id_usuario": 81,
        "rol_nombre": "Docente",
        "nombres": "Ana",
        "apellidos": "Pérez",
        "correo": "ana@example.test",
        "documento": "12345",
    }
    initial = avatar.avatar_inicial(user["id_usuario"])
    with app.test_request_context("/cuenta/"):
        sidebar = render_template(
            "_desktop_sidebar.html",
            usuario_navegacion=user,
            avatar_config=initial,
            avatar_choices=avatar.AVATAR_CHOICES,
        )
        account = render_template(
            "cuenta/index.html",
            usuario=user,
            perfil={},
            avatar_config=initial,
            avatar_choices=avatar.AVATAR_CHOICES,
            puede_configurar=False,
        )

    assert 'data-avatar-save-url="/cuenta/avatar"' in sidebar
    assert sidebar.count("data-avatar-choice") == sum(
        len(group["options"]) for group in avatar.AVATAR_CHOICES.values()
    )
    svg = re.search(r'<svg viewBox="0 0 120 144".*?</svg>', sidebar, re.DOTALL)
    assert svg is not None
    ET.fromstring(svg.group(0))
    assert 'data-avatar-open' in account
    assert 'class="cuenta-avatar-preview"' in account
    assert 'data-hairstyle="short"' in sidebar
    assert f'style="--avatar-hair:{initial["hairColor"]};' in sidebar
