from pathlib import Path

from app import app


ROOT = Path(__file__).resolve().parents[1]


def test_mi_cuenta_muestra_flechas_en_seguridad_y_calendarios():
    template = (ROOT / "templates" / "cuenta" / "index.html").read_text(
        encoding="utf-8"
    )

    assert template.count('class="cuenta-section-back"') == 2
    assert 'aria-label="Ir a Seguridad"' in template
    assert 'aria-label="Ir a Calendarios conectados"' in template
    assert 'class="account-back-button"' not in template


def test_portada_conserva_legibilidad_de_los_botones_al_enfocar():
    response = app.test_client().get("/")
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    assert response.status_code == 200
    assert b"Iniciar sesi" in response.data
    assert b"Crear cuenta" in response.data
    assert ".acciones .boton-principal:focus-visible" in template
    assert ".acciones .boton-secundario:focus-visible" in template


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
    assert "max-width: 760px !important;" in admin_styles


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

    assert 'id="seguimiento-filtro-situacion"' in template
    assert '<select id="seguimiento-filtro-situacion"' in template
    assert "data-seguimiento-empty" in template
    assert "data-seguimiento-count" in template
    assert 'data-seguimiento-filter="observador"' not in template
    assert 'data-seguimiento-filter="segunda-cita"' not in template
    assert "const matches = filter === \"todos\"" in template
    assert "if (empty) empty.hidden = visible !== 0" in template
    assert ".seguimiento-filtros select" in template


def test_modal_avatar_movil_tiene_cierre_de_tamano_limitado():
    styles = (ROOT / "static" / "css" / "desktop-sidebar.css").read_text(
        encoding="utf-8"
    )

    assert "html body dialog.avatar-customizer .avatar-customizer-header>[data-avatar-close]" in styles
    assert "width:40px!important" in styles
    assert "max-height:calc(100dvh - 24px - env(safe-area-inset-top))!important" in styles
    assert "grid-template-columns:repeat(2,minmax(0,1fr))!important;" in styles


def test_android_incrementa_la_version_de_la_app():
    gradle = (ROOT / "mobile-app" / "android" / "app" / "build.gradle").read_text(
        encoding="utf-8"
    )

    assert "versionCode 20" in gradle
    assert 'versionName "3.0"' in gradle
