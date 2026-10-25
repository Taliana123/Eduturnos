from __future__ import annotations

import re
import time
from urllib.parse import urlsplit, urlunsplit

from flask import Blueprint, current_app, jsonify, request, session, redirect, Response

from routes.helpers import login_requerido, usuario_actual
from servicios.asistente import generar_respuesta

asistente_bp = Blueprint("asistente", __name__, url_prefix="/asistente")
ROLES_PERMITIDOS = {
    "Super Admin",
    "Rector",
    "Administrador / Coordinador",
    "Docente",
    "Estudiante",
    "Acudiente",
}


@asistente_bp.get("/beepy")
@login_requerido
def abrir_beepy():
    if not current_app.config.get("BEEPY_ENABLED"):
        return Response("El chat no esta disponible.", status=503, mimetype="text/plain")
    destination = urlsplit(current_app.config.get("BEEPY_CHAT_URL", ""))
    if destination.scheme != "https" or destination.netloc != "www.beepychatbot.com" or not re.fullmatch(r"/u/[A-Za-z0-9]+/", destination.path):
        return Response("El enlace de EDUBOT no esta configurado correctamente.", status=503, mimetype="text/plain")
    result = redirect(urlunsplit((destination.scheme, destination.netloc, destination.path, "", "")))
    result.headers["Cache-Control"] = "no-store"
    return result


@asistente_bp.post("/preguntar")
@login_requerido
def preguntar():
    usuario = usuario_actual()
    if not usuario:
        return jsonify(error="La sesión expiró. Vuelve a iniciar sesión."), 401
    if usuario["rol_nombre"] not in ROLES_PERMITIDOS:
        return jsonify(error="El asistente está disponible para personal institucional."), 403
    payload = request.get_json(silent=True)
    pregunta = payload.get("mensaje") if isinstance(payload, dict) else None
    if not isinstance(pregunta, str):
        return jsonify(error="El mensaje debe ser texto."), 400
    pregunta = pregunta.strip()
    if not pregunta or len(pregunta) > 1200:
        return jsonify(error="Escribe una pregunta de hasta 1200 caracteres."), 400
    ahora = time.time()
    peticiones = [marca for marca in session.get("assistant_requests", []) if ahora - marca < 60]
    if len(peticiones) >= 8:
        return jsonify(error="Espera un minuto antes de enviar más preguntas."), 429
    peticiones.append(ahora)
    session["assistant_requests"] = peticiones
    try:
        respuesta = generar_respuesta(pregunta, rol=usuario["rol_nombre"])
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except RuntimeError as exc:
        current_app.logger.warning("No se pudo generar la respuesta de EDUBOT: %s", exc)
        return jsonify(error=str(exc)), 503
    return jsonify(respuesta=respuesta)
