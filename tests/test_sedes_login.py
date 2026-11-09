from pathlib import Path


def test_login_template_has_personal_fields():
    text = Path('templates/auth/login.html').read_text(encoding='utf-8')
    assert 'Sede' in text
    assert 'codigo_institucional' in text
    assert 'pattern="[0-9]{6}"' in text
    assert 'data-staff-code-field hidden' in text
    assert 'v=20261109_staff_code_by_email_v1' in text


def test_login_muestra_codigo_solo_para_correo_institucional_del_personal():
    script = Path('static/js/institution-login.js').read_text(encoding='utf-8')
    assert "const isInstitutionalStaffEmail = /@jjfh\\.edu\\.co$/i.test" in script
    assert "staffCodeField.hidden = !isJjfh || !isInstitutionalStaffEmail" in script
    assert "identifier?.addEventListener('input', update)" in script
    assert "field === staffCodeInput && !isInstitutionalStaffEmail" in script


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
