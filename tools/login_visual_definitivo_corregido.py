from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(r"F:\edu_Final")

BASE = ROOT / "templates" / "base.html"
LOGIN = ROOT / "templates" / "auth" / "login.html"
CSS = ROOT / "static" / "css" / "estilos.css"

MASTER = ROOT / "static" / "css" / "eduturnos_login_final_absolute.css"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

print()
print("=" * 80)
print(" EDUTURNOS - LOGIN FINAL ABSOLUTO")
print("=" * 80)
print()

# ============================================================
# COMPROBAR
# ============================================================

for f in [BASE, LOGIN, CSS]:
    if not f.exists():
        raise RuntimeError(
            f"NO EXISTE: {f}"
        )

print("OK archivos principales")

# ============================================================
# BACKUPS
# ============================================================

BASE_BAK = BASE.with_name(
    BASE.name + f".BACKUP_LOGIN_{STAMP}.bak"
)

LOGIN_BAK = LOGIN.with_name(
    LOGIN.name + f".BACKUP_LOGIN_{STAMP}.bak"
)

CSS_BAK = CSS.with_name(
    CSS.name + f".BACKUP_LOGIN_{STAMP}.bak"
)

shutil.copy2(BASE, BASE_BAK)
shutil.copy2(LOGIN, LOGIN_BAK)
shutil.copy2(CSS, CSS_BAK)

print("OK backups creados")

# ============================================================
# LEER
# ============================================================

base = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

login = LOGIN.read_text(
    encoding="utf-8",
    errors="ignore"
)

css = CSS.read_text(
    encoding="utf-8",
    errors="ignore"
)

# ============================================================
# COMPROBAR FORMULARIO
# ============================================================

required = [
    'name="identificador"',
    'name="password"',
    'name="codigo_institucional"',
    'name="sede_id"',
    'name="jornada_id"',
]

for item in required:

    if item not in login:

        raise RuntimeError(
            f"FALTA EN auth/login.html: {item}"
        )

print("OK formulario real")

# ============================================================
# GUARDAR SELECTS EXACTOS
# ============================================================

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
    raise RuntimeError(
        "NO SE ENCONTRO SELECT SEDE"
    )

if not jornada_match:
    raise RuntimeError(
        "NO SE ENCONTRO SELECT JORNADA"
    )

sede_original = sede_match.group(0)
jornada_original = jornada_match.group(0)

print("OK selects encontrados")

# ============================================================
# LIMPIAR 123456 SOLO DEL INPUT
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
# ELIMINAR BLOQUES NUESTROS ANTERIORES DEL LOGIN
# ============================================================

ids_style = [
    "EDUTURNOS_LOGIN_VISUAL_MASTER",
    "EDUTURNOS_LOGIN_MASTER_INLINE",
    "EDUTURNOS_LOGIN_MASTER_ORDEN_FINAL",
    "EDUTURNOS_LOGIN_VISUAL_DEFINITIVO",
    "EDUTURNOS_COMPACTO_REAL",
    "EDUTURNOS_AJUSTE_FINAL_DIRECT",
    "EDUTURNOS_LOGIN_FINAL_DIRECT",
    "EDUTURNOS_LOGIN_MASTER_ABSOLUTO_STYLE",
]

for sid in ids_style:

    patron = re.compile(
        rf'<style\b[^>]*id="{re.escape(sid)}"[^>]*>.*?</style>',
        re.I | re.S
    )

    login = patron.sub(
        '',
        login
    )

ids_script = [
    "EDUTURNOS_LOGIN_DIBUJO_SIN_FONDO_FINAL",
    "EDUTURNOS_DIBUJO_SIN_FONDO_FINAL",
    "EDUTURNOS_LOGIN_MASTER_ABSOLUTO_JS",
    "EDUTURNOS_LOGIN_VISUAL_DEFINITIVO_JS",
    "EDUTURNOS_VISUAL_REAL_SCRIPT",
    "EDUTURNOS_LINEA_BLANCA_UNICA_FINAL",
]

for sid in ids_script:

    patron = re.compile(
        rf'<script\b[^>]*id="{re.escape(sid)}"[^>]*>.*?</script>',
        re.I | re.S
    )

    login = patron.sub(
        '',
        login
    )

print("OK bloques anteriores limpiados")

# ============================================================
# CSS FINAL
# ============================================================

MASTER_CSS = r'''
/* ===============================================================
   EDUTURNOS - LOGIN FINAL ABSOLUTO
   =============================================================== */


/* ===============================================================
   PERSONAL INSTITUCIONAL
   =============================================================== */

html body .login-page .personal-login {

    width: 100% !important;

    max-width: 100% !important;

    box-sizing: border-box !important;

    overflow: hidden !important;

    padding: 18px 20px !important;
}


/* ===============================================================
   UNA SOLA FILA
   DISTANCIAS IGUALES
   =============================================================== */

html body .login-page .personal-login .form-grid,

html body .login-page .personal-login .personal-fields-grid {

    display: grid !important;

    grid-template-columns:
        94px
        210px
        82px !important;

    column-gap: 8px !important;

    row-gap: 0 !important;

    width: 402px !important;

    max-width: 100% !important;

    margin-left: auto !important;

    margin-right: auto !important;

    padding: 0 !important;

    justify-content: center !important;

    align-items: end !important;

    box-sizing: border-box !important;
}


/* ===============================================================
   CADA CAMPO
   =============================================================== */

html body .login-page .personal-login .personal-field {

    width: auto !important;

    min-width: 0 !important;

    max-width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    box-sizing: border-box !important;
}


/* ===============================================================
   TITULOS
   =============================================================== */

html body .login-page
.personal-login .personal-field-title {

    display: block !important;

    width: 100% !important;

    text-align: center !important;

    white-space: nowrap !important;

    margin: 0 0 6px 0 !important;

    padding: 0 !important;

    line-height: 1.1 !important;
}


/* ===============================================================
   CUADRO CODIGO
   =============================================================== */

html body .login-page
.personal-login input[name="codigo_institucional"] {

    display: block !important;

    width: 94px !important;

    min-width: 94px !important;

    max-width: 94px !important;

    height: 42px !important;

    min-height: 42px !important;

    max-height: 42px !important;

    margin: 0 !important;

    padding: 7px 8px !important;

    box-sizing: border-box !important;

    background: #ffffff !important;

    color: #273142 !important;
}


/* ===============================================================
   CUADRO SEDE
   =============================================================== */

html body .login-page
.personal-login select[name="sede_id"] {

    display: block !important;

    width: 210px !important;

    min-width: 210px !important;

    max-width: 210px !important;

    height: 42px !important;

    min-height: 42px !important;

    max-height: 42px !important;

    margin: 0 !important;

    padding: 7px 9px !important;

    box-sizing: border-box !important;
}


/* ===============================================================
   CUADRO JORNADA
   =============================================================== */

html body .login-page
.personal-login select[name="jornada_id"] {

    display: block !important;

    width: 82px !important;

    min-width: 82px !important;

    max-width: 82px !important;

    height: 42px !important;

    min-height: 42px !important;

    max-height: 42px !important;

    margin: 0 !important;

    padding: 7px 7px !important;

    box-sizing: border-box !important;
}


/* ===============================================================
   DOCUMENTO / PASSWORD
   =============================================================== */

html body .login-page
input[name="identificador"],

html body .login-page
input[name="password"] {

    color: #273142 !important;

    caret-color: #273142 !important;
}

html body .login-page
label:has(input[name="identificador"]),

html body .login-page
label:has(input[name="password"]) {

    color: #273142 !important;
}


/* ===============================================================
   NO DEBES ESCOGERLO
   =============================================================== */

html body .login-page
.section-heading p,

html body .login-page
.section-heading p *,

html body .login-page
.section-heading strong {

    border: 0 !important;

    border-bottom: 0 !important;

    text-decoration: none !important;

    box-shadow: none !important;

    background-image: none !important;
}

html body .login-page
.section-heading::before,

html body .login-page
.section-heading::after {

    content: none !important;

    display: none !important;
}


/* ===============================================================
   BOTON INGRESAR
   =============================================================== */

html body .login-page
.boton-full {

    min-height: 52px !important;

    height: 52px !important;

    padding: 14px 30px !important;

    font-size: 15px !important;

    box-sizing: border-box !important;
}


/* ===============================================================
   DIBUJO
   SIN FONDO EXTERIOR
   =============================================================== */

html body .login-page svg {

    background: transparent !important;

    background-color: transparent !important;
}


/* ===============================================================
   CONTENEDORES TIPICOS DE ILUSTRACION
   =============================================================== */

html body .login-page
.login-illustration,

html body .login-page
.illustration,

html body .login-page
.login-art,

html body .login-page
.visual-art,

html body .login-page
.drawing {

    background: transparent !important;

    background-color: transparent !important;

    background-image: none !important;

    box-shadow: none !important;

    border: 0 !important;
}


/* ===============================================================
   NO TOCAR APPEARANCE
   =============================================================== */


/* ===============================================================
   RESPONSIVE
   =============================================================== */

@media (max-width: 700px) {

    html body .login-page
    .personal-login .form-grid,

    html body .login-page
    .personal-login .personal-fields-grid {

        width: 100% !important;

        grid-template-columns: 1fr !important;

        column-gap: 0 !important;

        row-gap: 10px !important;
    }

    html body .login-page
    .personal-login .personal-field {

        width: 100% !important;
    }

    html body .login-page
    .personal-login input[name="codigo_institucional"],

    html body .login-page
    .personal-login select[name="sede_id"],

    html body .login-page
    .personal-login select[name="jornada_id"] {

        width: 100% !important;

        min-width: 0 !important;

        max-width: 100% !important;
    }
}
'''

MASTER.write_text(
    MASTER_CSS.strip() + "\n",
    encoding="utf-8"
)

print("OK CSS master creado")

# ============================================================
# SCRIPT PARA QUITAR FONDO AZUL DEL DIBUJO
# ============================================================

DRAWING_JS = r'''
<script id="EDUTURNOS_LOGIN_DIBUJO_TRANSPARENTE_FINAL">
(function () {

    function azul(v) {

        if (!v) return false;

        v = v
            .toLowerCase()
            .replace(/\s/g, "");

        return (
            v === "#2563eb" ||
            v === "#1d4ed8" ||
            v === "#1e40af" ||
            v === "#1e3a8a" ||
            v === "#172554" ||
            v === "#0f172a" ||
            v.includes("rgb(37,99,235)") ||
            v.includes("rgb(29,78,216)") ||
            v.includes("rgb(30,64,175)")
        );
    }


    function limpiar() {

        const page =
            document.querySelector(
                ".login-page"
            );

        if (!page) return;


        page.querySelectorAll(
            "svg"
        ).forEach(
            function (svg) {

                svg.style.setProperty(
                    "background",
                    "transparent",
                    "important"
                );

                svg.style.setProperty(
                    "background-color",
                    "transparent",
                    "important"
                );


                const svgBox =
                    svg.getBoundingClientRect();


                svg.querySelectorAll(
                    "rect"
                ).forEach(
                    function (rect) {

                        const r =
                            rect.getBoundingClientRect();

                        const s =
                            getComputedStyle(
                                rect
                            );


                        const cubreTodo =
                            svgBox.width > 0 &&
                            svgBox.height > 0 &&
                            r.width >=
                                svgBox.width * 0.80 &&
                            r.height >=
                                svgBox.height * 0.80;


                        if (
                            cubreTodo &&
                            (
                                azul(s.fill) ||
                                azul(s.backgroundColor)
                            )
                        ) {

                            rect.style.setProperty(
                                "fill",
                                "transparent",
                                "important"
                            );

                            rect.style.setProperty(
                                "fill-opacity",
                                "0",
                                "important"
                            );

                        }

                    }
                );

            }
        );
    }


    function campos() {

        const page =
            document.querySelector(
                ".login-page"
            );

        if (!page) return;


        const grid =
            page.querySelector(
                ".personal-fields-grid, .personal-login .form-grid"
            );

        if (grid) {

            grid.style.setProperty(
                "display",
                "grid",
                "important"
            );

            grid.style.setProperty(
                "grid-template-columns",
                "94px 210px 82px",
                "important"
            );

            grid.style.setProperty(
                "column-gap",
                "8px",
                "important"
            );

            grid.style.setProperty(
                "width",
                "402px",
                "important"
            );

            grid.style.setProperty(
                "max-width",
                "100%",
                "important"
            );

            grid.style.setProperty(
                "margin-left",
                "auto",
                "important"
            );

            grid.style.setProperty(
                "margin-right",
                "auto",
                "important"
            );

            grid.style.setProperty(
                "align-items",
                "end",
                "important"
            );

            grid.style.setProperty(
                "justify-content",
                "center",
                "important"
            );
        }


        const codigo =
            page.querySelector(
                'input[name="codigo_institucional"]'
            );

        if (codigo) {

            codigo.removeAttribute(
                "placeholder"
            );

            if (
                codigo.value === "123456"
            ) {

                codigo.value = "";
            }

            codigo.style.setProperty(
                "width",
                "94px",
                "important"
            );

            codigo.style.setProperty(
                "min-width",
                "94px",
                "important"
            );

            codigo.style.setProperty(
                "max-width",
                "94px",
                "important"
            );
        }


        const sede =
            page.querySelector(
                'select[name="sede_id"]'
            );

        if (sede) {

            sede.style.setProperty(
                "width",
                "210px",
                "important"
            );

            sede.style.setProperty(
                "min-width",
                "210px",
                "important"
            );

            sede.style.setProperty(
                "max-width",
                "210px",
                "important"
            );
        }


        const jornada =
            page.querySelector(
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


        limpiar();
    }


    document.addEventListener(
        "DOMContentLoaded",
        campos
    );

    window.addEventListener(
        "load",
        campos
    );

    setTimeout(
        campos,
        100
    );

    setTimeout(
        campos,
        300
    );

    setTimeout(
        campos,
        700
    );

    setTimeout(
        campos,
        1200
    );

})();
</script>
'''

# ============================================================
# INSERTAR DIRECTAMENTE EN LOGIN
# ============================================================

login = login.replace(
    '<script id="EDUTURNOS_LOGIN_DIBUJO_TRANSPARENTE_FINAL">',
    ''
)

# Añadir al final del HTML real.
if "</body>" in login.lower():

    pos = login.lower().rfind("</body>")

    login = (
        login[:pos]
        + "\n"
        + DRAWING_JS
        + "\n"
        + login[pos:]
    )

else:

    login += "\n" + DRAWING_JS

# ============================================================
# CORREGIR SELECTS SIN ALTERARLOS
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
        "CAMBIO EL HTML DE SEDE. NO SE GUARDA."
    )

if jornada_after.group(0) != jornada_original:
    raise RuntimeError(
        "CAMBIO EL HTML DE JORNADA. NO SE GUARDA."
    )

print("OK opciones Sede intactas")
print("OK opciones Jornada intactas")

# ============================================================
# GUARDAR LOGIN
# ============================================================

LOGIN.write_text(
    login,
    encoding="utf-8"
)

# ============================================================
# ESTILOS.CSS
# ============================================================

css = CSS.read_text(
    encoding="utf-8",
    errors="ignore"
)

# Eliminar nuestro bloque anterior si existiera.
inicio_marca = "/* ===== EDUTURNOS LOGIN ABSOLUTO INICIO ===== */"
fin_marca = "/* ===== EDUTURNOS LOGIN ABSOLUTO FIN ===== */"

if inicio_marca in css and fin_marca in css:

    patron = re.compile(
        re.escape(inicio_marca)
        + r".*?"
        + re.escape(fin_marca),
        re.I | re.S
    )

    css = patron.sub(
        '',
        css
    )

css += (
    "\n\n"
    + inicio_marca
    + "\n"
    + MASTER_CSS
    + "\n"
    + fin_marca
    + "\n"
)

CSS.write_text(
    css,
    encoding="utf-8"
)

print("OK estilos.css actualizado")

# ============================================================
# BASE.HTML
# ============================================================

base = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

# Quitar enlaces previos a nuestro master.
base = re.sub(
    r'<link\b[^>]*eduturnos_login_final_absolute\.css[^>]*>',
    '',
    base,
    flags=re.I
)

master_link = (
    '<link rel="stylesheet" '
    'href="{{ url_for(\'static\', filename=\'css/eduturnos_login_final_absolute.css\') }}"'
    f'?v={STAMP}>'
)

pos_head = base.lower().rfind("</head>")

if pos_head == -1:

    raise RuntimeError(
        "NO SE ENCONTRO </head> EN BASE.HTML"
    )

base = (
    base[:pos_head]
    + "\n"
    + master_link
    + "\n"
    + base[pos_head:]
)

BASE.write_text(
    base,
    encoding="utf-8"
)

print("OK master cargado al final de base.html")

# ============================================================
# VERIFICAR
# ============================================================

login_final = LOGIN.read_text(
    encoding="utf-8",
    errors="ignore"
)

base_final = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

checks = {

    "Documento":
        'name="identificador"' in login_final,

    "Password":
        'name="password"' in login_final,

    "Codigo":
        'name="codigo_institucional"' in login_final,

    "Sede":
        'name="sede_id"' in login_final,

    "Jornada":
        'name="jornada_id"' in login_final,

    "123456":
        not bool(
            re.search(
                r'<input\b[^>]*name\s*=\s*"codigo_institucional"[^>]*'
                r'(placeholder|value)\s*=\s*["\']123456["\']',
                login_final,
                re.I
            )
        ),

    "Master login":
        "EDUTURNOS LOGIN FINAL ABSOLUTO"
        in login_final,

    "JS dibujo":
        "EDUTURNOS_LOGIN_DIBUJO_TRANSPARENTE_FINAL"
        in login_final,

    "Master CSS archivo":
        MASTER.exists(),

    "Master en base":
        "eduturnos_login_final_absolute.css"
        in base_final,

    "Sede intacta":
        sede_original in login_final,

    "Jornada intacta":
        jornada_original in login_final,
}

print()
print("=" * 80)
print(" VERIFICACION FINAL")
print("=" * 80)

for nombre, ok in checks.items():

    print(
        ("OK    " if ok else "ERROR ")
        + nombre
    )

if not all(checks.values()):

    raise RuntimeError(
        "ALGUNA VERIFICACION FALLO."
    )

print()
print("=" * 80)
print(" MEDIDAS FINALES")
print("=" * 80)
print()
print("Codigo   : 94 px")
print("Sede     : 210 px")
print("Jornada  : 82 px")
print("Separacion: 8 px")
print("Altura   : 42 px")
print()
print("El 123456 fue eliminado.")
print("El fondo azul del dibujo se vuelve transparente.")
print("El dibujo se conserva.")
print("Los select mantienen exactamente sus opciones.")
print()
print("BACKUP LOGIN:")
print(LOGIN_BAK)
print()
print("BACKUP BASE:")
print(BASE_BAK)
print()
print("BACKUP CSS:")
print(CSS_BAK)
print()
print("=" * 80)
print(" CAMBIOS GUARDADOS")
print("=" * 80)
