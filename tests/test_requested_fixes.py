import re
from contextlib import contextmanager
from types import SimpleNamespace
from pathlib import Path

import pytest
from flask import render_template

from app import app
from roles import es_documento_valido
from routes import acudientes as acudientes_routes, citas as citas_routes, docentes as docentes_routes, estudiantes
from routes import helpers as route_helpers


def _student_form(**overrides):
    values = {
        "tipo_documento": "CC",
        "documento": "123456789",
        "nombres": "Ana María",
        "apellidos": "Pérez López",
        "sede": "1",
        "jornada": "1",
        "periodo": "1",
        "grado": "",
        "grupo": "",
    }
    values.update(overrides)
    return values


@pytest.mark.parametrize("documento,valid", [
    ("123456789", True),
    ("0", True),
    ("1" * 30, True),
    ("1" * 31, False),
    ("12A45", False),
    ("١٢٣٤٥", False),
    ("", False),
])
def test_documento_solo_acepta_digitos_hasta_el_limite_de_base(documento, valid):
    assert es_documento_valido(documento) is valid


def test_formulario_estudiante_rechaza_documento_no_numerico():
    error = estudiantes.validar_formulario(_student_form(documento="ABC123"))

    assert error == "El documento debe contener solo dígitos y no superar 30 caracteres."


def test_formulario_estudiante_rechaza_nombres_con_numeros():
    error = estudiantes.validar_formulario(_student_form(nombres="Ana 2"))

    assert error == "Los nombres y apellidos solo pueden contener letras y espacios."


def test_grupo_se_valida_contra_el_grado(monkeypatch):
    consultas = []
    monkeypatch.setattr(
        estudiantes,
        "consultar",
        lambda sql, params, uno=False: consultas.append((sql, params, uno)) or {"id": 18},
    )

    assert estudiantes.validar_formulario(_student_form(grado="6", grupo="18")) is None
    assert consultas[0][1] == ("18", "6")
    assert consultas[0][2] is True


def test_grupo_de_otro_grado_no_pasa_validacion(monkeypatch):
    monkeypatch.setattr(estudiantes, "consultar", lambda *args, **kwargs: None)

    error = estudiantes.validar_formulario(_student_form(grado="6", grupo="24"))

    assert error == "El grupo seleccionado no corresponde al grado."


def test_registro_conserva_campos_y_aplica_reglas_de_password_y_documento():
    template = Path("templates/auth/registro_portal.html").read_text(encoding="utf-8")
    script = Path("static/js/registro.js").read_text(encoding="utf-8")
    passwords = re.findall(r'<input\b[^>]*type="password"[^>]*>', template, re.DOTALL)

    assert len(passwords) == 3
    assert all('minlength="12"' in field and 'maxlength="15"' in field for field in passwords)
    assert 'La contraseña debe tener entre 12 y 15 caracteres.' in template
    assert 'class="portal-registro-back"' not in template
    assert 'class="portal-registro-cancel"' in template
    assert 'class="portal-registro-login-link"' in template
    assert 'data-form-values="{{ datos|tojson|forceescape }}"' in template
    assert "@gmail" in template
    assert "@jjfh.edu.co" in template
    assert 'field.type === "password"' in script
    assert "field.value = values[field.name]" in script
    assert 'field.addEventListener("blur"' in script
    assert "field.reportValidity()" in script
    assert "option.dataset.idGrado === gradeId" in script
    assert 'groupSelect.disabled = !gradeId' in script


def test_correos_de_acudiente_y_personal_se_validan_sin_texto_auxiliar():
    acudientes = Path("templates/acudientes/form.html").read_text(encoding="utf-8")
    docentes = Path("templates/docentes/form.html").read_text(encoding="utf-8")
    recuperar = Path("templates/auth/recuperar.html").read_text(encoding="utf-8")

    assert 'pattern="[^@\\s]+@[gG][mM][aA][iI][lL]\\.[cC][oO][m]"' in acudientes
    assert 'pattern="[^@\\s]+@[jJ][jJ][fF][hH]\\.[eE][dD][uU]\\.[cC][oO]"' in docentes
    assert 'pattern="[^@\\s]+@([gG][mM][aA][iI][lL]\\.[cC][oO][m]|[jJ][jJ][fF][hH]\\.[eE][dD][uU]\\.[cC][oO])"' in recuperar


@pytest.mark.parametrize(
    ("portal", "domain_pattern"),
    [
        ("estudiante", r"[^@\s]+@[gG][mM][aA][iI][lL]\.[cC][oO][m]"),
        ("acudiente", r"[^@\s]+@[gG][mM][aA][iI][lL]\.[cC][oO][m]"),
        ("docente", r"[^@\s]+@[jJ][jJ][fF][hH]\.[eE][dD][uU]\.[cC][oO]"),
    ],
)
def test_registro_renderiza_el_dominio_de_correo_correspondiente(portal, domain_pattern):
    with app.test_request_context(f"/auth/registro/{portal}"):
        html = render_template(
            "auth/registro_portal.html",
            portal=portal,
            info={"descripcion": "Registro"},
            datos={},
            sedes=[],
            jornadas=[],
            grados=[],
            grupos=[],
            csrf_token=lambda: "csrf-test",
        )

    assert f'pattern="{domain_pattern}"' in html


@pytest.mark.parametrize("portal", ["estudiante", "acudiente"])
def test_registro_filtra_grupos_por_grado_para_ambos_portales(portal):
    grupos = [
        SimpleNamespace(id=18, id_grado=6, nombre="1"),
        SimpleNamespace(id=24, id_grado=7, nombre="1"),
    ]
    with app.test_request_context(f"/auth/registro/{portal}"):
        html = render_template(
            "auth/registro_portal.html",
            portal=portal,
            info={"descripcion": "Registro"},
            datos={},
            sedes=[],
            jornadas=[],
            grados=[
                SimpleNamespace(id=6, nombre="6"),
                SimpleNamespace(id=7, nombre="7"),
            ],
            grupos=grupos,
            csrf_token=lambda: "csrf-test",
        )

    grado_name = "estudiante_id_grado" if portal == "acudiente" else "id_grado"
    assert f'data-grupo-de="{grado_name}"' in html
    assert 'data-id-grado="6"' in html
    assert 'data-id-grado="7"' in html


def test_mensaje_de_verificacion_separa_el_formulario_en_escritorio_y_movil():
    template = Path("templates/auth/verificar_codigo.html").read_text(encoding="utf-8")

    assert "#contenido:has(.verification-code-page) > .alerta{margin-bottom:14px!important;}" in template
    assert "#contenido .verification-code-page{padding-top:14px!important;}" in template


def test_barra_movil_mantiene_mes_flechas_y_hoy_en_una_fila():
    mobile = Path("static/css/mobile/eduturnos-mobile.css").read_text(encoding="utf-8")
    calendar = Path("templates/calendario/index.html").read_text(encoding="utf-8")

    assert "grid-template-columns: minmax(0, 1fr) auto !important;" in mobile
    assert not re.search(
        r"html body #contenido \.edc-page \.eduturnos-barra-real \.eduturnos-hoy\s*\{[^}]*grid-row:\s*2",
        mobile,
    )
    assert "eduturnos-barra-mes-correccion-final" not in calendar


def test_formulario_estudiante_renderiza_selector_grado_grupo():
    catalogs = {
        "sedes": [SimpleNamespace(id=1, nombre="Sede Principal")],
        "jornadas": [SimpleNamespace(id=1, nombre="Mañana")],
        "periodos": [SimpleNamespace(id=1)],
        "grados": [SimpleNamespace(id=6, nombre="6")],
        "grupos": [SimpleNamespace(id=18, id_grado=6, nombre="1")],
    }
    with app.test_request_context("/estudiantes/nuevo"):
        html = render_template(
            "estudiantes/form.html",
            catalogos=catalogs,
            estudiante=None,
            datos={},
        )

    assert 'id="grado" name="grado"' in html
    assert 'data-grade="6" data-group-number="1"' in html
    assert ">Selecciona un grupo</option>" in html


def test_lista_movil_estudiante_respeta_permisos_de_gestion():
    student = SimpleNamespace(
        id_estudiante=12,
        nombres="Ana",
        apellidos="Pérez",
        documento="123456",
        grado="6",
        grupo="1",
        curso="6A",
        sede="Principal",
        jornada="Mañana",
        acudiente="Laura Pérez",
        estado="Activo",
    )
    with app.test_request_context("/estudiantes/"):
        html = render_template(
            "estudiantes/lista.html",
            estudiantes=[student],
            q="",
            puede_gestionar=False,
        )

    assert "Laura Pérez" in html
    assert "Documento" in html
    assert "Mañana" in html
    assert 'class="directory-desktop-detail"' in html
    assert "Grado" in html
    assert "Principal" in html
    assert "Editar" not in html
    assert "Registrar estudiante" not in html
    assert 'class="directory-page"' in html
    assert 'class="directory-table"' in html


def test_estudiante_nuevo_genera_codigo_y_ya_no_pide_curso():
    template = Path("templates/estudiantes/form.html").read_text(encoding="utf-8")
    route = Path("routes/estudiantes.py").read_text(encoding="utf-8")

    assert 'name="curso"' not in template
    assert 'name="codigo"' not in template
    assert "codigo_temporal()" in route
    assert "codigo_final(eid)" in route
    assert 'placeholder="EST_" readonly' in template
    assert "Solo dígitos; máximo 30." not in template
    assert "máximo 30)." not in template


def test_crear_estudiante_asigna_codigo_automatico_en_la_misma_transaccion(monkeypatch):
    from routes import helpers

    class Cursor:
        lastrowid = 143

        def __init__(self):
            self.statements = []

        def execute(self, sql, params):
            self.statements.append((sql, params))

        def close(self):
            pass

    cursor = Cursor()
    connection = SimpleNamespace(cursor=lambda: cursor)
    monkeypatch.setattr(estudiantes, "catalogos", lambda: {})
    monkeypatch.setattr(estudiantes, "auditoria", lambda *args, **kwargs: None)
    monkeypatch.setattr(estudiantes, "codigo_final", lambda student_id: f"EST_{student_id:05d}")
    monkeypatch.setattr(helpers, "usuario_actual", lambda: {"rol_nombre": "Rector"})

    @contextmanager
    def transaction():
        yield connection

    monkeypatch.setattr(estudiantes, "transaccion", transaction)
    with app.test_request_context("/estudiantes/nuevo", method="POST", data=_student_form()):
        response = estudiantes.nuevo()

    assert response.status_code == 302
    assert cursor.statements[0][0].startswith("INSERT INTO estudiantes")
    assert "curso" not in cursor.statements[0][0]
    assert cursor.statements[1] == (
        "UPDATE estudiantes SET codigo_estudiantil=%s WHERE id_estudiante=%s",
        ("EST_00143", 143),
    )


def test_forms_preserve_fields_on_validation_errors_without_storing_passwords():
    template = Path("templates/base.html").read_text(encoding="utf-8")
    script = Path("static/js/form-preserve.js").read_text(encoding="utf-8")

    assert "js/form-preserve.js" in template
    assert "sessionStorage" in script
    assert 'field.type !== "password"' in script
    assert 'field.type !== "hidden"' in script
    assert "errorNotice" in script


def test_botones_de_mi_cuenta_conservan_tamano_compacto_sin_flecha_extra():
    template = Path("templates/cuenta/index.html").read_text(encoding="utf-8")

    assert template.count('class="boton"') == 1
    assert template.count('class="boton secundario"') == 3
    assert 'class="account-back-button"' not in template
    assert "cuenta-action-button" not in template
    assert "height:64px!important;" not in template


def test_homepage_hero_title_and_copy_are_lifted_together():
    homepage = Path("templates/index.html").read_text(encoding="utf-8")
    row_styles = homepage.split("html body.public-home-page .hero-message-row {", 1)[1].split("}", 1)[0]
    title_styles = homepage.split("html body.public-home-page .hero-message-row h1", 1)[1].split("}", 1)[0]
    copy_styles = homepage.split("html body.public-home-page .hero-texto", 1)[1].split("}", 1)[0]

    assert "transform: translateY(-10px) !important;" in row_styles
    assert "transform: none !important;" in title_styles
    assert "transform: translateY(-12px) !important;" in copy_styles
    assert "margin: 0 0 12px !important;" in row_styles
    illustration_styles = homepage.split(
        '<style id="eduturnos-home-hero-illustration">', 1
    )[1]
    mobile_styles = illustration_styles.split(
        "@media (max-width: 900px)", 1
    )[1].split("}", 1)[0]
    assert "margin-bottom: 10px !important;" in mobile_styles
    assert "Descargar app Android" not in homepage
    assert "downloads/EDUTURNOS-Android-v1.1.apk" not in homepage


def test_recovery_illustration_keeps_mobile_proportions():
    recovery = Path("templates/auth/recuperar.html").read_text(encoding="utf-8")
    mobile = Path("static/css/mobile/eduturnos-mobile.css").read_text(encoding="utf-8")
    illustration = recovery.split(
        "@media (max-width: 760px)", 1
    )[1].split("</style>", 1)[0]

    assert "min-height: 120px;" in illustration
    assert "width: 200px;" in illustration
    assert "height: 180px;" in illustration
    assert ".eduturnos-recovery-art-content" in illustration
    assert "width: 166px;" in illustration
    assert "height: 166px;" in illustration
    assert "width: 300px;" in illustration
    assert "height: 270px;" in illustration
    assert "transform: translate(-50%, -50%) scale(.72);" in illustration
    assert "width: 72px;" in recovery
    assert "height: 66px;" in recovery
    assert "width: 34px;" in recovery
    assert "height: 35px;" in recovery
    assert "width: 9px;" in recovery
    assert "height: 18px;" in recovery
    assert "min-height: 190px !important;" in mobile.split(
        "html body #contenido .eduturnos-recuperar-final-illustration", 1
    )[1].split("}", 1)[0]


def test_recovery_page_is_not_cached_by_the_browser():
    response = app.test_client().get("/auth/recuperar")

    assert response.headers["Cache-Control"] == "no-store"


def test_mobile_account_creation_choices_share_one_button_style():
    mobile_css = Path("static/css/mobile/eduturnos-mobile.css").read_text(encoding="utf-8")

    assert "html body.auth-page .registro-pagina .registro-grid .registro-opcion .registro-boton" in mobile_css
    assert "width: 72px !important;" in mobile_css
    assert "height: 32px !important;" in mobile_css
    assert "background: #2f78ff !important;" in mobile_css


def test_requested_account_calendar_search_and_followup_navigation():
    cuenta = Path("templates/cuenta/index.html").read_text(encoding="utf-8")
    calendarios = Path("templates/integraciones_google.html").read_text(encoding="utf-8")
    institucion = Path("templates/institucion.html").read_text(encoding="utf-8")
    estudiantes = Path("templates/estudiantes/lista.html").read_text(encoding="utf-8")
    seguimiento = Path("templates/seguimiento/lista.html").read_text(encoding="utf-8")
    seguimiento_form = Path("templates/seguimiento/form.html").read_text(encoding="utf-8")

    assert "← Panel" not in cuenta
    assert calendarios.count('">Conectar</a>') == 2
    assert 'class="link-back institucion-back account-settings-back history-back-button"' in institucion
    assert 'aria-label="Volver al inicio"' in institucion
    assert "url_for('cuenta.index')" not in institucion
    assert 'class="directory-search-all"' in estudiantes
    assert "data-mobile-cita-url" not in seguimiento
    assert "data-mobile-cita-url" not in seguimiento_form


def test_calendar_stylesheet_has_valid_rule_boundary_before_page_descendants():
    calendar = Path("templates/calendario/index.html").read_text(encoding="utf-8")
    page_rule = calendar.split(".edc-page {", 1)[1].split(".edc-page *,", 1)[0]

    assert page_rule.rstrip().endswith("}")


def test_teacher_and_guardian_directories_have_search_and_show_all_controls():
    teachers = Path("templates/docentes/lista.html").read_text(encoding="utf-8")
    guardians = Path("templates/acudientes/lista.html").read_text(encoding="utf-8")
    students = Path("templates/estudiantes/lista.html").read_text(encoding="utf-8")
    teacher_route = Path("routes/docentes.py").read_text(encoding="utf-8")
    guardian_route = Path("routes/acudientes.py").read_text(encoding="utf-8")

    for template, endpoint in (
        (teachers, "docentes.lista"),
        (guardians, "acudientes.lista"),
        (students, "estudiantes.lista"),
    ):
        assert 'role="search"' in template
        assert 'name="q"' in template
        assert f"url_for('{endpoint}')" in template
        assert "Mostrar todos" in template
        assert "directory-new" in template
        assert 'aria-label="Buscar"' in template
    assert "d.correo_institucional LIKE %s" in teacher_route
    assert "documento LIKE %s" in guardian_route
    assert 'class="directory-table"' in teachers
    assert 'class="directory-table"' in guardians
    assert 'data-label="Correo institucional"' in teachers
    assert 'data-label="Documento"' in guardians
    for label in ("Teléfono", "Estudiantes", "Grado / Grupo", "Sede", "Jornada", "Acciones"):
        assert f'data-label="{label}"' in teachers
        assert f'data-label="{label}"' in guardians
    assert 'url_for(\'docentes.editar\'' in teachers
    assert 'url_for(\'acudientes.editar\'' in guardians
    assert "Asignaciones" not in teachers
    assert "url_for('acudientes.relaciones'" not in guardians


def test_teacher_and_guardian_directories_load_associated_school_data(monkeypatch):
    queries = []
    monkeypatch.setattr(
        route_helpers,
        "usuario_actual",
        lambda: {"rol_nombre": "Rector"},
    )

    def capture_query(sql, params, uno=False):
        queries.append((sql, params))
        return []

    monkeypatch.setattr(docentes_routes, "consultar", capture_query)
    monkeypatch.setattr(acudientes_routes, "consultar", capture_query)

    with app.test_request_context("/docentes/"):
        docentes_routes.lista()
    with app.test_request_context("/acudientes/"):
        acudientes_routes.lista()

    teacher_sql, teacher_params = queries[0]
    guardian_sql, guardian_params = queries[1]
    assert "FROM asignaciones_docentes ad" in teacher_sql
    assert "GROUP_CONCAT(DISTINCT CONCAT(e.nombres,' ',e.apellidos)" in teacher_sql
    assert "grados_grupos" in teacher_sql and "j.nombre jornada" in teacher_sql
    assert len(teacher_params) == 8
    assert "LEFT JOIN estudiante_acudiente ea" in guardian_sql
    assert "GROUP_CONCAT(DISTINCT CONCAT(e.nombres,' ',e.apellidos)" in guardian_sql
    assert all(field in guardian_sql for field in ("grados_grupos", "s.nombre", "j.nombre"))
    assert len(guardian_params) == 4


def test_mobile_directories_keep_records_in_one_box_and_student_controls_in_one_row():
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")

    assert ".directory-page .table-wrap" in responsive
    assert "border-radius: 0 !important;" in responsive
    assert "flex-flow: row nowrap !important;" in responsive
    assert "flex: 1 1 0% !important;" in responsive
    assert "background: transparent !important;" in responsive


def test_mobile_directory_rows_remain_horizontal_and_compact():
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    students = Path("templates/estudiantes/lista.html").read_text(encoding="utf-8")

    assert "table.directory-table tbody tr {" in responsive
    assert "display: table-row !important;" in responsive
    assert "overflow-x: auto !important;" in responsive
    assert "padding: 10px 14px !important;" in responsive
    assert "html body.has-desktop-sidebar #contenido .directory-page table.directory-table tbody tr {" not in responsive
    assert 'class="directory-table"' in students
    assert 'class="estudiantes-mobile-legacy"' not in students


def test_mobile_seguimiento_spacing_and_section_titles_are_consistent():
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    assert "html body #contenido .seguimiento-page-head" in responsive
    assert "padding-top: 10px !important;" in responsive
    assert "html body #contenido .page-head:not(.config-section-heading)" in responsive
    assert "html body #contenido .section-heading" in responsive
    assert "html body #contenido .institucion-heading" in responsive
    assert "html body #contenido .edc-header" in responsive
    assert "margin-bottom: 8px !important;" in responsive
    assert "html body #contenido .seguimiento-procesos" in responsive
    assert "margin-top: 0 !important;" in responsive


def test_student_name_and_mobile_directory_icons_match_shared_directory_style():
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    students = Path("templates/estudiantes/lista.html").read_text(encoding="utf-8")

    assert 'class="directory-table"' in students
    assert "table.directory-table tbody td:first-child a" in responsive
    assert "color: #17365d !important;" in responsive
    assert "width: 22px !important;" in responsive
    assert "font-size: 22px !important;" in responsive
    assert "transform: none !important;" in responsive
    assert "flex: 0 0 56px !important;" in responsive
    assert "width: 56px !important;" in responsive


def test_cancel_new_citation_clears_form_without_navigation_or_submission():
    template = Path("templates/citas/nueva.html").read_text(encoding="utf-8")

    assert '<form method="post"' in template
    assert '<button class="boton" type="submit">Crear citación</button>' in template
    assert '<button class="boton secundario" type="reset">Cancelar</button>' in template
    assert 'class="boton secundario" href=' not in template


def test_back_buttons_use_same_origin_history_and_student_picker_is_spaced():
    back_script = Path("static/js/public-back.js").read_text(encoding="utf-8")
    account = Path("templates/cuenta/index.html").read_text(encoding="utf-8")
    password = Path("templates/auth/cambiar_password.html").read_text(encoding="utf-8")
    institution = Path("templates/institucion.html").read_text(encoding="utf-8")
    calendar = Path("templates/integraciones_google.html").read_text(encoding="utf-8")
    config = Path("templates/configuracion/index.html").read_text(encoding="utf-8")
    citations = Path("templates/citas/nueva.html").read_text(encoding="utf-8")
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    base = Path("templates/base.html").read_text(encoding="utf-8")

    assert 'class="account-back-button"' not in account
    assert 'class="account-subpage-title"' in password
    assert 'account-settings-back' in password
    assert '<span>Mi cuenta</span>' not in password
    assert 'class="institucion-title-row"' in institution
    assert 'account-settings-back' in institution
    assert 'class="account-back-button account-settings-back history-back-button"' in calendar
    assert "flex-direction:row!important" in calendar
    assert "flex-wrap:nowrap!important" in calendar
    assert "width:0!important" in calendar
    assert 'config-page-title' in config
    assert 'config-institution-back account-settings-back history-back-button' in config
    assert '".link-back"' in back_script
    assert "new URL(document.referrer).origin === location.origin" in back_script
    assert "history.back();" in back_script
    assert 'class="citation-student-field"' in citations
    assert 'class="citation-student-select"' in citations
    assert "citation-student-field" not in responsive
    assert "max-height: 36px !important;" in responsive
    assert "html body.has-desktop-sidebar #contenido .password-account-back" in responsive
    assert "v=20261021_public_back_v3" in base
    agenda = Path("templates/calendario/index.html").read_text(encoding="utf-8")
    assert "grid-template-columns: repeat(2, minmax(0, 1fr)) !important;" in agenda
    assert "max-height: 36px !important;" in agenda


def test_new_citation_picker_shows_name_grade_and_jornada_without_personal_details(monkeypatch):
    queries = []
    monkeypatch.setattr(
        citas_routes,
        "consultar",
        lambda sql, *args, **kwargs: (queries.append(sql), [])[1],
    )

    catalogs = citas_routes.catalogos()
    template = Path("templates/citas/nueva.html").read_text(encoding="utf-8")

    assert catalogs["estudiantes"] == []
    assert catalogs["docentes"] == []
    assert catalogs["acudientes"] == []
    assert "e.documento" not in queries[0]
    assert "grado" in queries[0] and "jornada.nombre AS jornada" in queries[0]
    assert "GROUP_CONCAT" in queries[1] and "jornada.nombre AS jornada" in queries[1]
    assert "GROUP_CONCAT" in queries[2] and "contexto.jornadas AS jornada" in queries[2]
    for persona in ("e", "d", "a"):
        assert f"{persona}.grado" in template
        assert f"{persona}.jornada" in template
    assert "e.documento" not in template
    assert ".sede" not in template
    assert "detalle" not in template
    assert ".citation-student-select" not in Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    assert ".citation-student-select" not in Path("static/css/mobile/eduturnos-mobile.css").read_text(encoding="utf-8")


def test_requested_visual_updates_are_present():
    assistant = Path("templates/_asistente_widget.html").read_text(encoding="utf-8")
    home = Path("templates/index.html").read_text(encoding="utf-8")
    verification = Path("templates/auth/verificar_codigo.html").read_text(encoding="utf-8")
    account = Path("templates/cuenta/index.html").read_text(encoding="utf-8")

    assert "no compartas información personal ni documentos" in assistant
    assert "flex-basis: 190px !important;" in home
    assert "transform: translateX(-20px) !important;" in home
    assert "width: clamp(196px, calc(36vw + 80px), 224px) !important;" in home
    assert "verification-code-page" in verification
    assert "Solicitar otro código" in verification
    assert "Iniciar sesión" not in verification
    assert "margin-bottom:14px!important" in verification
    assert account.count('class="boton"') == 1
    assert account.count('class="boton secundario"') == 3
    assert "cuenta-action-button" not in account


def test_mobile_menu_reopens_at_the_top_with_all_links_scrollable():
    app_js = Path("static/js/app.js").read_text(encoding="utf-8")
    sidebar_css = Path("static/css/desktop-sidebar.css").read_text(encoding="utf-8")
    base = Path("templates/base.html").read_text(encoding="utf-8")

    assert "mobileNav.scrollTop = 0;" in app_js
    assert "navigation.scrollTop = 0;" in app_js
    assert "z-index:1201!important;" in sidebar_css
    assert "flex:1 1 0%!important;min-height:0!important;" in sidebar_css
    assert "overflow-y:auto!important;overscroll-behavior:contain!important;" in sidebar_css
    assert ".dashboard-assistant[open]>.dashboard-assistant-panel{position:fixed;" in sidebar_css
    assert ".dashboard-assistant[open]>.dashboard-assistant-panel" in sidebar_css
    assert "grid-template-rows:auto auto auto minmax(0,1fr) auto auto!important;" in sidebar_css
    assert "padding:0 18px!important;z-index:40;" in sidebar_css
    assert "requestAnimationFrame(resetNavigationScroll)" in app_js
    assert "a[aria-current=\"page\"]" in app_js
    assert "v=20261024_account_back_targeted_v1" in base


def test_configuration_catalog_forms_follow_motives_layout_without_changing_institution_periods():
    template = Path("templates/configuracion/index.html").read_text(encoding="utf-8")
    css = Path("static/css/configuracion.css").read_text(encoding="utf-8")

    assert 'config-entry-form config-entry-sede' in template
    assert 'config-entry-form config-entry-grupo' in template
    assert 'class="config-record-form config-record-grupo"' in template
    assert 'class="motivo-edit-form config-record-form"' in template
    assert 'class="state-form state-form-row config-record-form"' in template
    assert "config-record-actions" in template
    assert "20261021_mobile_config_v28" in template
    assert ".configuracion-page .config-entry-form," in css
    assert "height: 38px !important;" in css
    assert "flex: 0 0 108px !important;" in css
    assert ".configuracion-page .config-record-form," in css
    assert "grid-template-columns: minmax(0, 1fr) minmax(72px, 92px) !important;" in css
    assert "background: #2f78ff !important;" in css
    assert "config-entry-form" not in template.split('action="{{ url_for(\'configuracion.nuevo_periodo\') }}"', 1)[1].split("</form>", 1)[0]
    assert "config-entry-form" not in template.split('action="{{ url_for(\'configuracion.guardar_institucion\') }}"', 1)[1].split("</form>", 1)[0]
    assert 'class="config-institution-back account-settings-back history-back-button"' in template
    assert ".configuracion-page .institucion-form .institution-name input," in css
    assert "font-size: 24px !important;" in css
    assert "field-sizing: fixed !important;" in css
    assert "min-width: 92px !important;" in css
    assert "config-entry-sede > label:nth-of-type(3)" in css
    assert "config-entry-sede > label:nth-of-type(4)" in css
    assert "flex: 1 1 0 !important;" in css
    assert "config-record-sede > label:nth-of-type(3)" in css
    assert "grid-template-rows: 14px 40px !important;" in css
    assert "grid-column: 1 / -1 !important;" in css
    excluded_sections = template.split('<h2>Institución</h2>', 1)[0].rsplit('<section class="panel">', 1)[1].split("</section>", 1)[0]
    excluded_periods = template.split('<h2>Periodos académicos</h2>', 1)[0].rsplit('<section class="panel">', 1)[1].split("</section>", 1)[0]
    assert "config-section-heading" not in excluded_sections
    assert "config-section-heading" not in excluded_periods


def test_configuration_catalog_titles_follow_followup_page_heading_layout():
    template = Path("templates/configuracion/index.html").read_text(encoding="utf-8")
    css = Path("static/css/configuracion.css").read_text(encoding="utf-8")
    seguimiento = Path("templates/seguimiento/lista.html").read_text(encoding="utf-8")

    assert 'class="page-head seguimiento-page-head"' in seguimiento
    assert template.count('class="page-head config-section-heading"') == 6
    assert ".configuracion-page .panel > .config-section-heading" in css
    assert ".configuracion-page .config-section-heading h2" in css
    assert "min-height: 58px !important;" in css


def test_homepage_artwork_is_next_to_slogan_and_login_back_link_is_symbol_only():
    login = Path("templates/auth/login.html").read_text(encoding="utf-8")
    homepage = Path("templates/index.html").read_text(encoding="utf-8")
    illustration = Path("templates/_eduturnos_illustration.html").read_text(encoding="utf-8")
    recovery = Path("templates/auth/recuperar.html").read_text(encoding="utf-8")

    assert '<div class="hero-message-row">' in homepage
    assert '{% include "_eduturnos_illustration.html" %}' in homepage
    assert 'class="illustration-svg ill-float"' in illustration
    assert "flex: 0 0 200px !important;" in homepage
    assert 'class="login-visual"' not in login
    assert "align-items: center;" in login.split(".login-page {", 1)[1].split("}", 1)[0]
    assert "36px 30px;" in login
    assert 'aria-label="Volver al inicio de sesión"' in recovery
    assert 'class="eduturnos-recuperar-final-back account-settings-back"' in recovery
    assert '<svg aria-hidden="true" viewBox="0 0 24 24">' in recovery
    assert 'aria-label="Volver al inicio"' in login


def test_homepage_artwork_scales_on_mobile_and_login_remains_plain():
    mobile = Path("static/css/mobile/eduturnos-mobile.css").read_text(encoding="utf-8")
    login = Path("templates/auth/login.html").read_text(encoding="utf-8")
    homepage = Path("templates/index.html").read_text(encoding="utf-8")

    assert 'class="login-visual"' not in login
    assert "@media (max-width: 560px)" in homepage
    assert "flex-basis: clamp(195px, calc(36vw + 80px), 230px) !important;" in homepage
    assert "transform: translateX(-49px) !important;" in homepage
    assert "transform: translateY(-8px) !important;" in homepage
    assert "@media (max-width: 420px)" in homepage
    assert "font-size: clamp(24px, 7.3vw, 28px) !important;" in homepage
    assert "width: clamp(196px, calc(36vw + 80px), 224px) !important;" in homepage
    assert "transform: translateX(-20px) !important;" in homepage
    assert "@media (max-width: 350px)" in homepage
    assert "min-height: clamp(160px, calc(33vw + 48px), 180px) !important;" in homepage
    assert "flex: 0 0 60% !important;" in homepage
    assert "right: -4px !important;" in homepage
    assert "width: clamp(173px, calc(33.33vw + 73px), 190px) !important;" in homepage
    assert "overflow: hidden !important;" in homepage
    assert "@media (max-width: 280px)" in homepage
    assert "prefers-reduced-motion: reduce" in homepage
    assert "align-items: center !important;" in mobile
    assert "padding: 14px !important;" in mobile.split("html body main.login-page {", 1)[1].split("}", 1)[0]
    assert "header.eduturnos-header .mobile-back-link::before" in mobile
    assert "font-size: 0 !important;" in mobile
    assert "min-height: 40px !important;" in mobile
    assert "min-height: 34px !important;" in mobile


def test_public_mobile_navigation_dropdown_is_not_clipped_by_header():
    mobile = Path("static/css/mobile/eduturnos-mobile.css").read_text(encoding="utf-8")
    public_base = Path("templates/publico/base_publica.html").read_text(encoding="utf-8")

    assert "html body.public-info-page > header.barra" in mobile
    assert "overflow: visible !important;" in mobile.split(
        "html body.public-info-page > header.barra", 1
    )[1].split("}", 1)[0]
    assert "v=20261026_public_menu_title_v65" in public_base
    assert "padding: 6px 12px !important;" in mobile.split(
        "html body.public-info-page > header.barra", 1
    )[1].split("}", 1)[0]
    assert "margin-top: -20px !important;" in mobile.split(
        "html body.public-info-page > header.barra", 1
    )[1].split("}", 1)[0]


def test_follow_up_status_stays_readable_on_mobile():
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")

    assert "grid-template-columns: minmax(76px, max-content) minmax(0, 1fr) 16px !important;" in responsive
    assert "white-space: nowrap !important;" in responsive
    assert "overflow-wrap: normal !important;" in responsive


def test_mobile_notification_and_directory_layouts_use_available_width():
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    notifications = Path("templates/notificaciones/index.html").read_text(encoding="utf-8")
    reports = Path("templates/reportes/index.html").read_text(encoding="utf-8")

    assert "@media (max-width: 900px)" in responsive
    assert ".notificaciones-page .notification-card" in responsive
    assert "flex-direction: column !important;" in responsive
    assert ".directory-page table.directory-table tbody tr" in responsive
    assert "grid-template-columns: minmax(0, 1fr) 56px 56px auto !important;" in responsive
    assert "directory-page table.directory-table tbody td:nth-child(2)" not in responsive
    assert "@media (min-width: 901px)" in responsive
    assert ".directory-page .directory-search" in responsive
    assert ".notificaciones-page > .page-head > form" in responsive
    assert ".notificaciones-page .notification-card > form button" in responsive
    assert "border-left: 1px solid #e5e7eb;" in notifications
    assert "transform: translateY(-4px);" in notifications
    assert "align-self: flex-end !important;" in responsive
    assert responsive.count("display: none !important;") == 1
    assert "grid-template-columns: repeat(2, minmax(0, 1fr)) !important;" in responsive
    assert "grid-column: 1 / -1 !important;" in responsive
    assert ".notification-content" in notifications
    assert 'class="reportes-page reportes-panorama-activo"' in reports
    assert 'class="reportes-panorama-chart"' in reports
    assert 'class="tarjeta reportes-filter"' in reports
    assert 'class="tarjeta reportes-results"' in reports


def test_support_opens_prefilled_email_without_extra_form_or_chat():
    sidebar = Path("templates/_desktop_sidebar.html").read_text(encoding="utf-8")
    assistant_widget = Path("templates/_asistente_widget.html").read_text(encoding="utf-8")
    route = Path("routes/soporte.py").read_text(encoding="utf-8")
    email = Path("servicios/email.py").read_text(encoding="utf-8")

    assert "('soporte.index', 'Ayuda y soporte')" in sidebar
    assert "'soporte.index': 'mail'" in sidebar
    assert "mailto:coliejjfh@hotmail.com" in sidebar
    assert "Hola%2C%20necesito%20ayuda%20con%20EDUTURNOS" in sidebar
    assert 'class="support-nav-link" href="{{ url_for(\'soporte.index\') }}"' not in assistant_widget
    assert "mail.google.com/mail/" not in sidebar
    assert "redirect(" in route
    assert "mailto:coliejjfh@hotmail.com" in route
    assert "Hola%2C%20necesito%20ayuda%20con%20EDUTURNOS" in route
    assert not Path("templates/soporte/index.html").exists()
    assert "Respuesta automática de EDUBOT" in email


def test_los_filtros_de_listas_tienen_opciones_por_defecto_descriptivas():
    calendar = Path("templates/calendario/index.html").read_text(encoding="utf-8")
    reports = Path("templates/reportes/index.html").read_text(encoding="utf-8")
    citas = Path("templates/citas/index.html").read_text(encoding="utf-8")

    assert ">Todas las sedes</option>" in calendar
    assert ">Todas las jornadas</option>" in calendar
    assert ">Todos los docentes</option>" in calendar
    assert ">Todos los estados</option>" in calendar
    assert ">Todos los estados</option>" in reports
    assert ">Todos los estados</option>" in citas
    assert '<option value="" selected disabled hidden></option>' not in calendar


def test_citas_list_has_no_new_citation_button_and_stays_close_to_heading():
    citas = Path("templates/citas/index.html").read_text(encoding="utf-8")

    assert "citas-new-button" not in citas
    assert "Nueva citación" not in citas
    assert "@media(max-width:750px)" in citas
    assert "#contenido .citas-page > .page-head{margin:0 0 10px!important;" in citas
    assert "#contenido .citas-desktop-view > .page-head{margin-bottom:12px!important;}" in citas


def test_mobile_directory_refresh_icon_matches_search_and_tables_do_not_clip():
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    for path in (
        "templates/docentes/lista.html",
        "templates/estudiantes/lista.html",
        "templates/acudientes/lista.html",
    ):
        template = Path(path).read_text(encoding="utf-8")
        assert 'class="directory-search-all"' in template
        assert '<svg aria-hidden="true" viewBox="0 0 24 24">' in template
        assert ">↻</a>" not in template

    assert "html body #contenido .directory-page .directory-search > .directory-search-all svg" in responsive
    assert "width: 24px !important;" in responsive
    assert "@media (max-width: 720px)" in responsive
    assert "html body.has-desktop-sidebar #contenido .directory-page table.directory-table {" in responsive
    assert "table-layout: auto !important;" in responsive
    assert "html body.has-desktop-sidebar #contenido .directory-page table.directory-table tbody tr {" not in responsive


def test_support_is_available_in_sidebar_and_legacy_gmail_composer_is_removed():
    sidebar = Path("templates/_desktop_sidebar.html").read_text(encoding="utf-8")
    assistant_widget = Path("templates/_asistente_widget.html").read_text(encoding="utf-8")
    app_source = Path("app.py").read_text(encoding="utf-8")
    app_js = Path("static/js/app.js").read_text(encoding="utf-8")

    assert "Bandeja de soporte" not in sidebar
    assert "{% include '_asistente_widget.html' %}" in sidebar
    assert "Ayuda y soporte" in assistant_widget
    assert sidebar.index("include '_asistente_widget.html'") < sidebar.index("Mi cuenta")
    assert "mail.google.com/mail/" not in sidebar
    assert "soporte_bp" in app_source
    assert "supportEmailLink" not in app_js
    assert "mailto:coliejjfh@hotmail.com" in Path("routes/soporte.py").read_text(encoding="utf-8")
    assert "mailto:coliejjfh@hotmail.com" in sidebar


def test_administracion_usa_enlaces_de_seccion_y_un_panel_activo():
    app_js = Path("static/js/app.js").read_text(encoding="utf-8")
    config_css = Path("static/css/configuracion.css").read_text(encoding="utf-8")
    desktop_css = Path("static/css/desktop-sidebar.css").read_text(encoding="utf-8")
    responsive_css = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")

    assert 'document.createElement("a")' in app_js
    assert 'document.createElement("button")' not in app_js[app_js.index('const administration ='):app_js.index('document.addEventListener("click", (event)')]
    assert ".admin-catalog-tabs a[aria-selected=\"true\"]" in config_css
    assert ".admin-catalog-tabs button" not in desktop_css
    assert ".admin-catalog-tabs > button" not in responsive_css


def test_titulos_de_secciones_comparten_encabezado():
    seguimiento = Path("templates/seguimiento/lista.html").read_text(encoding="utf-8")
    solicitudes = Path("templates/solicitudes/index.html").read_text(encoding="utf-8")
    desktop_css = Path("static/css/desktop-sidebar.css").read_text(encoding="utf-8")
    dashboard_css = Path("templates/dashboard.html").read_text(encoding="utf-8")
    with app.test_request_context("/solicitudes"):
        solicitudes_html = render_template(
            "solicitudes/index.html",
            rol="Rector",
            solicitudes=[],
            solicitudes_reprogramacion=[],
            usuario_id=1,
        )

    assert '<header class="page-head seguimiento-page-head">' in seguimiento
    assert '<header class="page-head solicitudes-encabezado">' in solicitudes
    assert re.search(
        r'(?s)<header class="page-head solicitudes-encabezado">\s*<div class="menu-page-heading">.*?<h1>Solicitudes de cita</h1>',
        solicitudes_html,
    )
    assert "margin: 0 0 8px !important;" in solicitudes
    assert "padding-top: 10px !important;" in solicitudes
    assert "#contenido .page-head h1{margin:0!important;line-height:1.2!important;}" in desktop_css
    assert 'html body #contenido .dashboard-page.dashboard-overview[class*="dashboard-rol-"] .dashboard-head {' in dashboard_css
    assert 'html body #contenido .dashboard-page.dashboard-overview[class*="dashboard-rol-"] .dashboard-greeting-row {' in dashboard_css
    assert "border: 1px solid #dce7f4 !important;" in dashboard_css


def test_calendar_month_year_navigation_stays_together_with_today_on_right():
    calendar = Path("templates/calendario/index.html").read_text(encoding="utf-8")
    responsive = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")

    assert "{{ nombre_mes }} {{ anio }}" in calendar
    assert 'class="eduturnos-mes-navegacion"' in calendar
    assert 'class="edc-hoy eduturnos-hoy"' in calendar
    assert "edc-page .eduturnos-barra-real .eduturnos-mes-navegacion" in responsive
    assert "edc-page .eduturnos-barra-real > .eduturnos-hoy" in responsive


def test_new_student_codes_use_est_prefix_and_historical_codes_remain_valid():
    from servicios.estudiantes import codigo_final, validar_codigo_estudiantil

    assert codigo_final(1) == "EST_00001"
    assert codigo_final(143) == "EST_00143"
    assert validar_codigo_estudiantil("EST_00143")
    assert validar_codigo_estudiantil("EDU-2026-00143")
    assert not validar_codigo_estudiantil("EST_ABC")


def test_rectors_are_authorized_for_all_institutional_admin_sections():
    from routes import configuracion

    def allowed_roles(endpoint):
        return next(
            cell.cell_contents
            for cell in endpoint.__closure__
            if isinstance(cell.cell_contents, tuple)
        )

    for endpoint in (
        configuracion.guardar_institucion,
        configuracion.nuevo_periodo,
        configuracion.guardar_sede,
        configuracion.guardar_jornada,
        configuracion.guardar_grado,
        configuracion.guardar_grupo,
        configuracion.guardar_motivo,
        configuracion.guardar_estado,
    ):
        assert "Rector" in allowed_roles(endpoint)


def test_dashboard_header_directory_controls_and_mobile_actions_are_compact():
    responsive_css = Path("static/css/layout-responsive.css").read_text(encoding="utf-8")
    dashboard = Path("templates/dashboard.html").read_text(encoding="utf-8")
    base = Path("templates/base.html").read_text(encoding="utf-8")
    overview_css = Path("static/css/dashboard-overview.css").read_text(encoding="utf-8")
    registration = Path("templates/auth/registro_portal.html").read_text(encoding="utf-8")
    assistant = Path("templates/_asistente_widget.html").read_text(encoding="utf-8")
    teacher_list = Path("templates/docentes/lista.html").read_text(encoding="utf-8")
    guardian_list = Path("templates/acudientes/lista.html").read_text(encoding="utf-8")

    assert ".dashboard-page .dashboard-head::before" in responsive_css
    assert "content: none !important;" in responsive_css
    assert ".dashboard-page.dashboard-overview[class*=\"dashboard-rol-\"] .dashboard-head::before" in dashboard
    assert ".dashboard-head::after" in dashboard
    assert "v=20261022_local_edubot_v1" in dashboard
    assert ".dashboard-greeting-row::before" in dashboard
    assert ".dashboard-head-info h1::before" in dashboard
    assert ".dashboard-head-info::before" in overview_css
    assert ".dashboard-page.dashboard-overview .dashboard-head" in overview_css
    assert "background: #ffffff !important;" in overview_css
    role_header_rule = base.split(
        '.dashboard-page[class*="dashboard-rol-"]\n.dashboard-head::before {', 1
    )[1].split("}", 1)[0]
    assert "content: none !important;" in role_header_rule
    assert "background: none !important;" in role_header_rule
    assert "width: min(100%, 760px) !important;" in responsive_css
    assert "min-width: 36px !important;" in responsive_css
    assert ".student-form-actions > .boton" in responsive_css
    assert ".portal-registro-action-buttons > button" in registration
    assert ".portal-registro-action-buttons > .portal-registro-cancel" in registration
    assert "data-eduturnos-assistant" in assistant
    assert '<iframe' not in assistant
    for template in (teacher_list, guardian_list):
        assert 'class="boton pequeno directory-new"' in template
        assert 'class="directory-search-all"' in template
        assert "<svg aria-hidden=" in template
