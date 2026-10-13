from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(r"F:\edu_Final")

LOGIN = ROOT / "templates" / "auth" / "login.html"
BASE = ROOT / "templates" / "base.html"
CSSDIR = ROOT / "static" / "css"

MASTER = CSSDIR / "eduturnos_login_master.css"

# Backup especifico que el diagnostico encontro
OLD_LOGIN = (
    ROOT
    / "templates"
    / "auth"
    / "login.html.BACKUP_ANTES_LOGIN_LIMPIO_20260925_150109.bak"
)

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

print()
print("=" * 78)
print(" EDUTURNOS - APLICACION VISUAL DEFINITIVA DEL LOGIN")
print("=" * 78)
print()

# ============================================================
# COMPROBAR ARCHIVOS
# ============================================================

for f in [LOGIN, BASE, CSSDIR, OLD_LOGIN]:

    if not f.exists():
        raise RuntimeError(
            f"NO EXISTE: {f}"
        )

print("OK archivos principales")

# ============================================================
# BACKUPS
# ============================================================

LOGIN_BAK = LOGIN.with_name(
    LOGIN.name + f".BACKUP_DEFINITIVO_{STAMP}.bak"
)

BASE_BAK = BASE.with_name(
    BASE.name + f".BACKUP_DEFINITIVO_{STAMP}.bak"
)

MASTER_BAK = None

shutil.copy2(LOGIN, LOGIN_BAK)
shutil.copy2(BASE, BASE_BAK)

if MASTER.exists():

    MASTER_BAK = MASTER.with_name(
        MASTER.name + f".BACKUP_DEFINITIVO_{STAMP}.bak"
    )

    shutil.copy2(
        MASTER,
        MASTER_BAK
    )

print("OK backups")

# ============================================================
# LEER LOGIN ACTUAL Y LOGIN ANTIGUO
# ============================================================

login = LOGIN.read_text(
    encoding="utf-8",
    errors="ignore"
)

old_login = OLD_LOGIN.read_text(
    encoding="utf-8",
    errors="ignore"
)

# ============================================================
# COMPROBAR ELEMENTOS FUNCIONALES
# ============================================================

required = [
    'name="identificador"',
    'name="password"',
    'name="codigo_institucional"',
    'name="sede_id"',
    'name="jornada_id"',
    "csrf_field",
    "passwords.recuperar",
    "auth.registro",
]

for item in required:

    if item not in login:

        raise RuntimeError(
            f"FALTA ELEMENTO FUNCIONAL: {item}"
        )

print("OK elementos funcionales")

# ============================================================
# GUARDAR SELECTS ACTUALES
# ============================================================

sede_current = re.search(
    r'<select\b[^>]*name\s*=\s*"sede_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

jornada_current = re.search(
    r'<select\b[^>]*name\s*=\s*"jornada_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

if not sede_current:
    raise RuntimeError(
        "NO se encontro select Sede"
    )

if not jornada_current:
    raise RuntimeError(
        "NO se encontro select Jornada"
    )

sede_original = sede_current.group(0)
jornada_original = jornada_current.group(0)

# ============================================================
# RECUPERAR DIBUJO ANTERIOR
# ============================================================

svg_pattern = re.compile(
    r"<svg\b[^>]*>.*?</svg>",
    re.I | re.S
)

def buscar_dibujos(html):

    salida = []

    for match in svg_pattern.finditer(html):

        svg = match.group(0)

        if len(svg) < 300:
            continue

        inicio = svg[:700].lower()

        # Evitar iconos pequenos
        if any(
            palabra in inicio
            for palabra in [
                "chevron",
                "arrow",
                "menu",
                "close",
                "search"
            ]
        ):
            continue

        salida.append(svg)

    return salida


actual_svgs = buscar_dibujos(login)
old_svgs = buscar_dibujos(old_login)

print()
print(
    "SVG actuales encontrados:",
    len(actual_svgs)
)

print(
    "SVG anteriores encontrados:",
    len(old_svgs)
)

dibujo_actual = None
dibujo_anterior = None

if actual_svgs:

    dibujo_actual = max(
        actual_svgs,
        key=len
    )

if old_svgs:

    dibujo_anterior = max(
        old_svgs,
        key=len
    )

if dibujo_actual and dibujo_anterior:

    print("OK dibujo anterior localizado")
    print("Origen:")
    print(OLD_LOGIN)

    if dibujo_actual.strip() != dibujo_anterior.strip():

        login = login.replace(
            dibujo_actual,
            dibujo_anterior,
            1
        )

        print("OK dibujo anterior restaurado")

    else:

        print(
            "AVISO: el SVG anterior y actual son iguales."
        )

else:

    raise RuntimeError(
        "No fue posible localizar el dibujo SVG."
    )

# ============================================================
# LIMPIAR 123456 DEL INPUT
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

print("OK 123456 eliminado")

# ============================================================
# LIMPIAR SCRIPTS VISUALES ANTERIORES
# ============================================================

old_script_patterns = [

    r'<script\b[^>]*id="EDUTURNOS_VISUAL_REAL_SCRIPT"[^>]*>.*?</script>',

    r'<script\b[^>]*id="EDUTURNOS_LINEA_BLANCA_UNICA_FINAL"[^>]*>.*?</script>',

    r'<script\b[^>]*id="EDUTURNOS_LINEA_DIBUJO_FINAL"[^>]*>.*?</script>',

    r'<script\b[^>]*id="EDUTURNOS_LINEA_DIBUJO"[^>]*>.*?</script>',

    r'<script\b[^>]*id="EDUTURNOS_AJUSTE_FINAL"[^>]*>.*?</script>',

    r'<script\b[^>]*id="EDUTURNOS_VISUAL_FINAL_SCRIPT"[^>]*>.*?</script>',
]

for pattern in old_script_patterns:

    login = re.sub(
        pattern,
        '',
        login,
        flags=re.I | re.S
    )

print("OK scripts visuales anteriores retirados")

# ============================================================
# LIMPIAR BLOQUES STYLE ANTERIORES CONOCIDOS
# ============================================================

style_ids = [

    "EDUTURNOS_COMPACTO_REAL",

    "EDUTURNOS_AJUSTE_FINAL_DIRECT",

    "EDUTURNOS_LOGIN_FINAL_DIRECT",

    "EDUTURNOS_LOGIN_MASTER_INLINE",

    "EDUTURNOS_BASE_VISUAL_FINAL",

    "EDUTURNOS_VISUAL_FINAL",

    "EDUTURNOS_UNIFICADO_LOGIN_REGISTRO_2026",

    "EDUTURNOS_LOGIN_REAL_FINAL",

]

for sid in style_ids:

    login = re.sub(
        rf'<style\b[^>]*id="{re.escape(sid)}"[^>]*>.*?</style>',
        '',
        login,
        flags=re.I | re.S
    )

print("OK estilos visuales anteriores limpiados")

# ============================================================
# ESTILO FINAL DENTRO DEL LOGIN
# SE INSERTA ANTES DE </body>, NO DEPENDE DE JINJA
# ============================================================

FINAL_STYLE = r'''
<style id="EDUTURNOS_LOGIN_VISUAL_DEFINITIVO">

/* ============================================================
   PERSONAL INSTITUCIONAL
   ============================================================ */

html body .personal-login {

    width: 100% !important;

    max-width: 100% !important;

    box-sizing: border-box !important;

    overflow: hidden !important;

    padding-left: 10px !important;

    padding-right: 10px !important;
}


/* ============================================================
   TRES CAMPOS
   COMPACTOS Y DENTRO DEL CUADRO
   ============================================================ */

html body .personal-login .personal-fields-grid,

html body .personal-login .form-grid {

    display: grid !important;

    grid-template-columns:
        96px
        220px
        82px !important;

    column-gap: 7px !important;

    row-gap: 0 !important;

    width: 405px !important;

    max-width: 100% !important;

    margin-left: auto !important;

    margin-right: auto !important;

    justify-content: center !important;

    align-items: end !important;

    box-sizing: border-box !important;
}


/* ============================================================
   CAMPOS INDIVIDUALES
   ============================================================ */

html body .personal-login .personal-field {

    width: auto !important;

    min-width: 0 !important;

    max-width: 100% !important;

    margin: 0 !important;

    box-sizing: border-box !important;
}


/* ============================================================
   TITULOS
   ============================================================ */

html body .personal-login .personal-field-title {

    display: block !important;

    width: 100% !important;

    text-align: center !important;

    white-space: nowrap !important;

    line-height: 1.15 !important;

    margin-bottom: 5px !important;
}


/* ============================================================
   CODIGO
   ============================================================ */

html body
.personal-login input[name="codigo_institucional"] {

    width: 96px !important;

    min-width: 96px !important;

    max-width: 96px !important;

    box-sizing: border-box !important;

    margin: 0 !important;

    background: #ffffff !important;
}


/* ============================================================
   SEDE
   ============================================================ */

html body
.personal-login select[name="sede_id"] {

    width: 220px !important;

    min-width: 220px !important;

    max-width: 220px !important;

    box-sizing: border-box !important;

    margin: 0 !important;
}


/* ============================================================
   JORNADA
   ============================================================ */

html body
.personal-login select[name="jornada_id"] {

    width: 82px !important;

    min-width: 82px !important;

    max-width: 82px !important;

    box-sizing: border-box !important;

    margin: 0 !important;
}


/* ============================================================
   DOCUMENTO Y CONTRASEÑA
   ============================================================ */

html body input[name="identificador"],
html body input[name="password"] {

    color: #273142 !important;

    caret-color: #273142 !important;
}

html body label:has(input[name="identificador"]),
html body label:has(input[name="password"]) {

    color: #273142 !important;
}


/* ============================================================
   NO DEBES ESCOGERLO
   ============================================================ */

html body .section-heading p,
html body .section-heading p *,
html body .section-heading strong {

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
}


/* ============================================================
   DIBUJO
   SE CONSERVA EL DIBUJO ANTERIOR
   SIN MOVIMIENTO
   ============================================================ */

html body .login-page svg,
html body .login-page svg * {

    animation: none !important;

    animation-name: none !important;

    animation-duration: 0s !important;

    animation-delay: 0s !important;
}


/* ============================================================
   BOTON
   ============================================================ */

html body .login-page .boton-full {

    min-height: 52px !important;

    padding: 14px 30px !important;

    font-size: 15px !important;
}


/* ============================================================
   CELULAR
   ============================================================ */

@media (max-width: 700px) {

    html body .personal-login .personal-fields-grid,

    html body .personal-login .form-grid {

        width: 100% !important;

        grid-template-columns: 1fr !important;

        gap: 10px !important;
    }

    html body .personal-login .personal-field {

        width: 100% !important;
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

# ============================================================
# SCRIPT FINAL
# ============================================================

FINAL_SCRIPT = r'''
<script id="EDUTURNOS_LOGIN_VISUAL_DEFINITIVO_JS">
(function () {

    function aplicar() {

        const login =
            document.querySelector(".login-page");

        if (!login) return;


        /* ------------------------------------------------------
           LIMPIAR 123456
           ------------------------------------------------------ */

        const codigo =
            login.querySelector(
                'input[name="codigo_institucional"]'
            );

        if (codigo) {

            if (
                codigo.getAttribute("placeholder") ===
                "123456"
            ) {

                codigo.removeAttribute("placeholder");
            }

            if (
                codigo.getAttribute("value") ===
                "123456"
            ) {

                codigo.removeAttribute("value");
            }

            codigo.style.setProperty(
                "width",
                "96px",
                "important"
            );

            codigo.style.setProperty(
                "min-width",
                "96px",
                "important"
            );

            codigo.style.setProperty(
                "max-width",
                "96px",
                "important"
            );
        }


        /* ------------------------------------------------------
           SEDE
           ------------------------------------------------------ */

        const sede =
            login.querySelector(
                'select[name="sede_id"]'
            );

        if (sede) {

            sede.style.setProperty(
                "width",
                "220px",
                "important"
            );

            sede.style.setProperty(
                "min-width",
                "220px",
                "important"
            );

            sede.style.setProperty(
                "max-width",
                "220px",
                "important"
            );
        }


        /* ------------------------------------------------------
           JORNADA
           ------------------------------------------------------ */

        const jornada =
            login.querySelector(
                'select[name="jornada_id"]'
            );

        if (jornada) {

            jornada.style.setProperty(
                "width",
                "82px",
                "important"
            );

            jornada.style.setProperty(
                "min-width",
                "82px",
                "important"
            );

            jornada.style.setProperty(
                "max-width",
                "82px",
                "important"
            );
        }


        /* ------------------------------------------------------
           GRID
           ------------------------------------------------------ */

        login.querySelectorAll(
            ".personal-fields-grid, .personal-login .form-grid"
        ).forEach(function (grid) {

            grid.style.setProperty(
                "display",
                "grid",
                "important"
            );

            grid.style.setProperty(
                "grid-template-columns",
                "96px 220px 82px",
                "important"
            );

            grid.style.setProperty(
                "column-gap",
                "7px",
                "important"
            );

            grid.style.setProperty(
                "width",
                "405px",
                "important"
            );

            grid.style.setProperty(
                "max-width",
                "100%",
                "important"
            );

            grid.style.setProperty(
                "justify-content",
                "center",
                "important"
            );

            grid.style.setProperty(
                "align-items",
                "end",
                "important"
            );
        });


        /* ------------------------------------------------------
           TITULOS
           ------------------------------------------------------ */

        login.querySelectorAll(
            ".personal-field-title"
        ).forEach(function (titulo) {

            titulo.style.setProperty(
                "text-align",
                "center",
                "important"
            );

            titulo.style.setProperty(
                "white-space",
                "nowrap",
                "important"
            );
        });


        /* ------------------------------------------------------
           DOCUMENTO / PASSWORD
           ------------------------------------------------------ */

        login.querySelectorAll(
            'input[name="identificador"], input[name="password"]'
        ).forEach(function (input) {

            input.style.setProperty(
                "color",
                "#273142",
                "important"
            );
        });
    }


    document.addEventListener(
        "DOMContentLoaded",
        aplicar
    );

    window.addEventListener(
        "load",
        aplicar
    );

    setTimeout(aplicar, 100);
    setTimeout(aplicar, 400);
    setTimeout(aplicar, 900);

})();
</script>
'''

# ============================================================
# INSERTAR ESTILO Y SCRIPT ANTES DE </body>
# ============================================================

login = re.sub(
    r'<style\b[^>]*id="EDUTURNOS_LOGIN_VISUAL_DEFINITIVO"[^>]*>.*?</style>',
    '',
    login,
    flags=re.I | re.S
)

login = re.sub(
    r'<script\b[^>]*id="EDUTURNOS_LOGIN_VISUAL_DEFINITIVO_JS"[^>]*>.*?</script>',
    '',
    login,
    flags=re.I | re.S
)

bloque_final = (
    "\n"
    + FINAL_STYLE
    + "\n"
    + FINAL_SCRIPT
    + "\n"
)

if re.search(
    r'</body>',
    login,
    re.I
):

    login = re.sub(
        r'</body>',
        bloque_final + '</body>',
        login,
        count=1,
        flags=re.I
    )

elif re.search(
    r'</html>',
    login,
    re.I
):

    login = re.sub(
        r'</html>',
        bloque_final + '</html>',
        login,
        count=1,
        flags=re.I
    )

else:

    login += bloque_final

print("OK estilos insertados al final real del login")

# ============================================================
# COMPROBAR SELECTS ANTES DE GUARDAR
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
        "DESAPARECIO SELECT SEDE"
    )

if not jornada_after:
    raise RuntimeError(
        "DESAPARECIO SELECT JORNADA"
    )

if sede_after.group(0) != sede_original:
    raise RuntimeError(
        "CAMBIO SELECT SEDE. NO SE GUARDA."
    )

if jornada_after.group(0) != jornada_original:
    raise RuntimeError(
        "CAMBIO SELECT JORNADA. NO SE GUARDA."
    )

print("OK opciones de Sede intactas")
print("OK opciones de Jornada intactas")

# ============================================================
# GUARDAR LOGIN
# ============================================================

LOGIN.write_text(
    login,
    encoding="utf-8"
)

# ============================================================
# MASTER CSS GLOBAL
# ============================================================

MASTER.write_text(
r'''/* ===============================================================
   EDUTURNOS - LOGIN MASTER DEFINITIVO
   =============================================================== */

html body .personal-login {
    width:100% !important;
    max-width:100% !important;
    box-sizing:border-box !important;
    overflow:hidden !important;
    padding-left:10px !important;
    padding-right:10px !important;
}

html body .personal-login .personal-fields-grid,
html body .personal-login .form-grid {
    display:grid !important;
    grid-template-columns:96px 220px 82px !important;
    column-gap:7px !important;
    row-gap:0 !important;
    width:405px !important;
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
    box-sizing:border-box !important;
}

html body .personal-login .personal-field-title {
    display:block !important;
    width:100% !important;
    text-align:center !important;
    white-space:nowrap !important;
    line-height:1.15 !important;
    margin-bottom:5px !important;
}

html body .personal-login input[name="codigo_institucional"] {
    width:96px !important;
    min-width:96px !important;
    max-width:96px !important;
    box-sizing:border-box !important;
    margin:0 !important;
    background:#ffffff !important;
}

html body .personal-login select[name="sede_id"] {
    width:220px !important;
    min-width:220px !important;
    max-width:220px !important;
    box-sizing:border-box !important;
    margin:0 !important;
}

html body .personal-login select[name="jornada_id"] {
    width:82px !important;
    min-width:82px !important;
    max-width:82px !important;
    box-sizing:border-box !important;
    margin:0 !important;
}

html body input[name="identificador"],
html body input[name="password"] {
    color:#273142 !important;
    caret-color:#273142 !important;
}

html body .section-heading p,
html body .section-heading p *,
html body .section-heading strong {
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
    padding:14px 30px !important;
    font-size:15px !important;
}

@media (max-width:700px) {

    html body .personal-login .personal-fields-grid,
    html body .personal-login .form-grid {
        width:100% !important;
        grid-template-columns:1fr !important;
        gap:10px !important;
    }

    html body .personal-login input[name="codigo_institucional"],
    html body .personal-login select[name="sede_id"],
    html body .personal-login select[name="jornada_id"] {
        width:100% !important;
        min-width:0 !important;
        max-width:100% !important;
    }
}
''',
    encoding="utf-8"
)

# ============================================================
# CARGAR MASTER CSS AL FINAL DE BASE
# ============================================================

base = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

base = re.sub(
    r'<link\b[^>]*eduturnos_login_master\.css[^>]*>',
    '',
    base,
    flags=re.I
)

master_link = (
    '<link rel="stylesheet" '
    'href="{{ url_for(\'static\', filename=\'css/eduturnos_login_master.css\') }}"'
    f'?v={STAMP}>'
)

if not re.search(
    r'</head>',
    base,
    re.I
):
    raise RuntimeError(
        "base.html no tiene </head>"
    )

base = re.sub(
    r'</head>',
    master_link + '\n</head>',
    base,
    count=1,
    flags=re.I
)

BASE.write_text(
    base,
    encoding="utf-8"
)

print("OK master CSS agregado a base.html")

# ============================================================
# VERIFICACION FINAL
# ============================================================

final_login = LOGIN.read_text(
    encoding="utf-8"
)

final_base = BASE.read_text(
    encoding="utf-8"
)

checks = {

    "Documento":
        'name="identificador"' in final_login,

    "Password":
        'name="password"' in final_login,

    "Codigo":
        'name="codigo_institucional"' in final_login,

    "Sede":
        'name="sede_id"' in final_login,

    "Jornada":
        'name="jornada_id"' in final_login,

    "CSRF":
        "csrf_field" in final_login,

    "Recuperar":
        "passwords.recuperar" in final_login,

    "Registro":
        "auth.registro" in final_login,

    "123456 fuera del input":
        not bool(
            re.search(
                r'<input\b[^>]*name\s*=\s*"codigo_institucional"[^>]*'
                r'(placeholder|value)\s*=\s*["\']123456["\']',
                final_login,
                re.I
            )
        ),

    "Master inline":
        "EDUTURNOS_LOGIN_VISUAL_DEFINITIVO" in final_login,

    "Master JS":
        "EDUTURNOS_LOGIN_VISUAL_DEFINITIVO_JS" in final_login,

    "Master CSS":
        MASTER.exists(),

    "Base carga master":
        "eduturnos_login_master.css" in final_base,

    "Select Sede intacto":
        sede_original in final_login,

    "Select Jornada intacto":
        jornada_original in final_login,

    "Dibujo anterior":
        (
            dibujo_anterior is not None
            and dibujo_anterior in final_login
        ),
}

print()
print("=" * 78)
print(" VERIFICACION FINAL")
print("=" * 78)

for nombre, ok in checks.items():

    print(
        ("OK    " if ok else "ERROR ")
        + nombre
    )

print()

if not all(checks.values()):

    raise RuntimeError(
        "LA VERIFICACION NO PASO. REVISA LOS OK/ERROR."
    )

print("DIBUJO:")
print(OLD_LOGIN)

print()
print("MEDIDAS:")
print("Codigo  = 96px")
print("Sede    = 220px")
print("Jornada = 82px")
print("Gap     = 7px")
print("Grid    = 405px")

print()
print("BACKUP LOGIN:")
print(LOGIN_BAK)

print()
print("BACKUP BASE:")
print(BASE_BAK)

print()
if MASTER_BAK:
    print("BACKUP MASTER CSS:")
    print(MASTER_BAK)

print()
print("=" * 78)
print(" CAMBIOS APLICADOS CORRECTAMENTE")
print("=" * 78)
