from __future__ import annotations

import html

from flask import current_app
from flask_mail import Message

from servicios.mail import mail


def correo_configurado() -> bool:
    """Comprueba si EDUTURNOS tiene configurado un remitente SMTP."""
    return bool(
        current_app.config.get("MAIL_SERVER")
        and current_app.config.get("MAIL_USERNAME")
        and current_app.config.get("MAIL_PASSWORD")
        and current_app.config.get("MAIL_DEFAULT_SENDER")
    )


def enviar_correo_recuperacion(destinatario: str, codigo: str) -> bool:
    """
    Envía únicamente el código de recuperación.

    El código no se incluye en la URL ni se escribe en los logs.
    """
    destinatario = (destinatario or "").strip()

    if not destinatario:
        raise ValueError("El destinatario está vacío.")

    if len(codigo) != 6 or not codigo.isdigit():
        raise ValueError("El código de recuperación no es válido.")

    if not correo_configurado():
        raise RuntimeError("El correo de EDUTURNOS no está configurado.")

    safe_code = html.escape(codigo)

    mensaje = Message(
        subject="Código de recuperación · EDUTURNOS",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[destinatario],
    )

    mensaje.body = (
        "EDUTURNOS\n\n"
        "Recibimos una solicitud para recuperar el acceso a tu cuenta.\n\n"
        f"Tu código de recuperación es: {codigo}\n\n"
        "Este código vence en 10 minutos y solo puede utilizarse una vez.\n"
        "Si tú no solicitaste recuperar el acceso, ignora este mensaje."
    )

    mensaje.html = f"""
    <!doctype html>
    <html lang="es">
    <head><meta charset="utf-8"><title>Recuperación de acceso · EDUTURNOS</title></head>
    <body style="font-family:Arial,sans-serif;line-height:1.6;color:#1f2937">
        <h2>EDUTURNOS</h2>
        <p>Recibimos una solicitud para recuperar el acceso a tu cuenta.</p>
        <p>Tu código de recuperación es:</p>
        <p style="font-size:30px;font-weight:700;letter-spacing:6px">{safe_code}</p>
        <p>Este código vence en <strong>10 minutos</strong> y solo puede utilizarse una vez.</p>
        <p>Si tú no solicitaste recuperar el acceso, puedes ignorar este mensaje.</p>
    </body>
    </html>
    """

    try:
        mail.send(mensaje)
        current_app.logger.info("Correo de recuperación enviado correctamente.")
        return True
    except Exception:
        current_app.logger.exception("No se pudo enviar el correo de recuperación.")
        raise
