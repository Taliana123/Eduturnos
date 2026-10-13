from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_easy_start_files_exist():
    for name in ("PRIMERA_VEZ.bat", "ABRIR_EDUTURNOS.vbs", "DETENER_EDUTURNOS.bat", "ESTADO_EDUTURNOS.bat", "requirements.txt", ".env.example", "README.md"):
        assert (ROOT / name).exists()


def test_root_does_not_contain_legacy_launchers():
    for name in ("INICIAR_EDUTURNOS.bat", "INICIAR_DOCKER_LOCAL.bat", "PROBAR_TODO.bat", "CREAR_ENV.bat", "MIGRAR_BD_EDUTURNOS.bat"):
        assert not (ROOT / name).exists()


def test_distribution_excludes_runtime_and_duplicate_artifacts():
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
    for pattern in (
        ".env",
        "venv/",
        ".venv/",
        "EDUTURNOS/",
        "tests/",
        "backups/",
        "*.pyc",
        "*.log",
        "data/directorio_institucional.csv",
    ):
        assert pattern in dockerignore

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore
    assert "venv/" in gitignore
    assert ".venv/" in gitignore
    assert "passwords_full.txt" in gitignore


def test_both_sql_copies_are_identical():
    assert (ROOT / "database/eduturnos.sql").read_text(encoding="utf-8") == (ROOT / "sql/eduturnos.sql").read_text(encoding="utf-8")


def test_sql_has_no_duplicate_cita_unique_indexes():
    text = (ROOT / "sql/eduturnos.sql").read_text(encoding="utf-8")
    assert text.count("UNIQUE KEY uq_cita_estudiante_hora") == 1
    assert text.count("UNIQUE KEY uq_cita_acudiente_hora") == 1
