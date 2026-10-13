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


def test_report_exports_neutralize_spreadsheet_formulas():
    from routes.reportes import _valor_hoja_calculo

    for valor in ("=1+1", "+1+1", "-1+1", "@SUM(A1:A2)", "  =1+1", "\t=1+1"):
        assert _valor_hoja_calculo(valor) == "'" + valor
    assert _valor_hoja_calculo("Texto normal") == "Texto normal"
    assert _valor_hoja_calculo(123) == 123


def test_beepy_script_solo_en_inicio_del_dominio_registrado():
    from app import app

    client = app.test_client()
    for ruta, dominio, permitido in (('/', 'seventy-excavator-designate.ngrok-free.dev', True), ('/', '192.168.18.24:5000', False), ('/auth/login', 'seventy-excavator-designate.ngrok-free.dev', False)):
        response = client.get(ruta, base_url='https://' + dominio)
        assert response.status_code == 200
        assert ('js/beepy.js' in response.get_data(as_text=True)) == permitido
        policy = response.headers['Content-Security-Policy']
        script_rule = next(rule for rule in policy.split(';') if rule.strip().startswith('script-src'))
        assert ('https://www.beepychatbot.com' in script_rule) == permitido
        assert "'unsafe-inline'" not in script_rule


def test_beepy_redirige_a_proveedor_sin_datos_del_usuario(monkeypatch):
    import json
    from app import app
    from routes import asistente, helpers

    monkeypatch.setattr(helpers, 'usuario_actual', lambda: {'id_usuario': 17, 'rol_nombre': 'Estudiante'})
    calls = []

    class ConfiguracionPublica:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, limit):
            return json.dumps({'ifrurl': 'https://www.beepychatbot.com/visitor/events/contact/chat/server/contact.chat.load.php?cid=27952&vid=visitor-test'}).encode()

    def consultar_publica(request, timeout):
        calls.append(request)
        return ConfiguracionPublica()

    monkeypatch.setattr(asistente, 'urlopen', consultar_publica)
    response = app.test_client().get('/asistente/beepy')
    assert response.status_code == 302
    assert response.location.startswith('https://www.beepychatbot.com/')
    assert response.headers['Cache-Control'] == 'no-store'
    assert not calls
    from urllib.parse import parse_qs, urlsplit

    assert response.location == 'https://www.beepychatbot.com/u/1nLBFlV/'
    public_response = app.test_client().get('/asistente/beepy', base_url='https://seventy-excavator-designate.ngrok-free.dev')
    assert public_response.location == response.location


def test_beepy_rechaza_redireccion_a_otro_dominio(monkeypatch):
    from app import app
    from routes import asistente, helpers

    monkeypatch.setattr(helpers, 'usuario_actual', lambda: {'id_usuario': 17, 'rol_nombre': 'Acudiente'})
    monkeypatch.setitem(app.config, 'BEEPY_CHAT_URL', 'https://example.com/chat')

    class ConfiguracionInvalida:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, limit):
            return b'{"ifrurl":"https://example.com/chat"}'

    monkeypatch.setattr(asistente, 'urlopen', lambda *args, **kwargs: ConfiguracionInvalida())
    response = app.test_client().get('/asistente/beepy')
    assert response.status_code == 503
    assert 'Location' not in response.headers


def test_beepy_ayuda_requiere_sesion():
    from app import app

    response = app.test_client().get('/asistente/beepy')
    assert response.status_code == 302
    assert '/auth/login' in response.location
