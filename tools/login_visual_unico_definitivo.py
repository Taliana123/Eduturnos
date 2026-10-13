from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(r"F:\edu_Final")

BASE  = ROOT / "templates" / "base.html"
LOGIN = ROOT / "templates" / "auth" / "login.html"
CSS   = ROOT / "static" / "css" / "estilos.css"

FINAL_CSS = ROOT / "static" / "css" / "eduturnos_login_visual_unico.css"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

print()
print("=" * 82)
print(" EDUTURNOS - UNIFICACION VISUAL DEFINITIVA DEL LOGIN")
print("=" * 82)
print()

# ============================================================
# COMPROBAR
# ============================================================

for archivo in [BASE, LOGIN, CSS]:

    if not archivo.exists():
        raise RuntimeError(
            f"No existe: {archivo}"
        )

print("OK archivos principales")

# ============================================================
# BACKUPS
# ============================================================

base_bak = BASE.with_name(
    BASE.name + f".BACKUP_VISUAL_UNICO_{STAMP}.bak"
)

login_bak = LOGIN.with_name(
    LOGIN.name + f".BACKUP_VISUAL_UNICO_{STAMP}.bak"
)

css_bak = CSS.with_name(
    CSS.name + f".BACKUP_VISUAL_UNICO_{STAMP}.bak"
)

shutil.copy2(BASE, base_bak)
shutil.copy2(LOGIN, login_bak)
shutil.copy2(CSS, css_bak)

print("OK backups creados")

# ============================================================
# LEER
# ============================================================

login = LOGIN.read_text(
    encoding="utf-8",
    errors="ignore"
)

base = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

# ============================================================
# VERIFICAR FUNCIONALIDAD
# ============================================================

for campo in [
    'name="identificador"',
    'name="password"',
    'name="codigo_institucional"',
    'name="sede_id"',
    'name="jornada_id"',
]:

    if campo not in login:
        raise RuntimeError(
            f"SE PERDIO {campo}"
        )

print("OK campos funcionales")

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
    raise RuntimeError("No se encontro select sede")

if not jornada_match:
    raise RuntimeError("No se encontro select jornada")

sede_original = sede_match.group(0)
jornada_original = jornada_match.group(0)

print("OK selects originales guardados")

# ============================================================
# LIMPIAR 123456
# ============================================================

def limpiar_codigo(match):

    tag = match.group(0)

    patrones = [
        r'\splaceholder\s*=\s*"123456"',
        r"\splaceholder\s*=\s*'123456'",
        r'\svalue\s*=\s*"123456"',
        r"\svalue\s*=\s*'123456'",
    ]

    for patron in patrones:

        tag = re.sub(
            patron,
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

print("OK 123456 eliminado")

# ============================================================
# CSS VISUAL UNICO
# ============================================================

MASTER_CSS = r'''
/* ==========================================================
   EDUTURNOS
   LOGIN VISUAL UNICO DEFINITIVO
   ========================================================== */


/* ==========================================================
   PERSONAL INSTITUCIONAL
   ========================================================== */

html body .login-page .personal-login {

    width: 100% !important;

    max-width: 100% !important;

    box-sizing: border-box !important;

    overflow: hidden !important;

    padding: 18px 14px !important;

    margin: 0 !important;
}


/* ==========================================================
   LOS TRES CAMPOS
   UNA FILA
   SEPARACION IGUAL
   ========================================================== */

html body .login-page
.personal-login .personal-fields-grid,

html body .login-page
.personal-login .form-grid {

    display: grid !important;

    grid-template-columns:
        88px
        185px
        78px !important;

    column-gap: 8px !important;

    row-gap: 0 !important;

    width: 367px !important;

    max-width: 100% !important;

    margin: 0 auto !important;

    padding: 0 !important;

    box-sizing: border-box !important;

    justify-content: center !important;

    align-items: end !important;
}


/* ==========================================================
   CAMPOS INDIVIDUALES
   ========================================================== */

html body .login-page
.personal-login .personal-field {

    width: auto !important;

    min-width: 0 !important;

    max-width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    box-sizing: border-box !important;
}


/* ==========================================================
   TITULOS
   ========================================================== */

html body .login-page
.personal-login .personal-field-title {

    display: block !important;

    width: 100% !important;

    margin: 0 0 6px 0 !important;

    padding: 0 !important;

    text-align: center !important;

    white-space: nowrap !important;

    line-height: 1.1 !important;

    box-sizing: border-box !important;
}


/* ==========================================================
   CODIGO
   ========================================================== */

html body .login-page
.personal-login input[name="codigo_institucional"] {

    width: 88px !important;

    min-width: 88px !important;

    max-width: 88px !important;

    height: 42px !important;

    min-height: 42px !important;

    max-height: 42px !important;

    margin: 0 !important;

    padding: 7px 7px !important;

    box-sizing: border-box !important;

    background: #ffffff !important;

    color: #273142 !important;
}


/* ==========================================================
   SEDE
   MAS PEQUEÑA
   ========================================================== */

html body .login-page
.personal-login select[name="sede_id"] {

    width: 185px !important;

    min-width: 185px !important;

    max-width: 185px !important;

    height: 42px !important;

    min-height: 42px !important;

    max-height: 42px !important;

    margin: 0 !important;

    padding: 7px 8px !important;

    box-sizing: border-box !important;
}


/* ==========================================================
   JORNADA
   ========================================================== */

html body .login-page
.personal-login select[name="jornada_id"] {

    width: 78px !important;

    min-width: 78px !important;

    max-width: 78px !important;

    height: 42px !important;

    min-height: 42px !important;

    max-height: 42px !important;

    margin: 0 !important;

    padding: 7px 6px !important;

    box-sizing: border-box !important;
}


/* ==========================================================
   DOCUMENTO Y CONTRASEÑA
   ========================================================== */

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


/* ==========================================================
   TEXTO NO DEBES ESCOGERLO
   ========================================================== */

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

    border: 0 !important;
}


/* ==========================================================
   BOTON INGRESAR
   ========================================================== */

html body .login-page
.boton-full {

    min-height: 52px !important;

    height: 52px !important;

    padding: 14px 30px !important;

    font-size: 15px !important;

    box-sizing: border-box !important;
}


/* ==========================================================
   DIBUJO
   ELIMINAR CUADRO DE FONDO
   ========================================================== */

html body .login-page svg {

    background: transparent !important;

    background-color: transparent !important;

    box-shadow: none !important;

    border: 0 !important;
}


/* ==========================================================
   ELEMENTOS DEL DIBUJO
   ========================================================== */

html body .login-page svg rect {

    background: transparent !important;
}


/* ==========================================================
   LINEAS DECORATIVAS EXTERNAS
   ========================================================== */

html body .login-page
.drawing,

html body .login-page
.illustration,

html body .login-page
.login-illustration,

html body .login-page
.login-art,

html body .login-page
.visual-art {

    background: transparent !important;

    background-color: transparent !important;

    background-image: none !important;

    border: 0 !important;

    box-shadow: none !important;
}


/* ==========================================================
   NO MODIFICAR APPEARANCE
   SELECT NATIVO
   ========================================================== */


/* ==========================================================
   MOVIL
   ========================================================== */

@media (max-width: 700px) {

    html body .login-page
    .personal-login .personal-fields-grid,

    html body .login-page
    .personal-login .form-grid {

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

FINAL_CSS.write_text(
    MASTER_CSS.strip() + "\n",
    encoding="utf-8"
)

print("OK CSS unico creado")

# ============================================================
# INSERTAR CSS EN LOGIN COMO ULTIMA CAPA
# ============================================================

STYLE_ID = "EDUTURNOS_LOGIN_VISUAL_UNICO_INLINE"

patron_style = re.compile(
    rf'<style\b[^>]*id="{STYLE_ID}"[^>]*>.*?</style>',
    re.I | re.S
)

login = patron_style.sub(
    "",
    login
)

INLINE = (
    '<style id="' + STYLE_ID + '">\n'
    + MASTER_CSS
    + "\n</style>\n"
)

# Insertar antes del ultimo endblock.
match_endblock = re.search(
    r'\{%?\s*endblock\s*%\}',
    login,
    re.I
)

if match_endblock:

    posicion = match_endblock.start()

    login = (
        login[:posicion]
        + INLINE
        + "\n"
        + login[posicion:]
    )

else:

    # Si no existe endblock, insertar antes de body.
    match_body = re.search(
        r'</body>',
        login,
        re.I
    )

    if match_body:

        posicion = match_body.start()

        login = (
            login[:posicion]
            + INLINE
            + "\n"
            + login[posicion:]
        )

    else:

        login += "\n" + INLINE

print("OK CSS inline final")

# ============================================================
# JAVASCRIPT VISUAL
# ============================================================

JS = r'''
<script id="EDUTURNOS_LOGIN_VISUAL_UNICO_JS">
(function () {

    function aplicarLoginVisual() {

        const page =
            document.querySelector(".login-page");

        if (!page) {
            return;
        }


        /* ============================================
           GRID
           ============================================ */

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
                "88px 185px 78px",
                "important"
            );

            grid.style.setProperty(
                "column-gap",
                "8px",
                "important"
            );

            grid.style.setProperty(
                "width",
                "367px",
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
        }


        /* ============================================
           CODIGO
           ============================================ */

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
                "88px",
                "important"
            );

            codigo.style.setProperty(
                "min-width",
                "88px",
                "important"
            );

            codigo.style.setProperty(
                "max-width",
                "88px",
                "important"
            );
        }


        /* ============================================
           SEDE
           ============================================ */

        const sede =
            page.querySelector(
                'select[name="sede_id"]'
            );

        if (sede) {

            sede.style.setProperty(
                "width",
                "185px",
                "important"
            );

            sede.style.setProperty(
                "min-width",
                "185px",
                "important"
            );

            sede.style.setProperty(
                "max-width",
                "185px",
                "important"
            );
        }


        /* ============================================
           JORNADA
           ============================================ */

        const jornada =
            page.querySelector(
                'select[name="jornada_id"]'
            );

        if (jornada) {

            jornada.style.setProperty(
                "width",
                "78px",
                "important"
            );

            jornada.style.setProperty(
                "min-width",
                "78px",
                "important"
            );

            jornada.style.setProperty(
                "max-width",
                "78px",
                "important"
            );
        }


        /* ============================================
           DIBUJO
           QUITAR FONDOS
           ============================================ */

        const svgs =
            page.querySelectorAll("svg");

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

                svg.style.setProperty(
                    "border",
                    "0",
                    "important"
                );

                svg.style.setProperty(
                    "box-shadow",
                    "none",
                    "important"
                );


                /*
                 * Quitar rectangulos grandes
                 * que funcionan como fondo.
                 */

                const box =
                    svg.getBoundingClientRect();

                svg.querySelectorAll(
                    "rect"
                ).forEach(
                    function (rect) {

                        const r =
                            rect.getBoundingClientRect();

                        const style =
                            getComputedStyle(rect);

                        const grande =
                            box.width > 0 &&
                            box.height > 0 &&
                            r.width >=
                                box.width * 0.75 &&
                            r.height >=
                                box.height * 0.75;

                        const fondoOscuro =
                            style.fill &&
                            (
                                style.fill.includes(
                                    "rgb(15"
                                ) ||
                                style.fill.includes(
                                    "rgb(17"
                                ) ||
                                style.fill.includes(
                                    "rgb(23"
                                ) ||
                                style.fill.includes(
                                    "rgb(30"
                                ) ||
                                style.fill.includes(
                                    "rgb(31"
                                ) ||
                                style.fill.includes(
                                    "rgb(37"
                                )
                            );

                        if (
                            grande &&
                            fondoOscuro
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
                 * Quitar líneas blancas verticales
                 * del dibujo.
                 */

                svg.querySelectorAll(
                    "line, path, polyline, rect"
                ).forEach(
                    function (element) {

                        const style =
                            getComputedStyle(
                                element
                            );

                        const stroke =
                            (
                                style.stroke || ""
                            ).toLowerCase();

                        const fill =
                            (
                                style.fill || ""
                            ).toLowerCase();

                        const r =
                            element.getBoundingClientRect();

                        const esBlanco =
                            stroke.includes(
                                "255, 255, 255"
                            ) ||
                            stroke ===
                                "white" ||
                            stroke ===
                                "#fff" ||
                            stroke ===
                                "#ffffff";

                        const esVertical =
                            r.height >
                            r.width * 3;

                        if (
                            esBlanco &&
                            esVertical
                        ) {

                            element.style.setProperty(
                                "stroke",
                                "transparent",
                                "important"
                            );

                            element.style.setProperty(
                                "stroke-opacity",
                                "0",
                                "important"
                            );

                            element.style.setProperty(
                                "fill",
                                "transparent",
                                "important"
                            );
                        }
                    }
                );
            }
        );


        /*
         * Quitar bordes blancos verticales
         * en el contenedor inmediato del dibujo.
         */

        const dibujos =
            page.querySelectorAll(
                "svg"
            );

        dibujos.forEach(
            function (svg) {

                let padre =
                    svg.parentElement;

                let nivel = 0;

                while (
                    padre &&
                    nivel < 3
                ) {

                    const cs =
                        getComputedStyle(
                            padre
                        );

                    const borderLeft =
                        (
                            cs.borderLeftColor || ""
                        ).toLowerCase();

                    const borderRight =
                        (
                            cs.borderRightColor || ""
                        ).toLowerCase();

                    if (
                        borderLeft.includes(
                            "255, 255, 255"
                        )
                    ) {

                        padre.style.setProperty(
                            "border-left",
                            "0",
                            "important"
                        );
                    }

                    if (
                        borderRight.includes(
                            "255, 255, 255"
                        )
                    ) {

                        padre.style.setProperty(
                            "border-right",
                            "0",
                            "important"
                        );
                    }

                    padre.style.setProperty(
                        "background-color",
                        "transparent",
                        "important"
                    );

                    nivel++;
                    padre =
                        padre.parentElement;
                }
            }
        );
    }


    document.addEventListener(
        "DOMContentLoaded",
        aplicarLoginVisual
    );

    window.addEventListener(
        "load",
        aplicarLoginVisual
    );

    setTimeout(
        aplicarLoginVisual,
        100
    );

    setTimeout(
        aplicarLoginVisual,
        300
    );

    setTimeout(
        aplicarLoginVisual,
        700
    );

    setTimeout(
        aplicarLoginVisual,
        1200
    );

})();
</script>
'''

# Quitar nuestro JS anterior
login = re.sub(
    r'<script\b[^>]*id="EDUTURNOS_LOGIN_VISUAL_UNICO_JS"[^>]*>.*?</script>',
    '',
    login,
    flags=re.I | re.S
)

# Insertarlo antes del final del bloque/body
m = re.search(
    r'\{%?\s*endblock\s*%\}',
    login,
    re.I
)

if m:

    pos = m.start()

    login = (
        login[:pos]
        + JS
        + "\n"
        + login[pos:]
    )

else:

    m = re.search(
        r'</body>',
        login,
        re.I
    )

    if m:

        pos = m.start()

        login = (
            login[:pos]
            + JS
            + "\n"
            + login[pos:]
        )

    else:

        login += "\n" + JS

# ============================================================
# VERIFICAR SELECTS ANTES DE GUARDAR
# ============================================================

sede_final = re.search(
    r'<select\b[^>]*name\s*=\s*"sede_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

jornada_final = re.search(
    r'<select\b[^>]*name\s*=\s*"jornada_id"[^>]*>.*?</select>',
    login,
    re.I | re.S
)

if not sede_final:
    raise RuntimeError(
        "DESAPARECIO SELECT SEDE"
    )

if not jornada_final:
    raise RuntimeError(
        "DESAPARECIO SELECT JORNADA"
    )

if sede_final.group(0) != sede_original:

    raise RuntimeError(
        "EL SELECT SEDE CAMBIO. NO SE GUARDA."
    )

if jornada_final.group(0) != jornada_original:

    raise RuntimeError(
        "EL SELECT JORNADA CAMBIO. NO SE GUARDA."
    )

print("OK select Sede intacto")
print("OK select Jornada intacto")

# ============================================================
# GUARDAR LOGIN
# ============================================================

LOGIN.write_text(
    login,
    encoding="utf-8"
)

# ============================================================
# GUARDAR CSS
# ============================================================

css_path = FINAL_CSS

# ============================================================
# ACTUALIZAR BASE
# ============================================================

base = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

base = re.sub(
    r'<link\b[^>]*eduturnos_login_visual_unico\.css[^>]*>',
    '',
    base,
    flags=re.I
)

link = (
    '<link rel="stylesheet" '
    'href="{{ url_for(\'static\', filename=\'css/eduturnos_login_visual_unico.css\') }}"'
    f'?v={STAMP}>'
)

pos = base.lower().rfind("</head>")

if pos == -1:

    raise RuntimeError(
        "base.html no contiene </head>"
    )

base = (
    base[:pos]
    + "\n"
    + link
    + "\n"
    + base[pos:]
)

BASE.write_text(
    base,
    encoding="utf-8"
)

print("OK CSS final cargado en base.html")

# ============================================================
# VERIFICACION FINAL
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

    "CSRF":
        "csrf_field" in login_final,

    "Recuperar":
        "passwords.recuperar" in login_final,

    "Registro":
        "auth.registro" in login_final,

    "123456 eliminado":
        not bool(
            re.search(
                r'<input\b[^>]*name\s*=\s*"codigo_institucional"[^>]*'
                r'(placeholder|value)\s*=\s*["\']123456["\']',
                login_final,
                re.I
            )
        ),

    "Select Sede intacto":
        sede_original in login_final,

    "Select Jornada intacto":
        jornada_original in login_final,

    "CSS final":
        FINAL_CSS.exists(),

    "CSS cargado":
        "eduturnos_login_visual_unico.css"
        in base_final,

    "JS dibujo":
        "EDUTURNOS_LOGIN_VISUAL_UNICO_JS"
        in login_final,
}

print()
print("=" * 82)
print(" VERIFICACION")
print("=" * 82)

for nombre, ok in checks.items():

    print(
        ("OK    " if ok else "ERROR ")
        + nombre
    )

if not all(checks.values()):

    raise RuntimeError(
        "LA VERIFICACION NO PASO. NO CONTINUAR."
    )

print()
print("=" * 82)
print(" DISEÑO FINAL")
print("=" * 82)
print()
print("Codigo       : 88 px")
print("Sede         : 185 px")
print("Jornada      : 78 px")
print("Separacion   : 8 px")
print("Altura       : 42 px")
print("Grid total   : 367 px")
print()
print("Personal institucional: campos centrados y contenidos.")
print("Sede reducida para no salir del contenedor.")
print("123456 eliminado.")
print("Fondo azul del dibujo neutralizado.")
print("Linea blanca vertical neutralizada.")
print("Opciones de Sede intactas.")
print("Opciones de Jornada intactas.")
print("Backend intacto.")
print()
print("BACKUP LOGIN:")
print(login_bak)
print()
print("BACKUP BASE:")
print(base_bak)
print()
print("BACKUP CSS:")
print(css_bak)
print()
print("=" * 82)
print(" CAMBIOS APLICADOS")
print("=" * 82)
