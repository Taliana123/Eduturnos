from flask import Blueprint, redirect, request
from urllib.parse import urlencode

soporte_bp = Blueprint("soporte", __name__, url_prefix="/soporte")


@soporte_bp.get("/")
def index():
    correo = "coliejjfh@hotmail.com"
    asunto = "Ayuda con EDUTURNOS"
    mensaje = "Hola, necesito ayuda con EDUTURNOS"
    plataforma = (request.user_agent.platform or "").lower()
    if plataforma in ("android", "iphone", "ipad"):
        destino = f"mailto:{correo}?{urlencode({'subject': asunto, 'body': mensaje})}"
    else:
        destino = "https://mail.google.com/mail/?" + urlencode(
            {"view": "cm", "fs": 1, "to": correo, "su": asunto, "body": mensaje}
        )
    return redirect(destino)
