import json
from pathlib import Path

import pytest

from app import app
from servicios import avatar


ROOT = Path(__file__).resolve().parents[1]


def test_avatar_inicial_es_estable_y_variado_por_usuario():
    first = avatar.avatar_inicial(1)

    assert first == avatar.avatar_inicial(1)
    assert first != avatar.avatar_inicial(2)
    assert set(first) == avatar.AVATAR_FIELDS
    assert first["seed"] == "eduturnos-1"
    assert first["gender"] is None
    assert first["selections"] == {}
    assert first["background"] == "transparent"


def test_normalizar_avatar_acepta_solo_partes_y_colores_humation():
    catalog = json.loads((ROOT / "static" / "vendor" / "humation-parts.json").read_text(encoding="utf-8"))
    valid = avatar.avatar_inicial(5)
    valid["selections"] = {"head": catalog["head"][0]["id"], "glasses": catalog["glasses"][0]["id"]}
    assert avatar.normalizar_avatar(valid) == valid
    valid["gender"] = "nina"
    assert avatar.normalizar_avatar(valid) == valid
    with pytest.raises(ValueError, match="género"):
        avatar.normalizar_avatar({**valid, "gender": "otro"})
    assert avatar.normalizar_avatar({key: value for key, value in valid.items() if key != "gender"})["gender"] is None

    invalid_part = {**valid, "selections": {"head": "not-an-official-part"}}
    with pytest.raises(ValueError, match="catálogo oficial"):
        avatar.normalizar_avatar(invalid_part)

    invalid_color = {**valid, "colors": {"hair": "url(https://example.invalid/avatar.svg)"}}
    with pytest.raises(ValueError, match="color"):
        avatar.normalizar_avatar(invalid_color)

    with pytest.raises(ValueError, match="formato esperado"):
        avatar.normalizar_avatar({**valid, "unexpected": True})


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


def test_obtener_avatar_migra_configuracion_anterior_sin_perder_colores(monkeypatch):
    legacy = {
        "character": "neutral",
        "ageStyle": "teen",
        "hairstyle": "curly",
        "hairColor": "#69432f",
        "skinColor": "#efc19a",
        "eyeColor": "#493124",
        "outfit": "hoodie",
        "shirtColor": "#2875c7",
        "accessory": "glasses",
    }
    stored = {"avatar_json": json.dumps(legacy)}
    writes = []

    def fake_consultar(_sql, _params, uno=False):
        assert uno is True
        return stored

    def fake_ejecutar(_sql, params):
        writes.append(params)
        stored["avatar_json"] = params[0]

    monkeypatch.setattr(avatar, "consultar", fake_consultar)
    monkeypatch.setattr(avatar, "ejecutar", fake_ejecutar)
    migrated = avatar.obtener_o_crear_avatar(24)

    assert migrated["seed"] == "eduturnos-24"
    assert migrated["colors"]["hair"] == "#69432F"
    assert migrated["colors"]["skin"] == "#EFC19A"
    assert migrated["colors"]["clothes"] == "#2875C7"
    assert len(writes) == 1


def test_endpoint_guarda_solo_el_avatar_de_la_cuenta_autenticada(monkeypatch):
    import app as app_module
    import routes.cuenta as cuenta
    import routes.helpers as helpers

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


def test_personalizador_usa_renderizador_y_catalogo_oficiales():
    sidebar = (ROOT / "templates" / "_desktop_sidebar.html").read_text(encoding="utf-8")
    account = (ROOT / "templates" / "cuenta" / "index.html").read_text(encoding="utf-8")
    art = (ROOT / "templates" / "_avatar_art.html").read_text(encoding="utf-8")
    source = (ROOT / "tools" / "humation" / "src.js").read_text(encoding="utf-8")
    base = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    license_text = (ROOT / "static" / "vendor" / "HUMATION-LICENSE.md").read_text(encoding="utf-8")

    assert "@humation/core" in source
    assert "@humation/assets-humation-1" in source
    assert "getPartsForSlot(humation1, slot)" in source
    assert "createAvatar(humation1" in source
    assert 'filename=\'js/humation-avatar.js\'' in base
    assert "data-avatar-image" in art
    assert "data-avatar-user" in sidebar
    assert 'data-avatar-open' in account
    assert "data-avatar-cancel" in sidebar
    assert "avatar-category-list" in source
    assert "avatar-category-panel" in source
    assert "discardChanges();" in source
    assert "data-avatar-randomize" not in sidebar
    assert "data-avatar-randomize" not in source
    assert 'mujer: { head: "hm1-p-000024", body: "hm1-p-000030", bottom: "hm1-p-000036" }' in source
    assert 'hombre: { head: "hm1-p-000003", body: "hm1-p-000028", bottom: "hm1-p-000034" }' in source
    assert 'nina: { head: "hm1-p-000016", body: "hm1-p-000025", bottom: "hm1-p-000037" }' in source
    assert 'nino: { head: "hm1-p-000007", body: "hm1-p-000032", bottom: "hm1-p-000033" }' in source
    assert "selections: { ...currentState.selections, ...genderPresets[gender] }" in source
    assert '["nina", "Niña"]' in source
    assert "Copyright (c) 2026 Humation contributors" in license_text
    assert not (ROOT / "static" / "js" / "avatar-customizer.js").exists()


def test_menu_y_mi_cuenta_renderizan_las_imagenes_de_avatar():
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
        )
        account = render_template(
            "cuenta/index.html",
            usuario=user,
            perfil={},
            avatar_config=initial,
            puede_configurar=False,
        )

    assert 'data-avatar-save-url="/cuenta/avatar"' in sidebar
    assert sidebar.count("data-avatar-image") == 1
    assert 'data-avatar-preview-image' in sidebar
    assert 'class="desktop-sidebar-account-avatar" aria-hidden="true"' in sidebar
    assert 'data-avatar-open' not in sidebar
    assert 'data-avatar-image' in account
    assert "eduturnos-81" in json.dumps(initial)
