from __future__ import annotations

import html
import re
from pathlib import Path

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
        sender=("EDUTURNOS", current_app.config["MAIL_DEFAULT_SENDER"]),
        recipients=[destinatario],
    )

    mensaje.body = (
        "EDUTURNOS\n\n"
        "Recibimos una solicitud para recuperar el acceso a tu cuenta.\n\n"
        f"Tu código de recuperación es: {codigo}\n\n"
        "Este código vence en 10 minutos y solo puede utilizarse una vez.\n"
        "Si tú no solicitaste recuperar el acceso, ignora este mensaje."
    )
    logo_path = Path(current_app.root_path) / "static" / "icons" / "colegio-logo.png"
    mensaje.attach(
        filename="logo-eduturnos.png",
        content_type="image/png",
        data=logo_path.read_bytes(),
        disposition="inline",
        headers={"Content-ID": "<eduturnos-logo>"},
    )

    mensaje.html = f"""
    <!doctype html>
    <html lang="es">
    <head><meta charset="utf-8"><title>Recuperación de acceso · EDUTURNOS</title></head>
    <body style="font-family:Arial,sans-serif;line-height:1.6;color:#1f2937">
        <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 16px">
            <tr>
                <td style="vertical-align:middle;padding-right:12px">
                    <img src="cid:eduturnos-logo" width="48" height="48" alt="Logo institucional" style="display:block;width:48px;height:48px;object-fit:contain">
                </td>
                <td style="vertical-align:middle">
                    <h2 style="margin:0;color:#172942">EDUTURNOS</h2>
                </td>
            </tr>
        </table>
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


class AcuseSoporteError(RuntimeError):
    """El correo llegó al buzón de soporte, pero no se pudo enviar el acuse."""


def enviar_solicitud_soporte(
    destinatario: str,
    nombre: str,
    rol: str,
    detalle: str,
    respuesta_automatica: str | None = None,
) -> None:
    destinatario = (destinatario or "").strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", destinatario):
        raise ValueError("El correo de respuesta no es válido.")
    if not correo_configurado():
        raise RuntimeError("El correo de EDUTURNOS no está configurado.")
    soporte = (current_app.config.get("SUPPORT_EMAIL") or "").strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", soporte):
        raise RuntimeError("El buzón de soporte de EDUTURNOS no está configurado.")

    safe_name = html.escape(nombre)
    safe_role = html.escape(rol)
    safe_detail = html.escape(detalle)
    safe_answer = html.escape(respuesta_automatica or "")
    mensaje_soporte = Message(
        subject="Solicitud de ayuda · EDUTURNOS",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[soporte],
        reply_to=destinatario,
    )
    mensaje_soporte.body = (
        "Solicitud de ayuda recibida desde EDUTURNOS.\n\n"
        f"Usuario: {nombre}\nRol: {rol}\nCorreo para responder: {destinatario}\n\n"
        f"Mensaje:\n{detalle}"
        + (f"\n\nRespuesta automática de EDUBOT:\n{respuesta_automatica}" if respuesta_automatica else "")
    )
    mensaje_soporte.html = (
        '<!doctype html><html lang="es"><meta charset="utf-8"><body '
        'style="font-family:Arial,sans-serif;line-height:1.6;color:#1f2937">'
        "<h2>Solicitud de ayuda · EDUTURNOS</h2>"
        f"<p><strong>Usuario:</strong> {safe_name}<br>"
        f"<strong>Rol:</strong> {safe_role}<br>"
        f"<strong>Correo:</strong> {html.escape(destinatario)}</p>"
        f"<p><strong>Mensaje:</strong><br>{safe_detail.replace(chr(10), '<br>')}</p>"
        + (
            f"<p><strong>Respuesta automática de EDUBOT:</strong><br>{safe_answer.replace(chr(10), '<br>')}</p>"
            if respuesta_automatica else ""
        )
        + "</body></html>"
    )

    try:
        mail.send(mensaje_soporte)
    except Exception:
        current_app.logger.exception("No se pudo enviar la solicitud al buzón de soporte.")
        raise

    acuse = Message(
        subject="Recibimos tu mensaje · EDUTURNOS",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[destinatario],
    )
    acuse.body = (
        f"Hola {nombre},\n\n"
        "EDUBOT generó esta respuesta automática a tu consulta:\n\n"
        f"{respuesta_automatica or 'Recibimos tu mensaje y lo enviamos al buzón de soporte.'}\n\n"
        "La consulta también fue enviada al buzón de soporte de EDUTURNOS.\n\n"
        "Equipo EDUTURNOS"
    )
    acuse.html = (
        '<!doctype html><html lang="es"><meta charset="utf-8"><body '
        'style="font-family:Arial,sans-serif;line-height:1.6;color:#1f2937">'
        f"<h2>Hola {safe_name},</h2>"
        "<p>EDUBOT generó esta respuesta automática a tu consulta:</p>"
        f"<p>{safe_answer.replace(chr(10), '<br>') if respuesta_automatica else 'Recibimos tu mensaje y lo enviamos al buzón de soporte.'}</p>"
        "<p>La consulta también fue enviada al buzón de soporte de EDUTURNOS.</p>"
        "<p>Equipo EDUTURNOS</p></body></html>"
    )
    try:
        mail.send(acuse)
    except Exception as exc:
        current_app.logger.exception("La solicitud llegó a soporte, pero no se pudo enviar el acuse.")
        raise AcuseSoporteError(
            "La solicitud llegó a soporte, pero no se pudo enviar el acuse automático."
        ) from exc
