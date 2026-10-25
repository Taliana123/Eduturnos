from __future__ import annotations

import re
import unicodedata
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import current_app


INSTRUCCION = (
    "Eres EDUBOT, el asistente de ayuda de EDUTURNOS, una plataforma escolar colombiana. "
    "Responde en español, de forma amable, breve y práctica, a preguntas sobre cualquier módulo o "
    "flujo de EDUTURNOS. Presenta respuestas pulcras con párrafos breves y listas sencillas cuando "
    "ayuden; evita tablas y no muestres etiquetas Markdown sin formato. Nombra las secciones y pasos "
    "confirmados; adapta permisos al perfil "
    "recibido y no inventes opciones, políticas, horarios, estados ni datos institucionales. "
    "No tienes acceso a cuentas, citas, estudiantes ni expedientes; no solicites datos personales, "
    "contraseñas ni códigos. Si no hay información suficiente para una respuesta segura, dilo "
    "brevemente y pregunta qué sección o acción necesita aclarar."
)


RESPUESTAS_RAPIDAS = (
    (
        ("solicitar citacion", "solicito una citacion", "crear citacion", "nueva citacion", "pedir cita", "agendar reunion", "programar reunion"),
        "Para solicitar una reunión, inicia sesión y abre «Citaciones» o «Solicitudes», según las opciones de tu perfil. "
        "Completa los datos que te pide el formulario y envíalo. La disponibilidad para elegir participantes y horarios "
        "depende de tu rol; revisa después el estado de la solicitud o la notificación recibida.",
    ),
    (
        ("cancelar citacion", "cancelar cita", "reprogramar citacion", "cambiar fecha", "cambiar hora"),
        "Abre «Citaciones» o «Solicitudes» y busca la reunión correspondiente. Si aparece una opción para cancelar o "
        "proponer otro horario, úsala desde allí. Si no está disponible para tu perfil o la cita ya fue confirmada, "
        "contacta a coordinación; EDUBOT no puede modificar citas.",
    ),
    (
        ("estado de mi cita", "estado de la cita", "confirmar cita", "cita pendiente", "cita confirmada", "no asistio"),
        "Consulta «Citaciones» o «Solicitudes» para revisar el estado. Las citas pueden pasar por estados como pendiente, "
        "propuesta, aceptada, confirmada, realizada o cancelada. Las acciones para cambiar ese estado dependen del rol "
        "y de la cita; EDUBOT no puede consultar registros individuales.",
    ),
    (
        ("calendario", "agenda", "horario disponible", "ver mis citas", "fechas de reunion"),
        "Abre «Calendario» o «Ver agenda» desde el menú para consultar las fechas visibles para tu cuenta. Para proponer "
        "una reunión, usa «Citaciones» o «Solicitudes». Si no ves una cita esperada, revisa también «Notificaciones» "
        "y consulta a coordinación si necesitas verificar un registro.",
    ),
    (
        ("seguimiento", "compromiso", "acuerdo", "tarea pendiente", "seguimiento de cita"),
        "Abre «Seguimiento» desde el menú para consultar los compromisos registrados. El acceso depende del perfil "
        "institucional y de la información vinculada a tu cuenta. Si no aparece un compromiso, solicita a la persona "
        "responsable que revise el registro.",
    ),
    (
        ("justificacion", "justificar inasistencia", "excusa", "no pude asistir", "inasistencia"),
        "Estudiantes y acudientes pueden revisar «Justificaciones» y enviar una justificación desde esa sección. "
        "El personal institucional autorizado puede revisar las solicitudes. Adjunta o escribe únicamente la información "
        "que el formulario solicite; para consultar un caso particular, contacta a coordinación.",
    ),
    (
        ("recuperar contrasena", "olvide mi contrasena", "restablecer contrasena", "cambiar clave", "olvide mi clave", "password"),
        "En la pantalla de inicio de sesión selecciona «¿Olvidaste tu contraseña?» y sigue las instrucciones enviadas "
        "al correo registrado. Si no recibes el mensaje, revisa la carpeta de correo no deseado y confirma con coordinación "
        "que el correo de tu cuenta esté actualizado. Nunca compartas tu contraseña ni códigos de recuperación.",
    ),
    (
        ("iniciar sesion", "no puedo entrar", "no puedo ingresar", "acceder a mi cuenta", "problema de acceso", "entrar a eduturnos"),
        "En la portada selecciona «Iniciar sesión» e ingresa el correo y la contraseña de tu cuenta. Si no puedes entrar, "
        "usa «¿Olvidaste tu contraseña?». Si el sistema no reconoce tu cuenta, pide a coordinación que revise tu vinculación.",
    ),
    (
        ("crear cuenta", "registrarme", "hacer registro", "registrar usuario", "no reconoce mi documento"),
        "En la portada selecciona «Crear cuenta», elige el perfil disponible para ti y completa el formulario con los datos "
        "registrados por la institución. Si tu documento o correo no son reconocidos, solicita a coordinación que revise "
        "tu vinculación; no intentes crear una cuenta con datos de otra persona.",
    ),
    (
        ("permisos", "roles", "que puede hacer", "quien puede", "acceso de docente", "acceso de estudiante", "acceso de acudiente"),
        "EDUTURNOS muestra opciones distintas según el perfil. Super Admin y Rector tienen opciones institucionales; "
        "Administrador / Coordinador gestiona procesos autorizados; Docente consulta estudiantes vinculados y seguimiento; "
        "Estudiante y Acudiente acceden a sus trámites, notificaciones y justificaciones disponibles. Si no ves una opción, "
        "puede no corresponder a tu perfil: consulta a coordinación.",
    ),
    (
        ("notificacion", "aviso", "no me llego el correo", "recordatorio", "mensaje de eduturnos"),
        "Revisa «Notificaciones» dentro de EDUTURNOS y el correo asociado a tu cuenta, incluida la carpeta de correo no "
        "deseado. Si el aviso no aparece o los datos de contacto están desactualizados, pide ayuda a coordinación.",
    ),
    (
        ("estudiantes", "estudiante", "grado", "grupo", "sede", "jornada", "matricular estudiante"),
        "La información de estudiantes, grados, grupos, sedes y jornadas se consulta en «Estudiantes» cuando tu perfil "
        "tiene acceso. La creación y gestión de registros está restringida a perfiles institucionales autorizados; Docentes "
        "solo ven estudiantes vinculados a sus asignaciones. Para corregir un dato institucional, contacta a coordinación.",
    ),
    (
        ("acudiente", "padre de familia", "madre de familia", "responsable"),
        "El perfil «Acudiente» permite usar las opciones asociadas a la cuenta y al estudiante vinculado, como solicitudes, "
        "notificaciones y justificaciones disponibles. Los acudientes no administran los registros institucionales. "
        "Si el estudiante no aparece vinculado, contacta a coordinación.",
    ),
    (
        ("docente", "profesor", "asignacion docente", "mis cursos"),
        "El perfil «Docente» permite consultar estudiantes vinculados y opciones como citaciones, agenda y seguimiento "
        "cuando estén habilitadas. La gestión institucional de usuarios y registros corresponde a los perfiles autorizados. "
        "Si una asignación o estudiante no aparece, pide que revisen el vínculo institucional.",
    ),
    (
        ("importar estudiantes", "cargar estudiantes", "archivo csv", "archivo xlsx", "carga masiva"),
        "La importación de estudiantes está en «Importación» y solo está disponible para Super Admin, Rector y "
        "Administrador / Coordinador. Admite archivos CSV o XLSX con los campos y referencias institucionales requeridos. "
        "Revisa el resultado de cada fila antes de volver a importar para evitar duplicados.",
    ),
    (
        ("reporte", "informes", "exportar", "excel", "pdf", "csv"),
        "Los reportes de citaciones están disponibles para Super Admin, Rector y Administrador / Coordinador en «Reportes». "
        "Allí puedes filtrar y exportar la información en los formatos habilitados. No compartas archivos con datos "
        "personales fuera de los canales institucionales.",
    ),
    (
        ("editar mis datos", "cambiar mis datos", "actualizar mis datos", "correo incorrecto", "actualizar correo", "mi cuenta"),
        "Abre «Mi cuenta» para revisar los datos que estén habilitados para tu perfil. Los datos académicos y los vínculos "
        "institucionales deben corregirse desde el módulo autorizado. Si no puedes editarlos, solicita ayuda a coordinación.",
    ),
    (
        ("google calendar", "sincronizar calendario", "integracion calendario", "conectar calendario"),
        "EDUTURNOS incluye una integración opcional con Google Calendar. Si está habilitada para la institución, busca "
        "«Integraciones» en las opciones disponibles de tu perfil y sigue el flujo de autorización. No compartas códigos "
        "OAuth ni contraseñas; si no aparece la opción, consulta a coordinación.",
    ),
    (
        ("celular", "movil", "instalar aplicacion", "app", "pantalla pequena", "chrome"),
        "EDUTURNOS se puede abrir desde el navegador del celular o del computador. Inicia sesión con la misma cuenta y "
        "usa el menú para acceder a las secciones disponibles en tu perfil. Si la página no carga, comprueba tu conexión "
        "y vuelve a intentarlo; para una falla persistente usa «Ayuda y soporte».",
    ),
    (
        ("error", "problema", "no funciona", "no abre", "soporte", "reportar falla", "ayuda"),
        "Cuéntame qué sección estabas usando y qué ocurrió, sin incluir contraseñas, documentos, teléfonos ni nombres. "
        "También puedes abrir «Ayuda y soporte» desde el menú para enviar una consulta a la institución. EDUBOT no puede "
        "revisar tu cuenta ni corregir registros directamente.",
    ),
    (
        ("panel", "dashboard", "inicio", "resumen"),
        "El «Dashboard» o panel de inicio muestra accesos y resúmenes disponibles para tu perfil. Usa el menú lateral "
        "para abrir citaciones, calendario, notificaciones y otros módulos autorizados. Si esperabas ver una opción que "
        "no aparece, consulta a coordinación.",
    ),
)


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def _puntuar(texto: str, terminos: tuple[str, ...]) -> float:
    palabras = set(texto.split())
    puntuacion = 0.0
    for termino in terminos:
        normalizado = _normalizar(termino)
        if " " in normalizado and f" {normalizado} " in f" {texto} ":
            puntuacion += 3.0 + min(len(normalizado.split()), 3) * 0.25
        elif normalizado in palabras:
            puntuacion += 1.0
    return puntuacion


def respuesta_rapida(pregunta: str) -> str | None:
    texto = _normalizar(pregunta)
    if not texto:
        return None
    palabras = texto.split()
    if palabras[0] in {"hola", "buenas", "saludos"} and len(palabras) <= 3:
        return (
            "¡Hola! Soy EDUBOT. Puedo orientarte sobre citaciones, agenda, solicitudes, permisos, "
            "seguimiento, justificaciones, acceso y otros módulos de EDUTURNOS."
        )

    mejor_respuesta = None
    mejor_puntuacion = 0.0
    for terminos, respuesta in RESPUESTAS_RAPIDAS:
        puntuacion = _puntuar(texto, terminos)
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_respuesta = respuesta
    return mejor_respuesta if mejor_puntuacion >= 1.0 else None


def anonimizar_consulta(pregunta: str) -> str:
    consulta = re.sub(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "[correo omitido]",
        pregunta,
    )
    consulta = re.sub(r"(?<!\w)\+?\d[\d\s().-]{4,}\d(?!\w)", "[número omitido]", consulta)
    consulta = re.sub(r"(?<!\w)\d{5,}(?!\w)", "[número omitido]", consulta)
    consulta = re.sub(
        r"(?i)\b(mi hijo|mi hija|el estudiante|la estudiante|estudiante|docente|"
        r"profesor(?:a)?|rector(?:a)?|coordinador(?:a)?)\s+"
        r"((?-i:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,2})\b)",
        r"\1 [persona omitida]",
        consulta,
    )
    return consulta[:1200].strip()


def generar_respuesta(pregunta: str, rol: str | None = None) -> str:
    respuesta = respuesta_rapida(pregunta)
    if respuesta:
        return respuesta

    api_key = current_app.config.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "Las respuestas abiertas no están activadas todavía. Las preguntas frecuentes siguen disponibles."
        )

    consulta = anonimizar_consulta(pregunta)
    if not consulta:
        raise ValueError("No fue posible preparar una consulta general sin datos personales.")

    guias = "\n".join(dict.fromkeys(respuesta for _, respuesta in RESPUESTAS_RAPIDAS))
    system_prompt = f"{INSTRUCCION}\n"
    if rol:
        system_prompt += f"El perfil actual es «{rol}».\n"
    system_prompt += f"Guías confirmadas de EDUTURNOS:\n{guias}"
    payload = {
        "model": current_app.config.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": consulta},
        ],
        "temperature": 0.2,
        "max_tokens": 500,
    }
    req = Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "EDUTURNOS/1.0",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        current_app.logger.warning("Groq respondió HTTP %s", exc.code)
        raise RuntimeError("El asistente no está disponible en este momento.") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("No se pudo conectar con el asistente.") from exc

    try:
        respuesta = result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("El asistente no devolvió una respuesta utilizable.") from exc
    if not respuesta:
        raise RuntimeError("El asistente no devolvió una respuesta utilizable.")
    return respuesta[:4000]
