from __future__ import annotations

import time

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from routes.helpers import login_requerido, usuario_actual
from servicios.asistente import generar_respuesta
from servicios.email import AcuseSoporteError, enviar_solicitud_soporte

soporte_bp = Blueprint("soporte", __name__, url_prefix="/soporte")


@soporte_bp.route("/", methods=["GET", "POST"])
@login_requerido
def index():
    usuario = usuario_actual()
    if request.method == "POST":
        correo = (usuario.get("correo") or "").strip()[:254]
        detalle = (request.form.get("mensaje") or "").strip()
        ahora = time.time()
        solicitudes = [marca for marca in session.get("support_requests", []) if ahora - marca < 600]
        if len(solicitudes) >= 3:
            flash("Ya enviaste varias solicitudes. Espera unos minutos antes de intentarlo otra vez.", "error")
            return render_template("soporte/index.html", usuario=usuario, correo=correo, mensaje=detalle)
        if len(detalle) < 10 or len(detalle) > 3000:
            flash("Describe tu consulta con entre 10 y 3000 caracteres.", "error")
            return render_template("soporte/index.html", usuario=usuario, correo=correo, mensaje=detalle)
        if not correo:
            flash("Tu cuenta no tiene un correo registrado para recibir el acuse. Contacta a la institución para actualizarlo.", "error")
            return render_template("soporte/index.html", usuario=usuario, correo=correo, mensaje=detalle)

        solicitudes.append(ahora)
        session["support_requests"] = solicitudes
        try:
            respuesta = generar_respuesta(detalle)
        except (RuntimeError, ValueError) as exc:
            current_app.logger.warning("No se pudo generar la respuesta automática de soporte: %s", exc)
            flash("EDUBOT no pudo generar una respuesta en este momento. Inténtalo más tarde o usa el chat de ayuda.", "error")
            return render_template("soporte/index.html", usuario=usuario, correo=correo, mensaje=detalle)

        nombre = f"{usuario['nombres']} {usuario['apellidos']}".strip()
        try:
            enviar_solicitud_soporte(
                correo,
                nombre,
                usuario["rol_nombre"],
                detalle,
                respuesta_automatica=respuesta,
            )
        except AcuseSoporteError:
            flash(
                "La respuesta de EDUBOT quedó generada, pero no fue posible enviarla a tu correo.",
                "warning",
            )
            return redirect(url_for("soporte.index"))
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("soporte/index.html", usuario=usuario, correo=correo, mensaje=detalle)
        except RuntimeError as exc:
            current_app.logger.error("No se pudo completar el envío de soporte: %s", exc)
            flash("El correo de soporte no está disponible en este momento. Inténtalo más tarde.", "error")
            return render_template("soporte/index.html", usuario=usuario, correo=correo, mensaje=detalle)
        except Exception:
            current_app.logger.exception("No se pudo enviar la solicitud de ayuda de EDUTURNOS.")
            flash("No fue posible enviar tu solicitud. Inténtalo más tarde.", "error")
            return render_template("soporte/index.html", usuario=usuario, correo=correo, mensaje=detalle)
        else:
            flash("EDUBOT respondió tu consulta y enviamos la respuesta a tu correo. También enviamos tu solicitud al buzón de soporte.", "success")
            return redirect(url_for("soporte.index"))

    return render_template(
        "soporte/index.html",
        usuario=usuario,
        correo=(usuario.get("correo") or ""),
        mensaje="",
    )
