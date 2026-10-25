from pathlib import Path
from datetime import date, datetime, timezone

from routes import auth

def test_recovery_ui_spacing_and_back_links():
    text = Path("templates/auth/recuperar.html").read_text(encoding="utf-8")
    assert "Enviar código de recuperación" in text
    assert "Volver al inicio de sesión" in text
    assert "eduturnos-recuperar-final-box" in text
    assert ".eduturnos-recuperar-final-title-row" in text
    assert "margin: 0 0 16px;" in text
    assert "margin-bottom: 14px;" in text


def test_recovery_back_button_matches_institutional_square_and_messages_precede_form():
    text = Path("templates/auth/recuperar.html").read_text(encoding="utf-8")
    title_row = text.split('class="eduturnos-recuperar-final-title-row"', 1)[1]
    messages = text.index('class="eduturnos-recuperar-final-messages"')
    form = text.index('<form', messages)

    assert 'width: 36px !important;' in text
    assert 'height: 36px !important;' in text
    assert 'border-radius: 8px;' in text
    assert '<svg aria-hidden="true" viewBox="0 0 24 24">' in title_row
    assert title_row.index('class="eduturnos-recuperar-final-back account-settings-back"') < title_row.index("<h1>Recuperar acceso</h1>")
    assert messages < form
    assert "margin: 0 0 16px;" in text
    assert 'aria-live="polite"' in text


def test_cancelar_registro_y_volver_a_login_navegan_a_destinos_correctos(monkeypatch):
    from app import app as flask_app

    monkeypatch.setattr(auth, "_sedes", lambda: [])
    monkeypatch.setattr(auth, "_jornadas", lambda: [])
    monkeypatch.setattr(auth, "consultar", lambda *args, **kwargs: [])
    client = flask_app.test_client()

    selection = client.get("/auth/registro")
    assert selection.status_code == 200
    assert b'href="/auth/login"' in selection.data

    for portal in ("estudiante", "acudiente", "docente", "coordinador", "rector"):
        registration = client.get(f"/auth/registro/{portal}")
        assert registration.status_code == 200
        assert b'class="portal-registro-cancel" href="/auth/registro"' in registration.data
        assert b'class="portal-registro-login-link" href="/auth/login"' in registration.data

    login = client.get("/auth/login")
    assert login.status_code == 200


def test_regresos_de_mi_cuenta_son_especificos_y_no_se_agregan_globalmente():
    script = Path("static/js/app.js").read_text(encoding="utf-8")
    styles = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    base = Path("templates/base.html").read_text(encoding="utf-8")

    assert 'titleRow.append(backLink, heading)' not in script
    assert 'backLink.href = "/auth/dashboard"' not in script
    assert ".menu-page-title" not in styles
    assert ".menu-section-back" not in styles
    assert ".account-settings-back" in styles
    assert "20261024_account_back_targeted_v1" in base

    account = Path("templates/cuenta/index.html").read_text(encoding="utf-8")
    password = Path("templates/auth/cambiar_password.html").read_text(encoding="utf-8")
    institution = Path("templates/institucion.html").read_text(encoding="utf-8")
    calendars = Path("templates/integraciones_google.html").read_text(encoding="utf-8")
    assert 'class="account-back-button"' not in account
    assert 'class="password-account-back account-settings-back history-back-button"' in password
    assert 'class="link-back institucion-back account-settings-back history-back-button"' in institution
    assert 'class="account-back-button account-settings-back history-back-button"' in calendars


def test_verificacion_coloca_reenvio_debajo_y_conserva_mismo_diseno():
    template = Path("templates/auth/verificar_codigo.html").read_text(encoding="utf-8")
    actions = template.split('<div class="recovery-code-actions">', 1)[1].split("</div>", 1)[0]

    assert actions.index("Verificar código") < actions.index("Solicitar otro código")
    assert actions.count('class="boton boton-full recovery-code-action"') == 2
    assert 'name="accion" value="reenviar" formnovalidate' in actions
    assert "Iniciar sesión" not in template
    assert "recovery-code-actions{display:grid;gap:12px;" in template


def test_password_change_button_matches_title_width():
    template = Path("templates/auth/cambiar_password.html").read_text(encoding="utf-8")
    styles = Path("static/css/password-controls.css").read_text(encoding="utf-8")
    base = Path("templates/base.html").read_text(encoding="utf-8")

    assert 'class="boton boton-full password-change-submit"' in template
    assert "width: fit-content !important;" in styles
    assert "min-width: 0 !important;" in styles
    assert "v=20261023_account_actions_fit_v2" in base


def test_account_actions_keep_compact_default_button_size():
    account = Path("templates/cuenta/index.html").read_text(encoding="utf-8")
    calendar = Path("templates/integraciones_google.html").read_text(encoding="utf-8")
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")

    assert account.count('class="boton"') == 1
    assert account.count('class="boton secundario"') == 3
    assert "cuenta-action-button" not in account
    assert "height:64px" not in account
    assert "min-height:44px;" in Path("static/css/estilos.css").read_text(encoding="utf-8")
    assert "width: 36px !important;" in responsive
    assert "width: 18px !important;" in responsive
    assert "html body #contenido .integraciones-page .integracion-actions .boton" in calendar
    assert "html body #contenido .integraciones-page .integracion-row > .boton" in calendar
    assert "margin-inline: 0 !important;" in responsive
    assert "margin-inline: -25px !important;" not in responsive


def test_password_change_back_button_stays_aligned_with_title_on_mobile():
    template = Path("templates/auth/cambiar_password.html").read_text(encoding="utf-8")
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")

    assert template.index('class="password-account-back') < template.index("<h1>Cambiar contraseña</h1>")
    assert "flex-flow: row nowrap !important;" in responsive
    assert "width: auto !important;" in responsive
    assert "form-card > .section-heading > .account-subpage-title > h1" in responsive


def test_password_reset_login_link_is_below_save_button_and_uses_blue_text():
    template = Path("templates/auth/restablecer.html").read_text(encoding="utf-8")

    assert "form-top-actions" not in template
    assert template.index("Guardar contraseña") < template.index("Iniciar sesión")
    assert '<div class="restablecer-login-link"><a href="{{ url_for(\'auth.login\') }}">Iniciar sesión</a></div>' in template
    assert ".restablecer-login-link a{color:#2f78ff;" in template


def test_login_illustration_is_restored_only_on_desktop():
    login = Path("templates/auth/login.html").read_text(encoding="utf-8")
    desktop_rules = login.split("@media (min-width: 981px)", 1)[1].split("</style>", 1)[0]
    mobile_styles = Path("static/css/mobile/eduturnos-mobile.css").read_text(encoding="utf-8")

    assert '{% include "_eduturnos_illustration.html" %}' in login
    assert ".login-shell" in desktop_rules
    assert "grid-template-columns: minmax(0, 1fr) minmax(500px, 560px);" in desktop_rules
    assert ".login-desktop-visual" in desktop_rules
    assert "login-desktop-visual" not in mobile_styles


def test_account_title_and_description_align_with_personal_info_heading_on_mobile():
    template = Path("templates/cuenta/index.html").read_text(encoding="utf-8")
    mobile_styles = template.split("@media(max-width:720px)", 1)[1]

    assert ".cuenta-page>.page-head>div{flex:1;min-width:0;padding-left:0;box-sizing:border-box}" in mobile_styles
    assert 'class="account-back-button"' not in template


def test_support_link_opens_prefilled_email_to_institution():
    sidebar = Path("templates/_desktop_sidebar.html").read_text(encoding="utf-8")
    assistant_widget = Path("templates/_asistente_widget.html").read_text(encoding="utf-8")
    route = Path("routes/soporte.py").read_text(encoding="utf-8")
    assert "('soporte.index', 'Ayuda y soporte')" in sidebar
    assert "'soporte.index': 'mail'" in sidebar
    assert "mailto:coliejjfh@hotmail.com" in sidebar
    assert "Hola%2C%20necesito%20ayuda%20con%20EDUTURNOS" in sidebar
    assert "url_for('soporte.index')" not in assistant_widget
    assert "redirect(" in route
    assert "mailto:coliejjfh@hotmail.com" in route
    assert "Hola%2C%20necesito%20ayuda%20con%20EDUTURNOS" in route
    assert not Path("templates/soporte/index.html").exists()


def test_registration_email_domain_blocks_blur_and_tab_until_valid():
    script = Path("static/js/registro.js").read_text(encoding="utf-8")
    template = Path("templates/auth/registro_portal.html").read_text(encoding="utf-8")

    assert 'input[type="email"][pattern]' in script
    assert 'field.addEventListener("keydown"' in script
    assert 'event.key === "Tab" && !validateEmail()' in script
    assert "event.preventDefault();" in script
    assert 'form.addEventListener("pointerdown"' in script
    assert "const focusedEmail = emailFields.find(" in script
    assert "window.requestAnimationFrame(() => field.focus());" in script
    assert 'pattern="{% if portal in (\'estudiante\', \'acudiente\') %}' in template
    assert "@gmail.com" in template
    assert "@jjfh.edu.co" in template


def test_role_dashboard_pages_do_not_show_back_arrows():
    pages = (
        "templates/citas/index.html",
        "templates/citas/nueva.html",
        "templates/calendario/index.html",
        "templates/notificaciones/index.html",
        "templates/estudiantes/lista.html",
        "templates/seguimiento/lista.html",
        "templates/solicitudes/index.html",
        "templates/reportes/index.html",
        "templates/docentes/lista.html",
        "templates/acudientes/lista.html",
        "templates/justificaciones/index.html",
    )
    for page in pages:
        source = Path(page).read_text(encoding="utf-8")
        assert "dashboard_back_button" not in source
        assert "menu-page-back" not in source
        assert "menu-page-heading" in source

    account = Path("templates/auth/cambiar_password.html").read_text(encoding="utf-8")
    public = Path("templates/institucion.html").read_text(encoding="utf-8")
    assert "account-settings-back" in account
    assert "account-settings-back" in public


def test_home_hero_and_recovery_actions_are_raised_and_aligned():
    home = Path("templates/index.html").read_text(encoding="utf-8")
    recovery = Path("templates/auth/recuperar.html").read_text(encoding="utf-8")
    verification = Path("templates/auth/verificar_codigo.html").read_text(encoding="utf-8")
    base = Path("templates/base.html").read_text(encoding="utf-8")

    assert "margin: 0 0 20px !important;" in home
    assert "transform: translateY(-6px) !important;" in home
    assert "translateY(-4px)" in recovery
    assert "eduturnos-recuperar-final-back account-settings-back" in recovery
    assert verification.count('class="boton boton-full recovery-code-action"') == 2
    assert ">Iniciar sesión<" in base


def test_solicitudes_docente_no_duplica_solicitar_y_acudiente_conserva_acceso():
    from flask import render_template
    from app import app as flask_app

    with flask_app.test_request_context("/solicitudes/"):
        docente = render_template(
            "solicitudes/index.html",
            rol="Docente",
            solicitudes=[],
        )
        acudiente = render_template(
            "solicitudes/index.html",
            rol="Acudiente",
            solicitudes=[],
        )

    assert docente.count("+ Solicitar cita") == 1
    assert 'class="btn btn-primary solicitudes-final-seguimiento"' not in docente
    assert acudiente.count("+ Solicitar cita") == 1
    assert 'class="btn btn-primary solicitudes-final-seguimiento"' in acudiente
    assert ".solicitudes-header-actions { margin-top:-8px !important; }" in docente


def test_student_registration_has_no_student_code_field():
    text = Path("templates/auth/registro_portal.html").read_text(encoding="utf-8")
    # The template may render a personal institutional code only conditionally; it must not
    # include a specific student code field.
    assert "codigo_estudiantil" not in text


def test_password_eye_is_loaded_on_base_and_standalone_login():
    app_js = Path("static/js/app.js").read_text(encoding="utf-8")
    base = Path("templates/base.html").read_text(encoding="utf-8")
    login = Path("templates/auth/login.html").read_text(encoding="utf-8")
    password_css = Path("static/css/password-controls.css").read_text(encoding="utf-8")
    password_enhancer = app_js.split("const enhancePasswordFields = () => {", 1)[1].split("\n\t};", 1)[0]
    assert "mobileDialogMedia.matches" not in password_enhancer
    assert "passwordFields.forEach" not in app_js
    assert 'document.querySelectorAll(\'input[type="password"]\')' in app_js
    assert 'filename=\'css/password-controls.css\'' in base
    assert 'filename=\'css/password-controls.css\'' in login
    assert ".password-toggle" in password_css


def test_mobile_navigation_reuses_role_sidebar_as_drawer():
    base = Path("templates/base.html").read_text(encoding="utf-8")
    publico = Path("templates/publico/base_publica.html").read_text(encoding="utf-8")
    portada = Path("templates/index.html").read_text(encoding="utf-8")
    sidebar = Path("templates/_desktop_sidebar.html").read_text(encoding="utf-8")
    app_js = Path("static/js/app.js").read_text(encoding="utf-8")
    sidebar_css = Path("static/css/desktop-sidebar.css").read_text(encoding="utf-8")
    assert "data-mobile-nav-toggle" in base
    assert 'id="eduturnos-mobile-nav"' in sidebar
    assert "data-mobile-nav-backdrop" in base
    assert "mobile-nav-open" in app_js
    assert "mobile-nav-toggle-lines" in sidebar_css
    assert "v=20261024_account_back_targeted_v1" in base
    assert "v=20261026_mobile_recovery_v63" in base
    assert "overflow-y:auto!important" in sidebar_css
    assert "Volver al inicio" not in publico
    assert 'filename=\'js/public-back.js\'' in publico
    assert "history.back()" in Path("static/js/public-back.js").read_text(encoding="utf-8")
    assert "margin-top: auto;" in publico
    assert ".dashboard-assistant[open]>.dashboard-assistant-panel{position:fixed;" in sidebar_css
    assert ".dashboard-assistant[open]>.dashboard-assistant-panel" in sidebar_css
    assert "v=20261026_mobile_recovery_v63" in base
    for template in (publico, portada):
        assert "v=20261026_mobile_recovery_v63" in template


def test_portada_muestra_ilustracion_junto_al_lema_y_login_mantiene_registro_compacto():
    login = Path("templates/auth/login.html").read_text(encoding="utf-8")
    homepage = Path("templates/index.html").read_text(encoding="utf-8")
    register = Path("templates/auth/registro.html").read_text(encoding="utf-8")
    mobile_css = Path("static/css/mobile/eduturnos-mobile.css").read_text(encoding="utf-8")

    assert "width: min(560px, 100%);" in login
    assert "grid-template-columns: minmax(0, 1fr);" in login
    assert 'class="login-visual"' not in login
    assert '<div class="hero-message-row">' in homepage
    assert '{% include "_eduturnos_illustration.html" %}' in homepage
    assert 'class="illustration-svg ill-float"' in Path("templates/_eduturnos_illustration.html").read_text(encoding="utf-8")
    assert "flex: 0 0 200px !important;" in homepage
    assert "flex-basis: 190px !important;" in homepage
    assert "width: 190px !important;" in homepage
    assert "transform: translateX(-20px) !important;" in homepage
    assert "clamp(195px, calc(36vw + 80px), 230px)" in homepage
    assert "clamp(196px, calc(36vw + 80px), 224px)" in homepage
    assert "transform: translateX(-49px) !important;" in homepage
    assert "clamp(173px, calc(33.33vw + 73px), 190px)" in homepage
    assert "@media (min-width: 901px)" in homepage
    assert ".hero-message-row > .hero-illustration {\n            display: none !important;" in homepage
    assert "eduturnos-home-float" in homepage
    assert "flex-basis: 68px !important;" in register
    assert "flex: 0 0 72px !important;" in mobile_css
    assert "height: 32px !important;" in mobile_css


def test_project_layout_uses_fluid_grids_and_safe_table_overflow():
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    assert "minmax(min(100%, 260px), 1fr)" in responsive
    assert "#contenido .table-wrap" in responsive
    assert "overscroll-behavior-inline: contain" in responsive
    assert "@media (max-width: 600px)" in responsive
    assert "font-family" not in responsive
    assert "@media (max-width: 720px) {\n    html body #contenido .directory-page .directory-search > button," in responsive
    assert "padding: 0 !important;\n        line-height: 1 !important;" in responsive
    assert "html body #contenido .page-head:not(.config-section-heading) h1," in responsive
    assert "html body #contenido .integraciones-page > header.page-head {" in responsive
    assert "html body #contenido .cuenta-page > .page-head {" in responsive
    assert "html body #contenido .edc-page > .edc-header {" in responsive
    assert "margin-inline: 0 !important;" in responsive
    assert "font-size: 22px !important;" in responsive
    assert "font-size: 12px !important;" in responsive
    assert responsive.count("display: none !important;") == 1
    assert "visibility: hidden" not in responsive
    dashboard_styles = Path("static/css/dashboard-overview.css").read_text(encoding="utf-8")
    dashboard_layout = dashboard_styles.split(
        "/* Responsive layout adjustments preserve the existing typography. */", 1
    )[1]
    assert "font-family" not in dashboard_layout
    assert "font-size" not in dashboard_layout
    assert "display: none" not in dashboard_layout
    assert "visibility: hidden" not in dashboard_layout


def test_resumen_muestra_seguimiento_en_acceso_rapido():
    dashboard = Path("templates/dashboard.html").read_text(encoding="utf-8")
    sidebar = Path("templates/_desktop_sidebar.html").read_text(encoding="utf-8")
    seguimiento = Path("templates/seguimiento/lista.html").read_text(encoding="utf-8")
    assert 'class="dashboard-quick-link quick-follow-up"' in dashboard
    assert "url_for('seguimiento.lista')" in dashboard
    assert "Compromisos activos" in dashboard
    assert 'class="dashboard-kpi metric-month"' in dashboard
    assert "citas_activas_mes" in dashboard
    assert 'class="dashboard-attention"' in dashboard
    assert 'class="dashboard-attention-item"' in dashboard
    assert "solicitudes_pendientes" in dashboard
    assert "Revisar solicitudes" in dashboard
    assert "Ver seguimiento" in dashboard
    assert "Abrir cita" in dashboard
    overview_styles = Path('static/css/dashboard-overview.css').read_text(encoding='utf-8')
    assert '.dashboard-page.dashboard-overview .dashboard-attention-item .dashboard-attention-action' in overview_styles
    assert 'fecha_actual.isoformat()' in dashboard
    assert 'Vista institucional para coordinar citaciones y compromisos.' in dashboard
    assert 'id="dashboard-mobile-hero-fix"' in dashboard
    assert dashboard.index('class="dashboard-greeting-row"') < dashboard.index('class="dashboard-quick-links"')
    assert 'dashboard-mobile-section-link' not in dashboard
    desktop_styles = Path('static/css/desktop-sidebar.css').read_text(encoding='utf-8')
    assert 'container-type:inline-size;width:100%!important;max-width:1600px!important' in desktop_styles
    assert 'repeat(auto-fit,minmax(min(100%,280px),1fr))' in desktop_styles
    assert '@container (max-width: 900px)' in desktop_styles
    mobile_styles = Path('static/css/dashboard-overview.css').read_text(encoding='utf-8').split('@media (max-width: 900px)', 1)[1]
    assert 'grid-template-columns: repeat(2, minmax(0, 1fr)) !important;' in mobile_styles
    assert 'dashboard-quick-links {\n        display: grid !important;' in mobile_styles
    assert 'class="dashboard-head-action"' not in dashboard
    assert 'class="desktop-sidebar-logout-form"' in sidebar
    assert 'class="desktop-sidebar-account-avatar"' in sidebar
    assert "dar continuidad al acompañamiento de los estudiantes" in seguimiento
    assert 'class="table-wrap seguimiento-historial"' in seguimiento


def test_dashboard_date_uses_colombia_timezone(monkeypatch):
    class FixedDateTime:
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 24, 4, 30, tzinfo=timezone.utc).astimezone(tz)

    monkeypatch.setattr(auth, "datetime", FixedDateTime)

    assert auth._fecha_actual_colombia() == date(2026, 10, 23)


def test_secciones_autenticadas_usan_el_menu_en_lugar_de_botones_volver():
    paginas = (
        "templates/seguimiento/lista.html",
        "templates/estudiantes/lista.html",
        "templates/seguimiento/form.html",
        "templates/estudiantes/form.html",
        "templates/notificaciones/index.html",
        "templates/reportes/index.html",
        "templates/citas/index.html",
        "templates/citas/historial.html",
        "templates/calendario/index.html",
        "templates/solicitudes/index.html",
        "templates/solicitudes/nueva_docente.html",
        "templates/solicitudes/nueva_acudiente.html",
        "templates/importacion/index.html",
        "templates/integraciones_google.html",
    )
    for archivo in paginas:
        texto = Path(archivo).read_text(encoding="utf-8")
        assert "desktop-back-link" not in texto
        assert "← Volver" not in texto
        assert "← Atrás" not in texto
    seguimiento = Path("templates/seguimiento/lista.html").read_text(encoding="utf-8")
    assert "seguimiento-detail-back" not in seguimiento
    assert 'class="seguimiento-detail-close" data-seguimiento-close' in seguimiento


def test_barra_lateral_respeta_roles_y_seccion_activa():
    from flask import render_template
    from app import app

    for rol in ('Rector', 'Administrador / Coordinador', 'Super Admin', 'Docente', 'Estudiante', 'Acudiente'):
        with app.test_request_context('/estudiantes/'):
            html = render_template('_desktop_sidebar.html', usuario_navegacion={'rol_nombre': rol, 'nombres': 'Ana', 'apellidos': 'Perez'})
        assert '/auth/dashboard' in html
        assert '/citas/' in html
        assert ('/citas/nueva' in html) == (rol in ('Rector', 'Administrador / Coordinador', 'Super Admin', 'Docente'))
        assert 'Ver agenda' in html and 'Recordatorios' in html
        assert ('Seguimiento' in html) == (rol in ('Rector', 'Administrador / Coordinador', 'Super Admin', 'Docente'))
        assert ('/reportes/' in html) == (rol in ('Rector', 'Administrador / Coordinador', 'Super Admin'))
        assert ('/estudiantes/' in html) == (rol not in ('Estudiante', 'Acudiente'))
        assert ('aria-current="page"' in html) == (rol not in ('Estudiante', 'Acudiente'))
        assert 'aria-label="Cerrar sesión"' in html
        assert 'desktop-sidebar-logout-form' in html
        assert 'Ayuda y soporte' in html
        assert 'href="mailto:coliejjfh@hotmail.com' in html
        assert 'Bandeja de soporte' not in html
        assert 'Soporte por Gmail' not in html
        assert 'mail.google.com/mail/' not in html
        assert ('/configuracion/' in html) == (rol in ('Rector', 'Super Admin'))
        assert ('/justificaciones/' in html) == (rol in ('Estudiante', 'Acudiente'))
    with app.test_request_context('/auth/login'):
        assert not render_template('_desktop_sidebar.html', usuario_navegacion=None).strip()


def test_pc_organiza_cuenta_catalogos_y_simplifica_calendario():
    calendario = Path('templates/calendario/index.html').read_text(encoding='utf-8')
    configuracion = Path('templates/configuracion/index.html').read_text(encoding='utf-8')
    estilos = Path('static/css/desktop-sidebar.css').read_text(encoding='utf-8')
    controles = Path('static/js/app.js').read_text(encoding='utf-8')
    assert "url_for('citas.nueva', origen='calendario')" not in calendario
    assert 'class="administracion-page"' in configuracion
    assert 'admin-catalog-tabs' in controles
    assert 'panel.hidden = index !== selected' in controles
    assert '"aria-controls", panel.id' in controles
    assert '"ArrowLeft", "ArrowRight", "Home", "End"' in controles
    assert '.cuenta-section{border:0!important' in estilos
    assert '.edc-calendar-card' in estilos
    assert '.enlace-atras' in estilos


def test_catalogos_orden_numerico_y_campos_compactos():
    configuracion = Path('routes/configuracion.py').read_text(encoding='utf-8')
    plantilla_configuracion = Path('templates/configuracion/index.html').read_text(encoding='utf-8')
    estilos_configuracion = Path('static/css/configuracion.css').read_text(encoding='utf-8')
    assert plantilla_configuracion.count('{% block page_styles %}') == 1
    assert 'ORDER BY CAST(nombre AS UNSIGNED), nombre' in configuracion
    assert 'ORDER BY CAST(gr.nombre AS UNSIGNED), gr.nombre, CAST(g.nombre AS UNSIGNED), g.nombre' in configuracion
    orden_jornadas = ("WHEN 'Mañana' THEN 1", "WHEN 'Tarde' THEN 2", "WHEN 'Noche' THEN 3")
    for archivo in ('routes/auth.py', 'routes/docentes.py', 'routes/estudiantes.py'):
        contenido = Path(archivo).read_text(encoding='utf-8')
        posiciones = [contenido.index(parte) for parte in orden_jornadas]
        assert posiciones == sorted(posiciones)
    posiciones = [configuracion.index(parte) for parte in orden_jornadas]
    assert posiciones == sorted(posiciones)
    for archivo in ('routes/estudiantes.py', 'routes/docentes.py'):
        assert 'ORDER BY CAST(gr.nombre AS UNSIGNED),gr.nombre,CAST(g.nombre AS UNSIGNED),g.nombre' in Path(archivo).read_text(encoding='utf-8')
    plantilla = Path('templates/configuracion/index.html').read_text(encoding='utf-8')
    assert 'Activar/desactivar' not in plantilla_configuracion
    assert 'Cambiar</button>' not in plantilla_configuracion
    assert '>Activar</button>' in plantilla_configuracion and '>Desactivar</button>' in plantilla_configuracion
    assert 'field-sizing: content' in estilos_configuracion
    assert 'max-width: 1120px' in estilos_configuracion
    assert 'Ver arquitectura' not in plantilla
    assert 'Ver auditoría' not in plantilla
    assert 'name="nombre" maxlength="180"' in plantilla
    assert '.institucion-form .institution-name input' in estilos_configuracion
    assert 'name="nombre" maxlength="80" required placeholder="Periodo académico 2027"' in plantilla
    assert 'institution-phone' not in plantilla
    assert 'institution-address' not in plantilla
    assert 'institution-status' not in plantilla
    assert '<details class="catalogos-avanzados">' not in plantilla
    assert 'name="descripcion"' not in plantilla
    assert 'border-top:1px solid var(--borde)' not in plantilla
    assert 'type="reset" aria-label="Limpiar formulario"' in plantilla
    assert 'class="state-form state-form-row config-record-form"' in plantilla
    assert 'class="motivo-edit-form config-record-form"' in plantilla
    assert 'Motivos disponibles al crear una citación.' not in plantilla
    assert 'aria-label="Nombre del motivo"' in plantilla
    assert 'class="motivo-edit-form config-record-form"' in plantilla
    app_js = Path('static/js/app.js').read_text(encoding='utf-8')
    assert 'document.querySelector(".administracion-page .configuracion-page")' in app_js


def test_citaciones_pc_reutiliza_detalle_y_conserva_movil():
    plantilla = Path('templates/citas/index.html').read_text(encoding='utf-8')
    controles = Path('static/js/app.js').read_text(encoding='utf-8')
    estilos = Path('static/css/citas-desktop.css').read_text(encoding='utf-8')
    assert 'Citaciones escolares' in plantilla
    assert 'data-citas-search' in plantilla
    assert 'data-citas-state="Realizada"' in plantilla
    assert 'data-desktop-cita-dialog="cita-desktop-detail-{{ cita.id }}"' in plantilla
    assert 'aria-label="Filtrar por estado"' in plantilla
    assert 'value="Realizada">Atendida' in plantilla
    assert 'Historial de seguimiento' in plantilla
    assert 'data-cita-print' in plantilla
    assert 'cita-mobile-summary-row' in plantilla
    assert "+ Nueva citación" not in plantilla
    assert "Nueva citación" not in plantilla
    assert "citas-new-button" not in plantilla
    assert "row.dataset.student.toLocaleLowerCase()" in controles
    assert '@media(min-width:901px)' in estilos


def test_impresion_citacion_es_documento_completo_fuera_del_dialogo():
    plantilla = Path('templates/citas/index.html').read_text(encoding='utf-8')
    controles = Path('static/js/app.js').read_text(encoding='utf-8')
    estilos = Path('static/css/citas-desktop.css').read_text(encoding='utf-8')
    assert 'data-cita-print-content' in plantilla
    for texto in ('Información del estudiante', 'Información del encuentro', 'Responsable', 'Acudiente', 'Observaciones', 'Historial de seguimiento'):
        assert texto in plantilla
    assert "sheet.className = 'cita-print-document'" in controles
    assert 'document.body.append(sheet)' in controles
    assert 'size:A4;margin:14mm' in estilos
    assert 'print-color-adjust:exact' in estilos


def test_reportes_muestra_panorama_movil_y_conserva_filtros_y_detalle():
    plantilla = Path('templates/reportes/index.html').read_text(encoding='utf-8')
    estilos_escritorio = Path('static/css/desktop-sidebar.css').read_text(encoding='utf-8')
    assert 'class="tarjeta reportes-filter"' in plantilla
    assert 'class="tarjeta reportes-results"' in plantilla
    assert 'class="report-mobile-list" id="reportes-lista"' in plantilla
    assert 'class="reportes-page reportes-panorama-activo"' in plantilla
    assert 'class="reportes-panorama-chart"' in plantilla
    assert 'reportes-page.reportes-panorama-activo .reportes-results' in Path(
        'static/css/layout-responsive.css'
    ).read_text(encoding='utf-8')
    assert '.edc-page{width:100%!important;max-width:none!important;margin:0!important;padding:0!important;}' in estilos_escritorio
    assert '\ufeff' not in Path('templates/calendario/index.html').read_text(encoding='utf-8')


def test_cierre_sesion_en_fila_de_identidad():
    base = Path('templates/base.html').read_text(encoding='utf-8')
    lateral = Path('templates/_desktop_sidebar.html').read_text(encoding='utf-8')
    assert 'desktop-header-session' not in base
    assert 'desktop-sidebar-logout-form' in lateral
    assert 'desktop-sidebar-account-avatar' in lateral
    assert 'Acceso institucional' in lateral
    assert 'aria-label="Cerrar sesión"' in lateral
    assert 'Mi cuenta' in lateral
    estilos = Path('static/css/desktop-sidebar.css').read_text(encoding='utf-8')
    assert '.desktop-header-session{display:none;}' in estilos
    assert 'nav{margin-left:auto!important;' in estilos
    assert 'desktop-sidebar-logout-button' in estilos


def test_ayuda_eduturnos_esta_plegada_en_menu_antes_de_mi_cuenta():
    widget = Path('templates/_asistente_widget.html').read_text(encoding='utf-8')
    lateral = Path('templates/_desktop_sidebar.html').read_text(encoding='utf-8')
    base = Path('templates/base.html').read_text(encoding='utf-8')
    app_js = Path('static/js/app.js').read_text(encoding='utf-8')
    assistant_script = Path('static/js/asistente.js').read_text(encoding='utf-8')
    dashboard = Path('templates/dashboard.html').read_text(encoding='utf-8')
    assert 'aria-label="Ayuda y soporte"' in widget
    assert 'data-eduturnos-assistant' in widget
    assert 'id="dashboard-help-title">EDUBOT</strong>' in widget
    assert 'Respuesta inmediata a tus dudas' in widget
    assert '¿En qué puedo ayudarte hoy?' in widget
    assert 'Ayuda EDUTURNOS' in widget
    assert 'data-assistant-clear' not in widget
    assert 'data-assistant-toggle' in widget
    assert 'aria-expanded="false"' in widget
    assert 'data-assistant-open' in widget
    assert 'data-assistant-close' in widget
    assert 'class="assistant-sidebar-toggle"' not in widget
    assert 'class="assistant-sidebar-entry assistant-sidebar-card"' in widget
    assert 'm6 6 12 12M18 6 6 18' in widget
    assert '<strong>Ayuda y soporte</strong>' not in widget
    assert '<small>Pregunta a EDUBOT</small>' in widget
    assert 'Ir al centro de ayuda' not in widget
    assert 'url_for(\'soporte.index\')' not in widget
    assert 'assistant-suggestions' not in widget
    assert 'Las preguntas abiertas se envían a Groq' not in widget
    assert 'Por tu seguridad, no compartas información personal ni documentos.' in widget
    assert 'datos de estudiantes' not in widget
    assert "{% include '_asistente_widget.html' %}" in lateral
    assert "{% include '_asistente_widget.html' %}" not in dashboard
    assert "endpoint != 'auth.dashboard'" not in lateral
    assert 'class="desktop-sidebar-account-link"' in lateral
    assert lateral.index("include '_asistente_widget.html'") < lateral.index('class="desktop-sidebar-account-link"')
    assert 'css/edubot.css' in base
    assert 'js/asistente.js' in base
    assert "request.endpoint != 'soporte.index'" not in base
    assert "css/edubot.css') }}?v=20261023_assistant_compact_v2" in base
    assert "js/asistente.js') }}?v=20261023_assistant_compact_v2" in base
    assert 'setChatOpen(toggleButton.hasAttribute("data-assistant-open"), toggleButton)' in assistant_script
    assert 'if (isOpen) {\n            clearChatPosition();\n        } else {' in assistant_script
    assert 'assistantWidget' not in app_js


def test_edubot_tiene_compositor_compacto_y_sin_indicador_ia():
    widget = Path('templates/_asistente_widget.html').read_text(encoding='utf-8')
    styles = Path('static/css/edubot.css').read_text(encoding='utf-8')

    assert 'IA activa' not in widget
    assert 'Escribe tu pregunta' not in widget
    assert 'placeholder="Mensaje para EDUBOT…"' in widget
    assert 'aria-label="Mensaje para EDUBOT"' in widget
    assert 'width: min(100%, 680px);' in styles
    assert '.dashboard-help-chat[hidden]' in styles
    assert 'flex-direction: row !important;' in styles
    assert 'right: 20px;' in styles
    assert 'bottom: max(20px, env(safe-area-inset-bottom));' in styles
    assert 'cursor: grab;' in styles
    assert 'touch-action: none;' in styles
    assistant_script = Path('static/js/asistente.js').read_text(encoding='utf-8')
    assert 'setPointerCapture(event.pointerId)' in assistant_script
    assert 'localStorage.removeItem(chatPositionKey)' in assistant_script
    assert 'width: min(320px, calc(100vw - 32px));' in styles
    assert 'height: min(400px, calc(100vh - 48px));' in styles
    assert 'Arrastra este encabezado para mover el chat' in widget
    assert 'border-radius: 16px !important;' in styles
    assert '.assistant-clear-button' not in styles
    assert 'height: min(380px, calc(100dvh - 100px));' in styles
    assert '.dashboard-help-chat .assistant-actions button svg' in styles
    assert 'background: #2458e8 !important;' in styles


def test_edubot_local_se_integra_en_ayuda_sin_iframe_externo():
    plantilla = Path('templates/_asistente_widget.html').read_text(encoding='utf-8')
    dashboard = Path('templates/dashboard.html').read_text(encoding='utf-8')
    styles = Path('static/css/edubot.css').read_text(encoding='utf-8')
    script = Path('static/js/asistente.js').read_text(encoding='utf-8')
    environment = Path('.env.example').read_text(encoding='utf-8')
    assert '<iframe' not in plantilla
    assert 'icons/edubot.png' in plantilla
    assert 'data-assistant-suggestion=' not in plantilla
    assert 'assistant-suggestions' not in styles
    base = Path('templates/base.html').read_text(encoding='utf-8')
    assert "js/asistente.js" in base
    assert "defer></script>" in base
    assert 'BOTPRESS_SHARE_URL' not in environment
    assert 'animation' not in plantilla
    assert 'css/edubot.css' in base
    assert 'assistant-mark-float' in styles
    assert 'background: #2458e8' in styles
    assert 'assistant-chat-body[hidden]' in styles
    assert 'prefers-reduced-motion: reduce' in styles
    assert 'data-eduturnos-assistant' in script
    assert 'fetch(root.dataset.endpoint' in script
    assert 'data-assistant-clear' not in script
    assert 'data-assistant-toggle' in script
    assert 'resetConversation' in script
    assert 'new AbortController()' in script
    assert 'dashboard-assistant-panel' not in script


def test_formularios_y_acciones_de_listas_conservan_contexto():
    nueva_cita = Path('templates/citas/nueva.html').read_text(encoding='utf-8')
    docente = Path('templates/docentes/form.html').read_text(encoding='utf-8')
    cambio_password = Path('templates/auth/cambiar_password.html').read_text(encoding='utf-8')
    calendario = Path('templates/calendario/index.html').read_text(encoding='utf-8')
    lista_estudiantes = Path('templates/estudiantes/lista.html').read_text(encoding='utf-8')
    lista_docentes = Path('templates/docentes/lista.html').read_text(encoding='utf-8')
    estudiante_form = Path('templates/estudiantes/form.html').read_text(encoding='utf-8')
    lista_acudientes = Path('templates/acudientes/lista.html').read_text(encoding='utf-8')
    cuenta = Path('templates/cuenta/index.html').read_text(encoding='utf-8')
    css = Path('static/css/desktop-sidebar.css').read_text(encoding='utf-8')
    portada = Path('templates/index.html').read_text(encoding='utf-8')
    mobile_css = Path('static/css/mobile/eduturnos-mobile.css').read_text(encoding='utf-8')
    vistas = (
        'templates/citas/index.html',
        'templates/solicitudes/index.html',
        'templates/calendario/index.html',
        'templates/seguimiento/lista.html',
        'templates/reportes/index.html',
        'templates/estudiantes/lista.html',
        'templates/acudientes/lista.html',
        'templates/docentes/lista.html',
    )
    assert 'type="hidden" name="id_periodo"' in nueva_cita
    assert '<label>Periodo' not in nueva_cita
    assert 'name="area"' not in docente and 'name="asignatura"' in docente
    assert "url_for('cuenta.index')" in cambio_password
    assert 'icon-refresh-link' not in calendario
    assert all('icon-refresh-link' not in Path(vista).read_text(encoding='utf-8') for vista in vistas)
    assert 'Buscar por nombre, sede o grado...' not in lista_estudiantes
    assert 'icon-refresh-link' not in css
    assert '.eduturnos-mes-navegacion{\n  position:static!important;' in css
    assert 'white-space:normal!important;' in css
    assert '.estudiantes-search input' in css
    assert '.tarjeta:has(>form)' in css
    assert '<td class="table-actions-cell" data-label="Acciones"><a href="{{ url_for(\'docentes.editar\'' in lista_docentes
    assert 'url_for(\'docentes.asignaciones\'' not in lista_docentes
    assert 'table-icon-action' not in lista_docentes
    assert '<td class="table-actions-cell" data-label="Acciones"><a href="{{ url_for(\'acudientes.editar\'' in lista_acudientes
    assert 'url_for(\'acudientes.relaciones\'' not in lista_acudientes
    assert '.cuenta-page{width:100%;max-width:1100px' in cuenta
    assert '<label>Periodo' not in estudiante_form
    assert 'type="hidden" name="periodo"' in estudiante_form
    assert '.institution-name > input' in css
    assert 'padding-inline:5px!important' in css
    dashboard_styles = Path('static/css/dashboard-overview.css').read_text(encoding='utf-8')
    assert 'margin-bottom: 7px !important;' in dashboard_styles
    assert '<th>Área</th>' not in lista_docentes
    assert 'url_for(\'docentes.asignaciones\'' not in lista_docentes
    assert 'url_for(\'acudientes.relaciones\'' not in lista_acudientes
    assert portada.count('v=20261026_mobile_recovery_v63') == 2
    assert 'font-size: 16px;' in portada
    assert 'font-size: 14px;' in portada
    assert 'eduturnos-footer-mobile-text' in portada
    assert 'html body .pagina > header.barra > .barra-interior > .nav' in mobile_css
    assert 'html body .pagina > footer .footer-interior .footer-legal-links' in mobile_css


def test_menu_marca_nueva_citacion_sin_marcar_citaciones():
    from flask import render_template, request
    from app import app

    usuario = {'rol_nombre': 'Rector', 'nombres': 'Ana', 'apellidos': 'Perez'}
    endpoint_rule = next(rule for rule in app.url_map.iter_rules() if rule.endpoint == 'citas.nueva')
    with app.test_request_context('/citas/nueva'):
        request.url_rule = endpoint_rule
        html = render_template('_desktop_sidebar.html', usuario_navegacion=usuario)

    assert 'href="/citas/nueva" aria-current="page"' in html
    assert 'href="/citas/" aria-current="page"' not in html


def test_edubot_dashboard_help_se_muestra_a_todos_los_roles_autenticados():
    from flask import render_template
    from app import app

    for rol in ('Rector', 'Administrador / Coordinador', 'Docente', 'Super Admin', 'Estudiante', 'Acudiente'):
        with app.test_request_context('/auth/dashboard'):
            html = render_template(
                '_asistente_widget.html',
                usuario_navegacion={'rol_nombre': rol, 'nombres': 'Ana'},
            )
        assert 'class="dashboard-help"' in html
        assert 'data-eduturnos-assistant' in html
        assert '<iframe' not in html
        assert 'eye.js' not in html
        assert 'El chat todavía no está activado.' not in html
