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

    assert "flex: 0 0 76px;" in edubot_styles
    assert "width: 76px;" in edubot_styles
    assert ".state-list {" in admin_styles
    assert ".administracion-page .configuracion-page .state-form-row" in admin_styles
    assert "grid-template-columns: minmax(0, 1fr) !important;" in admin_styles
    assert "max-width: 760px !important;" in admin_styles


def test_android_incrementa_la_version_de_la_app():
    gradle = (ROOT / "mobile-app" / "android" / "app" / "build.gradle").read_text(
        encoding="utf-8"
    )

    assert "versionCode 18" in gradle
    assert 'versionName "2.8"' in gradle
