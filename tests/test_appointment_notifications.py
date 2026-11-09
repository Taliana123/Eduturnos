from datetime import datetime, timedelta, timezone
from pathlib import Path

from app import app


ROOT = Path(__file__).resolve().parents[1]


def test_appointment_reminder_api_requires_authenticated_user():
    response = app.test_client().get("/notificaciones/api/citas-futuras")

    assert response.status_code == 401
    assert response.json == {"error": "authentication_required"}


def test_appointment_reminder_api_returns_only_future_active_visible_citations(monkeypatch):
    from routes import calendario, helpers, notificaciones

    usuario = {"id_usuario": 27, "rol_nombre": "Docente"}
    inicio = datetime.now(timezone(timedelta(hours=-5))) + timedelta(days=2)
    cita_futura = {
        "id": 71,
        "fecha": inicio.date(),
        "hora": inicio.time().replace(tzinfo=None),
        "estado_nombre": "Confirmada",
        "estudiante": "Dato privado",
    }
    cita_pasada = {
        "id": 72,
        "fecha": inicio.date() - timedelta(days=4),
        "hora": inicio.time().replace(tzinfo=None),
        "estado_nombre": "Pendiente",
    }
    cita_cancelada = {
        **cita_futura,
        "id": 73,
        "estado_nombre": "Cancelada",
    }
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(notificaciones, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(
        calendario,
        "citas_visibles",
        lambda current_user: [cita_futura, cita_pasada, cita_cancelada],
    )
    client = app.test_client()
    with client.session_transaction() as session:
        session["usuario_id"] = usuario["id_usuario"]

    response = client.get("/notificaciones/api/citas-futuras")

    assert response.status_code == 200
    appointments = response.json["appointments"]
    assert len(appointments) == 1
    assert appointments[0]["id"] == cita_futura["id"]
    assert set(appointments[0]) == {"id", "startAt"}


def test_android_appointment_notification_permission_and_schedule_are_wired():
    manifest = (ROOT / "mobile-app/android/app/src/main/AndroidManifest.xml").read_text(
        encoding="utf-8"
    )
    activity = (
        ROOT
        / "mobile-app/android/app/src/main/java/co/eduturnos/app/MainActivity.java"
    ).read_text(encoding="utf-8")
    scheduler = (
        ROOT
        / "mobile-app/android/app/src/main/java/co/eduturnos/app/AppointmentNotificationScheduler.java"
    ).read_text(encoding="utf-8")
    receiver = (
        ROOT
        / "mobile-app/android/app/src/main/java/co/eduturnos/app/AppointmentNotificationReceiver.java"
    ).read_text(encoding="utf-8")
    template = (ROOT / "templates/notificaciones/index.html").read_text(
        encoding="utf-8"
    )

    assert 'android:name="android.permission.POST_NOTIFICATIONS"' in manifest
    assert "EDUTURNOSNativeNotifications" in activity
    assert "Manifest.permission.POST_NOTIFICATIONS" in activity
    assert "setAndAllowWhileIdle" in scheduler
    assert "REMINDER_MINUTES = {1440, 120}" in scheduler
    assert "BOOT_COMPLETED" in (
        ROOT
        / "mobile-app/android/app/src/main/java/co/eduturnos/app/AppointmentNotificationBootReceiver.java"
    ).read_text(encoding="utf-8")
    assert "Dato privado" not in receiver
    assert "Tienes una cita" in receiver
    assert "Abre EDUTURNOS para ver los detalles." in receiver
    assert 'data-appointment-notifications-enable' in template
