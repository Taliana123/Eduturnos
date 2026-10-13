from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(r"F:\edu_Final")

LOGIN = ROOT / "templates" / "auth" / "login.html"
BASE = ROOT / "templates" / "base.html"
DASH = ROOT / "templates" / "dashboard.html"
DASHBACK = ROOT / "templates" / "dashboard.html.backup_solo_interno"

CSSDIR = ROOT / "static" / "css"
FINALCSS = CSSDIR / "eduturnos_final_real.css"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

print()
print("=" * 72)
print(" EDUTURNOS - AJUSTE FINAL LOGIN")
print("=" * 72)
print()

# ============================================================
# COMPROBAR ARCHIVOS
# ============================================================

for f in [LOGIN, BASE, DASH, DASHBACK, CSSDIR]:
    if not f.exists():
        raise RuntimeError(f"NO EXISTE: {f}")

# ============================================================
# BACKUPS
# ============================================================

login_backup = LOGIN.with_name(
    LOGIN.name + f".BACKUP_AJUSTE_{STAMP}.bak"
)

base_backup = BASE.with_name(
    BASE.name + f".BACKUP_AJUSTE_{STAMP}.bak"
)

dash_backup = DASH.with_name(
    DASH.name + f".BACKUP_AJUSTE_{STAMP}.bak"
)

shutil.copy2(LOGIN, login_backup)
shutil.copy2(BASE, base_backup)
shutil.copy2(DASH, dash_backup)

print("OK backups creados")

# ============================================================
# BUSCAR EL BACKUP DEL LOGIN ANTERIOR
# ============================================================

visual_backups = sorted(
    ROOT.glob(
        "templates/auth/login.html.BACKUP_VISUAL_REAL_*.bak"
    ),
    key=lambda p: p.stat().st_mtime,
    reverse=True
)

real_backups = sorted(
    ROOT.glob(
        "templates/auth/login.html.BACKUP_REAL_*.bak"
    ),
    key=lambda p: p.stat().st_mtime,
    reverse=True
)

candidatos = visual_backups + real_backups

if not candidatos:
    raise RuntimeError(
        "No existe ningun backup anterior del login."
    )

LOGIN_ANTERIOR = candidatos[0]

print()
print("LOGIN ANTERIOR UTILIZADO:")
print(LOGIN_ANTERIOR)

# ============================================================
# RESTAURAR LOGIN ANTERIOR
# ESTO DEVUELVE EL DIBUJO A SU ESTADO ANTERIOR
# ============================================================

login_original = LOGIN_ANTERIOR.read_text(
    encoding="utf-8"
)

LOGIN.write_text(
    login_original,
    encoding="utf-8"
)

login = LOGIN.read_text(
    encoding="utf-8"
)

print("OK login restaurado desde backup anterior")

# ============================================================
# CONSERVAR EXACTAMENTE LOS SELECTS
# ============================================================

sede_original = re.search(
    r'<select\b[^>]*name\s*=\s*"sede_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

jornada_original = re.search(
    r'<select\b[^>]*name\s*=\s*"jornada_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

if not sede_original:
    raise RuntimeError(
        "No se encontro el select de Sede."
    )

if not jornada_original:
    raise RuntimeError(
        "No se encontro el select de Jornada."
    )

sede_original = sede_original.group(0)
jornada_original = jornada_original.group(0)

# ============================================================
# CORREGIR TEXTO "NO DEBES ESCOGERLO"
# ============================================================

login = login.replace(
    'No debes escogerlo-limpio">escogerlo.',
    'No debes escogerlo.'
)

login = login.replace(
    'escogerlo-limpio">escogerlo.',
    'escogerlo.'
)

login = re.sub(
    r'No debes escogerlo[^<]{0,100}escogerlo\.',
    'No debes escogerlo.',
    login
)

# ============================================================
# QUITAR 123456 DEL CAMPO DE CODIGO
# SOLO PLACEHOLDER/VALUE DEL INPUT
# ============================================================

def limpiar_codigo(match):
    tag = match.group(0)

    tag = re.sub(
        r'\splaceholder\s*=\s*"123456"',
        '',
        tag,
        flags=re.I
    )

    tag = re.sub(
        r"\splaceholder\s*=\s*'123456'",
        '',
        tag,
        flags=re.I
    )

    tag = re.sub(
        r'\svalue\s*=\s*"123456"',
        '',
        tag,
        flags=re.I
    )

    tag = re.sub(
        r"\svalue\s*=\s*'123456'",
        '',
        tag,
        flags=re.I
    )

    return tag

login = re.sub(
    r'<input\b[^>]*name\s*=\s*"codigo_institucional"[^>]*>',
    limpiar_codigo,
    login,
    flags=re.I
)

# ============================================================
# ELIMINAR ANIMACION DEL DIBUJO SIN BORRAR EL DIBUJO
# ============================================================

# Quitar animaciones SMIL dentro de SVG.
login = re.sub(
    r'<animateTransform\b[^>]*>.*?</animateTransform>',
    '',
    login,
    flags=re.I | re.S
)

login = re.sub(
    r'<animate\b[^>]*/?>',
    '',
    login,
    flags=re.I | re.S
)

# ============================================================
# CSS FINAL
# ============================================================

FINALCSS.write_text(
r'''/* ================================================================
   EDUTURNOS - AJUSTE VISUAL FINAL LOGIN
   ================================================================ */


/* ================================================================
   DOCUMENTO Y CONTRASEÑA
   ================================================================ */

html body input[name="identificador"],
html body input[name="password"] {
    color: #273142 !important;
    caret-color: #273142 !important;
}

html body label:has(input[name="identificador"]),
html body label:has(input[name="password"]),
html body label:has(input[name="identificador"]) *,
html body label:has(input[name="password"]) * {
    color: #273142 !important;
}


/* ================================================================
   PERSONAL INSTITUCIONAL
   ================================================================ */

html body .personal-login .form-grid,
html body .personal-login .personal-fields-grid {

    display: grid !important;

    grid-template-columns:
        145px
        240px
        108px !important;

    column-gap: 12px !important;

    row-gap: 0 !important;

    align-items: end !important;

    justify-content: center !important;
}


/* ================================================================
   TITULOS
   ================================================================ */

html body .personal-login .personal-field-title,
html body .personal-login label span.personal-field-title {

    display: block !important;

    width: 100% !important;

    text-align: center !important;

    white-space: nowrap !important;

    margin-bottom: 8px !important;
}


/* ================================================================
   CODIGO
   6 DIGITOS + POCO ESPACIO
   ================================================================ */

html body input[name="codigo_institucional"] {

    width: 112px !important;

    min-width: 112px !important;

    max-width: 112px !important;

    margin-left: auto !important;

    margin-right: auto !important;

    box-sizing: border-box !important;
}


/* ================================================================
   SEDE
   UN POCO MAS PEQUEÑA
   ================================================================ */

html body select[name="sede_id"] {

    width: 240px !important;

    min-width: 240px !important;

    max-width: 240px !important;

    margin-left: auto !important;

    margin-right: auto !important;

    box-sizing: border-box !important;
}


/* ================================================================
   JORNADA
   ================================================================ */

html body select[name="jornada_id"] {

    width: 108px !important;

    min-width: 108px !important;

    max-width: 108px !important;

    margin-left: auto !important;

    margin-right: auto !important;

    box-sizing: border-box !important;
}


/* ================================================================
   NO DEBES ESCOGERLO
   ================================================================ */

html body .section-heading p,
html body .section-heading p *,
html body .section-heading strong,
html body .section-heading span {

    border: 0 !important;

    border-bottom: 0 !important;

    text-decoration: none !important;

    box-shadow: none !important;

    background-image: none !important;
}

html body .section-heading::before,
html body .section-heading::after {

    content: none !important;

    display: none !important;

    border: 0 !important;
}


/* ================================================================
   DIBUJO
   CONSERVARLO, PERO SIN MOVIMIENTO ANIMADO
   ================================================================ */

html body .login-page svg,
html body .login-page svg * {

    animation: none !important;

    animation-name: none !important;

    animation-duration: 0s !important;

    animation-delay: 0s !important;
}


/* ================================================================
   BOTON INGRESAR
   UN POCO MAS GRANDE
   ================================================================ */

html body .login-page .boton-full {

    min-height: 52px !important;

    padding: 14px 28px !important;

    font-size: 15px !important;
}


/* ================================================================
   FIN
   ================================================================ */
''',
    encoding="utf-8"
)

print("OK CSS final actualizado")

# ============================================================
# ESTILO DIRECTO DENTRO DEL LOGIN
# GANA SOBRE REGLAS ANTIGUAS
# ============================================================

direct_style = r'''
<style id="EDUTURNOS_AJUSTE_FINAL_DIRECT">

html body .personal-login .form-grid,
html body .personal-login .personal-fields-grid {
    display:grid !important;
    grid-template-columns:145px 240px 108px !important;
    column-gap:12px !important;
    row-gap:0 !important;
    align-items:end !important;
    justify-content:center !important;
}

html body .personal-login .personal-field-title {
    display:block !important;
    width:100% !important;
    text-align:center !important;
    white-space:nowrap !important;
    margin-bottom:8px !important;
}

html body input[name="codigo_institucional"] {
    width:112px !important;
    min-width:112px !important;
    max-width:112px !important;
    margin-left:auto !important;
    margin-right:auto !important;
}

html body select[name="sede_id"] {
    width:240px !important;
    min-width:240px !important;
    max-width:240px !important;
    margin-left:auto !important;
    margin-right:auto !important;
}

html body select[name="jornada_id"] {
    width:108px !important;
    min-width:108px !important;
    max-width:108px !important;
    margin-left:auto !important;
    margin-right:auto !important;
}

html body input[name="identificador"],
html body input[name="password"] {
    color:#273142 !important;
}

html body .section-heading p,
html body .section-heading p *,
html body .section-heading strong,
html body .section-heading span {
    border:0 !important;
    border-bottom:0 !important;
    text-decoration:none !important;
    box-shadow:none !important;
    background-image:none !important;
}

html body .section-heading::before,
html body .section-heading::after {
    content:none !important;
    display:none !important;
}

html body .login-page svg,
html body .login-page svg * {
    animation:none !important;
    animation-name:none !important;
    animation-duration:0s !important;
    animation-delay:0s !important;
}

html body .login-page .boton-full {
    min-height:52px !important;
    padding:14px 28px !important;
    font-size:15px !important;
}

</style>
'''

login = re.sub(
    r'<style\b[^>]*id="EDUTURNOS_AJUSTE_FINAL_DIRECT"[^>]*>.*?</style>',
    '',
    login,
    flags=re.I | re.S
)

if re.search(r'\{% endblock %\}', login, re.I):
    login = re.sub(
        r'\{% endblock %\}',
        direct_style + '\n{% endblock %}',
        login,
        count=1,
        flags=re.I
    )
else:
    login += '\n' + direct_style

# ============================================================
# COMPROBAR SELECTS
# ============================================================

sede_after = re.search(
    r'<select\b[^>]*name\s*=\s*"sede_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

jornada_after = re.search(
    r'<select\b[^>]*name\s*=\s*"jornada_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

if not sede_after:
    raise RuntimeError("DESAPARECIO SELECT SEDE")

if not jornada_after:
    raise RuntimeError("DESAPARECIO SELECT JORNADA")

if sede_after.group(0) != sede_original:
    raise RuntimeError(
        "CAMBIO EL SELECT DE SEDE O SUS OPCIONES"
    )

if jornada_after.group(0) != jornada_original:
    raise RuntimeError(
        "CAMBIO EL SELECT DE JORNADA O SUS OPCIONES"
    )

print("OK Sede y opciones intactas")
print("OK Jornada y opciones intactas")

# ============================================================
# GUARDAR LOGIN
# ============================================================

LOGIN.write_text(
    login,
    encoding="utf-8"
)

# ============================================================
# BASE: ASEGURAR QUE EL CSS FINAL ESTE AL FINAL
# ============================================================

base = BASE.read_text(
    encoding="utf-8"
)

base = re.sub(
    r'<link\b[^>]*eduturnos_final_real\.css[^>]*>',
    '',
    base,
    flags=re.I
)

base = re.sub(
    r'<style\b[^>]*id="EDUTURNOS_BASE_VISUAL_FINAL"[^>]*>.*?</style>',
    '',
    base,
    flags=re.I | re.S
)

link = (
    '<link rel="stylesheet" '
    'href="{{ url_for(\'static\', filename=\'css/eduturnos_final_real.css\') }}"'
    f'?v={STAMP}>'
)

if not re.search(r'</head>', base, re.I):
    raise RuntimeError(
        "base.html no contiene </head>"
    )

base = re.sub(
    r'</head>',
    link + '\n</head>',
    base,
    count=1,
    flags=re.I
)

BASE.write_text(
    base,
    encoding="utf-8"
)

# ============================================================
# RESTAURAR DASHBOARD EXACTAMENTE
# ============================================================

shutil.copy2(
    DASHBACK,
    DASH
)

if DASH.read_bytes() != DASHBACK.read_bytes():
    raise RuntimeError(
        "Dashboard no coincide con backup solo interno."
    )

# ============================================================
# VERIFICACION FINAL
# ============================================================

login_final = LOGIN.read_text(
    encoding="utf-8"
)

base_final = BASE.read_text(
    encoding="utf-8"
)

dash_final = DASH.read_text(
    encoding="utf-8"
)

checks = {

    "Documento o correo":
        'name="identificador"' in login_final,

    "Contraseña":
        'name="password"' in login_final,

    "Codigo":
        'name="codigo_institucional"' in login_final,

    "Sede":
        'name="sede_id"' in login_final,

    "Jornada":
        'name="jornada_id"' in login_final,

    "CSRF":
        'csrf_field' in login_final,

    "Recuperar":
        'passwords.recuperar' in login_final,

    "Crear cuenta":
        'auth.registro' in login_final,

    "123456 eliminado del input":
        not bool(
            re.search(
                r'<input\b[^>]*name\s*=\s*"codigo_institucional"[^>]*'
                r'(?:placeholder|value)\s*=\s*["\']123456["\']',
                login_final,
                re.I
            )
        ),

    "Sede intacta":
        sede_original in login_final,

    "Jornada intacta":
        jornada_original in login_final,

    "CSS final":
        FINALCSS.exists(),

    "CSS cargado":
        "eduturnos_final_real.css" in base_final,

    "Boton grande":
        "min-height:52px" in login_final,

    "Dashboard restaurado":
        dash_final == DASHBACK.read_text(
            encoding="utf-8"
        )
}

print()
print("=" * 72)
print(" VERIFICACION FINAL")
print("=" * 72)

for nombre, ok in checks.items():
    print(
        ("OK   " if ok else "ERROR ")
        + nombre
    )

print()

if not all(checks.values()):
    raise RuntimeError(
        "La verificacion final no paso."
    )

print("=" * 72)
print(" CAMBIOS COMPLETADOS")
print("=" * 72)

print()
print("DIBUJO:")
print("Restaurado desde el backup anterior.")
print("Animaciones internas del SVG eliminadas.")

print()
print("CODIGO:")
print("123456 eliminado.")
print("Cuadro conservado.")

print()
print("PERSONAL INSTITUCIONAL:")
print("Titulos separados y centrados.")
print("Codigo: 112px")
print("Sede: 240px")
print("Jornada: 108px")

print()
print("INGRESAR:")
print("Un poco mas grande.")

print()
print("BACKUPS:")
print(login_backup)
print(base_backup)
print(dash_backup)

print()
print("=" * 72)
print(" TODO LISTO")
print("=" * 72)
