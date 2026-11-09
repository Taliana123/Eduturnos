from pathlib import Path


def test_login_template_has_personal_fields():
    text = Path('templates/auth/login.html').read_text(encoding='utf-8')
    assert 'Sede' in text
    assert 'codigo_institucional' in text
    assert 'pattern="[0-9]{6}"' in text
    assert 'placeholder="6 dígitos"' not in text
    code_field = text.split('name="codigo_institucional"', 1)[1].split('>', 1)[0]
    assert 'placeholder=' not in code_field
    assert 'value=' not in code_field
    assert 'class="personal-field personal-field-code">' in text
    assert 'html body main.login-page .login-card > .section-heading > h1' in text
    assert 'justify-self: start !important;' in text
    assert 'text-align: left !important;' in text
    assert 'v=20261109_staff_code_always_visible_v1' in text
    assert 'right: 18px !important;' in text
    assert 'right: 12px !important;' in text
    assert 'background: #1769aa !important;' in text
    assert 'color: #fff !important;' in text


def test_login_mantiene_codigo_visible_para_acceso_jjfh_y_oculto_en_otras_instituciones():
    script = Path('static/js/institution-login.js').read_text(encoding='utf-8')
    assert "legacy.hidden = !isJjfh" in script
    assert "field.disabled = !isJjfh" in script
    assert "if (!isJjfh) field.value = ''" in script


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
