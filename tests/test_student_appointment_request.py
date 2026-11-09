from datetime import date
from pathlib import Path
from types import SimpleNamespace

import app as app_module
from routes import helpers, solicitudes
from servicios.avatar import avatar_inicial


ROOT = Path(__file__).resolve().parents[1]


def _client(monkeypatch, usuario):
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(solicitudes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(
        app_module,
        "obtener_o_crear_avatar",
        lambda user_id: avatar_inicial(user_id),
    )
    client = app_module.app.test_client()
    with client.session_transaction() as session:
        session["usuario_id"] = usuario["id_usuario"]
        session["_csrf_token"] = "student-request-csrf"
    return client


def _consultar_estudiante(sql, params=(), uno=False):
    if "FROM estudiantes e" in sql and "JOIN usuarios u" in sql:
        return {"id_estudiante": 51, "id_institucion": 8}
    if "FROM usuarios u" in sql and "r.nombre AS rol_nombre" in sql:
        return [
            {
                "id_usuario": 91,
                "nombres": "Laura",
                "apellidos": "Rectora",
                "rol_nombre": "Rector",
                "id_docente": None,
            },
            {
                "id_usuario": 92,
                "nombres": "Carlos",
                "apellidos": "Docente",
                "rol_nombre": "Docente",
                "id_docente": 17,
            },
        ]
    if "FROM motivos" in sql:
        return [{"id": 3, "nombre": "Orientación"}]
    if "FROM periodos_academicos" in sql:
        return {"id": 6}
    if "SELECT u.id_usuario FROM usuarios u JOIN roles r" in sql:
        return []
    return None if uno else []


def test_estudiante_puede_enviar_solicitud_a_destinatario_de_su_institucion(monkeypatch):
    usuario = {
        "id_usuario": 42,
        "id_institucion": 8,
        "rol_nombre": "Estudiante",
        "nombres": "Ana",
        "apellidos": "Pérez",
    }
    inserts = []
    notifications = []
    monkeypatch.setattr(solicitudes, "consultar", _consultar_estudiante)
    monkeypatch.setattr(
        solicitudes,
        "ejecutar",
        lambda sql, params: inserts.append((sql, params)) or 77,
    )
    monkeypatch.setattr(
        solicitudes,
        "notificar",
        lambda *args: notifications.append(args),
    )
    monkeypatch.setattr(solicitudes, "auditoria", lambda *args: None)

    response = _client(monkeypatch, usuario).post(
        "/solicitudes/nueva/estudiante",
        data={
            "csrf_token": "student-request-csrf",
            "destinatario_usuario_id": "92",
            "id_motivo": "3",
            "fecha_solicitada": date.today().isoformat(),
            "hora_solicitada": "10:00",
            "observaciones": "Necesito conversar sobre mi proceso.",
        },
    )

    assert response.status_code == 302
    assert response.location.endswith("/solicitudes/")
    sql, params = inserts[0]
    assert "INSERT INTO solicitudes_cita" in sql
    assert params == (
        42,
        51,
        17,
        "Docente",
        92,
        3,
        6,
        date.today().isoformat(),
        "10:00",
        "Necesito conversar sobre mi proceso.",
        8,
    )
    assert any(notification[0] == 92 for notification in notifications)


def test_solicitud_de_estudiante_no_acepta_destinatario_fuera_del_catalogo(monkeypatch):
    usuario = {
        "id_usuario": 42,
        "id_institucion": 8,
        "rol_nombre": "Estudiante",
        "nombres": "Ana",
        "apellidos": "Pérez",
    }
    monkeypatch.setattr(solicitudes, "consultar", _consultar_estudiante)
    monkeypatch.setattr(
        solicitudes,
        "ejecutar",
        lambda *args: (_ for _ in ()).throw(AssertionError("No debe guardar.")),
    )
    monkeypatch.setattr(solicitudes, "auditoria", lambda *args: None)

    response = _client(monkeypatch, usuario).post(
        "/solicitudes/nueva/estudiante",
        data={
            "csrf_token": "student-request-csrf",
            "destinatario_usuario_id": "999",
            "id_motivo": "3",
            "fecha_solicitada": date.today().isoformat(),
            "hora_solicitada": "10:00",
        },
    )

    assert response.status_code == 200
    assert "El destinatario no está disponible en tu institución." in response.get_data(
        as_text=True
    )


def test_dashboard_y_navegacion_muestran_solicitudes_por_rol():
    dashboard = (ROOT / "templates" / "dashboard.html").read_text(encoding="utf-8")
    sidebar = (ROOT / "templates" / "_desktop_sidebar.html").read_text(
        encoding="utf-8"
    )
    account_css = (ROOT / "static" / "css" / "desktop-sidebar.css").read_text(
        encoding="utf-8"
    )

    assert "solicitudes.nueva_acudiente" in dashboard
    assert "solicitudes.nueva_docente" in dashboard
    assert "solicitudes.nueva_estudiante" in dashboard
    assert "('solicitudes.index', 'Solicitudes de cita')" in sidebar
    assert "grid-template-columns:36px minmax(0,1fr) 36px" in account_css
    assert ".desktop-sidebar-account-avatar" in account_css


def test_estudiante_puede_aceptar_una_propuesta_desde_sus_solicitudes():
    from flask import render_template

    solicitud = SimpleNamespace(
        id=77,
        estudiante="Ana Pérez",
        destinatario_tipo="Docente",
        motivo="Orientación",
        docente="Carlos Docente",
        rol_solicitante="Estudiante",
        acudiente=None,
        fecha_solicitada=date.today(),
        hora_solicitada="10:00",
        estado="Propuesta",
        fecha_propuesta=date.today(),
        hora_propuesta="11:00",
    )
    with app_module.app.test_request_context("/solicitudes/"):
        html = render_template(
            "solicitudes/index.html",
            rol="Estudiante",
            solicitudes=[solicitud],
        )

    assert "Aceptar propuesta" in html
    assert 'action="/solicitudes/77/aceptar-propuesta"' in html
