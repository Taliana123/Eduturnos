from datetime import date, timedelta

from roles import es_codigo_institucional_valido
from routes.solicitudes import _validar_fecha_cita, _validar_horario_disponible


def test_fecha_cita_rechaza_ayer_y_acepta_hoy():
    ayer = (date.today() - timedelta(days=1)).isoformat()
    hoy = date.today().isoformat()

    try:
        _validar_fecha_cita(ayer)
    except ValueError as exc:
        assert "anterior a hoy" in str(exc)
    else:
        raise AssertionError("Se aceptó una fecha anterior a hoy.")

    assert _validar_fecha_cita(hoy) == hoy

def test_codigo_personal_6_digitos():
    assert es_codigo_institucional_valido("482615")
    assert not es_codigo_institucional_valido("48261")
    assert not es_codigo_institucional_valido("4826157")
    assert not es_codigo_institucional_valido("48A615")


def test_solicitud_rechaza_horario_ocupado_por_cualquier_participante(monkeypatch):
    import routes.solicitudes as solicitudes

    llamada = {}

    def horario_ocupado(*args):
        llamada["args"] = args
        return {"id": 14}

    monkeypatch.setattr(solicitudes, "_cita_horario_ocupado", horario_ocupado)
    solicitud = {
        "id_docente": 3,
        "id_estudiante": 4,
        "id_acudiente": 5,
    }

    try:
        _validar_horario_disponible(solicitud, "2026-10-01", "09:30")
    except ValueError as exc:
        assert "docente, estudiante o acudiente" in str(exc)
    else:
        raise AssertionError("Se aceptó un horario ocupado.")

    assert llamada["args"] == (3, 4, 5, "2026-10-01", "09:30")


def test_solicitud_siempre_reserva_en_coordinacion(monkeypatch):
    import routes.solicitudes as solicitudes

    reservas = []
    monkeypatch.setattr(solicitudes, "consultar", lambda *args, **kwargs: {"id": 1})
    monkeypatch.setattr(solicitudes, "reservar_cita", lambda sql, params: reservas.append(params) or 17)
    solicitud = {"id_estudiante": 2, "id_acudiente": 3, "id_docente": 4, "id_motivo": 5, "lugar": "Sala de reuniones"}
    identidad = solicitudes._cita_desde_solicitud(solicitud, date.today().isoformat(), "10:30", "Confirmada", 9)
    assert identidad == 17
    assert reservas[0][8] == "Coordinación"
