from unittest.mock import patch

from app import app
from servicios import email as email_service


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
            assert mensaje.sender == "sender@example.com"
            assert mensaje.recipients == ["persona@example.com"]
            assert "123456" in mensaje.body
            send.assert_called_once()
