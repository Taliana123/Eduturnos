from roles import ROLES_LOGIN, PORTALES, es_correo_institucional

def test_roles_login_incluyen_roles_reales():
    roles={valor for _,valor in ROLES_LOGIN}
    assert roles=={"Estudiante","Acudiente","Docente","Rector","Administrador / Coordinador"}

def test_coordinador_nombre_amigable():
    assert ("Coordinador","Administrador / Coordinador") in ROLES_LOGIN

def test_dominio_institucional():
    assert es_correo_institucional("docente@jjfh.edu.co")
    assert not es_correo_institucional("docente@gmail.com")
