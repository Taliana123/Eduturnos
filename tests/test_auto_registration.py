from roles import PORTALES


def test_portals_have_distinct_roles():
    roles = [info["rol"] for info in PORTALES.values()]
    assert len(set(roles)) == len(roles)


def test_no_manual_access_code_field_required_in_portal_config():
    for info in PORTALES.values():
        assert "codigo" not in info
        assert "codigo_acceso" not in info
    # Los estudiantes no requieren un código que deban digitar en el registro.
    assert "codigo_estudiantil" not in PORTALES["estudiante"]
