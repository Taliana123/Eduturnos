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
CSS = CSSDIR / "estilos.css"
FINALCSS = CSSDIR / "eduturnos_final_real.css"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

print()
print("=" * 72)
print(" EDUTURNOS - REPARACION VISUAL REAL")
print("=" * 72)
print()

for f in (LOGIN, BASE, DASH, DASHBACK, CSSDIR):
    if not f.exists():
        raise FileNotFoundError(f"NO EXISTE: {f}")

# ============================================================
# BACKUPS
# ============================================================

login_bak = LOGIN.with_name(LOGIN.name + f".BACKUP_REAL_{STAMP}.bak")
base_bak = BASE.with_name(BASE.name + f".BACKUP_REAL_{STAMP}.bak")
dash_bak = DASH.with_name(DASH.name + f".BACKUP_REAL_{STAMP}.bak")
css_bak = CSS.with_name(CSS.name + f".BACKUP_REAL_{STAMP}.bak")

shutil.copy2(LOGIN, login_bak)
shutil.copy2(BASE, base_bak)
shutil.copy2(DASH, dash_bak)
shutil.copy2(CSS, css_bak)

print("OK backups creados")

# ============================================================
# RESTAURAR DASHBOARD EXACTAMENTE
# ============================================================

shutil.copy2(DASHBACK, DASH)

if DASH.read_bytes() != DASHBACK.read_bytes():
    raise RuntimeError(
        "El dashboard restaurado no coincide con dashboard.html.backup_solo_interno"
    )

print("OK dashboard.html restaurado exactamente")

# ============================================================
# LEER
# ============================================================

login = LOGIN.read_text(encoding="utf-8")
base = BASE.read_text(encoding="utf-8")
css = CSS.read_text(encoding="utf-8")

# ============================================================
# COMPROBAR ESTRUCTURA ORIGINAL DEL LOGIN
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

for x in required:
    if x not in login:
        raise RuntimeError(f"FALTA EN LOGIN: {x}")

# ============================================================
# GUARDAR SELECTS ORIGINALES
# ============================================================

sede_match = re.search(
    r'<select\b[^>]*name\s*=\s*"sede_id"[^>]*>.*?</select>',
    login,
    re.I | re.S,
)

jornada_match = re.search(
    r'<select\b[^>]*name\s*=\s*"jornada_id"[^>]*>.*?</select>',
    login,
    re.I | re.S,
)

if not sede_match:
    raise RuntimeError("No se encontró el SELECT original de Sede")

if not jornada_match:
    raise RuntimeError("No se encontró el SELECT original de Jornada")

sede_original = sede_match.group(0)
jornada_original = jornada_match.group(0)

# ============================================================
# CORREGIR SOLAMENTE ESCOGERLO
# ============================================================

replacements = {
    'No debes escogerlo-limpio">escogerlo.': "No debes escogerlo.",
    'escogerlo-limpio">escogerlo.': "escogerlo.",
    'No debes escogerlo-limpio">': "No debes escogerlo.",
    "No debes escogerlo-limpio": "No debes escogerlo.",
}

for old, new in replacements.items():
    login = login.replace(old, new)

login = re.sub(
    r'No debes escogerlo[^<]{0,100}escogerlo\.',
    "No debes escogerlo.",
    login,
)

# ============================================================
# QUITAR BLOQUES FINALES DE INTENTOS ANTERIORES
# ============================================================

old_style_ids = [
    "EDUTURNOS_CAMBIO_EXACTO",
    "EDUTURNOS_FORZADO_FINAL",
    "EDUTURNOS_MASTER_VISUAL_FINAL",
    "EDUTURNOS_VISUAL_FINAL",
    "EDUTURNOS_LOGIN_MASTER",
    "EDUTURNOS_LOGIN_REAL_FINAL",
    "EDUTURNOS_UNIFICADO_LOGIN_REGISTRO_2026",
]

for sid in old_style_ids:
    login = re.sub(
        rf'<style\b[^>]*id="{re.escape(sid)}"[^>]*>.*?</style>',
        "",
        login,
        flags=re.I | re.S,
    )

old_script_ids = [
    "EDUTURNOS_LINEA_DIBUJO",
    "EDUTURNOS_FORZADO_FINAL_SCRIPT",
    "EDUTURNOS_LINEA_DIBUJO_FINAL",
    "EDUTURNOS_VISUAL_FINAL_SCRIPT",
    "EDUTURNOS_LOGIN_APPLY_FINAL",
    "EDUTURNOS_LOGIN_REAL_FINAL_SCRIPT",
]

for sid in old_script_ids:
    login = re.sub(
        rf'<script\b[^>]*id="{re.escape(sid)}"[^>]*>.*?</script>',
        "",
        login,
        flags=re.I | re.S,
    )

# ============================================================
# CSS FINAL
# ============================================================

final_css = r"""
/* =================================================================
   EDUTURNOS - FINAL REAL
   Este archivo se carga despues de estilos.css
   ================================================================= */

/* ================================================================
   LOGIN - CAMPOS REALES
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
   TRES CAMPOS JUNTOS
   ================================================================ */

html body
.personal-fields-grid,

html body
.personal-login .form-grid {

    display: grid !important;

    grid-template-columns:
        112px
        255px
        100px !important;

    column-gap: 10px !important;
    row-gap: 0 !important;

    align-items: end !important;
    justify-content: center !important;
}

/* ================================================================
   TITULOS CENTRADOS
   ================================================================ */

html body
.personal-fields-grid
.personal-field-title,

html body
.personal-login
.personal-field-title {

    display: block !important;

    width: 100% !important;

    text-align: center !important;
}

/* ================================================================
   CODIGO
   ================================================================ */

html body
input[name="codigo_institucional"] {

    width: 112px !important;

    min-width: 112px !important;

    max-width: 112px !important;

    box-sizing: border-box !important;
}

/* ================================================================
   SEDE
   ================================================================ */

html body
select[name="sede_id"] {

    width: 255px !important;

    min-width: 255px !important;

    max-width: 255px !important;

    box-sizing: border-box !important;
}

/* ================================================================
   JORNADA
   ================================================================ */

html body
select[name="jornada_id"] {

    width: 100px !important;

    min-width: 100px !important;

    max-width: 100px !important;

    box-sizing: border-box !important;
}

/* ================================================================
   NO DEBES ESCOGERLO
   ================================================================ */

html body
.section-heading p,

html body
.section-heading p *,

html body
.section-heading strong,

html body
.section-heading span {

    border: 0 !important;

    border-bottom: 0 !important;

    text-decoration: none !important;

    box-shadow: none !important;

    background-image: none !important;
}

html body
.section-heading::before,

html body
.section-heading::after {

    content: none !important;

    display: none !important;

    border: 0 !important;

    box-shadow: none !important;

    background-image: none !important;
}

/* ================================================================
   DASHBOARD
   DETENER ANIMACIONES SIN CAMBIAR SU CONTENIDO
   ================================================================ */

html body .ed-dashboard,
html body .ed-dashboard * {

    animation: none !important;

    animation-name: none !important;

    animation-duration: 0s !important;

    animation-delay: 0s !important;
}

/* Pseudo-elementos usados por brillos */

html body .ed-dashboard::before,
html body .ed-dashboard::after,
html body .ed-dashboard *::before,
html body .ed-dashboard *::after {

    animation: none !important;
}

/* ================================================================
   FIN
   ================================================================ */
"""

FINALCSS.write_text(final_css.strip() + "\n", encoding="utf-8")

# ============================================================
# AGREGAR CSS DIRECTAMENTE AL LOGIN
# ============================================================

login_inline = r"""
<style id="EDUTURNOS_LOGIN_FINAL_DIRECT">
html body input[name="identificador"],
html body input[name="password"] {
    color:#273142 !important;
    caret-color:#273142 !important;
}

html body label:has(input[name="identificador"]),
html body label:has(input[name="password"]),
html body label:has(input[name="identificador"]) *,
html body label:has(input[name="password"]) * {
    color:#273142 !important;
}

html body .personal-fields-grid,
html body .personal-login .form-grid {
    display:grid !important;
    grid-template-columns:112px 255px 100px !important;
    column-gap:10px !important;
    row-gap:0 !important;
    align-items:end !important;
    justify-content:center !important;
}

html body .personal-field-title {
    display:block !important;
    width:100% !important;
    text-align:center !important;
}

html body input[name="codigo_institucional"] {
    width:112px !important;
    min-width:112px !important;
    max-width:112px !important;
}

html body select[name="sede_id"] {
    width:255px !important;
    min-width:255px !important;
    max-width:255px !important;
}

html body select[name="jornada_id"] {
    width:100px !important;
    min-width:100px !important;
    max-width:100px !important;
}

html body .section-heading p,
html body .section-heading p *,
html body .section-heading strong,
html body .section-heading span {
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
</style>
"""

login = re.sub(
    r'<style\b[^>]*id="EDUTURNOS_LOGIN_FINAL_DIRECT"[^>]*>.*?</style>',
    "",
    login,
    flags=re.I | re.S,
)

# Colocarlo al final del contenido, antes de endblock.
if re.search(r"\{% endblock %\}", login, re.I):
    login = re.sub(
        r"\{% endblock %\}",
        login_inline + "\n{% endblock %}",
        login,
        count=1,
        flags=re.I,
    )
else:
    login += "\n" + login_inline

# ============================================================
# JS FINAL
# ============================================================

js = r"""
<script id="EDUTURNOS_VISUAL_REAL_SCRIPT">
(function () {

    function medirTexto(elemento, texto, extra) {

        if (!elemento) return;

        const canvas =
            document.createElement("canvas");

        const ctx =
            canvas.getContext("2d");

        const cs =
            window.getComputedStyle(elemento);

        ctx.font =
            cs.font ||
            (
                cs.fontSize +
                " " +
                cs.fontFamily
            );

        const width =
            Math.ceil(
                ctx.measureText(texto).width
            ) + extra;

        elemento.style.setProperty(
            "width",
            width + "px",
            "important"
        );

        elemento.style.setProperty(
            "min-width",
            width + "px",
            "important"
        );

        elemento.style.setProperty(
            "max-width",
            width + "px",
            "important"
        );
    }


    function aplicarLogin() {

        const identificador =
            document.querySelector(
                'input[name="identificador"]'
            );

        const password =
            document.querySelector(
                'input[name="password"]'
            );

        [identificador, password].forEach(
            function (input) {

                if (!input) return;

                input.style.setProperty(
                    "color",
                    "#273142",
                    "important"
                );

                const label =
                    input.closest("label");

                if (label) {

                    label.style.setProperty(
                        "color",
                        "#273142",
                        "important"
                    );
                }
            }
        );


        const codigo =
            document.querySelector(
                'input[name="codigo_institucional"]'
            );

        if (codigo) {

            const cs =
                getComputedStyle(codigo);

            const canvas =
                document.createElement("canvas");

            const ctx =
                canvas.getContext("2d");

            ctx.font =
                cs.font ||
                (
                    cs.fontSize +
                    " " +
                    cs.fontFamily
                );

            const six =
                Math.ceil(
                    ctx.measureText("000000").width
                );

            const width =
                six + 18;

            codigo.style.setProperty(
                "width",
                width + "px",
                "important"
            );

            codigo.style.setProperty(
                "min-width",
                width + "px",
                "important"
            );

            codigo.style.setProperty(
                "max-width",
                width + "px",
                "important"
            );
        }


        const sede =
            document.querySelector(
                'select[name="sede_id"]'
            );

        if (sede) {

            let texto =
                "Sede Principal (Las Américas)";

            for (
                let i = 0;
                i < sede.options.length;
                i++
            ) {

                const t =
                    sede.options[i]
                        .textContent
                        .trim();

                if (
                    t.toLowerCase()
                        .includes("sede principal")
                ) {

                    texto = t;
                    break;
                }
            }

            medirTexto(
                sede,
                texto,
                42
            );
        }


        const jornada =
            document.querySelector(
                'select[name="jornada_id"]'
            );

        if (jornada) {

            let texto =
                "Normal";

            for (
                let i = 0;
                i < jornada.options.length;
                i++
            ) {

                const t =
                    jornada.options[i]
                        .textContent
                        .trim();

                if (
                    t.toLowerCase() === "normal"
                ) {

                    texto = t;
                    break;
                }
            }

            medirTexto(
                jornada,
                texto,
                42
            );
        }


        const grids =
            document.querySelectorAll(
                ".personal-fields-grid, .personal-login .form-grid"
            );

        grids.forEach(
            function (grid) {

                grid.style.setProperty(
                    "display",
                    "grid",
                    "important"
                );

                grid.style.setProperty(
                    "grid-template-columns",
                    "112px 255px 100px",
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
        );


        document.querySelectorAll(
            ".personal-field-title"
        ).forEach(
            function (titulo) {

                titulo.style.setProperty(
                    "text-align",
                    "center",
                    "important"
                );
            }
        );


        /*
         * No debes escogerlo.
         */
        document.querySelectorAll(
            ".section-heading p"
        ).forEach(
            function (p) {

                if (
                    p.textContent
                        .toLowerCase()
                        .includes("no debes escogerlo")
                ) {

                    p.style.setProperty(
                        "border",
                        "0",
                        "important"
                    );

                    p.style.setProperty(
                        "border-bottom",
                        "0",
                        "important"
                    );

                    p.style.setProperty(
                        "text-decoration",
                        "none",
                        "important"
                    );

                    p.style.setProperty(
                        "box-shadow",
                        "none",
                        "important"
                    );
                }
            }
        );


        /*
         * Linea blanca fina del dibujo.
         */
        const page =
            document.querySelector(
                ".login-page"
            );

        if (!page) return;

        function white(value) {

            if (!value) return false;

            const v =
                value
                    .toLowerCase()
                    .replace(/\s/g, "");

            return (
                v === "#fff" ||
                v === "#ffffff" ||
                v === "white" ||
                v === "rgb(255,255,255)" ||
                v === "rgba(255,255,255,1)"
            );
        }

        const grafica =
            page.querySelectorAll(
                "svg, canvas, img"
            );

        grafica.forEach(
            function (grafico) {

                const container =
                    grafico.parentElement;

                if (!container) return;

                container
                    .querySelectorAll(
                        "line,hr,div,span,rect,path"
                    )
                    .forEach(
                        function (el) {

                            if (
                                el.matches(
                                    "input,select,textarea,button"
                                )
                            ) {
                                return;
                            }

                            const r =
                                el.getBoundingClientRect();

                            const s =
                                getComputedStyle(el);

                            if (
                                r.width < 70 ||
                                r.height > 5
                            ) {
                                return;
                            }

                            const isWhite =
                                white(
                                    s.backgroundColor
                                ) ||
                                white(
                                    s.borderTopColor
                                ) ||
                                white(
                                    s.borderBottomColor
                                ) ||
                                white(
                                    s.stroke
                                );

                            if (isWhite) {

                                el.style.setProperty(
                                    "display",
                                    "none",
                                    "important"
                                );

                                el.style.setProperty(
                                    "visibility",
                                    "hidden",
                                    "important"
                                );
                            }
                        }
                    );
            }
        );
    }


    function quitarAnimacionDashboard() {

        const dashboard =
            document.querySelector(
                ".ed-dashboard"
            );

        if (!dashboard) return;

        dashboard.querySelectorAll("*")
            .forEach(
                function (el) {

                    const cs =
                        getComputedStyle(el);

                    if (
                        cs.animationName &&
                        cs.animationName !== "none"
                    ) {

                        el.style.setProperty(
                            "animation",
                            "none",
                            "important"
                        );

                        el.style.setProperty(
                            "animation-name",
                            "none",
                            "important"
                        );
                    }
                }
            );
    }


    function ejecutar() {

        aplicarLogin();
        quitarAnimacionDashboard();
    }


    document.addEventListener(
        "DOMContentLoaded",
        ejecutar
    );

    window.addEventListener(
        "load",
        ejecutar
    );

    setTimeout(ejecutar, 150);
    setTimeout(ejecutar, 500);
    setTimeout(ejecutar, 1000);

})();
</script>
"""

login = re.sub(
    r'<script\b[^>]*id="EDUTURNOS_VISUAL_REAL_SCRIPT"[^>]*>.*?</script>',
    "",
    login,
    flags=re.I | re.S,
)

if re.search(r"\{% endblock %\}", login, re.I):
    login = re.sub(
        r"\{% endblock %\}",
        js + "\n{% endblock %}",
        login,
        count=1,
        flags=re.I,
    )
else:
    login += "\n" + js

# ============================================================
# COMPROBAR SELECTS ANTES DE GUARDAR
# ============================================================

sede_after = re.search(
    r'<select\b[^>]*name\s*=\s*"sede_id"[^>]*>.*?</select>',
    login,
    re.I | re.S,
)

jornada_after = re.search(
    r'<select\b[^>]*name\s*=\s*"jornada_id"[^>]*>.*?</select>',
    login,
    re.I | re.S,
)

if not sede_after:
    raise RuntimeError("DESAPARECIO SELECT SEDE. NO SE GUARDA.")

if not jornada_after:
    raise RuntimeError("DESAPARECIO SELECT JORNADA. NO SE GUARDA.")

if sede_after.group(0) != sede_original:
    raise RuntimeError(
        "CAMBIO EL HTML/OPCIONES DE SEDE. NO SE GUARDA."
    )

if jornada_after.group(0) != jornada_original:
    raise RuntimeError(
        "CAMBIO EL HTML/OPCIONES DE JORNADA. NO SE GUARDA."
    )

# ============================================================
# ESCRIBIR LOGIN
# ============================================================

LOGIN.write_text(login, encoding="utf-8")

# ============================================================
# BASE.HTML
# EL CSS FINAL VA DIRECTAMENTE DESPUES DE LOS CSS NORMALES
# ============================================================

base = re.sub(
    r'<link\b[^>]*eduturnos_final_real\.css[^>]*>',
    "",
    base,
    flags=re.I,
)

final_link = (
    '<link rel="stylesheet" '
    'href="{{ url_for(\'static\', filename=\'css/eduturnos_final_real.css\') }}'
    f'?v={STAMP}">'
)

# ============================================================
# BLOQUE BASE INLINE
# ============================================================

base_inline = r"""
<style id="EDUTURNOS_BASE_VISUAL_FINAL">

/* =========================================================
   LOGIN FINAL DIRECTO
   ========================================================= */

html body input[name="identificador"],
html body input[name="password"] {
    color:#273142 !important;
}

html body label:has(input[name="identificador"]),
html body label:has(input[name="password"]),
html body label:has(input[name="identificador"]) *,
html body label:has(input[name="password"]) * {
    color:#273142 !important;
}

html body
.personal-fields-grid,
html body
.personal-login .form-grid {
    display:grid !important;
    grid-template-columns:112px 255px 100px !important;
    column-gap:10px !important;
    row-gap:0 !important;
    align-items:end !important;
    justify-content:center !important;
}

html body
.personal-field-title {
    display:block !important;
    text-align:center !important;
    width:100% !important;
}

html body
input[name="codigo_institucional"] {
    width:112px !important;
    min-width:112px !important;
    max-width:112px !important;
}

html body
select[name="sede_id"] {
    width:255px !important;
    min-width:255px !important;
    max-width:255px !important;
}

html body
select[name="jornada_id"] {
    width:100px !important;
    min-width:100px !important;
    max-width:100px !important;
}

html body
.section-heading p,
html body
.section-heading p *,
html body
.section-heading strong,
html body
.section-heading span {
    border:0 !important;
    border-bottom:0 !important;
    text-decoration:none !important;
    box-shadow:none !important;
    background-image:none !important;
}

html body
.section-heading::before,
html body
.section-heading::after {
    content:none !important;
    display:none !important;
}

/* =========================================================
   DASHBOARD SIN ANIMACION EXTERIOR
   ========================================================= */

html body .ed-dashboard,
html body .ed-dashboard * {
    animation:none !important;
    animation-name:none !important;
    animation-duration:0s !important;
    animation-delay:0s !important;
}

</style>
"""

base = re.sub(
    r'<style\b[^>]*id="EDUTURNOS_BASE_VISUAL_FINAL"[^>]*>.*?</style>',
    "",
    base,
    flags=re.I | re.S,
)

if re.search(r"</head>", base, re.I):
    base = re.sub(
        r"</head>",
        base_inline + "\n" + final_link + "\n</head>",
        base,
        count=1,
        flags=re.I,
    )
else:
    raise RuntimeError("base.html no tiene </head>")

BASE.write_text(base, encoding="utf-8")

# ============================================================
# REESCRIBIR ESTILOS.CSS SIN TOCAR SU CONTENIDO EXISTENTE
# SOLO AGREGAR REFERENCIA CLARA AL MASTER
# ============================================================

master_comment = (
    "/* EDUTURNOS MASTER FINAL "
    f"{STAMP} */"
)

if master_comment not in css:
    css = (
        css.rstrip()
        + "\n\n"
        + master_comment
        + "\n"
        + "/* El archivo eduturnos_final_real.css es el override final. */\n"
    )

    CSS.write_text(css, encoding="utf-8")

# ============================================================
# VERIFICACIONES
# ============================================================

final_login = LOGIN.read_text(encoding="utf-8")
final_base = BASE.read_text(encoding="utf-8")
final_dash = DASH.read_text(encoding="utf-8")

checks = {
    "Documento/correo": 'name="identificador"' in final_login,
    "Contraseña": 'name="password"' in final_login,
    "Codigo": 'name="codigo_institucional"' in final_login,
    "Sede": 'name="sede_id"' in final_login,
    "Jornada": 'name="jornada_id"' in final_login,
    "CSRF": "csrf_field" in final_login,
    "Recuperar": "passwords.recuperar" in final_login,
    "Registro": "auth.registro" in final_login,
    "Escogerlo corregido": "escogerlo-limpio\">" not in final_login,
    "CSS final": FINALCSS.exists(),
    "CSS cargado por base": "eduturnos_final_real.css" in final_base,
    "JS final": "EDUTURNOS_VISUAL_REAL_SCRIPT" in final_login,
    "Dashboard exacto": final_dash == DASHBACK.read_text(encoding="utf-8"),
    "Sede intacta": sede_original in final_login,
    "Jornada intacta": jornada_original in final_login,
}

print()
print("=" * 72)
print(" VERIFICACION")
print("=" * 72)

for name, ok in checks.items():
    print(("OK  " if ok else "ERROR ") + name)

print()
print("CSS FINAL:")
print(FINALCSS)

print()
print("BACKUPS:")
print(login_bak)
print(base_bak)
print(dash_bak)
print(css_bak)

if not all(checks.values()):
    raise RuntimeError("La verificacion final no paso completamente.")

print()
print("=" * 72)
print(" TODO ESCRITO CORRECTAMENTE")
print("=" * 72)
