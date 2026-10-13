from pathlib import Path


def test_login_template_has_personal_fields():
    text = Path('templates/auth/login.html').read_text(encoding='utf-8')
    assert 'Sede' in text
    assert 'codigo_institucional' in text
    assert 'pattern="[0-9]{6}"' in text


def test_roles_define_the_institutional_sedes():
    from roles import SEDES_INSTITUCIONALES
    assert len(SEDES_INSTITUCIONALES) == 7
    nombres = [x[1] for x in SEDES_INSTITUCIONALES]
    assert nombres == [
        'Sede Principal (Las Américas)',
        'Sede Arboleda Campestre',
        'Sede Picaleña',
        'Sede Bello Horizonte',
        'Sede Secundino Porras Cruz',
        'Sede San Francisco Club',
        'Sede San Martín',
    ]


def test_login_template_does_not_expose_sede_codes():
    text = Path('templates/auth/login.html').read_text(encoding='utf-8')
    assert 'data-codigo' not in text
    assert 'Código {{ sede.codigo }}' not in text
