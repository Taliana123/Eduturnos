from roles import (
    ROLES_LOGIN,
    PORTALES,
    es_correo_gmail,
    es_correo_institucional,
    es_correo_valido_para_rol,
)

def test_roles_login_incluyen_roles_reales():
    roles={valor for _,valor in ROLES_LOGIN}
    assert roles=={"Estudiante","Acudiente","Docente","Rector","Administrador / Coordinador"}

def test_coordinador_nombre_amigable():
    assert ("Coordinador","Administrador / Coordinador") in ROLES_LOGIN

def test_dominio_institucional():
    assert es_correo_institucional("docente@jjfh.edu.co")
    assert es_correo_institucional("DOCENTE@JJFH.EDU.CO")
    assert not es_correo_institucional("docente@gmail.com")

def test_dominio_de_correo_segun_tipo_de_cuenta():
    assert es_correo_gmail("familia@gmail.com")
    assert es_correo_gmail("FAMILIA@GMAIL.COM")
    assert not es_correo_gmail("familia@outlook.com")
    assert es_correo_valido_para_rol("Estudiante", "estudiante@gmail.com")
    assert es_correo_valido_para_rol("Acudiente", "acudiente@gmail.com")
    assert es_correo_valido_para_rol("Docente", "docente@jjfh.edu.co")
    assert es_correo_valido_para_rol("Rector", "rector@jjfh.edu.co")
    assert es_correo_valido_para_rol(
        "Administrador / Coordinador",
        "coordinador@jjfh.edu.co",
    )
    assert not es_correo_valido_para_rol("Estudiante", "estudiante@jjfh.edu.co")
    assert not es_correo_valido_para_rol("Docente", "docente@gmail.com")
