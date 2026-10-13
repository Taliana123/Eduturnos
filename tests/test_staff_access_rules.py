from roles import es_correo_institucional, es_codigo_institucional_valido, PORTALES
from routes.citas import _acudiente_puede_confirmar, _cita_horario_ocupado


def test_dominio_institucional_exacto():
    assert es_correo_institucional("docente@jjfh.edu.co")
    assert es_correo_institucional("DOCENTE@JJFH.EDU.CO")
    assert not es_correo_institucional("docente@gmail.com")
    assert not es_correo_institucional("docente@jjfh.edu.co.ejemplo.com")
    assert not es_correo_institucional("@jjfh.edu.co")


def test_personal_requiere_codigo_y_sede():
    for portal in ("docente", "coordinador", "rector"):
        assert PORTALES[portal]["requiere_codigo"] is True
        assert PORTALES[portal]["requiere_sede"] is True


def test_estudiante_y_acudiente_no_requieren_codigo_institucional():
    assert PORTALES["estudiante"]["requiere_codigo"] is False
    assert PORTALES["acudiente"]["requiere_codigo"] is False


def test_codigo_institucional_tiene_seis_digitos():
    assert es_codigo_institucional_valido("482615")
    assert es_codigo_institucional_valido("000001")
    assert not es_codigo_institucional_valido("12345")
    assert not es_codigo_institucional_valido("1234567")
    assert not es_codigo_institucional_valido("12A456")


def test_acudiente_solo_confirma_citas_abiertas():
    assert _acudiente_puede_confirmar("Pendiente", "Confirmada")
    assert _acudiente_puede_confirmar("Reprogramada", "Confirmada")
    assert not _acudiente_puede_confirmar("Cancelada", "Confirmada")
    assert not _acudiente_puede_confirmar("Realizada", "Confirmada")
    assert not _acudiente_puede_confirmar("Pendiente", "Cancelada")


def test_validacion_horario_cubre_los_tres_participantes(monkeypatch):
    import routes.citas as citas

    consulta = {}

    def consultar_mock(sql, params=(), uno=False):
        consulta["sql"] = sql
        consulta["params"] = params
        consulta["uno"] = uno
        return {"id": 12}

    monkeypatch.setattr(citas, "consultar", consultar_mock)

    resultado = _cita_horario_ocupado(3, 4, 5, "2026-10-01", "09:30")

    assert resultado == {"id": 12}
    assert "id_docente = %s" in consulta["sql"]
    assert "id_estudiante = %s" in consulta["sql"]
    assert "id_acudiente = %s" in consulta["sql"]
    assert "id_estado" not in consulta["sql"]
    assert consulta["params"] == ("2026-10-01", "09:30", 3, 4, 5)
    assert consulta["uno"] is True


def test_confirmacion_no_sobrescribe_cancelacion_concurrente(monkeypatch):
    from app import app
    import routes.citas as citas

    usuario = {"id_usuario": 21, "rol_nombre": "Acudiente"}
    consultas = []
    actualizaciones = []
    notificaciones = []
    auditorias = []

    def consultar_mock(sql, params=(), uno=False):
        consultas.append(sql)
        if "SELECT *" in sql and "FROM citas" in sql:
            return {
                "id": 7,
                "id_estado": 1,
                "id_acudiente": 4,
                "creado_por": 10,
            }
        if "FROM estados_cita" in sql and "WHERE nombre" in sql:
            return {"id": 2, "nombre": "Confirmada"}
        if "SELECT nombre FROM estados_cita" in sql:
            return {"nombre": "Pendiente"}
        if "FROM acudientes" in sql:
            return {"id_acudiente": 4}
        if "SELECT id_estado FROM citas" in sql:
            return {"id_estado": 3}
        raise AssertionError(f"Consulta inesperada: {sql}")

    monkeypatch.setattr(citas, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(citas, "consultar", consultar_mock)
    monkeypatch.setattr(
        citas,
        "ejecutar",
        lambda sql, params=(): actualizaciones.append((sql, params)),
    )
    monkeypatch.setattr(
        citas,
        "_notificar",
        lambda *args, **kwargs: notificaciones.append(args),
    )
    monkeypatch.setattr(
        citas,
        "auditoria",
        lambda *args, **kwargs: auditorias.append(args),
    )

    with app.test_request_context(
        "/citas/7/estado",
        method="POST",
        data={"estado": "Confirmada"},
    ):
        response = citas.cambiar_estado.__wrapped__(7)

    assert response.status_code == 302
    assert "AND id_estado = %s" in actualizaciones[0][0]
    assert actualizaciones[0][1] == (2, 7, 1)
    assert notificaciones == []
    assert auditorias == []


def test_login_registra_codigo_institucional_incorrecto(monkeypatch):
    from werkzeug.security import generate_password_hash
    from app import app
    import routes.auth as auth

    usuario = {
        "id_usuario": 88,
        "rol_nombre": "Docente",
        "correo": "docente@jjfh.edu.co",
        "password_hash": generate_password_hash("CorrectPass1"),
        "bloqueado_hasta": None,
        "intentos_fallidos": 0,
        "estado": 1,
    }
    intentos = []

    monkeypatch.setattr(auth, "_asegurar_control_acceso", lambda: True)
    monkeypatch.setattr(auth, "_buscar_usuario", lambda identificador: usuario)
    monkeypatch.setattr(auth, "_mostrar_login", lambda: "login")
    monkeypatch.setattr(auth, "_registrar_intento_fallido", intentos.append)

    def consultar_mock(sql, params=(), uno=False):
        if "FROM control_acceso" in sql:
            return None
        if "FROM directorio_institucional" in sql:
            return {"codigo_institucional_hash": generate_password_hash("123456")}
        raise AssertionError(f"Consulta inesperada: {sql}")

    monkeypatch.setattr(auth, "consultar", consultar_mock)
    client = app.test_client()
    with client.session_transaction() as session:
        session["_csrf_token"] = "csrf-test-token"

    response = client.post(
        "/auth/login",
        data={
            "csrf_token": "csrf-test-token",
            "identificador": "docente@jjfh.edu.co",
            "password": "CorrectPass1",
            "codigo_institucional": "654321",
            "id_sede": "1",
            "id_jornada": "1",
        },
    )

    assert response.status_code == 200
    assert len(intentos) == 1
    assert len(intentos[0]) == 64
