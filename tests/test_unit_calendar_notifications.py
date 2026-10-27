from routes.calendario import _filtros_usuario

def test_estudiante_filtra_sus_citas():
    filtros, params = _filtros_usuario({'rol_nombre': 'Estudiante', 'id_usuario': 7})
    assert len(filtros) == 1
    assert 'c.id_estudiante' in filtros[0]
    assert params == [7, 7]
    assert 'cita_participantes' in filtros[0]

def test_docente_filtra_sus_citas():
    filtros, params = _filtros_usuario({'rol_nombre': 'Docente', 'id_usuario': 7})
    assert len(filtros) == 1
    assert 'c.id_docente' in filtros[0]
    assert params == [7, 7, 7, 7]
    assert 'cita_participantes' in filtros[0]

def test_acudiente_filtra_sus_citas():
    filtros, params = _filtros_usuario({'rol_nombre': 'Acudiente', 'id_usuario': 7})
    assert len(filtros) == 1
    assert 'c.id_acudiente' in filtros[0]
    assert params == [7, 7]
    assert 'cita_participantes' in filtros[0]

def test_directivos_ven_todo():
    for rol in ('Super Admin','Rector','Administrador / Coordinador'):
        filtros, params = _filtros_usuario({'rol_nombre': rol})
        assert filtros == []
        assert params == []
