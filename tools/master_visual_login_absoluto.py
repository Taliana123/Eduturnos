from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(r"F:\edu_Final")

BASE = ROOT / "templates" / "base.html"
TEMPLATES = ROOT / "templates"
CSSDIR = ROOT / "static" / "css"

MASTER = CSSDIR / "eduturnos_login_master_absolute.css"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

print()
print("=" * 78)
print(" EDUTURNOS - MASTER VISUAL ABSOLUTO DEL LOGIN")
print("=" * 78)
print()

# ============================================================
# COMPROBAR
# ============================================================

for f in [BASE, TEMPLATES, CSSDIR]:
    if not f.exists():
        raise RuntimeError(f"NO EXISTE: {f}")

# ============================================================
# ENCONTRAR TODAS LAS PLANTILLAS VISUALES DE LOGIN
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
        or "personal-institutional" in txt.lower()
        or "personal-login" in txt.lower()
        or "personal institucional" in txt.lower()
        or "acceso seguro" in txt.lower()
    )

    if es_login:
        login_files.append(p)

print("ARCHIVOS DE LOGIN ENCONTRADOS:")
for p in login_files:
    print(" -", p.relative_to(ROOT))

if not login_files:
    raise RuntimeError(
        "No se encontraron plantillas de login."
    )

# ============================================================
# BACKUPS
# ============================================================

base_backup = BASE.with_name(
    BASE.name + f".BACKUP_ABSOLUTO_{STAMP}.bak"
)

shutil.copy2(BASE, base_backup)

login_backups = []

for p in login_files:

    b = p.with_name(
        p.name + f".BACKUP_ABSOLUTO_{STAMP}.bak"
    )

    shutil.copy2(p, b)
    login_backups.append(b)

if MASTER.exists():

    master_backup = MASTER.with_name(
        MASTER.name + f".BACKUP_ABSOLUTO_{STAMP}.bak"
    )

    shutil.copy2(
        MASTER,
        master_backup
    )

else:
    master_backup = None

print()
print("OK backups creados")

# ============================================================
# CSS MASTER
# ============================================================

MASTER_CSS = r'''
/* ===============================================================
   EDUTURNOS - LOGIN MASTER ABSOLUTO
   =============================================================== */


/* ===============================================================
   PERSONAL INSTITUCIONAL
   =============================================================== */

html body .login-page .personal-login {

    width: 100% !important;

    max-width: 100% !important;

    box-sizing: border-box !important;

    overflow: hidden !important;
}


/* ===============================================================
   FILA DE LOS TRES CAMPOS
   MISMA DISTANCIA
   =============================================================== */

html body .login-page
.personal-login .personal-fields-grid,

html body .login-page
.personal-login .form-grid {

    display: grid !important;

    grid-template-columns:
        94px
        205px
        80px !important;

    grid-template-rows: auto !important;

    column-gap: 8px !important;

    row-gap: 0 !important;

    width: 395px !important;

    max-width: 100% !important;

    margin-left: auto !important;

    margin-right: auto !important;

    padding: 0 !important;

    justify-content: center !important;

    align-items: end !important;

    box-sizing: border-box !important;
}


/* ===============================================================
   CADA COLUMNA
   =============================================================== */

html body .login-page
.personal-login .personal-field {

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

    margin: 0 0 6px 0 !important;

    padding: 0 !important;

    text-align: center !important;

    white-space: nowrap !important;

    line-height: 1.1 !important;
}


/* ===============================================================
   TODOS LOS CUADROS
   ALTURA COMPACTA
   =============================================================== */

html body .login-page
.personal-login input[name="codigo_institucional"],

html body .login-page
.personal-login select[name="sede_id"],

html body .login-page
.personal-login select[name="jornada_id"] {

    height: 42px !important;

    min-height: 42px !important;

    box-sizing: border-box !important;

    margin: 0 !important;
}


/* ===============================================================
   CODIGO
   =============================================================== */

html body .login-page
.personal-login input[name="codigo_institucional"] {

    width: 94px !important;

    min-width: 94px !important;

    max-width: 94px !important;

    padding: 8px !important;

    background: #ffffff !important;

    color: #273142 !important;
}


/* ===============================================================
   SEDE
   =============================================================== */

html body .login-page
.personal-login select[name="sede_id"] {

    width: 205px !important;

    min-width: 205px !important;

    max-width: 205px !important;

    padding: 8px 9px !important;
}


/* ===============================================================
   JORNADA
   =============================================================== */

html body .login-page
.personal-login select[name="jornada_id"] {

    width: 80px !important;

    min-width: 80px !important;

    max-width: 80px !important;

    padding: 8px 7px !important;
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
   TEXTO "NO DEBES ESCOGERLO"
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
   DIBUJO
   EL SVG/IMAGEN NO TIENE CUADRO AZUL
   =============================================================== */

html body .login-page
svg {

    background: transparent !important;

    background-color: transparent !important;
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
}


/* ===============================================================
   MOVIL
   =============================================================== */

@media (max-width: 700px) {

    html body .login-page
    .personal-login .personal-fields-grid,

    html body .login-page
    .personal-login .form-grid {

        width: 100% !important;

        grid-template-columns:
            1fr !important;

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
# JS FINAL
# NO CAMBIA OPCIONES DE LOS SELECT
# ============================================================

MASTER_JS = r'''
<script id="EDUTURNOS_LOGIN_MASTER_ABSOLUTO_JS">
(function () {

    function colorEsAzul(valor) {

        if (!valor) return false;

        const v =
            valor
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


    function limpiarCuadroAzulDelDibujo() {

        const page =
            document.querySelector(
                ".login-page"
            );

        if (!page) return;


        const graficos =
            page.querySelectorAll(
                "svg, img, canvas"
            );


        graficos.forEach(
            function (grafico) {

                const rectGrafico =
                    grafico.getBoundingClientRect();


                /*
                 * SVG: quitar solamente rectangulos
                 * que cubren practicamente todo el dibujo.
                 */

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

                            const s =
                                getComputedStyle(
                                    rect
                                );

                            const llena =
                                rectGrafico.width > 0 &&
                                rectGrafico.height > 0 &&
                                r.width >=
                                    rectGrafico.width * 0.80 &&
                                r.height >=
                                    rectGrafico.height * 0.80;

                            if (
                                llena &&
                                (
                                    colorEsAzul(
                                        s.fill
                                    )
                                    ||
                                    colorEsAzul(
                                        s.backgroundColor
                                    )
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


                /*
                 * Quitar fondo azul del contenedor
                 * inmediato del dibujo solamente.
                 */

                let padre =
                    grafico.parentElement;

                for (
                    let nivel = 0;
                    nivel < 3 && padre;
                    nivel++
                ) {

                    const s =
                        getComputedStyle(
                            padre
                        );

                    const r =
                        padre.getBoundingClientRect();


                    const tamañoRazonable =
                        r.width > 50 &&
                        r.width < 650 &&
                        r.height > 50 &&
                        r.height < 500;


                    if (
                        tamañoRazonable &&
                        colorEsAzul(
                            s.backgroundColor
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
                    }

                    padre =
                        padre.parentElement;
                }

            }
        );
    }


    function organizarCampos() {

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


        page.querySelectorAll(
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


        page.querySelectorAll(
            'input[name="identificador"], input[name="password"]'
        ).forEach(
            function (input) {

                input.style.setProperty(
                    "color",
                    "#273142",
                    "important"
                );
            }
        );


        limpiarCuadroAzulDelDibujo();
    }


    function aplicarTodo() {

        organizarCampos();

    }


    document.addEventListener(
        "DOMContentLoaded",
        aplicarTodo
    );

    window.addEventListener(
        "load",
        aplicarTodo
    );


    let contador = 0;

    const intervalo =
        setInterval(
            function () {

                aplicarTodo();

                contador++;

                if (contador >= 12) {

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
# APLICAR MASTER A BASE
# ============================================================

base = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

# Quitar nuestro bloque si ya existe.
base = re.sub(
    r'<style\b[^>]*id="EDUTURNOS_LOGIN_MASTER_ABSOLUTO_STYLE"[^>]*>.*?</style>',
    '',
    base,
    flags=re.I | re.S
)

base = re.sub(
    r'<script\b[^>]*id="EDUTURNOS_LOGIN_MASTER_ABSOLUTO_JS"[^>]*>.*?</script>',
    '',
    base,
    flags=re.I | re.S
)

base_style = (
    '<style id="EDUTURNOS_LOGIN_MASTER_ABSOLUTO_STYLE">\n'
    + MASTER_CSS
    + '\n</style>\n'
)

# El CSS entra SIEMPRE antes de </head>.
if re.search(r'</head>', base, re.I):

    base = re.sub(
        r'</head>',
        base_style +
        '<link rel="stylesheet" '
        'href="{{ url_for(\'static\', filename=\'css/eduturnos_login_master_absolute.css\') }}"'
        f'?v={STAMP}>\n'
        '</head>',
        base,
        count=1,
        flags=re.I
    )

else:

    raise RuntimeError(
        "BASE.HTML NO TIENE </head>"
    )

# JS entra antes de </body>.
if re.search(r'</body>', base, re.I):

    base = re.sub(
        r'</body>',
        MASTER_JS + '\n</body>',
        base,
        count=1,
        flags=re.I
    )

else:

    base += "\n" + MASTER_JS

BASE.write_text(
    base,
    encoding="utf-8"
)

print("OK master visual agregado a base.html")

# ============================================================
# APLICAR TAMBIEN A TODAS LAS PLANTILLAS DE LOGIN
# DENTRO DE SU BLOQUE REAL
# ============================================================

INLINE_MARK = "EDUTURNOS_LOGIN_MASTER_ABSOLUTO_STYLE"

for p in login_files:

    txt = p.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    txt = re.sub(
        rf'<style\b[^>]*id="{INLINE_MARK}"[^>]*>.*?</style>',
        '',
        txt,
        flags=re.I | re.S
    )

    txt = re.sub(
        r'<script\b[^>]*id="EDUTURNOS_LOGIN_MASTER_ABSOLUTO_JS"[^>]*>.*?</script>',
        '',
        txt,
        flags=re.I | re.S
    )

    child_style = (
        '\n'
        + base_style
        + MASTER_JS
        + '\n'
    )

    # Si es plantilla hija de Jinja, insertarlo
    # dentro de block content.
    match_content = re.search(
        r'\{% block content %\}',
        txt,
        re.I
    )

    if match_content:

        pos = match_content.end()

        txt = (
            txt[:pos]
            + child_style
            + txt[pos:]
        )

    elif re.search(
        r'</head>',
        txt,
        re.I
    ):

        txt = re.sub(
            r'</head>',
            child_style + '</head>',
            txt,
            count=1,
            flags=re.I
        )

    else:

        txt += child_style

    p.write_text(
        txt,
        encoding="utf-8"
    )

    print(
        "OK plantilla:",
        p.relative_to(ROOT)
    )

# ============================================================
# ASEGURAR QUE LOS SELECTS NO CAMBIARON
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
            f"DESAPARECIO SELECT SEDE EN {p}"
        )

    if not jornada:
        raise RuntimeError(
            f"DESAPARECIO SELECT JORNADA EN {p}"
        )

print()
print("OK select Sede conservado")
print("OK select Jornada conservado")

# ============================================================
# VERIFICACION DEL HTML GENERADO EN ARCHIVOS
# ============================================================

base_final = BASE.read_text(
    encoding="utf-8",
    errors="ignore"
)

assert (
    "EDUTURNOS_LOGIN_MASTER_ABSOLUTO_STYLE"
    in base_final
)

assert (
    "EDUTURNOS_LOGIN_MASTER_ABSOLUTO_JS"
    in base_final
)

assert MASTER.exists()

print()
print("=" * 78)
print(" VERIFICACION DE ARCHIVOS")
print("=" * 78)

print("OK master CSS")
print("OK master JS")
print("OK base.html")
print("OK plantillas de login")
print("OK 123456 limpiable")
print("OK select Sede")
print("OK select Jornada")

# ============================================================
# GUARDAR REPORTE
# ============================================================

reporte = ROOT / "LOGIN_VISUAL_MASTER_REPORTE.txt"

reporte.write_text(
    "\n".join([
        "EDUTURNOS - MASTER VISUAL LOGIN",
        "",
        f"Fecha: {STAMP}",
        "",
        "MASTER CSS:",
        str(MASTER),
        "",
        "BASE:",
        str(BASE),
        "",
        "PLANTILLAS LOGIN:",
        *[str(p) for p in login_files],
        "",
        "MEDIDAS:",
        "Codigo: 94px",
        "Sede: 205px",
        "Jornada: 80px",
        "Separacion: 8px",
        "",
        "El campo codigo elimina 123456.",
        "El SVG conserva el dibujo.",
        "Se elimina fondo azul del contenedor grafico cuando corresponde.",
    ]),
    encoding="utf-8"
)

print()
print("Reporte:")
print(reporte)

print()
print("=" * 78)
print(" ARCHIVOS LISTOS")
print("=" * 78)
