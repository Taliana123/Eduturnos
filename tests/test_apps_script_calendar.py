import hashlib
import hmac
import json
from datetime import date, time, timedelta
from urllib.error import HTTPError

import pytest

from app import app
from servicios import google_calendar


def test_apps_script_bridge_requires_https_exec_url_and_long_secret(monkeypatch):
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_URL", "https://script.google.com/macros/s/test-id/exec")
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_SECRET", "s" * 32)
    with app.app_context():
        assert google_calendar.apps_script_configurada()
        assert google_calendar.configuracion_lista()

    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_URL", "https://example.com/exec")
    with app.app_context():
        assert not google_calendar.apps_script_configurada()


def test_apps_script_request_signs_payload_without_exposing_secret(monkeypatch):
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_URL", "https://script.google.com/macros/s/test-id/exec")
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_SECRET", "secret-for-test-only-" + "x" * 32)
    requests = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"ok":true,"protocol":"payload-json-v2"}'

    def fake_urlopen(request, timeout):
        requests.append((request, timeout))
        return Response()

    monkeypatch.setattr(google_calendar, "urlopen", fake_urlopen)
    payload = {"action": "test", "calendar": "Agenda", "location": "Ibagué · Sede 🌳"}
    with app.app_context():
        assert google_calendar._solicitud_apps_script(payload) == {"ok": True, "protocol": "payload-json-v2"}

    request, timeout = requests[0]
    envelope = json.loads(request.data.decode("utf-8"))
    canonical = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    assert envelope["payload_json"] == canonical
    assert envelope["payload_json"].isascii()
    message = f"{envelope['timestamp']}\n{envelope['nonce']}\n{canonical}".encode("utf-8")
    expected = hmac.new(app.config["GOOGLE_APPS_SCRIPT_SECRET"].encode(), message, hashlib.sha256).digest()
    import base64

    assert envelope["signature"] == base64.urlsafe_b64encode(expected).decode().rstrip("=")
    assert "GOOGLE_APPS_SCRIPT_SECRET" not in request.data.decode("utf-8")
    assert timeout == 20


def test_apps_script_http_401_explains_anonymous_web_app_access(monkeypatch):
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_URL", "https://script.google.com/macros/s/test-id/exec")
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_SECRET", "s" * 32)

    def unauthorized(request, timeout):
        raise HTTPError(request.full_url, 401, "Unauthorized", None, None)

    monkeypatch.setattr(google_calendar, "urlopen", unauthorized)
    with app.app_context(), pytest.raises(google_calendar.GoogleCalendarError) as error:
        google_calendar._solicitud_apps_script({"action": "test"})

    assert error.value.status == 401
    assert "Cualquier persona" in str(error.value)


def test_apps_script_probe_requires_payload_json_protocol(monkeypatch):
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_URL", "https://script.google.com/macros/s/test-id/exec")
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_SECRET", "s" * 32)
    monkeypatch.setattr(google_calendar, "_solicitud_apps_script", lambda payload: {"ok": True})

    with app.app_context(), pytest.raises(google_calendar.GoogleCalendarError, match="Actualiza y vuelve a implementar"):
        google_calendar.probar_apps_script()


def test_apps_script_config_enqueues_institutional_calendar_without_user_connection(monkeypatch):
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_URL", "https://script.google.com/macros/s/test-id/exec")
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_SECRET", "s" * 32)
    monkeypatch.setitem(app.config, "GOOGLE_OAUTH_CLIENT_ID", "")
    monkeypatch.setitem(app.config, "GOOGLE_OAUTH_CLIENT_SECRET", "")
    monkeypatch.setitem(app.config, "APP_ORIGIN", "")
    statements = []

    class Cursor:
        def execute(self, sql, params=()):
            statements.append((sql, params))

        def fetchall(self):
            return []

        def fetchone(self):
            return None

    with app.app_context():
        cantidad = google_calendar.encolar_cita_cursor(Cursor(), 91, 10)

    assert cantidad == 1
    assert any("INSERT INTO google_calendar_sync_queue" in sql for sql, _ in statements)
    assert any("institucional" in params for _, params in statements)


def test_apps_script_worker_sends_generic_event_and_records_id(monkeypatch):
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_URL", "https://script.google.com/macros/s/test-id/exec")
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_SECRET", "s" * 32)
    monkeypatch.setitem(app.config, "APP_ORIGIN", "https://eduturnos.example")
    monkeypatch.setattr(google_calendar, "apps_script_configurada", lambda: True)
    cita = {
        "id": 91,
        "fecha": date(2026, 11, 2),
        "hora": time(9, 30),
        "lugar": "Sede Central",
        "sede": "Sede Central",
        "estado": "Pendiente",
    }
    monkeypatch.setattr(google_calendar, "consultar", lambda *args, **kwargs: cita)
    payloads = []
    monkeypatch.setattr(
        google_calendar,
        "_solicitud_apps_script",
        lambda payload: payloads.append(payload) or {"ok": True, "eventId": "google-event-id"},
    )
    writes = []
    monkeypatch.setattr(google_calendar, "ejecutar", lambda sql, params=(): writes.append((sql, params)))

    with app.app_context():
        google_calendar._procesar_tarea_google({
            "id_cita": 91,
            "scope_key": "institucional",
            "operacion": "upsert",
            "google_event_id": "stable-event-id",
        })

    assert payloads[0]["title"] == "Citación escolar"
    assert payloads[0]["start"].endswith("-05:00")
    assert payloads[0]["description"] == (
        "Consulta los detalles de la cita en EDUTURNOS.\nhttps://eduturnos.example/citas/"
    )
    assert "estudiante" not in json.dumps(payloads[0], ensure_ascii=False).lower()
    assert writes[0][1] == (91, "institucional", "google-event-id")


def test_calendar_event_description_links_only_to_configured_https_eduturnos(monkeypatch):
    monkeypatch.setitem(app.config, "APP_ORIGIN", "https://eduturnos.example")
    with app.app_context():
        assert google_calendar._descripcion_evento_cita() == (
            "Consulta los detalles de la cita en EDUTURNOS.\nhttps://eduturnos.example/citas/"
        )

    monkeypatch.setitem(app.config, "APP_ORIGIN", "http://insecure.example")
    with app.app_context():
        assert google_calendar._descripcion_evento_cita() == (
            "Consulta los detalles de la cita en EDUTURNOS."
        )


def test_apps_script_source_sets_two_popup_reminders():
    from pathlib import Path

    source = Path("integrations/google_apps_script/EDUTURNOSCalendar.gs").read_text(encoding="utf-8")
    assert "const EDUTURNOS_PROTOCOL = 'payload-json-v2'" in source
    assert "const payloadJson = typeof envelope.payload_json" in source
    assert "const canonicalPayload = payloadJson || canonical_(envelope.payload)" in source
    assert "event.addPopupReminder(1440)" in source
    assert "event.addPopupReminder(120)" in source
    assert "event.setTag(EDUTURNOS_TAG, payload.external_id)" in source


def test_integrations_page_offers_eduturnos_calendar_to_every_role():
    from pathlib import Path
    from routes.integraciones_google import _url_abrir_calendario

    source = Path("templates/integraciones_google.html").read_text(encoding="utf-8")
    route_source = Path("routes/integraciones_google.py").read_text(encoding="utf-8")
    assert "package=com.google.android.calendar;end" in route_source
    assert "S.browser_fallback_url" not in route_source
    assert "Abrir Google Calendar" in source
    assert "Se intentará abrir la aplicación" in source
    assert "No hay una cita futura sincronizada" not in source
    assert "{% if calendar_open_url %}" not in source
    assert "EDUTURNOS conserva la información oficial" in source
    assert source.index("Sincronizar citas futuras") < source.index("Abrir Google Calendar")
    assert source.count("<h2>Agenda") == 1
    assert "google-calendar-actions" in source
    assert "{% if institucional_sync and institucional_sync.fallidas" in source
    assert "<script>" not in source
    assert "Reintentar citas fallidas" in source
    assert "{% if usuario.rol_nombre in ['Estudiante','Acudiente'] %}" not in source
    with app.test_request_context(headers={"User-Agent": "Mozilla/5.0 (Linux; Android 14)"}):
        intent_url = _url_abrir_calendario(1793328513689)
        assert intent_url.startswith(
            "intent://com.android.calendar/time/1793328513689"
            "#Intent;scheme=content;action=android.intent.action.VIEW;"
            "type=time/epoch;"
            "component=com.google.android.calendar/com.android.calendar.AllInOneActivity;"
        )
        assert (
            "component=com.google.android.calendar/com.android.calendar.AllInOneActivity;"
            in intent_url
        )
        assert intent_url.endswith("package=com.google.android.calendar;end")
        assert "S.browser_fallback_url" not in intent_url
    with app.test_request_context(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0)"}):
        assert _url_abrir_calendario(1793328513689).startswith("https://calendar.google.com/calendar/u/0/r/day/")
    with app.test_request_context(headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}):
        assert _url_abrir_calendario(1793328513689) == "googlecalendar://"


def test_android_synced_event_intent_targets_google_calendar_without_web_fallback(monkeypatch):
    from routes import integraciones_google

    monkeypatch.setattr(integraciones_google, "apps_script_configurada", lambda: True)
    monkeypatch.setattr(
        integraciones_google,
        "consultar",
        lambda *args, **kwargs: {
            "google_event_id": "stored-event-id",
            "scope_key": "institucional",
        },
    )
    monkeypatch.setattr(
        integraciones_google,
        "enlace_evento_apps_script",
        lambda event_id: "https://www.google.com/calendar/event?eid=abc_DEF-123",
    )

    with app.test_request_context(headers={"User-Agent": "Mozilla/5.0 (Linux; Android 14)"}):
        intent_url = integraciones_google._url_app_cita({"id": 91}, android=True)

    assert intent_url.startswith(
        "intent://www.google.com/calendar/event?eid=abc_DEF-123"
        "#Intent;scheme=https;action=android.intent.action.VIEW;"
        "component=com.google.android.calendar/com.android.calendar.AllInOneActivity;"
    )
    assert (
        "component=com.google.android.calendar/com.android.calendar.AllInOneActivity;"
        in intent_url
    )
    assert intent_url.endswith("package=com.google.android.calendar;end")
    assert "S.browser_fallback_url" not in intent_url

    ios_url = integraciones_google._url_app_cita({"id": 91}, android=False, ios=True)
    assert ios_url == "googlecalendar://"


def test_android_synced_personal_event_opens_that_specific_google_event(monkeypatch):
    import base64
    from urllib.parse import parse_qs, urlsplit
    from routes import integraciones_google

    monkeypatch.setattr(integraciones_google, "_scope_institucional", lambda _usuario: "institucion:7")
    monkeypatch.setattr(integraciones_google, "apps_script_configurada", lambda: False)

    queries = []

    def find_event(sql, params=(), uno=False):
        queries.append((sql, params, uno))
        return {
            "google_event_id": "eduturnos-personal-event",
            "scope_key": "usuario:12",
            "calendar_id": "primary",
            "correo_google": "docente@example.com",
        }

    monkeypatch.setattr(
        integraciones_google,
        "consultar",
        find_event,
    )
    usuario = {"id_usuario": 12, "rol_nombre": "Docente", "id_institucion": 7}
    cita = {"id": 91}

    with app.test_request_context(headers={"User-Agent": "Mozilla/5.0 (Linux; Android 14)"}):
        event_url = integraciones_google._url_evento_app_cita(cita, usuario)
        intent_url = integraciones_google._url_app_cita(
            cita, android=True, evento_url=event_url, usuario=usuario
        )

    encoded_intent_eid = parse_qs(urlsplit(intent_url).query)["eid"][0]
    encoded_eid = parse_qs(urlsplit(event_url).query)["eid"][0]
    decoded_eid = base64.urlsafe_b64decode(encoded_eid + "=" * (-len(encoded_eid) % 4)).decode()
    assert queries[0][1] == (91, "usuario:12", "institucion:7", "usuario:12")
    assert queries[0][2]
    assert decoded_eid == "eduturnos-personal-event docente@example.com"
    assert encoded_intent_eid == encoded_eid
    assert intent_url.startswith(
        f"intent://www.google.com/calendar/event?eid={encoded_eid}"
        "#Intent;scheme=https;action=android.intent.action.VIEW;"
        "component=com.google.android.calendar/com.android.calendar.AllInOneActivity;"
    )


def test_next_synced_appointment_prefers_personal_google_calendar_event(monkeypatch):
    from routes import calendario, integraciones_google

    tomorrow = date.today() + timedelta(days=1)
    cita_sincronizada = {"id": 92, "fecha": tomorrow, "hora": time(9, 0)}
    cita_sin_sincronizar = {"id": 91, "fecha": tomorrow, "hora": time(8, 0)}
    usuario = {"id_usuario": 12, "rol_nombre": "Docente", "id_institucion": 7}
    monkeypatch.setattr(
        calendario,
        "citas_visibles",
        lambda _usuario: [cita_sin_sincronizar, cita_sincronizada],
    )
    monkeypatch.setattr(
        integraciones_google,
        "_evento_sincronizado_cita",
        lambda cita, _usuario: {"scope_key": "usuario:12"} if cita["id"] == 92 else None,
    )
    monkeypatch.setattr(
        integraciones_google,
        "_scope_institucional",
        lambda _usuario: "institucion:7",
    )

    monkeypatch.setattr(
        integraciones_google,
        "consultar",
        lambda *_args, **_kwargs: [{
            "id_cita": 92,
            "google_event_id": "personal-event",
            "scope_key": "usuario:12",
            "calendar_id": "primary",
            "correo_google": "docente@example.com",
        }],
    )
    cita, _inicio_ms, evento = integraciones_google._proxima_cita(
        usuario, solo_sincronizadas=True
    )

    assert cita == cita_sincronizada
    assert evento["google_event_id"] == "personal-event"
