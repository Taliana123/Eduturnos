from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(r"F:\edu_Final")

TEMPLATES = ROOT / "templates"
LOGIN = TEMPLATES / "auth" / "login.html"
BASE = TEMPLATES / "base.html"
CSSDIR = ROOT / "static" / "css"

MASTER = CSSDIR / "eduturnos_login_master.css"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

print()
print("=" * 78)
print(" EDUTURNOS - ORDEN FINAL DEL LOGIN")
print("=" * 78)
print()

# ============================================================
# COMPROBAR
# ============================================================

for f in [LOGIN, BASE, CSSDIR]:
    if not f.exists():
        raise RuntimeError(f"NO EXISTE: {f}")

print("OK archivos principales")

# ============================================================
# BACKUPS
# ============================================================

LOGIN_BAK = LOGIN.with_name(
    LOGIN.name + f".BACKUP_ORDEN_{STAMP}.bak"
)

BASE_BAK = BASE.with_name(
    BASE.name + f".BACKUP_ORDEN_{STAMP}.bak"
)

shutil.copy2(LOGIN, LOGIN_BAK)
shutil.copy2(BASE, BASE_BAK)

if MASTER.exists():

    MASTER_BAK = MASTER.with_name(
        MASTER.name + f".BACKUP_ORDEN_{STAMP}.bak"
    )

    shutil.copy2(MASTER, MASTER_BAK)

else:
    MASTER_BAK = None

print("OK backups creados")

# ============================================================
# LEER LOGIN
# ============================================================

login = LOGIN.read_text(
    encoding="utf-8",
    errors="ignore"
)

# ============================================================
# COMPROBAR ELEMENTOS IMPORTANTES
# ============================================================

required = [
    'name="identificador"',
    'name="password"',
    'name="codigo_institucional"',
    'name="sede_id"',
    'name="jornada_id"',
    "csrf_field",
]

for item in required:

    if item not in login:

        raise RuntimeError(
            f"FALTA: {item}"
        )

print("OK elementos funcionales")

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
    raise RuntimeError("No existe select Sede")

if not jornada_match:
    raise RuntimeError("No existe select Jornada")

sede_original = sede_match.group(0)
jornada_original = jornada_match.group(0)

# ============================================================
# ELIMINAR ESTILOS VISUALES NUEVOS ANTERIORES
# ============================================================

style_ids = [
    "EDUTURNOS_COMPACTO_REAL",
    "EDUTURNOS_AJUSTE_FINAL_DIRECT",
    "EDUTURNOS_LOGIN_FINAL_DIRECT",
    "EDUTURNOS_LOGIN_MASTER_INLINE",
    "EDUTURNOS_BASE_VISUAL_FINAL",
    "EDUTURNOS_LOGIN_VISUAL_DEFINITIVO",
    "EDUTURNOS_LOGIN_VISUAL_DEFINITIVO_JS",
    "EDUTURNOS_LOGIN_MASTER_INLINE",
]

for sid in style_ids:

    login = re.sub(
        rf'<style\b[^>]*id="{re.escape(sid)}"[^>]*>.*?</style>',
        '',
        login,
        flags=re.I | re.S
    )

script_ids = [
    "EDUTURNOS_VISUAL_REAL_SCRIPT",
    "EDUTURNOS_LINEA_BLANCA_UNICA_FINAL",
    "EDUTURNOS_LINEA_DIBUJO_FINAL",
    "EDUTURNOS_LINEA_DIBUJO",
    "EDUTURNOS_VISUAL_REAL_SCRIPT",
    "EDUTURNOS_LOGIN_VISUAL_DEFINITIVO_JS",
]

for sid in script_ids:

    login = re.sub(
        rf'<script\b[^>]*id="{re.escape(sid)}"[^>]*>.*?</script>',
        '',
        login,
        flags=re.I | re.S
    )

print("OK estilos anteriores retirados")

# ============================================================
# 123456 FUERA
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
# ESTILO FINAL
# ============================================================

FINAL_STYLE = r'''
<style id="EDUTURNOS_LOGIN_MASTER_ORDEN_FINAL">

/* ============================================================
   PERSONAL INSTITUCIONAL
   ============================================================ */

html body .personal-login {

    width: 100% !important;

    max-width: 100% !important;

    box-sizing: border-box !important;

    overflow: hidden !important;
}


/* ============================================================
   TRES CAMPOS EN UNA SOLA FILA
   MISMA DISTANCIA
   ============================================================ */

html body .personal-login .personal-fields-grid,

html body .personal-login .form-grid {

    display: grid !important;

    grid-template-columns:
        96px
        215px
        86px !important;

    column-gap: 10px !important;

    row-gap: 0 !important;

    width: 417px !important;

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

    padding: 0 !important;

    box-sizing: border-box !important;
}


/* ============================================================
   TITULOS
   ============================================================ */

html body .personal-login .personal-field-title {

    display: block !important;

    width: 100% !important;

    margin: 0 0 6px 0 !important;

    padding: 0 !important;

    text-align: center !important;

    white-space: nowrap !important;

    line-height: 1.1 !important;
}


/* ============================================================
   CUADRO CODIGO
   ============================================================ */

html body
.personal-login input[name="codigo_institucional"] {

    display: block !important;

    width: 96px !important;

    min-width: 96px !important;

    max-width: 96px !important;

    height: 44px !important;

    margin: 0 !important;

    padding: 8px 9px !important;

    box-sizing: border-box !important;

    background-color: #ffffff !important;
}


/* ============================================================
   CUADRO SEDE
   ============================================================ */

html body
.personal-login select[name="sede_id"] {

    display: block !important;

    width: 215px !important;

    min-width: 215px !important;

    max-width: 215px !important;

    height: 44px !important;

    margin: 0 !important;

    padding: 8px 10px !important;

    box-sizing: border-box !important;
}


/* ============================================================
   CUADRO JORNADA
   ============================================================ */

html body
.personal-login select[name="jornada_id"] {

    display: block !important;

    width: 86px !important;

    min-width: 86px !important;

    max-width: 86px !important;

    height: 44px !important;

    margin: 0 !important;

    padding: 8px 8px !important;

    box-sizing: border-box !important;
}


/* ============================================================
   DOCUMENTO Y PASSWORD
   ============================================================ */

html body
input[name="identificador"],

html body
input[name="password"] {

    color: #273142 !important;

    caret-color: #273142 !important;
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
   SOLO DIBUJO
   ============================================================ */

/* Quitar fondos de contenedores inmediatos del dibujo */
html body .login-page svg {

    background: transparent !important;

    background-color: transparent !important;
}


/* El SVG conserva sus elementos */
html body .login-page svg * {

    background-color: transparent !important;
}


/* ============================================================
   BOTON INGRESAR
   ============================================================ */

html body .login-page .boton-full {

    min-height: 52px !important;

    padding: 14px 30px !important;

    font-size: 15px !important;
}


/* ============================================================
   MOVIL
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
# JAVASCRIPT PARA QUITAR SOLO EL CUADRADO AZUL DEL DIBUJO
# ============================================================

FINAL_JS = r'''
<script id="EDUTURNOS_LOGIN_DIBUJO_LIMPIO">

(function () {

    function azul(valor) {

        if (!valor) return false;

        const v =
            valor
                .toLowerCase()
                .replace(/\s/g, "");

        return (
            v.includes("#2563eb") ||
            v.includes("#1d4ed8") ||
            v.includes("#1e3a8a") ||
            v.includes("#1e40af") ||
            v.includes("#172554") ||
            v.includes("#0f172a") ||
            v.includes("rgb(37,99,235)") ||
            v.includes("rgb(29,78,216)") ||
            v.includes("rgb(30,64,175)") ||
            v.includes("rgb(23,37,84)")
        );
    }


    function limpiarDibujo() {

        const page =
            document.querySelector(
                ".login-page"
            );

        if (!page) return;


        const svgs =
            page.querySelectorAll(
                "svg"
            );


        svgs.forEach(
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


                /*
                 * Revisar rectangulos azules
                 * que sean practicamente el fondo
                 * completo del SVG.
                 */

                const rects =
                    svg.querySelectorAll(
                        "rect"
                    );

                const svgRect =
                    svg.getBoundingClientRect();

                rects.forEach(
                    function (rect) {

                        const r =
                            rect.getBoundingClientRect();

                        const fill =
                            getComputedStyle(
                                rect
                            ).fill;

                        const background =
                            getComputedStyle(
                                rect
                            ).backgroundColor;


                        const ocupaTodo =
                            svgRect.width > 0 &&
                            svgRect.height > 0 &&
                            r.width >= svgRect.width * 0.80 &&
                            r.height >= svgRect.height * 0.80;


                        if (
                            ocupaTodo &&
                            (
                                azul(fill) ||
                                azul(background)
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


                /*
                 * Revisar hasta tres contenedores
                 * alrededor del SVG.
                 */

                let contenedor =
                    svg.parentElement;

                let nivel = 0;

                while (
                    contenedor &&
                    nivel < 3
                ) {

                    if (
                        contenedor.matches(
                            "input,select,textarea,button,label"
                        )
                    ) {
                        break;
                    }


                    const cs =
                        getComputedStyle(
                            contenedor
                        );


                    if (
                        azul(cs.backgroundColor) ||
                        azul(cs.backgroundImage)
                    ) {

                        const r =
                            contenedor.getBoundingClientRect();


                        /*
                         * Solo limpiar si el contenedor
                         * corresponde visualmente al dibujo.
                         */

                        if (
                            r.width <=
                                svgRect.width + 100 &&
                            r.height <=
                                svgRect.height + 100
                        ) {

                            contenedor.style.setProperty(
                                "background",
                                "transparent",
                                "important"
                            );

                            contenedor.style.setProperty(
                                "background-color",
                                "transparent",
                                "important"
                            );

                            contenedor.style.setProperty(
                                "background-image",
                                "none",
                                "important"
                            );

                            contenedor.style.setProperty(
                                "box-shadow",
                                "none",
                                "important"
                            );

                            contenedor.style.setProperty(
                                "border",
                                "0",
                                "important"
                            );
                        }
                    }

                    contenedor =
                        contenedor.parentElement;

                    nivel++;
                }

            }
        );
    }


    function organizar() {

        const login =
            document.querySelector(
                ".login-page"
            );

        if (!login) return;


        const grid =
            login.querySelector(
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
                "96px 215px 86px",
                "important"
            );

            grid.style.setProperty(
                "column-gap",
                "10px",
                "important"
            );

            grid.style.setProperty(
                "row-gap",
                "0",
                "important"
            );

            grid.style.setProperty(
                "width",
                "417px",
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
                "justify-content",
                "center",
                "important"
            );

            grid.style.setProperty(
                "align-items",
                "end",
                "important"
            );
        }


        const codigo =
            login.querySelector(
                'input[name="codigo_institucional"]'
            );

        if (codigo) {

            codigo.removeAttribute(
                "placeholder"
            );

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


        const sede =
            login.querySelector(
                'select[name="sede_id"]'
            );

        if (sede) {

            sede.style.setProperty(
                "width",
                "215px",
                "important"
            );

            sede.style.setProperty(
                "min-width",
                "215px",
                "important"
            );

            sede.style.setProperty(
                "max-width",
                "215px",
                "important"
            );
        }


        const jornada =
            login.querySelector(
                'select[name="jornada_id"]'
            );

        if (jornada) {

            jornada.style.setProperty(
                "width",
                "86px",
                "important"
            );

            jornada.style.setProperty(
                "min-width",
                "86px",
                "important"
            );

            jornada.style.setProperty(
                "max-width",
                "86px",
                "important"
            );
        }


        login.querySelectorAll(
            ".personal-field-title"
        ).forEach(
            function (titulo) {

                titulo.style.setProperty(
                    "text-align",
                    "center",
                    "important"
                );

                titulo.style.setProperty(
                    "margin-bottom",
                    "6px",
                    "important"
                );
            }
        );


        limpiarDibujo();
    }


    document.addEventListener(
        "DOMContentLoaded",
        organizar
    );

    window.addEventListener(
        "load",
        organizar
    );

    setTimeout(
        organizar,
        100
    );

    setTimeout(
        organizar,
        400
    );

    setTimeout(
        organizar,
        900
    );

})();

</script>
'''

# ============================================================
# INSERTAR AL FINAL REAL DEL DOCUMENTO
# ============================================================

login = re.sub(
    r'<style\b[^>]*id="EDUTURNOS_LOGIN_MASTER_ORDEN_FINAL"[^>]*>.*?</style>',
    '',
    login,
    flags=re.I | re.S
)

login = re.sub(
    r'<script\b[^>]*id="EDUTURNOS_LOGIN_DIBUJO_LIMPIO"[^>]*>.*?</script>',
    '',
    login,
    flags=re.I | re.S
)

bloque = (
    "\n"
    + FINAL_STYLE
    + "\n"
    + FINAL_JS
    + "\n"
)

if re.search(
    r'</body>',
    login,
    re.I
):

    login = re.sub(
        r'</body>',
        bloque + '</body>',
        login,
        count=1,
        flags=re.I
    )

else:

    login += bloque

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
        "CAMBIO EL SELECT DE SEDE"
    )

if jornada_after.group(0) != jornada_original:
    raise RuntimeError(
        "CAMBIO EL SELECT DE JORNADA"
    )

print("OK Sede intacta")
print("OK Jornada intacta")

# ============================================================
# GUARDAR LOGIN
# ============================================================

LOGIN.write_text(
    login,
    encoding="utf-8"
)

# ============================================================
# CREAR CSS MASTER
# ============================================================

MASTER.write_text(
FINAL_STYLE
.replace(
    "<style id=\"EDUTURNOS_LOGIN_MASTER_ORDEN_FINAL\">",
    ""
)
.replace(
    "</style>",
    ""
)
.strip() + "\n",
    encoding="utf-8"
)

# ============================================================
# ASEGURAR MASTER EN BASE
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
        "base.html no contiene </head>"
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

print("OK master cargado en base")

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

    "123456 fuera":
        not bool(
            re.search(
                r'<input\b[^>]*name\s*=\s*"codigo_institucional"[^>]*'
                r'(placeholder|value)\s*=\s*["\']123456["\']',
                final_login,
                re.I
            )
        ),

    "Master inline":
        "EDUTURNOS_LOGIN_MASTER_ORDEN_FINAL"
        in final_login,

    "JS dibujo":
        "EDUTURNOS_LOGIN_DIBUJO_LIMPIO"
        in final_login,

    "Master CSS":
        MASTER.exists(),

    "Base master":
        "eduturnos_login_master.css"
        in final_base,

    "Sede intacta":
        sede_original in final_login,

    "Jornada intacta":
        jornada_original in final_login,
}

print()
print("=" * 78)
print(" VERIFICACION")
print("=" * 78)

for nombre, ok in checks.items():

    print(
        ("OK    " if ok else "ERROR ")
        + nombre
    )

print()

if not all(checks.values()):

    raise RuntimeError(
        "La verificacion NO paso."
    )

print("MEDIDAS FINALES")
print("----------------")
print("Codigo  : 96 px")
print("Sede    : 215 px")
print("Jornada : 86 px")
print("Espacio : 10 px")
print("Grid    : 417 px")

print()
print("DIBUJO:")
print("Se conserva el dibujo.")
print("Se elimina un fondo azul que funcione como cuadro.")

print()
print("BACKUP LOGIN:")
print(LOGIN_BAK)

print()
print("BACKUP BASE:")
print(BASE_BAK)

print()
print("=" * 78)
print(" LOGIN VISUAL ACTUALIZADO")
print("=" * 78)
