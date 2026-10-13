"""Controles de seguridad y utilidades comunes de EDUTURNOS."""
from __future__ import annotations
import secrets
from functools import wraps
from flask import abort, current_app, flash, redirect, request, session, url_for

CSRF_SESSION_KEY = "_csrf_token"


def csrf_token() -> str:
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def validar_csrf() -> None:
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return
    expected = session.get(CSRF_SESSION_KEY)
    provided = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
    if not expected or not provided or not secrets.compare_digest(expected, provided):
        abort(400, description="Solicitud no válida. Actualiza la página e inténtalo de nuevo.")


def csrf_protegido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        validar_csrf()
        return func(*args, **kwargs)
    return wrapper


def require_configured_secret(config) -> None:
    if config.get("APP_ENV", "development") != "production":
        return
    if config.get("SECRET_KEY_INSECURE"):
        raise RuntimeError("SECRET_KEY debe configurarse en producción.")


def origin_allowed() -> bool:
    """Comprobación básica para despliegues detrás de proxy."""
    expected = current_app.config.get("APP_ORIGIN", "").strip().rstrip("/")
    if not expected:
        return True
    origin = (request.headers.get("Origin") or request.headers.get("Referer") or "").rstrip("/")
    return not origin or origin.startswith(expected)
