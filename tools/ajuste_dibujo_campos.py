from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(r"F:\edu_Final")
LOGIN = ROOT / "templates" / "auth" / "login.html"
BASE = ROOT / "templates" / "base.html"
CSS = ROOT / "static" / "css" / "eduturnos_final_real.css"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

print()
print("=" * 72)
print(" EDUTURNOS - DIBUJO ANTERIOR + CAMPOS COMPACTOS")
print("=" * 72)
print()

# ============================================================
# COMPROBAR
# ============================================================

for f in [LOGIN, BASE, CSS]:
    if not f.exists():
        raise RuntimeError(f"NO EXISTE: {f}")

# ============================================================
# BACKUP
# ============================================================

login_backup = LOGIN.with_name(
    LOGIN.name + f".BACKUP_COMPACTO_{STAMP}.bak"
)

base_backup = BASE.with_name(
    BASE.name + f".BACKUP_COMPACTO_{STAMP}.bak"
)

css_backup = CSS.with_name(
    CSS.name + f".BACKUP_COMPACTO_{STAMP}.bak"
)

shutil.copy2(LOGIN, login_backup)
shutil.copy2(BASE, base_backup)
shutil.copy2(CSS, css_backup)

print("OK backups creados")

# ============================================================
# LEER LOGIN ACTUAL
# ============================================================

login = LOGIN.read_text(encoding="utf-8")

# ============================================================
# GUARDAR ELEMENTOS FUNCIONALES Y SELECTS
# ============================================================

required = [
    'name="identificador"',
    'name="password"',
    'name="codigo_institucional"',
    'name="sede_id"',
    'name="jornada_id"',
    "csrf_field",
    "passwords.recuperar",
    "auth.registro"
]

for item in required:
    if item not in login:
        raise RuntimeError(
            f"FALTA ELEMENTO FUNCIONAL: {item}"
        )

sede_match = re.search(
    r'<select\b[^>]*name\s*=\s*"sede_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

jornada_match = re.search(
    r'<select\b[^>]*name\s*=\s*"jornada_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

if not sede_match:
    raise RuntimeError("NO SE ENCONTRO SELECT SEDE")

if not jornada_match:
    raise RuntimeError("NO SE ENCONTRO SELECT JORNADA")

sede_original = sede_match.group(0)
jornada_original = jornada_match.group(0)

# ============================================================
# BUSCAR VERSIONES ANTERIORES DEL LOGIN
# ============================================================

archivos = []

for p in (ROOT / "templates").rglob("*"):
    if not p.is_file():
        continue

    nombre = p.name.lower()

    if "login" not in nombre:
        continue

    if p.resolve() == LOGIN.resolve():
        continue

    try:
        contenido = p.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception:
        continue

    if (
        'name="identificador"' not in contenido
        or 'name="password"' not in contenido
    ):
        continue

    archivos.append((p, contenido))

print()
print(f"Backups/versiones de login encontrados: {len(archivos)}")

# ============================================================
# EXTRAER SVGs GRANDES
# ============================================================

svg_pattern = re.compile(
    r'<svg\b[^>]*>.*?</svg>',
    re.I | re.S
)

def svg_candidates(html):

    encontrados = []

    for m in svg_pattern.finditer(html):

        bloque = m.group(0)

        if len(bloque) < 300:
            continue

        inicio = bloque[:700].lower()

        # Evitar iconos pequeños
        if any(
            x in inicio
            for x in [
                "icon",
                "chevron",
                "arrow",
                "menu",
                "logo-small"
            ]
        ):
            continue

        encontrados.append(bloque)

    return encontrados

svg_actuales = svg_candidates(login)

print(
    f"SVG grandes encontrados en login actual: "
    f"{len(svg_actuales)}"
)

# ============================================================
# ELEGIR DIBUJO ACTUAL
# ============================================================

dibujo_actual = None

if svg_actuales:
    dibujo_actual = max(
        svg_actuales,
        key=len
    )

# ============================================================
# BUSCAR DIBUJO ANTERIOR
# ============================================================

dibujo_anterior = None
archivo_anterior = None

# Primero buscar la versión más reciente que tenga
# un SVG diferente al actual.

for p, contenido in sorted(
    archivos,
    key=lambda x: x[0].stat().st_mtime,
    reverse=True
):

    candidatos = svg_candidates(contenido)

    if not candidatos:
        continue

    candidato = max(
        candidatos,
        key=len
    )

    if dibujo_actual is None:
        dibujo_anterior = candidato
        archivo_anterior = p
        break

    if candidato.strip() != dibujo_actual.strip():
        dibujo_anterior = candidato
        archivo_anterior = p
        break

# ============================================================
# REEMPLAZAR SOLO EL DIBUJO
# ============================================================

if dibujo_actual and dibujo_anterior:

    login = login.replace(
        dibujo_actual,
        dibujo_anterior,
        1
    )

    print()
    print("OK DIBUJO ANTERIOR ENCONTRADO")
    print(
        "Version utilizada:"
    )
    print(archivo_anterior)

elif dibujo_actual and not dibujo_anterior:

    print()
    print(
        "AVISO: no se encontro un SVG anterior diferente."
    )
    print(
        "Se conserva el dibujo actual para no dañar el login."
    )

else:

    print()
    print(
        "AVISO: el dibujo no esta construido como SVG."
    )
    print(
        "No se modifico esa parte para evitar alterar otras funciones."
    )

# ============================================================
# ELIMINAR 123456 SOLO DEL INPUT DE CODIGO
# ============================================================

def limpiar_codigo(match):

    tag = match.group(0)

    tag = re.sub(
        r'\splaceholder\s*=\s*"123456"',
        "",
        tag,
        flags=re.I
    )

    tag = re.sub(
        r"\splaceholder\s*=\s*'123456'",
        "",
        tag,
        flags=re.I
    )

    tag = re.sub(
        r'\svalue\s*=\s*"123456"',
        "",
        tag,
        flags=re.I
    )

    tag = re.sub(
        r"\svalue\s*=\s*'123456'",
        "",
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

print("OK 123456 eliminado del cuadro de codigo")

# ============================================================
# ELIMINAR SCRIPT DINAMICO ANTERIOR
# ESTE ERA EL QUE VOLVIA A AGRANDAR LOS CAMPOS
# ============================================================

login = re.sub(
    r'<script\b[^>]*id="EDUTURNOS_VISUAL_REAL_SCRIPT"[^>]*>.*?</script>',
    "",
    login,
    flags=re.I | re.S
)

login = re.sub(
    r'<script\b[^>]*id="EDUTURNOS_LINEA_BLANCA_UNICA_FINAL"[^>]*>.*?</script>',
    "",
    login,
    flags=re.I | re.S
)

login = re.sub(
    r'<script\b[^>]*id="EDUTURNOS_VISUAL_REAL_SCRIPT[^"]*"[^>]*>.*?</script>',
    "",
    login,
    flags=re.I | re.S
)

print("OK scriptos que forzaban anchos anteriores eliminados")

# ============================================================
# QUITAR ESTILOS DIRECTOS ANTERIORES
# ============================================================

ids_estilos = [
    "EDUTURNOS_AJUSTE_FINAL_DIRECT",
    "EDUTURNOS_LOGIN_FINAL_DIRECT",
    "EDUTURNOS_BASE_VISUAL_FINAL"
]

for sid in ids_estilos:

    login = re.sub(
        rf'<style\b[^>]*id="{re.escape(sid)}"[^>]*>.*?</style>',
        "",
        login,
        flags=re.I | re.S
    )

# ============================================================
# ESTILO COMPACTO FINAL DENTRO DEL LOGIN
# ============================================================

compact_style = r'''
<style id="EDUTURNOS_COMPACTO_REAL">

/* =========================================================
   PERSONAL INSTITUCIONAL
   TODO DENTRO DEL MISMO CUADRO
   ========================================================= */

html body .personal-login {

    width: 100% !important;

    max-width: 100% !important;

    box-sizing: border-box !important;

    overflow: hidden !important;
}


/* =========================================================
   LOS TRES CAMPOS
   UNA SOLA FILA COMPACTA
   ========================================================= */

html body
.personal-login .personal-fields-grid,

html body
.personal-login .form-grid {

    display: grid !important;

    grid-template-columns:
        96px
        210px
        86px !important;

    gap: 6px !important;

    column-gap: 6px !important;

    row-gap: 0 !important;

    width: fit-content !important;

    max-width: 100% !important;

    margin-left: auto !important;

    margin-right: auto !important;

    justify-content: center !important;

    align-items: end !important;

    box-sizing: border-box !important;
}


/* =========================================================
   CADA COLUMNA
   ========================================================= */

html body
.personal-login .personal-field {

    width: auto !important;

    min-width: 0 !important;

    max-width: 100% !important;

    box-sizing: border-box !important;

    margin: 0 !important;
}


/* =========================================================
   TITULOS CENTRADOS
   ========================================================= */

html body
.personal-login .personal-field-title {

    display: block !important;

    width: 100% !important;

    text-align: center !important;

    white-space: nowrap !important;

    margin-bottom: 6px !important;
}


/* =========================================================
   CUADRO CODIGO
   ========================================================= */

html body
.personal-login input[name="codigo_institucional"] {

    width: 96px !important;

    min-width: 96px !important;

    max-width: 96px !important;

    box-sizing: border-box !important;

    margin: 0 !important;
}


/* =========================================================
   CUADRO SEDE
   ========================================================= */

html body
.personal-login select[name="sede_id"] {

    width: 210px !important;

    min-width: 210px !important;

    max-width: 210px !important;

    box-sizing: border-box !important;

    margin: 0 !important;
}


/* =========================================================
   CUADRO JORNADA
   ========================================================= */

html body
.personal-login select[name="jornada_id"] {

    width: 86px !important;

    min-width: 86px !important;

    max-width: 86px !important;

    box-sizing: border-box !important;

    margin: 0 !important;
}


/* =========================================================
   NO TOCAR APPEARANCE
   SELECT NATIVO CONSERVADO
   ========================================================= */


/* =========================================================
   DOCUMENTO Y PASSWORD
   ========================================================= */

html body
input[name="identificador"],

html body
input[name="password"] {

    color: #273142 !important;

    caret-color: #273142 !important;
}


/* =========================================================
   BOTON INGRESAR
   UN POCO MAS GRANDE
   ========================================================= */

html body
.login-page .boton-full {

    min-height: 52px !important;

    padding-top: 14px !important;

    padding-bottom: 14px !important;

    padding-left: 28px !important;

    padding-right: 28px !important;

    font-size: 15px !important;
}


/* =========================================================
   NO DEBES ESCOGERLO
   ========================================================= */

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


/* =========================================================
   MOVIMIENTO DEL DIBUJO
   CONSERVAR DIBUJO, DETENER ANIMACION
   ========================================================= */

html body
.login-page svg,
html body
.login-page svg * {

    animation: none !important;

    animation-name: none !important;

    animation-duration: 0s !important;

    animation-delay: 0s !important;
}


/* =========================================================
   MOVIL
   ========================================================= */

@media (max-width: 700px) {

    html body
    .personal-login .personal-fields-grid,

    html body
    .personal-login .form-grid {

        width: 100% !important;

        grid-template-columns: 1fr !important;

        gap: 10px !important;

        justify-content: stretch !important;
    }

    html body
    .personal-login input[name="codigo_institucional"],

    html body
    .personal-login select[name="sede_id"],

    html body
    .personal-login select[name="jornada_id"] {

        width: 100% !important;

        min-width: 0 !important;

        max-width: 100% !important;
    }
}

</style>
'''

login = re.sub(
    r'<style\b[^>]*id="EDUTURNOS_COMPACTO_REAL"[^>]*>.*?</style>',
    "",
    login,
    flags=re.I | re.S
)

if re.search(r'\{% endblock %\}', login, re.I):

    login = re.sub(
        r'\{% endblock %\}',
        compact_style + '\n{% endblock %}',
        login,
        count=1,
        flags=re.I
    )

else:
    raise RuntimeError(
        "login.html no tiene {% endblock %}"
    )

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
    raise RuntimeError(
        "DESAPARECIO SELECT SEDE - NO SE GUARDA"
    )

if not jornada_after:
    raise RuntimeError(
        "DESAPARECIO SELECT JORNADA - NO SE GUARDA"
    )

if sede_after.group(0) != sede_original:
    raise RuntimeError(
        "CAMBIO EL SELECT DE SEDE O SUS OPCIONES - NO SE GUARDA"
    )

if jornada_after.group(0) != jornada_original:
    raise RuntimeError(
        "CAMBIO EL SELECT DE JORNADA O SUS OPCIONES - NO SE GUARDA"
    )

# ============================================================
# GUARDAR
# ============================================================

LOGIN.write_text(
    login,
    encoding="utf-8"
)

# ============================================================
# CSS EXTERNO FINAL
# ============================================================

css = CSS.read_text(
    encoding="utf-8"
)

css = re.sub(
    r'/\* EDUTURNOS AJUSTE COMPACTO REAL.*?\*/',
    '',
    css,
    flags=re.I | re.S
)

css += r'''

/* EDUTURNOS AJUSTE COMPACTO REAL */

html body .personal-login {
    width:100% !important;
    max-width:100% !important;
    box-sizing:border-box !important;
    overflow:hidden !important;
}

html body .personal-login .personal-fields-grid,
html body .personal-login .form-grid {
    display:grid !important;
    grid-template-columns:96px 210px 86px !important;
    gap:6px !important;
    column-gap:6px !important;
    row-gap:0 !important;
    width:fit-content !important;
    max-width:100% !important;
    margin-left:auto !important;
    margin-right:auto !important;
    justify-content:center !important;
    align-items:end !important;
    box-sizing:border-box !important;
}

html body .personal-login .personal-field {
    width:auto !important;
    min-width:0 !important;
    max-width:100% !important;
    margin:0 !important;
}

html body .personal-login .personal-field-title {
    display:block !important;
    width:100% !important;
    text-align:center !important;
    white-space:nowrap !important;
    margin-bottom:6px !important;
}

html body .personal-login input[name="codigo_institucional"] {
    width:96px !important;
    min-width:96px !important;
    max-width:96px !important;
    margin:0 !important;
    box-sizing:border-box !important;
}

html body .personal-login select[name="sede_id"] {
    width:210px !important;
    min-width:210px !important;
    max-width:210px !important;
    margin:0 !important;
    box-sizing:border-box !important;
}

html body .personal-login select[name="jornada_id"] {
    width:86px !important;
    min-width:86px !important;
    max-width:86px !important;
    margin:0 !important;
    box-sizing:border-box !important;
}

html body .login-page .boton-full {
    min-height:52px !important;
    padding:14px 28px !important;
    font-size:15px !important;
}

html body .login-page svg,
html body .login-page svg * {
    animation:none !important;
    animation-name:none !important;
    animation-duration:0s !important;
    animation-delay:0s !important;
}
'''

CSS.write_text(
    css,
    encoding="utf-8"
)

# ============================================================
# VERIFICACION
# ============================================================

final_login = LOGIN.read_text(
    encoding="utf-8"
)

checks = {
    "Documento": 'name="identificador"' in final_login,
    "Password": 'name="password"' in final_login,
    "Codigo": 'name="codigo_institucional"' in final_login,
    "Sede": 'name="sede_id"' in final_login,
    "Jornada": 'name="jornada_id"' in final_login,
    "CSRF": "csrf_field" in final_login,
    "Recuperar": "passwords.recuperar" in final_login,
    "Registro": "auth.registro" in final_login,
    "123456 eliminado": not bool(
        re.search(
            r'<input\b[^>]*name\s*=\s*"codigo_institucional"[^>]*'
            r'(placeholder|value)\s*=\s*["\']123456["\']',
            final_login,
            re.I
        )
    ),
    "Sede intacta": sede_original in final_login,
    "Jornada intacta": jornada_original in final_login,
    "Estilo compacto": "EDUTURNOS_COMPACTO_REAL" in final_login,
    "CSS externo": CSS.exists()
}

print()
print("=" * 72)
print(" VERIFICACION")
print("=" * 72)

for nombre, ok in checks.items():

    print(
        ("OK    " if ok else "ERROR ")
        + nombre
    )

print()

if not all(checks.values()):
    raise RuntimeError(
        "La verificacion no paso completamente."
    )

print("=" * 72)
print(" RESULTADO")
print("=" * 72)
print()
print("Tres campos:")
print("Codigo   = 96 px")
print("Sede     = 210 px")
print("Jornada  = 86 px")
print()
print("Los tres quedan dentro de Personal institucional.")
print("El 123456 fue eliminado.")
print("El boton Ingresar quedo ligeramente mayor.")

if archivo_anterior:
    print()
    print("DIBUJO RESTAURADO DESDE:")
    print(archivo_anterior)
else:
    print()
    print("DIBUJO: no se encontro una version anterior automaticamente.")

print()
print("BACKUP LOGIN:")
print(login_backup)

print()
print("BACKUP BASE:")
print(base_backup)

print()
print("BACKUP CSS:")
print(css_backup)

print()
print("=" * 72)
print(" TERMINADO")
print("=" * 72)
