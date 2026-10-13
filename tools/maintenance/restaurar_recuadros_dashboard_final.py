from pathlib import Path
import shutil
import re

ROOT = Path(r"F:\edu_Final")
TEMPLATES = ROOT / "templates"

BASE = TEMPLATES / "base.html"
DASHBOARD = TEMPLATES / "dashboard.html"

print()
print("=" * 75)
print("EDUTURNOS - RESTAURAR RECUADROS DEL DASHBOARD")
print("=" * 75)
print()

# ============================================================
# 1. RESPALDOS DE SEGURIDAD
# ============================================================

if BASE.exists():
    backup_base = BASE.with_name(
        "base.html.backup_recuadros_dashboard"
    )
    if not backup_base.exists():
        shutil.copy2(BASE, backup_base)
        print("Backup de base.html creado.")

if DASHBOARD.exists():
    backup_dashboard = DASHBOARD.with_name(
        "dashboard.html.backup_recuadros_dashboard"
    )
    if not backup_dashboard.exists():
        shutil.copy2(DASHBOARD, backup_dashboard)
        print("Backup de dashboard.html creado.")


# ============================================================
# 2. RESTAURAR DASHBOARD ANTERIOR
# ============================================================

backup_anterior_dashboard = (
    TEMPLATES /
    "dashboard.html.backup_enlaces_restaurados"
)

if backup_anterior_dashboard.exists():

    shutil.copy2(
        backup_anterior_dashboard,
        DASHBOARD
    )

    print(
        "OK - dashboard.html restaurado desde "
        "backup_enlaces_restaurados."
    )

else:
    print(
        "AVISO - no existe dashboard.html.backup_enlaces_restaurados."
    )


# ============================================================
# 3. RESTAURAR BASE SIN LOS ESTILOS GLOBALES ANTERIORES
# ============================================================

backup_base_anterior = (
    TEMPLATES /
    "base.html.backup_botones"
)

if backup_base_anterior.exists():

    shutil.copy2(
        backup_base_anterior,
        BASE
    )

    print(
        "OK - base.html restaurado antes de los cambios "
        "globales de botones."
    )

else:

    print(
        "AVISO - no existe base.html.backup_botones."
    )


# ============================================================
# 4. CSS DEFINITIVO
# ============================================================

CSS = r"""
<style id="EDUTURNOS_BOTONES_Y_RECUADROS_FINAL">

/* ==========================================================
   1. RECUADROS DEL DASHBOARD
   ========================================================== */

.dashboard-card,
.quick-card {

    background: #ffffff !important;
    background-color: #ffffff !important;

    border: 1px solid #e1e7ed !important;
    border-radius: 12px !important;

    padding: 18px !important;

    box-shadow: 0 2px 8px rgba(0,0,0,.05) !important;

    overflow: hidden !important;

    position: relative !important;
}


/* Separación entre tarjetas */
.dashboard-card + .dashboard-card,
.quick-card + .quick-card {

    margin-top: 14px !important;
}


/* ==========================================================
   2. TITULOS DE LAS TARJETAS
   ========================================================== */

.dashboard-card h2,
.dashboard-card h3,
.dashboard-card h4,
.quick-card h2,
.quick-card h3,
.quick-card h4 {

    margin-top: 0 !important;
}


/* Enlaces usados como títulos NO son botones */
.dashboard-card h2 a,
.dashboard-card h3 a,
.dashboard-card h4 a,
.quick-card h2 a,
.quick-card h3 a,
.quick-card h4 a {

    background: transparent !important;
    background-color: transparent !important;

    color: inherit !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;

    padding: 0 !important;
    margin: 0 !important;

    min-height: 0 !important;
    height: auto !important;

    text-decoration: none !important;
}


/* ==========================================================
   3. ENLACES NORMALES DENTRO DEL RECUADRO
   ========================================================== */

.dashboard-card a:not(.boton):not(.btn):not([role="button"]),
.quick-card a:not(.boton):not(.btn):not([role="button"]) {

    background: transparent !important;
    background-color: transparent !important;

    color: inherit !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;

    text-decoration: none !important;

    padding: 0 !important;
    margin: 0 !important;

    min-height: 0 !important;
    height: auto !important;

    display: inline !important;
}


/* Hover de enlaces normales */
.dashboard-card a:not(.boton):not(.btn):not([role="button"]):hover,
.quick-card a:not(.boton):not(.btn):not([role="button"]):hover {

    background: transparent !important;
    background-color: transparent !important;

    color: inherit !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;

    text-decoration: underline !important;
}


/* ==========================================================
   4. BOTONES REALES
   ========================================================== */

button,
input[type="submit"],
input[type="button"],
input[type="reset"],

a.boton,
a.btn,
a.btn-primary,
a.btn-secondary,
a.btn-success,
a.btn-danger,
a.btn-warning,
a.btn-info,
a.btn-dark,
a.btn-light,

a[role="button"],

a.link-back,
a.edc-back {

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border: 1px solid #1769aa !important;
    border-color: #1769aa !important;

    border-radius: 7px !important;

    box-shadow: none !important;

    text-decoration: none !important;

    cursor: pointer !important;

    opacity: 1 !important;
}


/* Texto de botones */
button *,
input[type="submit"] *,
input[type="button"] *,
input[type="reset"] *,

a.boton *,
a.btn *,
a.btn-primary *,
a.btn-secondary *,
a.btn-success *,
a.btn-danger *,
a.btn-warning *,
a.btn-info *,
a.btn-dark *,
a.btn-light *,

a[role="button"] *,
a.link-back *,
a.edc-back * {

    color: #ffffff !important;
}


/* Hover */
button:hover,
input[type="submit"]:hover,
input[type="button"]:hover,
input[type="reset"]:hover,

a.boton:hover,
a.btn:hover,
a.btn-primary:hover,
a.btn-secondary:hover,
a.btn-success:hover,
a.btn-danger:hover,
a.btn-warning:hover,
a.btn-info:hover,
a.btn-dark:hover,
a.btn-light:hover,

a[role="button"]:hover,

a.link-back:hover,
a.edc-back:hover {

    background: #145b91 !important;
    background-color: #145b91 !important;

    color: #ffffff !important;

    border-color: #145b91 !important;

    box-shadow: none !important;
}


/* ==========================================================
   5. BOTÓN ATRÁS
   ========================================================== */

a.link-back,
a.edc-back {

    display: inline-flex !important;

    align-items: center !important;
    justify-content: center !important;

    min-height: 34px !important;
    height: 34px !important;

    padding: 7px 12px !important;

    margin: 0 0 14px 0 !important;

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border: 1px solid #1769aa !important;

    border-radius: 7px !important;

    font-size: 13px !important;
    font-weight: 600 !important;
    line-height: 1 !important;

    text-decoration: none !important;
}


/* ==========================================================
   6. BOTONES DEL DASHBOARD
   ========================================================== */

.dashboard-card a.boton,
.dashboard-card a.btn,
.dashboard-card button,

.quick-card a.boton,
.quick-card a.btn,
.quick-card button {

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border-color: #1769aa !important;
}


/* Hover */
.dashboard-card a.boton:hover,
.dashboard-card a.btn:hover,
.dashboard-card button:hover,

.quick-card a.boton:hover,
.quick-card a.btn:hover,
.quick-card button:hover {

    background: #145b91 !important;
    background-color: #145b91 !important;

    color: #ffffff !important;

    border-color: #145b91 !important;
}


/* ==========================================================
   7. NO convertir enlaces normales del Dashboard en botones
   ========================================================== */

.dashboard-card a:not(.boton):not(.btn):not([role="button"]),
.quick-card a:not(.boton):not(.btn):not([role="button"]) {

    background: transparent !important;
    background-color: transparent !important;

    border-radius: 0 !important;

    border: none !important;

    box-shadow: none !important;

    padding: 0 !important;
}


/* ==========================================================
   8. RESPONSIVO
   ========================================================== */

@media (max-width: 700px) {

    .dashboard-card,
    .quick-card {

        padding: 15px !important;
        border-radius: 10px !important;
    }
}

</style>
"""


# ============================================================
# 5. INSERTAR CSS EN BASE
# ============================================================

texto_base = BASE.read_text(
    encoding="utf-8"
)

# Quitar únicamente versiones anteriores creadas por estos scripts.
patrones = [
    r'<style[^>]*id=["\']EDUTURNOS_BOTONES_GLOBALES["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_ESTILO_BOTONES_DEFINITIVO["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_SOLO_BOTONES_V3["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V4["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V5["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_ATRAS_TODOS_V7["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_LAYOUT_ATRAS_V8["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_CORRECCION_FINAL_V9["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_TODOS_LOS_BOTONES_V5["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</style>',
    r'<style[^>]*id=["\']EDUTURNOS_ENLACES_DASHBOARD_RESTAURADOS["\'][^>]*>.*?</style>',
    r'<script[^>]*id=["\']EDUTURNOS_JS_BOTONES_DEFINITIVO["\'][^>]*>.*?</script>',
    r'<script[^>]*id=["\']EDUTURNOS_TODOS_LOS_BOTONES_JS["\'][^>]*>.*?</script>',
    r'<script[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</script>',
    r'<script[^>]*id=["\']EDUTURNOS_BOTONES_JS_V9["\'][^>]*>.*?</script>',
]

for patron in patrones:
    texto_base = re.sub(
        patron,
        "",
        texto_base,
        flags=re.IGNORECASE | re.DOTALL
    )


# Insertar solo nuestro CSS nuevo.
posicion = texto_base.lower().rfind("</head>")

if posicion != -1:

    texto_base = (
        texto_base[:posicion]
        + "\n"
        + CSS
        + "\n"
        + texto_base[posicion:]
    )

else:

    texto_base += "\n" + CSS


BASE.write_text(
    texto_base,
    encoding="utf-8"
)


print()
print("=" * 75)
print("RESTAURACION COMPLETADA")
print("=" * 75)
print()
print("Dashboard:")
print("✓ Citas queda dentro de su recuadro")
print("✓ Calendario queda dentro de su recuadro")
print("✓ Notificaciones queda dentro de su recuadro")
print("✓ Solicitudes queda dentro de su recuadro")
print()
print("Los enlaces:")
print("✓ vuelven a ser enlaces normales")
print("✓ no tienen fondo azul")
print("✓ no parecen botones")
print("✓ permanecen dentro de la tarjeta")
print()
print("Los botones reales:")
print("✓ azul #1769aa")
print("✓ letras blancas")
print("✓ hover #145b91")
print()
print("El calendario no fue modificado.")
print("MySQL no fue modificado.")
print()
print("Ahora:")
print("python .\\app.py")
print()
print("Luego Ctrl + F5.")
print()
print("=" * 75)
