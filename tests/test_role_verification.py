from roles import PORTALES


def test_portales_tienen_un_rol_unico():
    roles = [info["rol"] for info in PORTALES.values()]
    assert len(roles) == len(set(roles))


def test_acudiente_es_un_portal_separado():
    assert PORTALES["acudiente"]["rol"] == "Acudiente"


def test_directivos_no_comparten_portal():
    assert PORTALES["coordinador"]["rol"] != PORTALES["rector"]["rol"]
