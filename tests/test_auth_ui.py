from pathlib import Path

def test_recovery_ui_spacing_and_back_links():
    text = Path("templates/auth/recuperar.html").read_text(encoding="utf-8")
    assert "Enviar código de recuperación" in text
    assert "Volver al inicio de sesión" in text
    assert "eduturnos-recuperar-final-box" in text


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
    sidebar = Path("templates/_desktop_sidebar.html").read_text(encoding="utf-8")
    app_js = Path("static/js/app.js").read_text(encoding="utf-8")
    sidebar_css = Path("static/css/desktop-sidebar.css").read_text(encoding="utf-8")
    assert "data-mobile-nav-toggle" in base
    assert 'id="eduturnos-mobile-nav"' in sidebar
    assert "data-mobile-nav-backdrop" in base
    assert "mobile-nav-open" in app_js
    assert "mobile-nav-toggle-lines" in sidebar_css


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
    assert dashboard.index('class="dashboard-greeting-row"') < dashboard.index('class="dashboard-quick-links"')
    assert 'dashboard-mobile-section-link' not in dashboard
    mobile_styles = Path('static/css/dashboard-overview.css').read_text(encoding='utf-8').split('@media (max-width: 900px)', 1)[1]
    assert '.dashboard-page.dashboard-overview .dashboard-quick-links {\n        display: none !important;' in mobile_styles
    assert 'class="dashboard-head-action"' not in dashboard
    assert 'class="desktop-sidebar-logout-form"' in sidebar
    assert 'class="desktop-sidebar-account-avatar"' in sidebar
    assert "dar continuidad al acompañamiento de los estudiantes" in seguimiento
    assert 'class="table-wrap seguimiento-historial"' in seguimiento


def test_paginas_pc_tienen_regreso_al_nivel_anterior():
    destinos = {
        "templates/seguimiento/lista.html": "auth.dashboard",
        "templates/estudiantes/lista.html": "auth.dashboard",
        "templates/seguimiento/form.html": "seguimiento.lista",
        "templates/estudiantes/form.html": "estudiantes.lista",
    }
    for archivo, destino in destinos.items():
        texto = Path(archivo).read_text(encoding="utf-8")
        assert f'class="boton secundario desktop-back-link" href="{{{{ url_for(\'{destino}\') }}}}"' in texto
    seguimiento = Path("templates/seguimiento/lista.html").read_text(encoding="utf-8")
    assert 'class="boton secundario seguimiento-detail-back" data-seguimiento-close' in seguimiento


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
        assert ('/configuracion/' in html) == (rol in ('Rector', 'Super Admin'))
        assert ('/justificaciones/' in html) == (rol in ('Estudiante', 'Acudiente'))
        assert ('aria-current="page"' in html) == (rol not in ('Estudiante', 'Acudiente'))
        assert 'aria-label="Cerrar sesión"' in html
        assert 'desktop-sidebar-logout-form' in html
        assert 'Soporte por Gmail' in html
        assert 'https://mail.google.com/mail/' in html
        assert 'to=coliejjfh@hotmail.com' in html
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
    assert 'size="{{ institucion.nombre|length + 2 if institucion else 24 }}" maxlength="180"' in plantilla
    assert 'size="24" maxlength="80" required placeholder="Periodo académico 2027"' in plantilla
    assert 'institution-phone' not in plantilla
    assert 'institution-address' not in plantilla
    assert 'institution-status' not in plantilla
    assert '<details class="catalogos-avanzados">' not in plantilla
    assert 'name="descripcion"' not in plantilla
    assert 'border-top:1px solid var(--borde)' not in plantilla
    assert 'type="reset" aria-label="Limpiar formulario"' in plantilla
    assert 'class="state-form state-form-row"' in plantilla
    assert 'class="motivo-edit-form"' in plantilla
    assert 'Motivos disponibles al crear una citación.' not in plantilla
    assert 'aria-label="Nombre del motivo"' in plantilla
    assert 'class="motivo-edit-form"' in plantilla
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


def test_reportes_pc_comparte_resumen_y_grafico_con_datos_reales():
    plantilla = Path('templates/reportes/index.html').read_text(encoding='utf-8')
    estilos = Path('static/css/desktop-sidebar.css').read_text(encoding='utf-8')
    assert 'class="reportes-panorama-chart"' in plantilla
    assert 'Citaciones por estado' in plantilla
    assert '{% set escala = ((maximo + 3) // 4) * 4 %}' in plantilla
    assert 'nivel * (escala // 4)' in plantilla
    assert '|round(1)' not in plantilla
    assert '.reportes-page.reportes-panorama-activo .reportes-results' in estilos
    assert '.edc-page{width:100%!important;max-width:none!important;margin:0!important;padding:0!important;}' in estilos
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


def test_ayuda_lateral_pc_conserva_ubicacion_movil():
    controles = Path('static/js/app.js').read_text(encoding='utf-8')
    asistente = Path('static/js/asistente.js').read_text(encoding='utf-8')
    assert 'sidebarNavigation.after(assistantWidget)' in controles
    assert 'originalParent.insertBefore(assistantWidget, originalNext)' in controles
    assert 'if (!form || !input || !output) return;' in asistente
    widget = Path('templates/_asistente_widget.html').read_text(encoding='utf-8')
    lateral = Path('templates/_desktop_sidebar.html').read_text(encoding='utf-8')
    dashboard = Path('templates/dashboard.html').read_text(encoding='utf-8')
    assert 'class="assistant-desktop-label">Ayuda</span>' in widget
    assert 'class="assistant-chat-header"' in widget
    assert lateral.index('Soporte por Gmail') < lateral.index("include '_asistente_widget.html'")
    assert "endpoint != 'auth.dashboard'" not in lateral
    assert "include '_asistente_widget.html'" not in dashboard
    assert 'class="desktop-sidebar-account-link"' in lateral


def test_cuenta_alinea_acciones_y_ayuda_prepara_chat():
    estilos = Path('static/css/desktop-sidebar.css').read_text(encoding='utf-8')
    plantilla = Path('templates/_asistente_widget.html').read_text(encoding='utf-8')
    controles = Path('static/js/asistente.js').read_text(encoding='utf-8')
    assert '.cuenta-section:has(>a.boton){display:grid;grid-template-rows:auto 1fr auto' in estilos
    assert 'height:38px;min-height:38px' in estilos
    assert 'role="log"' in plantilla
    assert '{% if not asistente_disponible %}disabled{% endif %}' in plantilla
    assert 'button.disabled = input.disabled || !input.value.trim()' in controles
    for control in ('data-assistant-clear', 'data-assistant-expand', 'data-assistant-close', 'data-assistant-greeting'):
        assert control in plantilla


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
    assert 'Editar</a> ·' not in lista_docentes
    assert 'table-icon-action' not in lista_docentes
    assert '.cuenta-page{width:100%;max-width:1100px' in cuenta
    assert '<label>Periodo' not in estudiante_form
    assert 'type="hidden" name="periodo"' in estudiante_form
    assert '.institution-name > input' in css
    assert 'padding-inline:5px!important' in css
    dashboard_styles = Path('static/css/dashboard-overview.css').read_text(encoding='utf-8')
    assert 'margin-bottom: 7px !important;' in dashboard_styles
    assert '<th>Área</th>' not in lista_docentes
    assert '>Editar</a>' in lista_docentes and 'Asignaciones</a>' not in lista_docentes
    assert '>Editar</a>' in lista_acudientes and 'Estudiantes</a>' not in lista_acudientes
    assert portada.count('v=20261013_public_mobile_nav_v55') == 2
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


def test_beepy_ayuda_para_todos_los_roles_sin_script_externo_en_modulos():
    from flask import render_template
    from app import app

    for rol in ('Rector', 'Administrador / Coordinador', 'Docente', 'Super Admin', 'Estudiante', 'Acudiente'):
        with app.test_request_context('/auth/dashboard'):
            html = render_template('_asistente_widget.html', usuario={'rol_nombre': rol}, beepy_disponible=True)
        assert 'data-beepy-frame' in html
        assert 'referrerpolicy="no-referrer"' in html
        assert 'Abrir EDUBOT' not in html
        assert 'target="_blank"' not in html
        assert 'eye.js' not in html
        assert 'El chat todavía no está activado.' not in html
