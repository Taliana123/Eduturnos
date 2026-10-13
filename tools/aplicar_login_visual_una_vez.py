from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(r"F:\edu_Final")

TEMPLATES = ROOT / "templates"
CSSDIR = ROOT / "static" / "css"
BASE = TEMPLATES / "base.html"
CSS = CSSDIR / "estilos.css"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

print()
print("=" * 80)
print(" EDUTURNOS - LOGIN VISUAL FINAL FORZADO")
print("=" * 80)
print()

# ============================================================
# COMPROBAR
# ============================================================

for f in [TEMPLATES, CSSDIR, BASE, CSS]:
    if not f.exists():
        raise RuntimeError(f"NO EXISTE: {f}")

print("OK estructura")

# ============================================================
# ENCONTRAR TODAS LAS PLANTILLAS QUE REALMENTE CORRESPONDEN
# AL LOGIN
# ============================================================

login_files = []

for p in TEMPLATES.rglob("*.html"):

    try:
        txt = p.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception:
        continue

    nombre = p.name.lower()

    es_login = (
        "login" in nombre
        or 'name="identificador"' in txt
        or 'name="codigo_institucional"' in txt
        or "personal-login" in txt.lower()
        or "acceso seguro" in txt.lower()
    )

    if es_login:
        login_files.append(p)

print()
print("PLANTILLAS DETECTADAS:")

for p in login_files:
    print(" -", p.relative_to(ROOT))

if not login_files:
    raise RuntimeError(
        "NO se encontro ninguna plantilla de login."
    )

# ============================================================
# BACKUPS
# ============================================================

BASE_BAK = BASE.with_name(
    BASE.name + f".BACKUP_FINAL_{STAMP}.bak"
)

CSS_BAK = CSS.with_name(
    CSS.name + f".BACKUP_FINAL_{STAMP}.bak"
)

shutil.copy2(BASE, BASE_BAK)
shutil.copy2(CSS, CSS_BAK)

LOGIN_BAKS = []

for p in login_files:

    b = p.with_name(
        p.name + f".BACKUP_FINAL_{STAMP}.bak"
    )

    shutil.copy2(p, b)
    LOGIN_BAKS.append(b)

print()
print("OK backups")

# ============================================================
# CREAR MASTER CSS FINAL
# ============================================================

MASTER = CSSDIR / "eduturnos_login_forzado_final.css"

MASTER_CSS = r'''
/* =================================================================
   EDUTURNOS - LOGIN VISUAL FORZADO FINAL
   ================================================================= */


/* ================================================================
   PERSONAL INSTITUCIONAL
   ================================================================ */

html body .login-page .personal-login {

    width: 100% !important;

    max-width: 100% !important;

    box-sizing: border-box !important;

    overflow: hidden !important;

    padding: 16px 18px 18px !important;
}


/* ================================================================
   LOS TRES CAMPOS
   MISMA DISTANCIA
   UNA SOLA FILA
   ================================================================ */

html body .login-page
.personal-login .form-grid,

html body .login-page
.personal-login .personal-fields-grid {

    display: grid !important;

    grid-template-columns:
        94px
        205px
        80px !important;

    column-gap: 8px !important;

    row-gap: 0 !important;

    width: 395px !important;

    max-width: 100% !important;

    margin: 0 auto !important;

    padding: 0 !important;

    justify-content: center !important;

    align-items: end !important;

    box-sizing: border-box !important;
}


/* ================================================================
   CADA COLUMNA
   ================================================================ */

html body .login-page
.personal-login .personal-field {

    width: auto !important;

    min-width: 0 !important;

    max-width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    box-sizing: border-box !important;
}


/* ================================================================
   TITULOS
   ================================================================ */

html body .login-page
.personal-login .personal-field-title {

    display: block !important;

    width: 100% !important;

    margin: 0 0 6px 0 !important;

    padding: 0 !important;

    text-align: center !important;

    white-space: nowrap !important;

    line-height: 1.1 !important;
}


/* ================================================================
   CUADROS
   ================================================================ */

html body .login-page
.personal-login input[name="codigo_institucional"],

html body .login-page
.personal-login select[name="sede_id"],

html body .login-page
.personal-login select[name="jornada_id"] {

    display: block !important;

    height: 42px !important;

    min-height: 42px !important;

    box-sizing: border-box !important;

    margin: 0 !important;
}


/* ================================================================
   CODIGO
   ================================================================ */

html body .login-page
.personal-login input[name="codigo_institucional"] {

    width: 94px !important;

    min-width: 94px !important;

    max-width: 94px !important;

    padding: 7px 8px !important;

    background: #ffffff !important;

    color: #273142 !important;
}


/* ================================================================
   SEDE
   ================================================================ */

html body .login-page
.personal-login select[name="sede_id"] {

    width: 205px !important;

    min-width: 205px !important;

    max-width: 205px !important;

    padding: 7px 8px !important;
}


/* ================================================================
   JORNADA
   ================================================================ */

html body .login-page
.personal-login select[name="jornada_id"] {

    width: 80px !important;

    min-width: 80px !important;

    max-width: 80px !important;

    padding: 7px 6px !important;
}


/* ================================================================
   DOCUMENTO Y PASSWORD
   ================================================================ */

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


/* ================================================================
   NO DEBES ESCOGERLO
   ================================================================ */

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


/* ================================================================
   BOTON INGRESAR
   ================================================================ */

html body .login-page
.boton-full {

    min-height: 52px !important;

    height: 52px !important;

    padding: 14px 30px !important;

    font-size: 15px !important;

    box-sizing: border-box !important;
}


/* ================================================================
   DIBUJO
   NO APAGAR SU ANIMACION
   SOLO QUITAR FONDO
   ================================================================ */

html body .login-page svg,

html body .login-page img,

html body .login-page canvas {

    background: transparent !important;

    background-color: transparent !important;
}


/* ================================================================
   CONTENEDORES DE LA ILUSTRACION
   ================================================================ */

html body .login-page
.login-illustration,

html body .login-page
.illustration,

html body .login-page
.hero-illustration,

html body .login-page
.login-art,

html body .login-page
.drawing,

html body .login-page
.visual {

    background: transparent !important;

    background-color: transparent !important;

    background-image: none !important;

    box-shadow: none !important;
}


/* ================================================================
   NO CAMBIAR APPEARANCE
   SELECTS NATIVOS
   ================================================================ */


/* ================================================================
   MOVIL
   ================================================================ */

@media (max-width: 700px) {

    html body .login-page
    .personal-login .form-grid,

    html body .login-page
    .personal-login .personal-fields-grid {

        width: 100% !important;

        grid-template-columns: 1fr !important;

        column-gap: 0 !important;

        gap: 10px !important;
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

print("OK master CSS creado")

# ============================================================
# JS PARA EL CUADRO AZUL DEL DIBUJO
# ============================================================

DRAWING_JS = r'''
<script id="EDUTURNOS_DIBUJO_SIN_FONDO_FINAL">
(function () {

    function esAzul(valor) {

        if (!valor) return false;

        const v =
            valor
                .toLowerCase()
                .replace(/\s/g, "");

        return (
            v.includes("#2563eb") ||
            v.includes("#1d4ed8") ||
            v.includes("#1e40af") ||
            v.includes("#1e3a8a") ||
            v.includes("#172554") ||
            v.includes("rgb(37,99,235)") ||
            v.includes("rgb(29,78,216)") ||
            v.includes("rgb(30,64,175)") ||
            v.includes("rgb(23,37,84)")
        );
    }


    function quitarFondoAzul() {

        const page =
            document.querySelector(".login-page");

        if (!page) return;


        const graficos =
            page.querySelectorAll(
                "svg, img, canvas"
            );


        graficos.forEach(
            function (grafico) {

                const bounds =
                    grafico.getBoundingClientRect();


                /* -------------------------------------------------
                   SVG: quitar rect azul que cubre casi todo
                   ------------------------------------------------- */

                if (
                    grafico.tagName.toLowerCase()
                    === "svg"
                ) {

                    grafico.querySelectorAll(
                        "rect"
                    ).forEach(
                        function (rect) {

                            const r =
                                rect.getBoundingClientRect();

                            const estilo =
                                getComputedStyle(rect);

                            const ocupaTodo =
                                bounds.width > 0 &&
                                bounds.height > 0 &&
                                r.width >=
                                    bounds.width * 0.80 &&
                                r.height >=
                                    bounds.height * 0.80;

                            const azul =
                                esAzul(estilo.fill) ||
                                esAzul(
                                    estilo.backgroundColor
                                );

                            if (
                                ocupaTodo &&
                                azul
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

                                rect.style.setProperty(
                                    "stroke",
                                    "none",
                                    "important"
                                );
                            }

                        }
                    );
                }


                /* -------------------------------------------------
                   Imagen/canvas/SVG y padres inmediatos
                   ------------------------------------------------- */

                let padre =
                    grafico.parentElement;

                let niveles = 0;

                while (
                    padre &&
                    niveles < 2
                ) {

                    const estilo =
                        getComputedStyle(padre);

                    const r =
                        padre.getBoundingClientRect();

                    const tamañoValido =
                        r.width >= 50 &&
                        r.width <= 650 &&
                        r.height >= 50 &&
                        r.height <= 550;

                    if (
                        tamañoValido &&
                        esAzul(
                            estilo.backgroundColor
                        )
                    ) {

                        padre.style.setProperty(
                            "background",
                            "transparent",
                            "important"
                        );

                        padre.style.setProperty(
                            "background-color",
                            "transparent",
                            "important"
                        );

                        padre.style.setProperty(
                            "background-image",
                            "none",
                            "important"
                        );

                        padre.style.setProperty(
                            "box-shadow",
                            "none",
                            "important"
                        );

                        padre.style.setProperty(
                            "border",
                            "0",
                            "important"
                        );
                    }

                    padre =
                        padre.parentElement;

                    niveles++;
                }
            }
        );
    }


    function limpiarCodigo() {

        const codigo =
            document.querySelector(
                '.login-page input[name="codigo_institucional"]'
            );

        if (!codigo) return;


        if (
            codigo.getAttribute("placeholder")
            === "123456"
        ) {

            codigo.removeAttribute(
                "placeholder"
            );
        }


        if (
            codigo.value === "123456"
        ) {

            codigo.value = "";
        }
    }


    function reforzarCampos() {

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
                "94px 205px 80px",
                "important"
            );

            grid.style.setProperty(
                "column-gap",
                "8px",
                "important"
            );

            grid.style.setProperty(
                "row-gap",
                "0",
                "important"
            );

            grid.style.setProperty(
                "width",
                "395px",
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

            codigo.style.setProperty(
                "height",
                "42px",
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
                "205px",
                "important"
            );

            sede.style.setProperty(
                "min-width",
                "205px",
                "important"
            );

            sede.style.setProperty(
                "max-width",
                "205px",
                "important"
            );

            sede.style.setProperty(
                "height",
                "42px",
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
                "80px",
                "important"
            );

            jornada.style.setProperty(
                "min-width",
                "80px",
                "important"
            );

            jornada.style.setProperty(
                "max-width",
                "80px",
                "important"
            );

            jornada.style.setProperty(
                "height",
                "42px",
                "important"
            );
        }


        limpiarCodigo();
        quitarFondoAzul();
    }


    document.addEventListener(
        "DOMContentLoaded",
        reforzarCampos
    );

    window.addEventListener(
        "load",
        reforzarCampos
    );


    let repeticiones = 0;

    const intervalo =
        setInterval(
            function () {

                reforzarCampos();

                repeticiones++;

                if (repeticiones >= 20) {

                    clearInterval(
                        intervalo
                    );
                }

            },
            250
        );

})();
</script>
'''

# ============================================================
# APLICAR MASTER INLINE A TODOS LOS LOGIN
# ============================================================

for p in login_files:

    txt = p.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    # ---------------------------------------------------------
    # Limpiar nuestras versiones anteriores
    # ---------------------------------------------------------

    txt = re.sub(
        r'<style\b[^>]*id="EDUTURNOS_LOGIN_MASTER_ABSOLUTO_STYLE"[^>]*>.*?</style>',
        "",
        txt,
        flags=re.I | re.S
    )

    txt = re.sub(
        r'<style\b[^>]*id="EDUTURNOS_LOGIN_MASTER_ORDEN_FINAL"[^>]*>.*?</style>',
        "",
        txt,
        flags=re.I | re.S
    )

    txt = re.sub(
        r'<style\b[^>]*id="EDUTURNOS_LOGIN_VISUAL_DEFINITIVO"[^>]*>.*?</style>',
        "",
        txt,
        flags=re.I | re.S
    )

    txt = re.sub(
        r'<style\b[^>]*id="EDUTURNOS_COMPACTO_REAL"[^>]*>.*?</style>',
        "",
        txt,
        flags=re.I | re.S
    )

    txt = re.sub(
        r'<script\b[^>]*id="EDUTURNOS_DIBUJO_SIN_FONDO_FINAL"[^>]*>.*?</script>',
        "",
        txt,
        flags=re.I | re.S
    )

    # ---------------------------------------------------------
    # Insertar ANTES del endblock si existe.
    # Si no existe, antes de body/html.
    # ---------------------------------------------------------

    bloque = (
        "\n"
        '<style id="EDUTURNOS_LOGIN_MASTER_ABSOLUTO_STYLE">\n'
        + MASTER_CSS
        + "\n</style>\n"
        + DRAWING_JS
        + "\n"
    )

    if re.search(
        r'\{% endblock %\}',
        txt,
        re.I
    ):

        txt = re.sub(
            r'\{% endblock %\}',
            bloque + '\n{% endblock %}',
            txt,
            count=1,
            flags=re.I
        )

    elif re.search(
        r'</body>',
        txt,
        re.I
    ):

        txt = re.sub(
            r'</body>',
            bloque + '\n</body>',
            txt,
            count=1,
            flags=re.I
        )

    elif re.search(
        r'</html>',
        txt,
        re.I
    ):

        txt = re.sub(
            r'</html>',
            bloque + '\n</html>',
            txt,
            count=1,
            flags=re.I
        )

    else:

        txt += bloque

    # ---------------------------------------------------------
    # Limpiar placeholder 123456 literal.
    # ---------------------------------------------------------

    def limpiar_input(match):

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

        return tag

    txt = re.sub(
        r'<input\b[^>]*name\s*=\s*"codigo_institucional"[^>]*>',
        limpiar_input,
        txt,
        flags=re.I
    )

    # ---------------------------------------------------------
    # Comprobar que el formulario siga intacto
    # ---------------------------------------------------------

    for item in [
        'name="identificador"',
        'name="password"',
        'name="codigo_institucional"',
        'name="sede_id"',
        'name="jornada_id"',
    ]:

        if item not in txt:

            raise RuntimeError(
                f"SE PERDIO {item} EN {p}"
            )

    # ---------------------------------------------------------
    # Guardar
    # ---------------------------------------------------------

    p.write_text(
        txt,
        encoding="utf-8"
    )

    print(
        "OK login actualizado:",
        p.relative_to(ROOT)
    )

# ============================================================
# CARGAR MASTER CSS AL FINAL DE ESTILOS.CSS
# ============================================================

css = CSS.read_text(
    encoding="utf-8",
    errors="ignore"
)

css = re.sub(
    r'/\* EDUTURNOS MASTER LOGIN ABSOLUTO.*?EDUTURNOS FIN MASTER LOGIN ABSOLUTO \*/',
    '',
    css,
    flags=re.I | re.S
)

css_master = (
    "\n\n"
    "/* EDUTURNOS MASTER LOGIN ABSOLUTO "
    + STAMP
    + " */\n"
    + MASTER_CSS
    + "\n"
    "/* EDUTURNOS FIN MASTER LOGIN ABSOLUTO */\n"
)

css += css_master

CSS.write_text(
    css,
    encoding="utf-8"
)

print("OK master agregado al final de estilos.css")

# ============================================================
# BASE.HTML
# CARGAR MASTER COMO ULTIMO CSS
# ============================================================

base = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

base = re.sub(
    r'<link\b[^>]*eduturnos_login_forzado_final\.css[^>]*>',
    "",
    base,
    flags=re.I
)

link = (
    '<link rel="stylesheet" '
    'href="{{ url_for(\'static\', filename=\'css/eduturnos_login_forzado_final.css\') }}"'
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
    link + '\n</head>',
    base,
    count=1,
    flags=re.I
)

BASE.write_text(
    base,
    encoding="utf-8"
)

print("OK master enlazado desde base.html")

# ============================================================
# VERIFICAR SELECTS
# ============================================================

for p in login_files:

    txt = p.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    sede = re.search(
        r'<select\b[^>]*name\s*=\s*"sede_id"[^>]*>.*?</select>',
        txt,
        re.I | re.S
    )

    jornada = re.search(
        r'<select\b[^>]*name\s*=\s*"jornada_id"[^>]*>.*?</select>',
        txt,
        re.I | re.S
    )

    if not sede:
        raise RuntimeError(
            f"FALTA SELECT SEDE EN {p}"
        )

    if not jornada:
        raise RuntimeError(
            f"FALTA SELECT JORNADA EN {p}"
        )

    print(
        "OK selects:",
        p.relative_to(ROOT)
    )

# ============================================================
# VERIFICACION
# ============================================================

base_final = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

checks = {
    "Master CSS": MASTER.exists(),
    "Master en base": "eduturnos_login_forzado_final.css" in base_final,
    "CSS final en estilos": "EDUTURNOS MASTER LOGIN ABSOLUTO" in css,
}

for p in login_files:

    txt = p.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    checks[
        f"Master inline {p.relative_to(ROOT)}"
    ] = (
        "EDUTURNOS_LOGIN_MASTER_ABSOLUTO_STYLE"
        in txt
    )

    checks[
        f"JS dibujo {p.relative_to(ROOT)}"
    ] = (
        "EDUTURNOS_DIBUJO_SIN_FONDO_FINAL"
        in txt
    )

    checks[
        f"Codigo {p.relative_to(ROOT)}"
    ] = (
        'name="codigo_institucional"'
        in txt
    )

    checks[
        f"Sede {p.relative_to(ROOT)}"
    ] = (
        'name="sede_id"'
        in txt
    )

    checks[
        f"Jornada {p.relative_to(ROOT)}"
    ] = (
        'name="jornada_id"'
        in txt
    )

print()
print("=" * 80)
print(" VERIFICACION")
print("=" * 80)

for nombre, ok in checks.items():

    print(
        ("OK    " if ok else "ERROR ")
        + nombre
    )

if not all(checks.values()):
    raise RuntimeError(
        "La verificacion no paso."
    )

print()
print("=" * 80)
print(" RESULTADO VISUAL")
print("=" * 80)
print()
print("Codigo   : 94 px")
print("Sede     : 205 px")
print("Jornada  : 80 px")
print("Distancia: 8 px")
print("Altura   : 42 px")
print()
print("Los tres campos quedan en una sola fila.")
print("El dibujo conserva su animacion.")
print("El fondo azul del dibujo se elimina.")
print("123456 se elimina del cuadro de codigo.")
print()
print("NO se modificaron las opciones de los select.")
print("NO se modificaron rutas.")
print("NO se modifico el backend.")
print()
print("BACKUP BASE:")
print(BASE_BAK)
print()
print("BACKUP CSS:")
print(CSS_BAK)
print()
for b in LOGIN_BAKS:
    print("BACKUP LOGIN:", b)

print()
print("=" * 80)
print(" LISTO")
print("=" * 80)
