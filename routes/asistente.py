from __future__ import annotations

import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlsplit, urlunsplit

from flask import Blueprint, current_app, jsonify, request, session, redirect, Response

from routes.helpers import login_requerido, usuario_actual

asistente_bp = Blueprint("asistente", __name__, url_prefix="/asistente")
ROLES_PERMITIDOS = {"Super Admin", "Rector", "Administrador / Coordinador", "Docente"}
INSTRUCCION = (
    "Eres el asistente de ayuda general de EDUTURNOS, una plataforma escolar colombiana. "
    "Responde en español, de forma clara, breve y respetuosa, sobre el uso general del sistema, "
    "calendario, citaciones, cuentas y buenas prácticas. No tienes acceso a cuentas, citas, "
    "estudiantes ni expedientes; no solicites ni infieras datos personales. Si preguntan por un "
    "caso particular, indica que consulten EDUTURNOS o coordinación por el canal autorizado. "
    "No inventes políticas ni datos institucionales no incluidos en la pregunta."
)


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


def _respuesta_gemini(pregunta: str) -> str:
    api_key = current_app.config.get("GEMINI_API_KEY", "")
    modelo = current_app.config.get("GEMINI_MODEL", "gemini-3.8-flash")
    if not api_key:
        raise RuntimeError("El asistente aún no está configurado en el servidor.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": INSTRUCCION}]},
        "contents": [{"role": "user", "parts": [{"text": pregunta}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 400},
    }
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    try:
        with urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        current_app.logger.warning("Gemini respondió HTTP %s", exc.code)
        raise RuntimeError("El asistente no está disponible en este momento.") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("No se pudo conectar con el asistente.") from exc
    try:
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("El asistente no devolvió una respuesta utilizable.") from exc


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
        respuesta = _respuesta_gemini(pregunta)
    except RuntimeError as exc:
        return jsonify(error=str(exc)), 503
    return jsonify(respuesta=respuesta)
