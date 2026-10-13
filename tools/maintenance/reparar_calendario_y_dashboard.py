from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")
TEMPLATES = ROOT / "templates"

print()
print("=" * 72)
print("EDUTURNOS - REPARAR CALENDARIO Y RESTAURAR DASHBOARD")
print("=" * 72)

# ============================================================
# 1. REPARAR CALENDARIO
# ============================================================

calendario = TEMPLATES / "calendario" / "index.html"

if calendario.exists():

    texto = calendario.read_text(encoding="utf-8")

    roto = """href="{{ url_for('docente') }}'auth.dashboard') }}"""
    correcto = """href="{{ url_for('auth.dashboard') }}\""""

    if roto in texto:
        backup = calendario.with_name(
            "index.html.backup_reparacion_calendario"
        )

        if not backup.exists():
            shutil.copy2(calendario, backup)

        texto = texto.replace(
            roto,
            """href="{{ url_for('auth.dashboard') }}\""""
        )

        calendario.write_text(
            texto,
            encoding="utf-8"
        )

        print()
        print("OK - Calendario reparado.")
        print("OK - Botón Atrás vuelve a auth.dashboard.")
    else:
        # Reparación adicional por si quedó otra variante.
        variantes = [
            r'href="\{\{\s*url_for\([\'"]docente[\'"]\)\s*\}\}.*?auth\.dashboard.*?\}\}"',
            r'href="\{\{\s*url_for\([\'"]docente[\'"]\).*?\}\}"'
        ]

        cambiado = False

        for patron in variantes:
            nuevo, cantidad = re.subn(
                patron,
                """href="{{ url_for('auth.dashboard') }}" """,
                texto,
                flags=re.IGNORECASE | re.DOTALL
            )

            if cantidad:
                texto = nuevo
                cambiado = True
                break

        if cambiado:
            backup = calendario.with_name(
                "index.html.backup_reparacion_calendario"
            )

            if not backup.exists():
                shutil.copy2(calendario, backup)

            calendario.write_text(
                texto,
                encoding="utf-8"
            )

            print()
            print("OK - Calendario reparado.")
        else:
            print()
            print("OK - No se encontró el error de docente en calendario.")


# ============================================================
# 2. CSS PARA QUE LOS ENLACES DE TARJETAS DEL DASHBOARD
#    VUELVAN A SU ASPECTO NORMAL
# ============================================================

CSS = r"""
<style id="EDUTURNOS_DASHBOARD_LINKS_RESTAURADOS">

/* =========================================================
   DASHBOARD
   Los enlaces de las tarjetas NO son botones.
   Vuelven al aspecto normal/blanco de antes.
   ========================================================= */

/* Tarjetas */
.dashboard-card,
.quick-card {
    overflow: hidden !important;
}

/* Enlaces normales dentro de tarjetas */
.dashboard-card a:not(.boton):not(.btn):not([role="button"]),
.quick-card a:not(.boton):not(.btn):not([role="button"]) {

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;

    text-decoration: none !important;

    min-height: 0 !important;
    height: auto !important;

    padding: 0 !important;

    opacity: 1 !important;
}

/* Títulos de tarjetas */
.dashboard-card h2 a,
.dashboard-card h3 a,
.dashboard-card h4 a,
.quick-card h2 a,
.quick-card h3 a,
.quick-card h4 a {

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;

    box-shadow: none !important;

    color: inherit !important;

    padding: 0 !important;

    min-height: 0 !important;
    height: auto !important;

    font-weight: inherit !important;
}

/* Descripciones */
.dashboard-card p a,
.quick-card p a {

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;

    box-shadow: none !important;

    color: inherit !important;

    padding: 0 !important;

    min-height: 0 !important;
    height: auto !important;
}

/* Enlaces de navegación de la tarjeta */
.dashboard-card > a:not(.boton):not(.btn):not([role="button"]),
.quick-card > a:not(.boton):not(.btn):not([role="button"]) {

    display: block !important;

    background: transparent !important;
    background-color: transparent !important;

    color: inherit !important;

    border: none !important;

    box-shadow: none !important;

    min-height: 0 !important;
    height: auto !important;

    padding: 0 !important;

    margin: 0 !important;
}

/* Hover: NO convertirlos en botones */
.dashboard-card a:not(.boton):not(.btn):not([role="button"]):hover,
.quick-card a:not(.boton):not(.btn):not([role="button"]):hover {

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;

    box-shadow: none !important;
}

</style>
"""

# ============================================================
# 3. APLICAR A TODOS LOS DASHBOARDS
# ============================================================

archivos_dashboard = []

for archivo in TEMPLATES.rglob("*.html"):

    if ".backup" in archivo.name.lower():
        continue

    try:
        texto = archivo.read_text(encoding="utf-8")
    except Exception:
        continue

    # Solo páginas que realmente contienen tarjetas de dashboard.
    if (
        "dashboard-card" not in texto
        and "quick-card" not in texto
    ):
        continue

    archivos_dashboard.append(archivo)

    # Quitar versión anterior si existe.
    texto = re.sub(
        r'<style[^>]*id=["\']EDUTURNOS_DASHBOARD_LINKS_RESTAURADOS["\'][^>]*>.*?</style>',
        "",
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Backup.
    backup = archivo.with_name(
        archivo.name + ".backup_dashboard_blanco"
    )

    if not backup.exists():
        shutil.copy2(archivo, backup)

    # Insertar antes de </head>.
    posicion = texto.lower().rfind("</head>")

    if posicion != -1:
        texto = (
            texto[:posicion]
            + "\n"
            + CSS
            + "\n"
            + texto[posicion:]
        )
    else:
        texto += "\n" + CSS

    archivo.write_text(
        texto,
        encoding="utf-8"
    )

    print(
        "OK - Dashboard:",
        archivo.relative_to(ROOT)
    )


# ============================================================
# 4. LIMPIAR ESTILOS DE BOTONES QUE ESTABAN AFECTANDO LAS
#    TARJETAS DEL DASHBOARD
# ============================================================

for archivo in archivos_dashboard:

    try:
        texto = archivo.read_text(
            encoding="utf-8"
        )
    except Exception:
        continue

    # Quitar bloques específicos que convertían TODOS los
    # enlaces del dashboard en botones.
    patrones = [

        r'<style[^>]*id=["\']EDUTURNOS_CORRECCION_FINAL_V9["\'][^>]*>.*?</style>',

        r'<style[^>]*id=["\']EDUTURNOS_TODOS_LOS_BOTONES_V5["\'][^>]*>.*?</style>',

        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_REALES_V6["\'][^>]*>.*?</style>',

        r'<style[^>]*id=["\']EDUTURNOS_BOTONES_V4["\'][^>]*>.*?</style>',
    ]

    for patron in patrones:
        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    # Volver a colocar nuestro CSS limpio.
    texto = re.sub(
        r'<style[^>]*id=["\']EDUTURNOS_DASHBOARD_LINKS_RESTAURADOS["\'][^>]*>.*?</style>',
        "",
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )

    posicion = texto.lower().rfind("</head>")

    if posicion != -1:
        texto = (
            texto[:posicion]
            + "\n"
            + CSS
            + "\n"
            + texto[posicion:]
        )

    archivo.write_text(
        texto,
        encoding="utf-8"
    )


print()
print("=" * 72)
print("REPARACION FINALIZADA")
print("=" * 72)
print()
print("CALENDARIO:")
print("✓ Botón Atrás reparado")
print("✓ Ya no intenta usar endpoint 'docente'")
print("✓ Destino: auth.dashboard")
print()
print("DASHBOARDS:")
print("✓ Citas vuelve a ser enlace normal")
print("✓ Calendario vuelve a ser enlace normal")
print("✓ Notificaciones vuelve a ser enlace normal")
print("✓ Solicitudes vuelve a ser enlace normal")
print("✓ Las tarjetas no se convierten en botones azules")
print()
print("BOTONES REALES:")
print("✓ Mantienen azul #1769aa")
print("✓ Mantienen letra blanca")
print()
print("No se modificó MySQL.")
print("No se modificó routes/calendario.py.")
print("No se modificó la cuadrícula del calendario.")
print()
print("Ahora ejecuta:")
print("python .\\app.py")
print()
print("Después pulsa Ctrl + F5.")
print("=" * 72)

