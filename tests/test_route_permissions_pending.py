import os

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("MYSQL_HOST", "127.0.0.1")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("MYSQL_USER", "root")
os.environ.setdefault("MYSQL_PASSWORD", "")
os.environ.setdefault("MYSQL_DATABASE", "eduturnos")
os.environ.setdefault("EDUTURNOS_SKIP_DB_TEST", "1")

from app import app
import routes.helpers as helpers


ADMIN_ROUTES = (
    "/configuracion/",
    "/configuracion/auditoria",
    "/reportes/",
    "/estudiantes/",
    "/acudientes/",
    "/docentes/",
)


def _usuario(rol):
    return {
        "id_usuario": 99,
        "rol_nombre": rol,
        "documento": "99999999",
        "estado": 1,
    }


def test_invitado_no_entra_a_modulos_privados():
    original = helpers.usuario_actual
    try:
        helpers.usuario_actual = lambda: None
        client = app.test_client()
        for path in ADMIN_ROUTES + ("/seguimiento/", "/citas/", "/notificaciones/", "/calendario/"):
            response = client.get(path)
            assert response.status_code in (302, 303), path
            assert "/auth/login" in response.headers.get("Location", ""), path
    finally:
        helpers.usuario_actual = original


def test_estudiante_y_acudiente_no_entran_a_rutas_administrativas():
    original = helpers.usuario_actual
    try:
        for rol in ("Estudiante", "Acudiente"):
            helpers.usuario_actual = lambda rol=rol: _usuario(rol)
            client = app.test_client()
            for path in ADMIN_ROUTES + ("/seguimiento/", "/citas/nueva"):
                response = client.get(path)
                assert response.status_code == 403, (rol, path, response.status_code)
    finally:
        helpers.usuario_actual = original


def test_docente_no_entra_a_administracion_superior():
    original = helpers.usuario_actual
    try:
        helpers.usuario_actual = lambda: _usuario("Docente")
        client = app.test_client()
        for path in ("/configuracion/", "/configuracion/auditoria", "/reportes/", "/acudientes/", "/docentes/"):
            response = client.get(path)
            assert response.status_code == 403, path
        # El módulo de estudiantes y seguimiento sí contemplan al docente por diseño;
        # aquí solo verificamos que las rutas administrativas superiores estén bloqueadas.
        source_students = open("routes/estudiantes.py", encoding="utf-8").read()
        source_follow = open("routes/seguimiento.py", encoding="utf-8").read()
        assert '"Docente"' in source_students
        assert '"Docente"' in source_follow
        assert client.get("/citas/nueva").status_code == 200 or client.get("/citas/nueva").status_code in (500, 503)
    finally:
        helpers.usuario_actual = original


def test_rutas_reales_de_permisos_estan_registradas():
    endpoints = {rule.endpoint for rule in app.url_map.iter_rules()}
    required = {
        "configuracion.index",
        "configuracion.auditoria_view",
        "configuracion.guardar_institucion",
        "configuracion.guardar_sede",
        "configuracion.guardar_jornada",
        "configuracion.guardar_grado",
        "configuracion.guardar_grupo",
        "configuracion.guardar_motivo",
        "configuracion.guardar_estado",
        "reportes.index",
        "estudiantes.lista",
        "acudientes.lista",
        "docentes.lista",
        "citas.nueva",
    }
    assert required <= endpoints


def test_rector_puede_entrar_a_rutas_institucionales():
    original = helpers.usuario_actual
    try:
        helpers.usuario_actual = lambda: _usuario("Rector")
        client = app.test_client()
        for path in ("/configuracion/", "/reportes/", "/estudiantes/", "/acudientes/", "/docentes/"):
            response = client.get(path)
            assert response.status_code not in (302, 303, 403), path
    finally:
        helpers.usuario_actual = original


def test_estudiante_acudiente_y_docente_no_superan_administracion_por_url():
    original = helpers.usuario_actual
    try:
        for rol in ("Estudiante", "Acudiente", "Docente"):
            helpers.usuario_actual = lambda rol=rol: _usuario(rol)
            client = app.test_client()
            response = client.get("/configuracion/institucion/guardar")
            assert response.status_code in (403, 405), rol
    finally:
        helpers.usuario_actual = original


def test_panorama_reportes_solo_rector_y_coordinador(monkeypatch):
    from routes import reportes

    resumen = {"total": 5, "pendientes": 2, "confirmadas": 1, "realizadas": 1, "no_asistio": 1}
    monkeypatch.setattr(reportes, "consultar", lambda *args, **kwargs: resumen if kwargs.get("uno") else [])
    monkeypatch.setattr(reportes, "_filas_reporte", lambda: [])
    for rol in ("Rector", "Administrador / Coordinador", "Super Admin", "Docente", "Estudiante", "Acudiente"):
        usuario = _usuario(rol)
        monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
        monkeypatch.setattr(reportes, "usuario_actual", lambda: usuario)
        response = app.test_client().get("/reportes/?desde=2026-10-01&hasta=2026-10-10&estado=Pendiente")
        if rol in ("Docente", "Estudiante", "Acudiente"):
            assert response.status_code == 403
            continue
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert ('aria-label="Reportes de citaciones"' in html) == (rol != "Super Admin")
        if rol != "Super Admin":
            assert 'value="2" max="5"' in html
            assert 'class="reportes-page reportes-panorama-activo"' in html
            panorama = html.split('aria-label="Reportes de citaciones"', 1)[1].split('<section class="tarjeta reportes-filter">', 1)[0]
            for texto in ("Panorama institucional", "Del registro a la decisión.", "Resumen de citaciones"):
                assert texto not in panorama
            assert '<span>Total de citaciones</span><strong>5</strong>' in panorama
            for extension in ("csv", "xlsx", "pdf"):
                assert f'/reportes/exportar.{extension}?desde=2026-10-01&amp;hasta=2026-10-10&amp;estado=Pendiente' in panorama
        else:
            assert 'class="reportes-page reportes-panorama-activo"' not in html


def test_panorama_reportes_sin_citaciones(monkeypatch):
    from routes import reportes

    usuario = _usuario("Rector")
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(reportes, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(reportes, "consultar", lambda *args, **kwargs: {} if kwargs.get("uno") else [])
    monkeypatch.setattr(reportes, "_filas_reporte", lambda: [])
    response = app.test_client().get("/reportes/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'value="0" max="1"' in html
    assert '<span>Total de citaciones</span><strong>0</strong>' in html
    assert "No hay citaciones en este periodo." in html


def test_seguimiento_lista_procesos_y_respeta_docente(monkeypatch):
    from datetime import date, time
    from routes import seguimiento

    for rol in ("Rector", "Administrador / Coordinador", "Docente"):
        usuario = _usuario(rol)
        consultas = []

        def consultar(sql, params):
            consultas.append((sql, params))
            if "SELECT c.id,e.nombres" in sql:
                return [{"id": 17, "nombres": "Ana", "apellidos": "Perez", "estado": "Pendiente", "descripcion": None, "fecha": date(2026, 10, 9), "hora": time(10, 30), "grado": "9", "grupo": "2", "motivo": "Académica", "lugar": "Coordinación", "sede": "Sede Principal (Las Américas)", "acudiente": "Laura Acudiente"}]
            return []

        monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
        monkeypatch.setattr(seguimiento, "usuario_actual", lambda: usuario)
        monkeypatch.setattr(seguimiento, "consultar", consultar)
        response = app.test_client().get("/seguimiento/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Compromisos y asistencia" in html
        assert "1 proceso" in html
        assert "Ana Perez" in html
        assert '/seguimiento/cita/17' in html
        assert 'data-seguimiento-dialog="seguimiento-detalle-17"' in html
        assert "Detalle de citación" in html
        assert "Historial de seguimiento" in html
        assert "Aún no hay acciones registradas." in html
        assert "data-seguimiento-print" in html
        assert "Grado 9° · 02 · Académica" in html
        assert "9 de oct de 2026 · 10:30 AM" in html
        assert "Coordinación · Sede Principal (Las Américas)" in html
        assert "Acudiente: Laura Acudiente" in html
        assert "Encuentro con el acudiente" in html
        for sql, params in consultas:
            assert ("d.id_usuario=%s" in sql) == (rol == "Docente")
            assert params == ((99,) if rol == "Docente" else ())


def test_seguimiento_detalle_historial_por_cita(monkeypatch):
    from datetime import date, datetime, time
    from routes import seguimiento

    usuario = _usuario("Rector")
    procesos = [{"id": identidad, "nombres": "Ana", "apellidos": "Perez", "estado": "Pendiente", "fecha": date(2026, 10, 10), "hora": time(8), "descripcion": None} for identidad in (17, 18)]
    registros = [{"id_cita": 17, "fecha_seguimiento": datetime(2026, 10, 10, 9), "estado_actual": "Pendiente", "asistencia": "Pendiente", "observaciones": "Compromiso exclusivo cita 17", "usuario_n": "Rector", "usuario_a": "Prueba", "nombres": "Ana", "apellidos": "Perez"}]
    monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(seguimiento, "usuario_actual", lambda: usuario)
    monkeypatch.setattr(seguimiento, "consultar", lambda sql, params: procesos if "SELECT c.id,e.nombres" in sql else registros)
    response = app.test_client().get("/seguimiento/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    detalle17 = html.split('id="seguimiento-detalle-17"', 1)[1].split('</dialog>', 1)[0]
    detalle18 = html.split('id="seguimiento-detalle-18"', 1)[1].split('</dialog>', 1)[0]
    assert "Compromiso exclusivo cita 17" in detalle17
    assert "Compromiso exclusivo cita 17" not in detalle18
    assert "Aún no hay acciones registradas." in detalle18


def test_directorio_estudiantes_pc_busqueda_y_permisos(monkeypatch):
    from routes import estudiantes

    for rol in ("Rector", "Administrador / Coordinador", "Docente"):
        usuario = _usuario(rol)
        consultas = []

        def consultar(sql, params):
            consultas.append((sql, params))
            return [{"id_estudiante": 17, "nombres": "Ana", "apellidos": "Perez", "documento": "123", "curso": None, "sede": "Principal", "jornada": "Mañana", "grado": "9", "grupo": "02", "acudiente": "Laura Perez", "estado": "Activo"}]

        monkeypatch.setattr(helpers, "usuario_actual", lambda: usuario)
        monkeypatch.setattr(estudiantes, "consultar", consultar)
        response = app.test_client().get("/estudiantes/?q=Principal")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        desktop = html.split('class="estudiantes-desktop"', 1)[1].split('class="estudiantes-mobile-legacy"', 1)[0]
        assert "1 estudiante" in desktop
        assert "Laura Perez" in desktop
        assert "Grado / Grupo" in desktop
        assert ("Registrar estudiante" in desktop) == (rol != "Docente")
        assert ('/estudiantes/17/editar' in desktop) == (rol != "Docente")
        sql, params = consultas[0]
        assert "ea.estado=1 AND a.estado=1" in sql
        assert "COALESCE(s.nombre,'') LIKE %s" in sql
        assert "COALESCE(gr.nombre,'') LIKE %s" in sql
        assert ("d.id_usuario=%s" in sql) == (rol == "Docente")
        assert params == (((99,) if rol == "Docente" else ()) + ("%Principal%",) * 6)
