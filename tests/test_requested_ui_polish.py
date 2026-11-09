from pathlib import Path

import pytest

from app import app
from routes import citas as citas_routes


ROOT = Path(__file__).resolve().parents[1]


def test_mi_cuenta_muestra_flechas_en_seguridad_y_calendarios():
    template = (ROOT / "templates" / "cuenta" / "index.html").read_text(
        encoding="utf-8"
    )

    assert 'class="cuenta-section-back"' not in template
    assert 'class="account-back-button"' not in template
    assert '.cuenta-section[aria-labelledby="cuenta-personal-title"]{padding-top:0;}' in template

    password = (ROOT / "templates" / "auth" / "cambiar_password.html").read_text(
        encoding="utf-8"
    )
    calendars = (ROOT / "templates" / "integraciones_google.html").read_text(
        encoding="utf-8"
    )
    assert 'class="password-account-back account-settings-back history-back-button"' in password
    assert 'class="account-back-button account-settings-back history-back-button"' in calendars


def test_cancelar_citacion_limpia_datos_y_cierra_dialogos():
    citation_form = (ROOT / "templates" / "citas" / "nueva.html").read_text(
        encoding="utf-8"
    )
    citation_script = (ROOT / "static" / "js" / "nueva-citacion.js").read_text(
        encoding="utf-8"
    )
    app_script = (ROOT / "static" / "js" / "app.js").read_text(encoding="utf-8")

    assert '<button class="boton secundario" type="reset">Cancelar</button>' in citation_form
    assert 'form.addEventListener(\'reset\'' in citation_script
    assert "clearStudent(" in citation_script
    assert "clearPersonal(" in citation_script
    assert 'event.target.closest("[data-mobile-dialog-close]")' in app_script
    assert 'dialog.close()' in app_script


def test_portada_conserva_legibilidad_de_los_botones_al_enfocar():
    response = app.test_client().get("/")
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    assert response.status_code == 200
    assert b"Iniciar sesi" in response.data
    assert b"Crear cuenta" in response.data
    assert ".acciones .boton-principal:focus-visible" in template
    assert ".acciones .boton-secundario:focus-visible" in template
    assert "nav a:hover" in (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    institution = (ROOT / "templates" / "institucion.html").read_text(encoding="utf-8")
    assert ".contenedor:has(>.institucion-page){margin-top:20px!important;}" in institution


def test_sugerencias_de_estudiantes_son_compactas_y_la_ficha_se_muestra_al_seleccionar():
    template = (ROOT / "templates" / "citas" / "nueva.html").read_text(
        encoding="utf-8"
    )
    script = (ROOT / "static" / "js" / "nueva-citacion.js").read_text(
        encoding="utf-8"
    )
    student_render = script.split(
        "renderSuggestions(studentSuggestions, matches,", 1
    )[1].split("status.textContent", 1)[0]

    assert "nueva-citacion.js') }}?v=20261109_document_suggestions_v3" in template
    assert "#coincidencias-estudiante .citation-suggestion" in template
    assert "background:#f1f7fc!important" in template
    assert "min-height:0!important" in template
    assert "Documento ${student.documento}" not in student_render
    assert "getDetails" not in student_render
    assert "searchStudent();" in student_render
    assert "studentCard.hidden = false;" in script


def test_solicitudes_registradas_reduce_espacio_superior_y_margen_del_titulo():
    template = (ROOT / "templates" / "solicitudes" / "index.html").read_text(
        encoding="utf-8"
    )

    assert "solicitudes-records-card" in template
    assert "padding-top: 14px !important;" in template
    assert "padding: 6px 24px 8px !important;" in template
    assert "padding:10px 12px !important;" in template


def test_ajustes_visuales_de_edubot_y_administracion():
    edubot_styles = (ROOT / "static" / "css" / "edubot.css").read_text(
        encoding="utf-8"
    )
    admin_styles = (ROOT / "static" / "css" / "configuracion.css").read_text(
        encoding="utf-8"
    )

    assert "flex: 0 0 88px;" in edubot_styles
    assert "width: 88px;" in edubot_styles
    assert ".state-list {" in admin_styles
    assert ".administracion-page .configuracion-page .state-form-row" in admin_styles
    assert "grid-template-columns: minmax(0, 1fr) !important;" in admin_styles
    assert "max-width: 780px !important;" in admin_styles


def test_edubot_mantiene_uniforme_la_franga_inferior_y_mi_cuenta_sin_flechas_externas():
    edubot_styles = (ROOT / "static" / "css" / "edubot.css").read_text(
        encoding="utf-8"
    )
    account = (ROOT / "templates" / "cuenta" / "index.html").read_text(
        encoding="utf-8"
    )

    assert ".dashboard-help-chat .assistant-chat-body" in edubot_styles
    assert ".dashboard-help-chat .assistant-privacy" in edubot_styles
    assert "background: #f7f9fd;" in edubot_styles
    assert 'class="cuenta-section cuenta-section--navigation"' in account
    assert 'class="cuenta-section-back"' not in account
    assert "position:absolute;top:16px;right:16px;" not in account


def test_configuracion_institucional_refresca_estilos_y_conserva_anchos_solicitados():
    template = (ROOT / "templates" / "configuracion" / "index.html").read_text(
        encoding="utf-8"
    )
    config_styles = (ROOT / "static" / "css" / "configuracion.css").read_text(
        encoding="utf-8"
    )

    assert "v=20261109_institution_fields_v5" in template
    assert "calc((100% - 14px) / 2 + 20px)" in config_styles
    assert "max-width: 560px !important;" in config_styles


def test_documento_en_nueva_cita_muestra_coincidencias_y_respeta_jornada(monkeypatch):
    template = (ROOT / "templates" / "citas" / "nueva.html").read_text(
        encoding="utf-8"
    )
    script = (ROOT / "static" / "js" / "nueva-citacion.js").read_text(
        encoding="utf-8"
    )
    assert 'id="coincidencias-estudiante" role="listbox"' in template
    assert 'id="coincidencias-personal" role="listbox"' in template
    assert "selector_hora('hora', 'hora-cita')" in template
    assert "suggestStudents" in script and "suggestPersonalRecipients" in script
    assert "filterTimesByJourney(data.estudiante.jornada)" in script

    consultas = []
    estudiante = {
        "id_estudiante": 12,
        "documento": "123456",
        "nombre": "Ana Pérez",
        "grado": "9",
        "jornada": "Mañana",
    }
    monkeypatch.setattr(
        citas_routes,
        "usuario_actual",
        lambda: {"id_usuario": 4, "rol_nombre": "Docente", "id_institucion": 2},
    )
    monkeypatch.setattr(
        citas_routes,
        "consultar",
        lambda sql, params=None, **kwargs: (
            consultas.append((sql, params, kwargs)),
            [estudiante],
        )[1],
    )
    with app.test_request_context(
        "/citas/buscar-estudiante-documento?documento=123&coincidencias=1"
    ):
        response = citas_routes.buscar_estudiante_documento.__wrapped__()

    assert response.get_json() == {"ok": True, "estudiantes": [estudiante]}
    sql, params, _ = consultas[0]
    assert "e.documento LIKE %s" in sql
    assert params[0] == "123%"
    assert "asignaciones_docentes" in sql
    assert "LIMIT 8" in sql


def test_coincidencias_de_personal_se_limitan_al_tipo_y_a_la_institucion(monkeypatch):
    consultas = []
    monkeypatch.setattr(
        citas_routes,
        "usuario_actual",
        lambda: {"id_usuario": 4, "rol_nombre": "Rector", "id_institucion": 2},
    )
    monkeypatch.setattr(
        citas_routes,
        "consultar",
        lambda sql, params=None, **kwargs: (
            consultas.append((sql, params)),
            [],
        )[1],
    )
    with app.test_request_context(
        "/citas/buscar-destinatario-documento?documento=56&tipo=Docente&coincidencias=1"
    ):
        response = citas_routes.buscar_destinatario_documento.__wrapped__()

    assert response.get_json() == {"ok": True, "destinatarios": []}
    sql, params = consultas[0]
    assert "r.nombre=%s" in sql
    assert "LIKE %s" in sql and params[1] == "56%"
    assert "u.id_institucion=%s" in sql
    assert "LIMIT 8" in sql


@pytest.mark.parametrize(
    "hora,jornada,valid",
    [
        ("10:30", "Mañana", True),
        ("13:00", "Mañana", False),
        ("13:00", "Tarde", True),
        ("10:30", "Tarde", False),
        ("10:30", "Completa", True),
    ],
)
def test_hora_de_cita_se_valida_contra_la_jornada(hora, jornada, valid):
    if valid:
        citas_routes._validar_hora_jornada(hora, jornada)
    else:
        with pytest.raises(ValueError, match="jornada"):
            citas_routes._validar_hora_jornada(hora, jornada)


def test_mascota_cerrada_sin_fondo_y_chat_conserva_su_avatar():
    styles = (ROOT / "static" / "css" / "edubot.css").read_text(
        encoding="utf-8"
    )
    widget = (ROOT / "templates" / "_asistente_widget.html").read_text(
        encoding="utf-8"
    )

    assert ".assistant-sidebar-entry .assistant-sidebar-avatar" in styles
    assert "background-color: transparent;" in styles
    assert ".dashboard-help-chat .assistant-avatar" in styles
    assert "class=\"assistant-avatar assistant-drone-avatar\"" in widget


def test_filtro_de_seguimiento_es_compacto_y_actualiza_cantidad():
    template = (ROOT / "templates" / "seguimiento" / "lista.html").read_text(
        encoding="utf-8"
    )
    script = (ROOT / "static" / "js" / "app.js").read_text(encoding="utf-8")

    assert 'id="seguimiento-filtro-situacion"' in template
    assert '<select id="seguimiento-filtro-situacion"' in template
    assert "data-seguimiento-empty" in template
    assert "data-seguimiento-count" in template
    assert 'data-seguimiento-filter="observador"' not in template
    assert 'data-seguimiento-filter="segunda-cita"' not in template
    assert "const matches = filter === \"todos\"" in script
    assert "if (empty) empty.hidden = visible !== 0" in script
    assert "<script>" not in template
    assert ".seguimiento-filtros select" in template


def test_busqueda_de_cuentas_inscritas_usa_un_script_permitido_por_csp():
    template = (ROOT / "templates" / "configuracion" / "index.html").read_text(
        encoding="utf-8"
    )
    script = (ROOT / "static" / "js" / "app.js").read_text(encoding="utf-8")

    assert 'data-cuentas-filter' in template
    assert 'data-cuentas-search-button' in template
    assert "<script>" not in template
    assert "data-cuenta-row" in script
    assert "accountsSearchButton?.addEventListener(\"click\", filterAccounts)" in script
    assert '.normalize("NFD")' in script


def test_genero_del_avatar_es_visible_y_refleja_la_seleccion():
    source = (ROOT / "tools" / "humation" / "src.js").read_text(encoding="utf-8")
    styles = (ROOT / "static" / "css" / "desktop-sidebar.css").read_text(
        encoding="utf-8"
    )

    assert 'className = "avatar-gender-choice"' in source
    assert 'dataset.avatarGenderChoice = value' in source
    assert 'currentState.gender === choice.dataset.avatarGenderChoice' in source
    assert "avatar-gender-options" in styles
    assert '.avatar-gender-choice[aria-pressed="true"]' in styles


def test_registro_conserva_ilustracion_y_enlace_completo_de_regreso():
    template = (ROOT / "templates" / "auth" / "registro.html").read_text(
        encoding="utf-8"
    )

    assert 'class="registro-dibujo"' in template
    assert 'class="link-back registro-back-button"' in template
    assert 'class="link-back registro-back-button account-settings-back"' not in template
    assert "background: #fff !important;" in template
    assert "min-height: 40px !important;" in template


def test_chat_es_solo_texto_y_muestra_aviso_de_privacidad():
    widget = (ROOT / "templates" / "_asistente_widget.html").read_text(
        encoding="utf-8"
    )
    assistant_script = (ROOT / "static" / "js" / "asistente.js").read_text(
        encoding="utf-8"
    )

    assert 'class="assistant-voice-toggle"' not in widget
    assert 'class="assistant-privacy"' in widget
    assert "No compartas información personal ni documentos" in widget
    assert 'class="assistant-voice-call__privacy"' in widget
    assert "voiceToggle" not in assistant_script


def test_sedes_calendario_y_seguimiento_muestran_campos_coherentes():
    sedes = (ROOT / "templates" / "configuracion" / "index.html").read_text(
        encoding="utf-8"
    )
    config_styles = (ROOT / "static" / "css" / "configuracion.css").read_text(
        encoding="utf-8"
    )
    calendar = (ROOT / "templates" / "calendario" / "index.html").read_text(
        encoding="utf-8"
    )
    calendar_route = (ROOT / "routes" / "calendario.py").read_text(
        encoding="utf-8"
    )
    followup = (ROOT / "templates" / "seguimiento" / "lista.html").read_text(
        encoding="utf-8"
    )
    followup_route = (ROOT / "routes" / "seguimiento.py").read_text(
        encoding="utf-8"
    )

    assert 'class="config-field-status"' in sedes
    assert sedes.index('class="config-field-status"') < sedes.index('class="config-field-code"')
    assert ".config-entry-sede > .config-field-status" in config_styles
    assert "{{ cita.estudiante }}" in calendar
    assert "{{ cita.estudiante_n }}" not in calendar
    day_event = calendar.split("{% for cita in dia.citas[:3] %}", 1)[1].split("{% endfor %}", 1)[0]
    assert day_event.count("{{ cita.estudiante }}") == 1
    assert "LEFT JOIN usuarios dest" in calendar_route
    assert "AS estudiante" in calendar_route
    assert "{{ descripcion }}" in followup
    assert "CASE WHEN c.destinatario_usuario_id IS NOT NULL" in followup_route
    assert "max-width: 1140px !important;" in config_styles
    assert "max-width: 560px !important;" in config_styles
    assert "grid-template-columns: minmax(0, calc((100% - 14px) / 2 + 20px))" in config_styles


def test_acciones_de_solicitud_tienen_el_mismo_tamano():
    template = (ROOT / "templates" / "solicitudes" / "index.html").read_text(
        encoding="utf-8"
    )

    assert ".solicitudes-table .acciones-tabla button" in template
    assert "min-height: 40px;" in template
    assert "width: 100%;" in template


def test_botones_de_regreso_tienen_estilo_unificado():
    login = (ROOT / "templates" / "auth" / "login.html").read_text(
        encoding="utf-8"
    )
    mobile = (ROOT / "static" / "css" / "mobile" / "eduturnos-mobile.css").read_text(
        encoding="utf-8"
    )
    selection = (ROOT / "templates" / "auth" / "registro.html").read_text(
        encoding="utf-8"
    )
    login_portal = (ROOT / "templates" / "auth" / "login_portal.html").read_text(
        encoding="utf-8"
    )
    institution = (ROOT / "templates" / "auth" / "crear_institucion.html").read_text(
        encoding="utf-8"
    )

    assert "left: 18px !important;" in login
    assert "border-radius: 8px !important;" in login
    assert "left: 12px !important;" in mobile
    assert 'class="link-back registro-back-button"' in selection
    assert 'class="link-back registro-back-button account-settings-back"' not in selection
    assert "portal-login-back" in login_portal
    assert '<a class="back"' in institution


def test_modal_avatar_movil_tiene_cierre_de_tamano_limitado():
    styles = (ROOT / "static" / "css" / "desktop-sidebar.css").read_text(
        encoding="utf-8"
    )

    assert "html body dialog.avatar-customizer .avatar-customizer-header>[data-avatar-close]" in styles
    assert "width:40px!important" in styles
    assert "max-height:calc(100dvh - 24px - env(safe-area-inset-top))!important" in styles
    assert "grid-template-columns:repeat(2,minmax(0,1fr))!important;" in styles


def test_busqueda_institucional_y_actualizaciones_de_calendario_y_solicitudes():
    accounts = (ROOT / "templates" / "configuracion" / "index.html").read_text(
        encoding="utf-8"
    )
    calendar = (ROOT / "templates" / "calendario" / "index.html").read_text(
        encoding="utf-8"
    )
    requests = (ROOT / "templates" / "solicitudes" / "index.html").read_text(
        encoding="utf-8"
    )
    assistant = (ROOT / "static" / "js" / "asistente.js").read_text(
        encoding="utf-8"
    )

    assert 'data-cuentas-search-button>Buscar</button>' in accounts
    assert "window.setInterval(refreshIfChanged, 10000)" in calendar
    assert 'border-bottom:0 !important;' in requests
    assert "const parseListItem = (line)" in assistant
    assert 'unordered[1].replace(/^(?:[-*+]\\s+)+/, "")' in assistant


def test_cache_de_app_js_se_actualiza_en_login_y_base():
    login = (ROOT / "templates" / "auth" / "login.html").read_text(
        encoding="utf-8"
    )
    base = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")

    cache_version = "app.js') }}?v=20261109_account_search_followup_filter_v2"
    assert cache_version in login
    assert cache_version in base


def test_android_incrementa_la_version_de_la_app():
    gradle = (ROOT / "mobile-app" / "android" / "app" / "build.gradle").read_text(
        encoding="utf-8"
    )

    assert "versionCode 29" in gradle
    assert 'versionName "3.0.9"' in gradle
