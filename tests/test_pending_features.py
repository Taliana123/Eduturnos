from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_recordatorios_es_proceso_independiente():
    text = (ROOT / "tools" / "enviar_recordatorios.py").read_text(encoding="utf-8")
    assert "from flask" not in text
    assert "import mysql.connector" in text
    assert "load_dotenv" in text
    assert "smtplib" in text
    assert "recordatorio_24h_enviado" in text
    assert "recordatorio_2h_enviado" in text
    assert "FOR UPDATE" in text
    assert "EDUTURNOS - Recordatorios" in (ROOT / "tools" / "INSTALAR_RECORDATORIOS.bat").read_text(encoding="utf-8")


def test_sql_y_migracion_tienen_campos_de_recordatorio():
    for rel in ("database/eduturnos.sql", "sql/eduturnos.sql"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "recordatorio_24h_enviado TINYINT(1) NOT NULL DEFAULT 0" in text
        assert "recordatorio_2h_enviado TINYINT(1) NOT NULL DEFAULT 0" in text
        assert "idx_cita_recordatorios" in text
        assert "estado TINYINT(1) NOT NULL DEFAULT 1" in text[text.index("CREATE TABLE IF NOT EXISTS estados_cita"):text.index("CREATE TABLE IF NOT EXISTS directorio_institucional")]

    bootstrap = (ROOT / "database/bootstrap.py").read_text(encoding="utf-8")
    assert "recordatorio_24h_enviado" in bootstrap
    assert "recordatorio_2h_enviado" in bootstrap
    assert "idx_cita_recordatorios" in bootstrap


def test_configuracion_tiene_los_siete_catalogos():
    text = (ROOT / "templates/configuracion/index.html").read_text(encoding="utf-8")
    for label in ("Institución", "Sedes", "Jornadas", "Grados", "Grupos", "Motivos", "Estados de citación"):
        assert label in text
    routes = (ROOT / "routes/configuracion.py").read_text(encoding="utf-8")
    for route_name in (
        '"/institucion/guardar"', '"/sede/guardar"', '"/jornada/guardar"',
        '"/grado/guardar"', '"/grupo/guardar"', '"/motivo/guardar"', '"/estado/guardar"',
    ):
        assert route_name in routes
    for role in ("Super Admin", "Rector", "Administrador / Coordinador"):
        assert role in routes


def test_gitignore_cubre_secretos_y_generados():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for entry in (".env", "venv/", ".venv/", "__pycache__/", "*.pyc", "*.pyo", "*.log", ".pytest_cache/", ".coverage", ".vscode/", ".idea/", "passwords_full.txt", "backups/", "*.bak"):
        assert entry in text


def test_recordatorio_normaliza_hora_mysql():
    from datetime import date, datetime, timedelta, time
    from tools.enviar_recordatorios import _cita_datetime
    assert _cita_datetime(date(2026, 9, 18), timedelta(hours=14, minutes=30)) == datetime(2026, 9, 18, 14, 30)
    assert _cita_datetime(date(2026, 9, 18), time(14, 30)) == datetime(2026, 9, 18, 14, 30)


def test_lock_recordatorios_reutiliza_archivo_con_pid_obsoleto(tmp_path, monkeypatch):
    import os
    from tools import enviar_recordatorios

    lock_file = tmp_path / "recordatorios.lock"
    lock_file.write_text("99999999", encoding="utf-8")
    monkeypatch.setattr(enviar_recordatorios, "LOCK_FILE", lock_file)

    assert enviar_recordatorios.obtener_bloqueo()
    enviar_recordatorios.liberar_bloqueo()
    assert lock_file.read_text(encoding="utf-8") == str(os.getpid())

    assert enviar_recordatorios.obtener_bloqueo()
    enviar_recordatorios.liberar_bloqueo()
