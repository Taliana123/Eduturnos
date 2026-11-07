from flask import Blueprint, redirect, request
from urllib.parse import quote, urlencode

soporte_bp = Blueprint("soporte", __name__, url_prefix="/soporte")


@soporte_bp.get("/")
def index():
    correo = "coliejjfh@hotmail.com"
    asunto = "Ayuda con EDUTURNOS"
    mensaje = "Hola, necesito ayuda con EDUTURNOS"
    consulta = urlencode(
        {"view": "cm", "fs": "1", "to": correo, "su": asunto, "body": mensaje},
        quote_via=quote,
    )
    destino_web = f"https://mail.google.com/mail/?{consulta}"
    if "Android" in request.user_agent.string:
        consulta_android = urlencode(
            {"subject": asunto, "body": mensaje},
            quote_via=quote,
        )
        fallback = quote(destino_web, safe="")
        destino = (
            f"intent://compose?to={quote(correo)}&{consulta_android}"
            "#Intent;scheme=mailto;action=android.intent.action.SENDTO;"
            f"package=com.google.android.gm;S.browser_fallback_url={fallback};end"
        )
    else:
        destino = destino_web
    return redirect(destino)
