from __future__ import annotations

import re
import time
import unicodedata
from urllib.parse import urlsplit, urlunsplit

from flask import Blueprint, current_app, jsonify, request, session, redirect, Response, url_for

from database.db import consultar
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
ROLES_CREAN_CITA = {
    "Super Admin",
    "Rector",
    "Administrador / Coordinador",
    "Docente",
}
ROLES_SEGUIMIENTO = {
    "Super Admin",
    "Rector",
    "Administrador / Coordinador",
    "Docente",
}
ROLES_CANCELAN_CITA = ROLES_SEGUIMIENTO
ROLES_REPROGRAMAN_CITA = ROLES_SEGUIMIENTO | {"Acudiente"}
SECCIONES_NAVEGABLES = (
    (("calendario", "agenda"), "calendario.index", "Abrir Calendario"),
    (("solicitudes", "solicitud"), "solicitudes.index", "Abrir Solicitudes"),
    (("citaciones", "citas"), "citas.index", "Abrir Citaciones"),
    (("justificaciones", "justificacion"), "justificaciones.index", "Abrir Justificaciones"),
    (("notificaciones", "notificacion"), "notificaciones.index", "Abrir Notificaciones"),
    (("ayuda", "soporte"), "soporte.index", "Abrir Ayuda y soporte"),
    (("configuracion",), "configuracion.index", "Abrir Configuración"),
    (("mi cuenta", "cuenta", "perfil"), "cuenta.index", "Abrir Mi cuenta"),
    (("estudiantes", "alumnos"), "estudiantes.lista", "Abrir Estudiantes"),
    (("docentes", "profesores"), "docentes.lista", "Abrir Docentes"),
    (("acudientes",), "acudientes.lista", "Abrir Acudientes"),
)


def _normalizar(texto):
    normalizado = unicodedata.normalize("NFD", texto.casefold())
    normalizado = "".join(
        caracter for caracter in normalizado
        if unicodedata.category(caracter) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", normalizado).strip()


def _solicita_crear_cita(texto):
    normalizado = _normalizar(texto)
    return any(
        expresion in normalizado
        for expresion in (
            "crear cita",
            "crear una cita",
            "crear citacion",
            "crear una citacion",
            "crea cita",
            "crea una cita",
            "crea citacion",
            "crea una citacion",
            "nueva cita",
            "nueva citacion",
            "agendar cita",
            "agendar una cita",
            "programar cita",
            "programar una cita",
            "solicitar cita",
            "solicitar una cita",
        )
    )


def _solicita_seguimiento(texto):
    normalizado = _normalizar(texto)
    tiene_seguimiento = any(
        termino in normalizado
        for termino in ("seguimiento", "compromiso", "compromisos")
    )
    solicita_consulta = any(
        termino in normalizado
        for termino in (
            "ver", "mira", "mire", "revisa", "revisar", "consulta",
            "consultar", "mostrar", "mostrame", "dame", "abrir",
        )
    )
    return tiene_seguimiento and solicita_consulta


def _solicitud_cancelacion(texto):
    normalizado = _normalizar(texto)
    verbos = {"cancelar", "cancela", "eliminar", "elimina", "borrar", "borra", "anular", "anula"}
    palabras = set(normalizado.split())
    if not verbos.intersection(palabras) or not {"cita", "citacion"}.intersection(palabras):
        return False, None
    identificador = re.search(r"\b(?:cita|citacion)\s*(?:numero\s*)?(\d{1,8})\b", normalizado)
    return True, int(identificador.group(1)) if identificador else None


def _solicitud_edicion_cita(texto):
    normalizado = _normalizar(texto)
    palabras = set(normalizado.split())
    quiere_editar = any(
        termino in normalizado
        for termino in ("editar", "edita", "reprogramar", "reprograma", "cambiar fecha", "cambiar hora")
    )
    if not quiere_editar or not {"cita", "citacion"}.intersection(palabras):
        return False, None
    identificador = re.search(r"\b(?:cita|citacion)\s*(?:numero\s*)?(\d{1,8})\b", normalizado)
    return True, int(identificador.group(1)) if identificador else None


def _seccion_solicitada(texto):
    normalizado = _normalizar(texto)
    verbos = {"abrir", "abre", "abrime", "ir", "entra", "muestra", "mostrar", "navega", "ver"}
    if not verbos.intersection(normalizado.split()):
        return None
    for terminos, endpoint, etiqueta in SECCIONES_NAVEGABLES:
        if any(termino in normalizado for termino in terminos):
            return endpoint, etiqueta
    return None


def _consultar_seguimiento(usuario):
    filtros = []
    parametros = []
    if usuario["rol_nombre"] != "Super Admin" and usuario.get("id_institucion"):
        filtros.append("c.id_institucion=%s")
        parametros.append(usuario["id_institucion"])
    if usuario["rol_nombre"] == "Docente":
        filtros.append(
            "(c.id_docente=(SELECT d.id_docente FROM docentes d "
            "WHERE d.id_usuario=%s) OR c.creado_por=%s)"
        )
        parametros.extend((usuario["id_usuario"], usuario["id_usuario"]))
    where = f" WHERE {' AND '.join(filtros)}" if filtros else ""
    return consultar(
        """SELECT c.id,c.fecha,c.hora,ec.nombre AS estado,
                  COUNT(DISTINCT s.id) AS seguimientos,
                  COUNT(DISTINCT cc.id) AS compromisos
           FROM citas c
           JOIN estados_cita ec ON ec.id=c.id_estado
           LEFT JOIN seguimiento_citas s ON s.id_cita=c.id
           LEFT JOIN compromisos_cita cc ON cc.id_cita=c.id"""
        + where
        + """ GROUP BY c.id,c.fecha,c.hora,ec.nombre
              ORDER BY c.fecha DESC,c.hora DESC,c.id DESC
              LIMIT 10""",
        tuple(parametros),
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
    solicita_cancelacion, cita_id = _solicitud_cancelacion(pregunta)
    if solicita_cancelacion:
        if usuario["rol_nombre"] not in ROLES_CANCELAN_CITA:
            return jsonify(
                respuesta="Este perfil no tiene permiso para cancelar citas."
            )
        if cita_id is None:
            return jsonify(
                respuesta=(
                    "Indica el número de la cita que quieres cancelar. La cancelación conservará "
                    "el historial y solo se realizará después de que revises y confirmes."
                ),
                accion="abrir_citas",
                accion_url=url_for("citas.index"),
                accion_label="Abrir citaciones",
            )
        from routes import citas as citas_routes

        cita = citas_routes._cita_autorizada(usuario, cita_id)
        if not citas_routes._transicion_estado_permitida(
            usuario["rol_nombre"], cita.get("estado"), "Cancelada"
        ):
            return jsonify(
                respuesta=(
                    f"La cita #{cita_id} está en estado «{cita.get('estado', 'desconocido')}» "
                    "y no se puede cancelar."
                )
            )
        if usuario["rol_nombre"] == "Docente":
            docente = consultar(
                "SELECT id_docente FROM docentes WHERE id_usuario=%s LIMIT 1",
                (usuario["id_usuario"],),
                uno=True,
            )
            if not docente or cita.get("id_docente") != docente.get("id_docente"):
                return jsonify(
                    respuesta="No tienes permiso para cancelar esta cita."
                )
        fecha = cita.get("fecha")
        hora = cita.get("hora")
        fecha = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha or "sin fecha")
        hora = hora.strftime("%H:%M") if hasattr(hora, "strftime") else str(hora or "sin hora")
        return jsonify(
            respuesta=(
                f"Revisa la cita #{cita_id}: {fecha} a las {hora}, estado "
                f"«{cita.get('estado', 'desconocido')}». Se conservará en el historial."
            ),
            accion="confirmar_cancelacion",
            accion_url=url_for("citas.cambiar_estado", cita_id=cita_id),
            cita_id=cita_id,
        )
    solicita_edicion, cita_id = _solicitud_edicion_cita(pregunta)
    if solicita_edicion:
        if usuario["rol_nombre"] not in ROLES_REPROGRAMAN_CITA:
            return jsonify(
                respuesta="Este perfil no tiene permiso para reprogramar citas."
            )
        if cita_id is None:
            return jsonify(
                respuesta=(
                    "Indica el número de la cita para abrir su detalle. Allí podrás usar las opciones de "
                    "reprogramación disponibles para tu perfil y revisar los datos antes de guardar."
                ),
                accion="abrir_citas",
                accion_url=url_for("citas.index"),
                accion_label="Abrir citaciones",
            )
        return jsonify(
            respuesta=(
                f"Abre el detalle de la cita #{cita_id} y usa la opción de reprogramación disponible para "
                "tu perfil. Revisa los cambios y confirma el formulario para guardarlos."
            ),
            accion="abrir_detalle_cita",
            accion_url=url_for("citas.index", _anchor=f"cita-desktop-detail-{cita_id}"),
            accion_label=f"Abrir cita #{cita_id}",
        )
    if _solicita_seguimiento(pregunta):
        if usuario["rol_nombre"] not in ROLES_SEGUIMIENTO:
            return jsonify(
                respuesta="Este perfil no tiene permiso para consultar Seguimiento."
            )
        procesos = _consultar_seguimiento(usuario)
        if not procesos:
            resumen = "No hay procesos de seguimiento disponibles para tu perfil."
        else:
            lineas = [
                f"Cita #{proceso['id']}: {proceso['fecha']} {proceso['hora']} · "
                f"{proceso['estado']} · {proceso['seguimientos']} seguimientos · "
                f"{proceso['compromisos']} compromisos"
                for proceso in procesos
            ]
            resumen = (
                "Resumen de los procesos más recientes. No incluí nombres ni observaciones para "
                "proteger datos personales:\n" + "\n".join(lineas)
            )
        return jsonify(
            respuesta=resumen,
            accion="abrir_seguimiento",
            accion_url=url_for("seguimiento.lista"),
            accion_label="Abrir Seguimiento",
        )
    if _solicita_crear_cita(pregunta):
        if usuario["rol_nombre"] in ROLES_CREAN_CITA:
            return jsonify(
                respuesta=(
                    "Puedo guiarte al formulario oficial de citaciones. Completa los datos allí; "
                    "el sistema validará tus permisos y la disponibilidad. Revisa los datos antes "
                    "de enviar y pulsa «Crear citación» solo cuando confirmes que están correctos."
                ),
                accion="crear_cita",
            )
        if usuario["rol_nombre"] == "Acudiente":
            return jsonify(
                respuesta=(
                    "Puedo guiarte al formulario oficial para solicitar una cita. Completa los "
                    "datos allí, revísalos y envía la solicitud para que siga el proceso institucional."
                ),
                accion="crear_cita",
            )
        return jsonify(
            respuesta=(
                "El perfil Estudiante no tiene habilitada la creación o solicitud de citaciones. "
                "Pide al acudiente relacionado o a la institución que gestione la cita."
            )
        )
    seccion = _seccion_solicitada(pregunta)
    if seccion:
        endpoint, etiqueta = seccion
        return jsonify(
            respuesta=f"Te llevo a «{etiqueta.removeprefix('Abrir ')}». El acceso y las acciones disponibles siguen sujetos a los permisos de tu perfil.",
            accion="abrir_seccion",
            accion_url=url_for(endpoint),
            accion_label=etiqueta,
        )
    try:
        respuesta = generar_respuesta(pregunta, rol=usuario["rol_nombre"])
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except RuntimeError as exc:
        current_app.logger.warning("No se pudo generar la respuesta de EDUBOT: %s", exc)
        return jsonify(error=str(exc)), 503
    return jsonify(respuesta=respuesta)
