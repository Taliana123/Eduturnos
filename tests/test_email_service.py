from unittest.mock import patch
import pytest
import json

from app import app
from servicios import email as email_service
from servicios import asistente as assistant_service


def test_email_requires_six_digit_code():
    with app.app_context():
        app.config.update(MAIL_SERVER="smtp.example.com", MAIL_USERNAME="sender@example.com", MAIL_PASSWORD="app-password", MAIL_DEFAULT_SENDER="sender@example.com")
        for code in ("12345", "1234567", "abcdef"):
            try:
                email_service.enviar_correo_recuperacion("persona@example.com", code)
            except ValueError:
                pass
            else:
                raise AssertionError("El servicio aceptó un código inválido")


def test_email_service_uses_flask_mail():
    with app.app_context():
        app.config.update(
            MAIL_SERVER="smtp.example.com",
            MAIL_USERNAME="sender@example.com",
            MAIL_PASSWORD="app-password",
            MAIL_DEFAULT_SENDER="sender@example.com",
        )
        with patch.object(email_service.mail, "send") as send:
            assert email_service.enviar_correo_recuperacion("persona@example.com", "123456") is True
            mensaje = send.call_args.args[0]
            assert mensaje.sender == "EDUTURNOS <sender@example.com>"
            assert mensaje.recipients == ["persona@example.com"]
            assert "123456" in mensaje.body
            assert 'src="cid:eduturnos-logo"' in mensaje.html
            assert len(mensaje.attachments) == 1
            send.assert_called_once()


def test_support_sends_request_and_receipt_with_safe_html():
    with app.app_context():
        app.config.update(
            MAIL_SERVER="smtp.example.com",
            MAIL_USERNAME="sender@example.com",
            MAIL_PASSWORD="app-password",
            MAIL_DEFAULT_SENDER="sender@example.com",
            SUPPORT_EMAIL="support@example.com",
        )
        with patch.object(email_service.mail, "send") as send:
            email_service.enviar_solicitud_soporte(
                "persona@example.com",
                "Ana <script>",
                "Docente",
                "No puedo abrir el calendario.",
                respuesta_automatica="Revisa tu calendario <script>alert(1)</script>.",
            )
            assert send.call_count == 2
            solicitud, acuse = (call.args[0] for call in send.call_args_list)
            assert solicitud.recipients == ["support@example.com"]
            assert solicitud.reply_to == "persona@example.com"
            assert "&lt;script&gt;" in solicitud.html
            assert "Respuesta automática de EDUBOT" in solicitud.body
            assert acuse.recipients == ["persona@example.com"]
            assert "EDUBOT generó esta respuesta automática" in acuse.body
            assert "&lt;script&gt;" in acuse.html


def test_assistant_answers_common_questions_without_external_api():
    with app.app_context():
        assert "citaciones" in assistant_service.generar_respuesta("¿Cómo solicito una citación?").lower()
        assert "recuperación" in assistant_service.generar_respuesta("Olvidé mi contraseña").lower()


def test_open_assistant_question_reports_when_groq_is_not_configured(monkeypatch):
    monkeypatch.setitem(app.config, "GROQ_API_KEY", "")
    with app.app_context():
        with patch.object(assistant_service, "urlopen", create=True) as open_url:
            with pytest.raises(RuntimeError, match="respuestas abiertas no están activadas"):
                assistant_service.generar_respuesta("¿Cómo configuro un proceso institucional especial?")
        open_url.assert_not_called()


def test_open_assistant_question_uses_groq_and_anonymizes_personal_data(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps(
                {"choices": [{"message": {"content": "Abre Seguimiento desde el menú."}}]}
            ).encode("utf-8")

    monkeypatch.setitem(app.config, "GROQ_API_KEY", "fake-groq-key")
    monkeypatch.setitem(app.config, "GROQ_MODEL", "test-model")
    with app.app_context():
        with patch.object(assistant_service, "urlopen", return_value=FakeResponse()) as open_url:
            answer = assistant_service.generar_respuesta(
                "Profesora Ana Pérez, juan@example.com, documento 1234567890: ¿cómo hago xyz?",
                rol="Docente",
            )

    request = open_url.call_args.args[0]
    payload = json.loads(request.data.decode("utf-8"))
    sent_question = payload["messages"][1]["content"]
    assert answer == "Abre Seguimiento desde el menú."
    assert request.full_url == "https://api.groq.com/openai/v1/chat/completions"
    assert request.get_header("User-agent") == "EDUTURNOS/1.0"
    assert request.get_header("Authorization") == "Bearer fake-groq-key"
    assert "fake-groq-key" not in request.full_url
    assert "juan@example.com" not in sent_question
    assert "Ana Pérez" not in sent_question
    assert "1234567890" not in sent_question
    assert "[correo omitido]" in sent_question
    assert "[número omitido]" in sent_question
    assert "El perfil actual es «Docente»." in payload["messages"][0]["content"]


def test_support_reports_when_receipt_fails_after_request_delivery():
    with app.app_context():
        app.config.update(
            MAIL_SERVER="smtp.example.com",
            MAIL_USERNAME="sender@example.com",
            MAIL_PASSWORD="app-password",
            MAIL_DEFAULT_SENDER="sender@example.com",
            SUPPORT_EMAIL="support@example.com",
        )
        with patch.object(email_service.mail, "send", side_effect=[None, OSError("SMTP unavailable")]) as send:
            try:
                email_service.enviar_solicitud_soporte(
                    "persona@example.com", "Ana", "Docente", "No puedo abrir el calendario."
                )
            except email_service.AcuseSoporteError:
                pass
            else:
                raise AssertionError("El servicio ocultó el fallo al enviar el acuse")
            assert send.call_count == 2
