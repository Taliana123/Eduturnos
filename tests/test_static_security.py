import base64
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_docker_context_excludes_virtual_environments_and_secrets():
    patterns = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
    assert "venv/" in patterns
    assert ".venv/" in patterns
    assert ".env" in patterns


def test_csrf_is_available():
    assert "csrf_token" in (ROOT / "security.py").read_text(encoding="utf-8")


def test_production_files_present():
    for name in ("Dockerfile", "docker-compose.prod.yml", "docker-compose.local.yml", "Caddyfile", ".env.example", "LANZAMIENTO.md", "PRIMERA_VEZ.bat", "ABRIR_EDUTURNOS.vbs"):
        assert (ROOT / name).exists()


def test_plaintext_directory_codes_are_not_distributed():
    assert not (ROOT / "data" / "directorio_institucional.csv").exists()
    assert (ROOT / "data" / "directorio_institucional.csv.example").exists()


def test_service_worker_version_invalidates_stale_app_assets():
    service_worker = (ROOT / "static" / "service-worker.js").read_text(encoding="utf-8")

    assert 'const CACHE_VERSION = "eduturnos-v9";' in service_worker
    assert "keys.filter((key) => key !== CACHE_VERSION).map((key) => caches.delete(key))" in service_worker


def test_report_exports_neutralize_spreadsheet_formulas():
    from routes.reportes import _valor_hoja_calculo

    for valor in ("=1+1", "+1+1", "-1+1", "@SUM(A1:A2)", "  =1+1", "\t=1+1"):
        assert _valor_hoja_calculo(valor) == "'" + valor
    assert _valor_hoja_calculo("Texto normal") == "Texto normal"
    assert _valor_hoja_calculo(123) == 123


def test_beepy_script_solo_en_inicio_del_dominio_registrado():
    from app import app

    client = app.test_client()
    for ruta, dominio, permitido in (
        ('/', 'seventy-excavator-designate.ngrok-free.dev', True),
        ('/', 'eduturnos-jjfh.alwaysdata.net', True),
        ('/', '192.168.18.24:5000', False),
        ('/auth/login', 'seventy-excavator-designate.ngrok-free.dev', False),
    ):
        response = client.get(ruta, base_url='https://' + dominio)
        assert response.status_code == 200
        assert ('js/beepy.js' in response.get_data(as_text=True)) == permitido
        policy = response.headers['Content-Security-Policy']
        script_rule = next(rule for rule in policy.split(';') if rule.strip().startswith('script-src'))
        assert ('https://www.beepychatbot.com' in script_rule) == permitido
        assert "'unsafe-inline'" not in script_rule


def test_csp_allows_only_hashed_base_inline_scripts():
    from app import app

    base = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    inline_scripts = re.findall(
        r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>",
        base,
        flags=re.IGNORECASE | re.DOTALL,
    )
    response = app.test_client().get("/auth/registro")
    script_rule = next(
        rule
        for rule in response.headers["Content-Security-Policy"].split(";")
        if rule.strip().startswith("script-src")
    )

    assert len(inline_scripts) == 2
    assert "'unsafe-inline'" not in script_rule
    for script in inline_scripts:
        digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
        assert f"'sha256-{digest}'" in script_rule


def test_beepy_redirige_a_proveedor_sin_datos_del_usuario(monkeypatch):
    from app import app
    from routes import helpers

    monkeypatch.setattr(helpers, 'usuario_actual', lambda: {'id_usuario': 17, 'rol_nombre': 'Estudiante'})
    response = app.test_client().get('/asistente/beepy')
    assert response.status_code == 302
    assert response.headers['Cache-Control'] == 'no-store'
    assert response.location == 'https://www.beepychatbot.com/u/1nLBFlV/'
    public_response = app.test_client().get('/asistente/beepy', base_url='https://seventy-excavator-designate.ngrok-free.dev')
    assert public_response.location == response.location


def test_beepy_rechaza_redireccion_a_otro_dominio(monkeypatch):
    from app import app
    from routes import helpers

    monkeypatch.setattr(helpers, 'usuario_actual', lambda: {'id_usuario': 17, 'rol_nombre': 'Acudiente'})
    monkeypatch.setitem(app.config, 'BEEPY_CHAT_URL', 'https://example.com/chat')
    response = app.test_client().get('/asistente/beepy')
    assert response.status_code == 503
    assert 'Location' not in response.headers


def test_beepy_ayuda_requiere_sesion():
    from app import app

    response = app.test_client().get('/asistente/beepy')
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_edubot_no_depende_de_una_csp_de_proveedor_externo():
    from app import app

    client = app.test_client()
    public_response = client.get("/")
    assert "dashboard-help-chat" not in public_response.get_data(as_text=True)
    public_policy = public_response.headers["Content-Security-Policy"]
    assert "https://cdn.botpress.cloud" not in public_policy.split("frame-src", 1)[1].split(";", 1)[0]

    with client.session_transaction() as session:
        session["usuario_id"] = 17
    private_response = client.get("/health/live")
    private_policy = private_response.headers["Content-Security-Policy"]
    assert "https://cdn.botpress.cloud" not in private_policy.split("frame-src", 1)[1].split(";", 1)[0]
