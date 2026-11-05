from flask import Blueprint, redirect, request
from urllib.parse import quote, urlencode

soporte_bp = Blueprint("soporte", __name__, url_prefix="/soporte")


@soporte_bp.get("/")
def index():
    correo = "coliejjfh@hotmail.com"
    asunto = "Ayuda con EDUTURNOS"
    mensaje = "Hola, necesito ayuda con EDUTURNOS"
    consulta = urlencode({'subject': asunto, 'body': mensaje}, quote_via=quote)
    if "Android" in request.user_agent.string:
        # Dirige la accion SENDTO a Gmail para evitar que Chrome abra Gmail web.
        destino = (
            f"intent://compose?to={quote(correo)}&{consulta}"
            "#Intent;scheme=mailto;action=android.intent.action.SENDTO;"
            "package=com.google.android.gm;end"
        )
    else:
        destino = f"mailto:{correo}?{consulta}"
    return redirect(destino)
