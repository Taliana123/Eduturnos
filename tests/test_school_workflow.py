from datetime import date, datetime, time, timedelta
from decimal import Decimal
import gzip
import hashlib
import json

import pytest

from tools.admin.respaldo import codificar, decodificar, leer_respaldo
from pathlib import Path
from servicios import reuniones
from tools import enviar_recordatorios
from app import app
from routes import citas as citas_routes, helpers
from werkzeug.exceptions import Forbidden


@pytest.mark.parametrize("valor", [date(2026, 10, 5), datetime(2026, 10, 5, 12, 30), time(10, 30), timedelta(hours=10, minutes=30), Decimal("123.45"), b"datos"])
def test_respaldo_conserva_tipos(valor):
    assert json.loads(json.dumps(valor, default=codificar), object_hook=decodificar) == valor


def test_respaldo_rechaza_archivo_modificado(tmp_path):
    archivo = tmp_path / "backup.json.gz"
    with gzip.open(archivo, "wt", encoding="utf-8") as salida:
        json.dump({"version": 1, "tablas": [{"nombre": "prueba"}]}, salida)
    checksum = archivo.with_suffix(".gz.sha256")
    checksum.write_text(hashlib.sha256(archivo.read_bytes()).hexdigest(), encoding="ascii")
    assert leer_respaldo(archivo)["version"] == 1
    archivo.write_bytes(b"alterado")
    with pytest.raises(ValueError, match="integridad"):
        leer_respaldo(archivo)


def test_migracion_escolar_no_elimina_datos():
    sql = (Path(__file__).resolve().parents[1] / "sql" / "school_workflow.sql").read_text(encoding="utf-8")
    assert sql.count("CREATE TABLE IF NOT EXISTS") == 7
    assert "DROP " not in sql
    assert "DELETE FROM " not in sql
    for nombre in ("compromisos_cita", "cierres_cita", "reprogramaciones_cita", "disponibilidad_docente", "entregas_correo", "integraciones_google", "eventos_google"):
        assert f"CREATE TABLE IF NOT EXISTS {nombre}" in sql


def test_migracion_google_calendar_crea_cola_durable_sin_borrar_datos():
    sql = (Path(__file__).resolve().parents[1] / "sql" / "google_calendar_sync.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS google_calendar_sync_queue" in sql
    assert "UNIQUE KEY uq_google_queue_cita_scope (id_cita, scope_key)" in sql
    assert "intentos SMALLINT UNSIGNED NOT NULL DEFAULT 0" in sql
    assert "ultimo_intento DATETIME NULL" in sql
    assert "proximo_intento DATETIME NULL" in sql
    assert "lease_until DATETIME NULL" in sql
    assert "ALTER TABLE eventos_google" in sql
    assert "DROP " not in sql
    assert "DELETE FROM " not in sql


def test_google_calendar_tokens_cifrados_y_configuracion_https():
    from servicios.google_calendar import cifrar_token, configuracion_lista, descifrar_token

    token = {"access_token": "token-prueba", "refresh_token": "refresh-prueba"}
    with app.app_context():
        cifrado = cifrar_token(token)
        assert "token-prueba" not in cifrado
        assert descifrar_token(cifrado) == token
        valores = {key: app.config.get(key) for key in ("APP_ORIGIN", "GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET")}
        try:
            app.config.update(APP_ORIGIN="http://192.168.18.24:5000", GOOGLE_OAUTH_CLIENT_ID="id", GOOGLE_OAUTH_CLIENT_SECRET="secret")
            assert not configuracion_lista()
            app.config["APP_ORIGIN"] = "https://eduturnos.example.edu.co"
            assert configuracion_lista()
        finally:
            app.config.update(valores)


def test_reserva_persiste_la_tarea_de_google_en_la_transaccion_local(monkeypatch):
    eventos = []

    class CursorPrueba:
        lastrowid = 321

        def execute(self, sql, params=()):
            eventos.append("insert")

        def close(self):
            pass

    class ConexionPrueba:
        def cursor(self, **kwargs):
            return CursorPrueba()

    from contextlib import contextmanager

    @contextmanager
    def transaccion_prueba():
        yield ConexionPrueba()
        eventos.append("commit")

    from servicios import google_calendar

    monkeypatch.setattr(reuniones, "transaccion", transaccion_prueba)
    monkeypatch.setattr(reuniones, "validar_disponibilidad", lambda *args: None)
    monkeypatch.setattr(reuniones, "bloquear_agenda", lambda *args: None)
    monkeypatch.setattr(reuniones, "comprobar_hueco", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        google_calendar,
        "encolar_cita_cursor",
        lambda cursor, cita_id, creador_id: eventos.append(("outbox", cita_id, creador_id)),
    )
    parametros = (2, 3, 1, 4, 5, 6, date.today() + timedelta(days=1), time(7), "", "", 77)

    with app.app_context():
        cita_id = reuniones.reservar_cita("INSERT INTO citas VALUES (...) ", parametros)

    assert cita_id == 321
    assert eventos == ["insert", ("outbox", 321, 77), "commit"]


def test_fallo_temporal_de_google_se_programa_para_reintento(monkeypatch):
    from servicios import google_calendar

    tarea = {
        "id": 9,
        "id_cita": 321,
        "scope_key": "institucional",
        "intentos": 2,
        "claim_token": "lease-de-prueba",
    }
    escrituras = []
    tareas = iter((tarea, None))

    def fallar(_tarea):
        raise google_calendar.GoogleCalendarError("Google no disponible", 503)

    monkeypatch.setattr(google_calendar, "_tomar_tarea_google", lambda: next(tareas))
    monkeypatch.setattr(google_calendar, "_procesar_tarea_google", fallar)
    monkeypatch.setattr(
        google_calendar,
        "ejecutar",
        lambda sql, params=(): escrituras.append((sql, params)),
    )

    with app.app_context():
        resultado = google_calendar.procesar_cola_google(limite=1)

    assert resultado == {"procesadas": 1, "sincronizadas": 0, "fallidas": 1}
    assert escrituras[0][1][0] == "Reintentar"
    assert "DATE_ADD(NOW(),INTERVAL 4 MINUTE)" in escrituras[0][0]
    assert escrituras[0][1][1] == "Google no disponible"


def test_identificador_de_evento_google_es_determinista_y_admitido_por_google():
    from servicios.google_calendar import _event_id

    first = _event_id(321, "institucional")
    assert first == _event_id(321, "institucional")
    assert first.startswith("eduturnos")
    assert all(character in "0123456789abcdefghijklmnopqrstuvwxyz" for character in first)


def test_actualizacion_google_no_incluye_id_en_el_payload(monkeypatch):
    from servicios import google_calendar

    solicitudes = []

    class Respuesta:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b"{}"

    monkeypatch.setattr(
        google_calendar,
        "urlopen",
        lambda solicitud, timeout: solicitudes.append((solicitud, timeout)) or Respuesta(),
    )

    with app.app_context():
        google_calendar._actualizar_evento_google(
            "https://calendar.google.test/evento",
            {"id": "evento-existente", "summary": "Citación escolar"},
            "token-prueba",
        )

    assert solicitudes[0][0].get_method() == "PATCH"
    assert json.loads(solicitudes[0][0].data) == {"summary": "Citación escolar"}


def test_solicitud_google_envia_token_bearer(monkeypatch):
    from servicios import google_calendar

    class Respuesta:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b"{}"

    solicitudes = []
    monkeypatch.setattr(
        google_calendar,
        "urlopen",
        lambda solicitud, timeout: solicitudes.append(solicitud) or Respuesta(),
    )

    google_calendar._solicitud_json(
        "https://calendar.google.test/events",
        {},
        "token-de-prueba",
    )

    assert solicitudes[0].get_header("Authorization") == "Bearer token-de-prueba"


def test_error_google_muestra_solo_mensajes_seguros():
    from servicios.google_calendar import GoogleCalendarError, error_google_seguro

    assert error_google_seguro(ValueError("detalle con datos sensibles")) == (
        "Error interno de tipo ValueError."
    )
    assert error_google_seguro(GoogleCalendarError("Google respondió HTTP 503.", 503)) == (
        "Google respondió HTTP 503."
    )


@pytest.mark.parametrize("hora_cita", [time(8), timedelta(hours=17)])
def test_evento_google_no_incluye_datos_del_estudiante(monkeypatch, hora_cita):
    import time as clock
    from servicios import google_calendar

    peticiones = []
    escrituras = []
    cita = {
        "id": 42,
        "fecha": date(2026, 10, 20),
        "hora": hora_cita,
        "lugar": "Coordinación",
        "motivo": "Convivencia",
        "sede": "Sede principal",
    }
    conexion = {
        "scope_key": "usuario:7",
        "calendar_id": "primary",
        "token_cifrado": "cifrado",
    }

    def consultar_mock(sql, params=(), uno=False):
        if "FROM integraciones_google" in sql:
            return [conexion]
        if "FROM eventos_google" in sql:
            return None
        if "FROM citas c" in sql:
            return cita
        raise AssertionError(sql)

    monkeypatch.setattr(google_calendar, "configuracion_lista", lambda: True)
    monkeypatch.setattr(google_calendar, "consultar", consultar_mock)
    monkeypatch.setattr(google_calendar, "descifrar_token", lambda value: {"access_token": "a", "refresh_token": "r", "expires_at": clock.time() + 3600})
    monkeypatch.setattr(google_calendar, "_renovar_token", lambda row, token: token)
    monkeypatch.setattr(google_calendar, "_solicitud_json", lambda url, event, token: peticiones.append(event) or event)
    monkeypatch.setattr(google_calendar, "ejecutar", lambda sql, params: escrituras.append((sql, params)))

    with app.app_context():
        resultado = google_calendar.sincronizar_cita(42, 7)

    assert resultado == [{"scope": "usuario:7", "estado": "Sincronizado"}]
    assert peticiones[0]["summary"] == "Citación escolar"
    assert peticiones[0]["location"] == "Coordinación"
    assert peticiones[0]["reminders"] == {
        "useDefault": False,
        "overrides": [
            {"method": "popup", "minutes": 1440},
            {"method": "popup", "minutes": 120},
        ],
    }
    assert "42" not in peticiones[0]["description"]
    assert "estudiante" not in peticiones[0]["description"].lower()
    assert escrituras and "Sincronizado" in escrituras[0][0]


def test_compromiso_valida_responsable_y_plazo():
    assert reuniones.validar_compromiso(" Acuerdo ", " Docente ", date.today().isoformat()) == ("Acuerdo", "Docente", date.today())
    with pytest.raises(ValueError):
        reuniones.validar_compromiso("Acuerdo", "", date.today().isoformat())
    with pytest.raises(ValueError):
        reuniones.validar_compromiso("Acuerdo", "Docente", (date.today() - timedelta(days=1)).isoformat())


@pytest.mark.parametrize("rol", ["Estudiante", "Acudiente"])
def test_roles_personales_pueden_conectar_google_calendar(rol):
    from routes.integraciones_google import _permite

    assert _permite("personal", rol)
    assert not _permite("institucional", rol)


def test_backfill_google_encola_citas_futuras_del_usuario(monkeypatch):
    from servicios import google_calendar

    user_id = 42
    consultas = []
    encoladas = []

    def consultar_mock(sql, params=(), uno=False):
        consultas.append((sql, params))
        return [{"id": 5, "creado_por": 77}]

    monkeypatch.setattr(google_calendar, "consultar", consultar_mock)
    monkeypatch.setattr(
        google_calendar,
        "encolar_cita",
        lambda cita_id, creador_id: encoladas.append((cita_id, creador_id)) or 2,
    )

    with app.app_context():
        resumen = google_calendar.encolar_citas_futuras(f"usuario:{user_id}", user_id)

    sql, parametros = consultas[0]
    assert "TIMESTAMP(c.fecha,c.hora)>=NOW()" in sql
    assert "e.id_usuario=%s" in sql
    assert "a.id_usuario=%s" in sql
    assert "d.id_usuario=%s" in sql
    assert parametros == (user_id, user_id, user_id, user_id, user_id)
    assert resumen == {"citas": 1, "encoladas": 2}
    assert encoladas == [(5, 77)]


@pytest.mark.parametrize("hora", ["07:00", "11:30", "13:00", "17:30"])
def test_horarios_automaticos_permiten_ambas_jornadas(monkeypatch, hora):
    def no_consultar(*args):
        pytest.fail("El horario no debe depender de la disponibilidad configurada por un rol.")
    monkeypatch.setattr(reuniones, "consultar", no_consultar)
    reuniones.validar_disponibilidad(1, date.today(), hora)


@pytest.mark.parametrize("hora", ["06:30", "12:00", "12:30", "18:00", "09:45"])
def test_horarios_automaticos_rechazan_fuera_de_jornada(hora):
    with pytest.raises(ValueError):
        reuniones.validar_disponibilidad(1, date.today(), hora)


@pytest.mark.parametrize("hora, esperado", [
    ("10:00:00", "10:00 AM"),
    ("10:30:00", "10:30 AM"),
    (time(17, 30, 45), "5:30 PM"),
    (timedelta(hours=13, minutes=5), "1:05 PM"),
    (datetime(2026, 10, 6, 0, 5), "12:05 AM"),
    (time(12), "12:00 PM"),
])
def test_hora_ampm_conserva_hora_y_minutos(hora, esperado):
    assert app.jinja_env.from_string("{{ hora|hora_ampm }}").render(hora=hora) == esperado


@pytest.mark.parametrize("extension", ["csv", "xlsx"])
def test_reporte_descargado_muestra_hora_ampm(monkeypatch, extension):
    import csv
    from io import BytesIO, StringIO
    from routes import reportes

    fila = {"id": 5, "fecha": date(2026, 10, 6), "hora": timedelta(hours=13, minutes=30), "lugar": "", "estado": "Pendiente", "motivo": "Reunión", "estudiante": "Estudiante", "docente": "Docente", "acudiente": "Acudiente", "observaciones": ""}
    monkeypatch.setattr(reportes, "_filas_reporte", lambda: [fila])
    with app.test_request_context(f"/reportes/exportar.{extension}"):
        respuesta = getattr(reportes, f"exportar_{extension}").__wrapped__()
    assert respuesta.status_code == 200
    if extension == "csv":
        filas = list(csv.reader(StringIO(respuesta.get_data(as_text=True).lstrip("\ufeff"))))
        assert filas[1][2] == "1:30 PM"
    else:
        from openpyxl import load_workbook

        libro = load_workbook(BytesIO(respuesta.get_data()))
        assert libro.active["C2"].value == "1:30 PM"
        libro.close()


def test_selector_hora_muestra_jornadas_y_ampm():
    from flask import render_template

    with app.test_request_context("/"):
        contenido = render_template("_hora_cita.html")
        selector = app.jinja_env.from_string("{% from '_hora_cita.html' import selector_hora %}{{ selector_hora('hora') }}").render()
    assert contenido.strip() == ""
    assert selector.count("<optgroup") == 2
    assert selector.count("<option value=") == 21
    for valor, etiqueta in (("07:00", "7:00 AM"), ("11:30", "11:30 AM"), ("13:00", "1:00 PM"), ("17:30", "5:30 PM")):
        assert f'<option value="{valor}">{etiqueta}</option>' in selector
    assert 'value="12:00"' not in selector


def test_solicitud_usa_reserva_transaccional(monkeypatch):
    from routes import solicitudes

    reservas = []
    monkeypatch.setattr(solicitudes, "consultar", lambda *args, **kwargs: {"id": 1})
    monkeypatch.setattr(solicitudes, "reservar_cita", lambda sql, params: reservas.append(params) or 901)
    solicitud = {"id_estudiante": 1, "id_acudiente": 2, "id_docente": 3, "id_motivo": 4}
    assert solicitudes._cita_desde_solicitud(solicitud, date.today().isoformat(), "13:00", "Pendiente", 7) == 901
    assert reservas[0][7] == "13:00"


def test_historial_privado_no_se_consulta_para_familias(monkeypatch):
    consultas = []
    def consultar(sql, params):
        consultas.append((sql, params))
        return []
    monkeypatch.setattr(reuniones, "consultar", consultar)
    datos = reuniones.datos_escolares([{"id": 5}], privado=False)
    assert len(consultas) == 1
    assert "compromisos_cita" in consultas[0][0]
    assert consultas[0][1] == (5,)
    assert datos[5]["cierre"] is None
    assert datos[5]["notas"] == []


def test_historial_personal_carga_notas_y_resultados(monkeypatch):
    consultas = []
    nota = {"id_cita": 5, "observaciones": "Acuerdo", "asistencia": "Asistió", "autor": "Docente"}
    def consultar(sql, params):
        consultas.append(sql)
        if "FROM seguimiento_citas" in sql:
            return [nota]
        return []
    monkeypatch.setattr(reuniones, "consultar", consultar)
    datos = reuniones.datos_escolares([{"id": 5}], privado=True)
    assert len(consultas) == 5
    assert any("seguimiento_citas" in consulta for consulta in consultas)
    assert datos[5]["notas"] == [nota]


def test_horario_detecta_cruces_de_treinta_minutos():
    class CursorPrueba:
        def execute(self, sql, params):
            self.sql = sql
            self.params = params
        def fetchone(self):
            return {"id": 5}
    cursor = CursorPrueba()
    with pytest.raises(ValueError, match="cruza"):
        reuniones.comprobar_hueco(cursor, 1, 2, 3, date.today(), "10:30", excluir=4)
    assert "00:30:00" in cursor.sql
    assert "FOR UPDATE" in cursor.sql
    assert cursor.params[1] == 4


@pytest.mark.parametrize("rol", ["Estudiante", "Acudiente"])
def test_operaciones_escolares_restringen_escritura(monkeypatch, rol):
    monkeypatch.setattr(helpers, "usuario_actual", lambda: {"id_usuario": 7, "rol_nombre": rol})
    with app.test_request_context("/citas/5/compromisos", method="POST"):
        for funcion in (citas_routes.agregar_compromiso, citas_routes.reprogramar_cita, citas_routes.acta_cita):
            with pytest.raises(Forbidden):
                funcion(5)


def test_compromiso_no_se_guarda_sin_responsable(monkeypatch):
    monkeypatch.setattr(citas_routes, "usuario_actual", lambda: {"id_usuario": 7, "rol_nombre": "Rector"})
    monkeypatch.setattr(citas_routes, "_cita_autorizada", lambda *args: {"estado": "Confirmada"})
    escrituras = []
    monkeypatch.setattr(citas_routes, "ejecutar", lambda *args: escrituras.append(args))
    with app.test_request_context("/citas/5/compromisos", method="POST", data={"descripcion": "Acuerdo", "responsable": "", "fecha_limite": date.today().isoformat()}):
        response = citas_routes.agregar_compromiso.__wrapped__(5)
    assert response.status_code == 302
    assert not escrituras


def test_recordatorio_registra_entrega_por_usuario(monkeypatch):
    class CursorPrueba:
        def __init__(self):
            self.sql = []
            self.filas = iter([{"id": 8, "recordatorio_24h_enviado": 0}])
            self.cerrado = False
        def execute(self, sql, params=()):
            self.sql.append((sql, params))
        def fetchone(self):
            return next(self.filas)
        def close(self):
            self.cerrado = True
    cursor = CursorPrueba()
    class ConexionPrueba:
        def cursor(self, **kwargs):
            return cursor
        def commit(self):
            pass
        def rollback(self):
            raise AssertionError("No debía revertirse el recordatorio")
        def close(self):
            pass
    monkeypatch.setattr(enviar_recordatorios, "conexion", lambda: ConexionPrueba())
    monkeypatch.setattr(enviar_recordatorios, "obtener_usuarios_cita", lambda cita: {1, 2})
    monkeypatch.setattr(enviar_recordatorios, "correos_usuarios", lambda ids: {1: "", 2: "persona@example.edu"})
    monkeypatch.setattr(enviar_recordatorios, "crear_notificacion", lambda *args: None)
    monkeypatch.setattr(enviar_recordatorios, "enviar_emails_recordatorio", lambda *args: 1)
    resultado = enviar_recordatorios.procesar_recordatorio({"id": 8}, "24h", "Aviso", "Mensaje")
    entregas = [params for sql, params in cursor.sql if sql.startswith("INSERT INTO entregas_correo")]
    assert resultado == (1, 1)
    assert set(entregas) == {(8, 1, "Recordatorio24h", "Sin correo"), (8, 2, "Recordatorio24h", "Pendiente")}
    assert cursor.cerrado


def test_recordatorios_reintentan_correos_pendientes_sin_cita_en_ventana(monkeypatch):
    llamadas = []
    monkeypatch.setattr(enviar_recordatorios, "obtener_citas", lambda: [])
    monkeypatch.setattr(enviar_recordatorios, "enviar_emails_recordatorio", lambda: llamadas.append("outbox") or 2)
    assert enviar_recordatorios.procesar_recordatorios() is None
    assert llamadas == ["outbox"]


@pytest.mark.parametrize("falla,estado", [(False, "Enviado"), (True, "Fallido")])
def test_entrega_recordatorio_registra_resultado_smtp(monkeypatch, falla, estado):
    monkeypatch.setattr(enviar_recordatorios, "MAIL_HOST", "smtp.example.edu")
    monkeypatch.setattr(enviar_recordatorios, "MAIL_USERNAME", "sender@example.edu")
    monkeypatch.setattr(enviar_recordatorios, "MAIL_PASSWORD", "solo-prueba")
    monkeypatch.setattr(enviar_recordatorios, "MAIL_FROM", "sender@example.edu")
    monkeypatch.setattr(enviar_recordatorios, "consultar", lambda *args: [{"id_cita": 8, "id_usuario": 2, "tipo": "Recordatorio24h", "correo": "persona@example.edu", "fecha": date.today(), "hora": time(10, 30), "lugar": "Coordinación", "estudiante": "Estudiante Prueba"}])
    actualizaciones = []
    monkeypatch.setattr(enviar_recordatorios, "_actualizar_entrega_correo", lambda *args, **kwargs: actualizaciones.append((args, kwargs)))
    def enviar(*args):
        if falla:
            raise TimeoutError("SMTP no disponible")
    monkeypatch.setattr(enviar_recordatorios, "_enviar_un_correo", enviar)
    enviados = enviar_recordatorios.enviar_emails_recordatorio()
    assert enviados == (0 if falla else 1)
    assert actualizaciones[0][0][3] == estado
    assert actualizaciones[0][1]["intento"] is True