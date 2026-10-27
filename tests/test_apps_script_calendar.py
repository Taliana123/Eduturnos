import hashlib
import hmac
import json
from datetime import date, time
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
    monkeypatch.setattr(google_calendar, "apps_script_configurada", lambda: True)
    cita = {
        "id": 91,
        "fecha": date(2026, 11, 2),
        "hora": time(9, 30),
        "lugar": "Sede Central",
        "sede": "Sede Central",
        "estado": "Pendiente",
    }
    monkeypatch.setattr(
        google_calendar,
        "consultar",
        lambda *args, **kwargs: [] if "cita_participantes" in str(args[0]) else cita,
    )
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
    assert "estudiante" not in json.dumps(payloads[0], ensure_ascii=False).lower()
    assert writes[0][1] == (91, "institucional", "google-event-id")


def test_apps_script_worker_invites_registered_citation_participants(monkeypatch):
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_URL", "https://script.google.com/macros/s/test-id/exec")
    monkeypatch.setitem(app.config, "GOOGLE_APPS_SCRIPT_SECRET", "s" * 32)
    monkeypatch.setattr(google_calendar, "apps_script_configurada", lambda: True)
    cita = {
        "id": 92, "fecha": date(2026, 11, 2), "hora": time(9, 30), "lugar": "Sede",
        "sede": "Sede", "estado": "Pendiente", "estudiante_correo": "student@example.com",
        "acudiente_correo": "guardian@example.com", "docente_correo": None,
        "destinatario_correo": "rector@example.com", "creador_correo": "teacher@example.com",
    }
    monkeypatch.setattr(
        google_calendar,
        "consultar",
        lambda sql, *args, **kwargs: ([{"correo": "coordinator@example.com"}] if "cita_participantes" in sql else cita),
    )
    payloads = []
    monkeypatch.setattr(google_calendar, "_solicitud_apps_script", lambda payload: payloads.append(payload) or {"ok": True, "eventId": "event-92"})
    monkeypatch.setattr(google_calendar, "ejecutar", lambda *args, **kwargs: None)

    with app.app_context():
        google_calendar._procesar_tarea_google({
            "id_cita": 92, "scope_key": "institucional", "operacion": "upsert", "google_event_id": None,
        })

    assert payloads[0]["attendees"] == [
        "coordinator@example.com", "guardian@example.com", "rector@example.com", "student@example.com", "teacher@example.com",
    ]
    assert "student@example.com" not in payloads[0]["description"]


def test_apps_script_source_sets_two_popup_reminders():
    from pathlib import Path

    source = Path("integrations/google_apps_script/EDUTURNOSCalendar.gs").read_text(encoding="utf-8")
    assert "const EDUTURNOS_PROTOCOL = 'payload-json-v2'" in source
    assert "const payloadJson = typeof envelope.payload_json" in source
    assert "const canonicalPayload = payloadJson || canonical_(envelope.payload)" in source
    assert "{ method: 'popup', minutes: 1440 }" in source
    assert "{ method: 'popup', minutes: 120 }" in source
    assert "sendUpdates: 'all'" in source
    assert "event.setTag(EDUTURNOS_TAG, payload.external_id)" in source


def test_integrations_page_offers_eduturnos_calendar_to_every_role():
    from pathlib import Path

    source = Path("templates/integraciones_google.html").read_text(encoding="utf-8")
    assert "https://calendar.google.com/calendar/u/0/r/month" in source
    assert "intent://calendar.google.com" not in source
    assert "S.browser_fallback_url" not in source
    assert "Abrir app de Google Calendar" in source
    assert "Al crear, cambiar o cancelar una cita en EDUTURNOS" in source
    assert source.count("<h2>Agenda") == 1
    assert "google-calendar-actions" in source
    assert "{% if institucional_sync and institucional_sync.fallidas" in source
    assert "<script>" not in source
    assert "Reintentar citas fallidas" in source
    assert "{% if usuario.rol_nombre in ['Estudiante','Acudiente'] %}" not in source
