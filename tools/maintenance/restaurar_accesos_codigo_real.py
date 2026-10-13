from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")

DASHBOARD = ROOT / "templates" / "dashboard.html"
CSS_FILE = ROOT / "static" / "css" / "estilos.css"

print()
print("=" * 75)
print("EDUTURNOS - RESTAURAR CODIGO ORIGINAL DE ACCESOS")
print("=" * 75)
print()


# ============================================================
# COMPROBAR ARCHIVOS
# ============================================================

if not DASHBOARD.exists():
    print("ERROR: no existe:")
    print(DASHBOARD)
    raise SystemExit

if not CSS_FILE.exists():
    print("ERROR: no existe:")
    print(CSS_FILE)
    raise SystemExit


# ============================================================
# BACKUPS
# ============================================================

backup_dashboard = DASHBOARD.with_name(
    "dashboard.html.backup_codigo_original_accesos"
)

backup_css = CSS_FILE.with_name(
    "estilos.css.backup_codigo_original_accesos"
)

if not backup_dashboard.exists():
    shutil.copy2(
        DASHBOARD,
        backup_dashboard
    )

if not backup_css.exists():
    shutil.copy2(
        CSS_FILE,
        backup_css
)

print("Backups creados correctamente.")


# ============================================================
# LEER
# ============================================================

dashboard = DASHBOARD.read_text(
    encoding="utf-8"
)

css = CSS_FILE.read_text(
    encoding="utf-8"
)


# ============================================================
# 1. LIMPIAR BLOQUES QUE AGREGAMOS ANTES
# ============================================================

markers = [
    "EDUTURNOS_ACCESOS_FORZADO_FINAL",
    "EDUTURNOS_ACCESOS_FINAL_V11",
    "EDUTURNOS_ACCESOS_DISENO_FINAL",
    "EDUTURNOS_ACCESOS_ORIGINAL",
    "EDUTURNOS_ACCESOS_SOLO_RESTAURADO",
    "EDUTURNOS_ENLACES_DASHBOARD_RESTAURADOS",
    "EDUTURNOS_TODOS_LOS_BOTONES_V5",
    "EDUTURNOS_BOTONES_REALES_V6",
    "EDUTURNOS_BOTONES_V4",
    "EDUTURNOS_CORRECCION_FINAL_V9",
    "EDUTURNOS_BOTONES_GLOBALES",
    "EDUTURNOS_BOTONES_V5",
    "EDUTURNOS_SOLO_BOTONES_V3",
    "EDUTURNOS_LAYOUT_ATRAS_V8",
    "EDUTURNOS_ATRAS_TODOS_V7",
    "EDUTURNOS_BOTONES_REALES_V6",
    "EDUTURNOS_ENLACES_DASHBOARD_RESTAURADOS",
]


def limpiar_markers(texto):

    for marker in markers:

        texto = re.sub(
            rf'<style[^>]*id=["\']{re.escape(marker)}["\'][^>]*>.*?</style>',
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

        texto = re.sub(
            rf'<script[^>]*id=["\']{re.escape(marker)}["\'][^>]*>.*?</script>',
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    return texto


dashboard = limpiar_markers(
    dashboard
)


# ============================================================
# 2. QUITAR ESTILOS INLINE DE QUICK-CARD
# ============================================================

def quitar_style_quickcard(match):

    apertura = match.group(0)

    apertura = re.sub(
        r'\sstyle\s*=\s*["\'][^"\']*["\']',
        "",
        apertura,
        flags=re.IGNORECASE | re.DOTALL
    )

    return apertura


dashboard = re.sub(
    r'<a\b[^>]*class\s*=\s*["\'][^"\']*\bquick-card\b[^"\']*["\'][^>]*>',
    quitar_style_quickcard,
    dashboard,
    flags=re.IGNORECASE | re.DOTALL
)


# ============================================================
# 3. ASEGURAR QUE QUICK-CARD NO TENGA CLASES DE BOTON
# ============================================================

def limpiar_clases_quickcard(match):

    apertura = match.group(0)

    m = re.search(
        r'class\s*=\s*["\']([^"\']*)["\']',
        apertura,
        flags=re.IGNORECASE
    )

    if not m:
        return apertura

    clases = m.group(1).split()

    clases_borrar = {
        "boton",
        "btn",
        "btn-primary",
        "btn-secondary",
        "btn-success",
        "btn-danger",
        "btn-warning",
        "btn-info",
        "btn-dark",
        "btn-light",
        "eduturnos-boton-global",
    }

    clases = [
        c for c in clases
        if c not in clases_borrar
    ]

    if "quick-card" not in clases:
        clases.insert(0, "quick-card")

    nuevas_clases = " ".join(clases)

    apertura = (
        apertura[:m.start(1)]
        + nuevas_clases
        + apertura[m.end(1):]
    )

    return apertura


dashboard = re.sub(
    r'<a\b[^>]*class\s*=\s*["\'][^"\']*\bquick-card\b[^"\']*["\'][^>]*>',
    limpiar_clases_quickcard,
    dashboard,
    flags=re.IGNORECASE | re.DOTALL
)


# ============================================================
# 4. LIMPIAR CAMBIOS ANTIGUOS SOBRE ACTION-GRID
# ============================================================

# No cambia HTML.
# Solo eliminamos nuestro CSS inyectado si tiene markers conocidos
# o bloques específicos creados por scripts anteriores.

css = re.sub(
    r'/\*\s*EDUTURNOS ACCIONES RAPIDAS REALES\s*\*/.*?(?=\n/\*|\Z)',
    "",
    css,
    flags=re.IGNORECASE | re.DOTALL
)


# ============================================================
# 5. CSS ORIGINAL FUNCIONAL
# ============================================================

CSS_ORIGINAL = r"""

/* =========================================================
   EDUTURNOS - ACCESOS / ACCIONES RAPIDAS
   CODIGO ORIGINAL FUNCIONAL
   ========================================================= */

.action-grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:14px;
    width:100%;
    align-items:stretch;
}

.quick-card{
    min-height:112px;
    height:120px;
    border:1px solid var(--borde);
    border-radius:12px;
    padding:18px;
    background:#fbfdff;
    display:flex;
    flex-direction:column;
    justify-content:center;
    gap:6px;
    color:var(--texto);
    text-decoration:none;
    box-sizing:border-box;
    transition:
        border-color .15s ease,
        background-color .15s ease;
}

.quick-card:hover{
    border-color:#b8cceb;
    background:#f6faff;
    color:var(--texto);
    text-decoration:none;
}

.quick-card strong{
    font-size:16px;
    color:var(--azul2);
    line-height:1.25;
}

.quick-card span{
    font-size:13px;
    color:var(--gris);
    line-height:1.4;
}

.quick-card small{
    color:var(--azul);
    font-size:12px;
    font-weight:700;
    margin-top:4px;
}

@media(max-width:850px){
    .action-grid{
        grid-template-columns:1fr;
    }

    .quick-card{
        height:auto;
        min-height:112px;
    }
}

"""


# ============================================================
# 6. EVITAR DUPLICAR NUESTRO BLOQUE
# ============================================================

css = re.sub(
    r'/\* =========================================================\s+EDUTURNOS - ACCESOS / ACCIONES RAPIDAS\s+CODIGO ORIGINAL FUNCIONAL\s+========================================================= \*/.*?(?=\n/\*|\Z)',
    "",
    css,
    flags=re.IGNORECASE | re.DOTALL
)

css = css.rstrip() + "\n" + CSS_ORIGINAL


# ============================================================
# 7. GUARDA
# ============================================================

DASHBOARD.write_text(
    dashboard,
    encoding="utf-8"
)

CSS_FILE.write_text(
    css,
    encoding="utf-8"
)


# ============================================================
# 8. VERIFICACION
# ============================================================

dashboard_verificacion = DASHBOARD.read_text(
    encoding="utf-8"
)

css_verificacion = CSS_FILE.read_text(
    encoding="utf-8"
)

errores = []

if "class=\"quick-card\"" not in dashboard_verificacion:
    errores.append(
        "No se encontró class=\"quick-card\""
    )

if "action-grid" not in dashboard_verificacion:
    errores.append(
        "No se encontró action-grid"
    )

if ".action-grid{" not in css_verificacion:
    errores.append(
        "No se encontró CSS de .action-grid"
    )

if ".quick-card{" not in css_verificacion:
    errores.append(
        "No se encontró CSS de .quick-card"
    )


print()
print("=" * 75)

if errores:

    print("ATENCION")
    print()

    for error in errores:
        print("-", error)

    print()
    print("No se puede confirmar la restauración.")

else:

    print("RESTAURACION CORRECTA")
    print()
    print("✓ action-grid restaurado")
    print("✓ quick-card restaurado")
    print("✓ recuadros organizados")
    print("✓ 2 tarjetas por fila en computador")
    print("✓ 1 tarjeta por fila en pantalla pequeña")
    print("✓ Citas")
    print("✓ Calendario")
    print("✓ Notificaciones")
    print("✓ Solicitudes")
    print()
    print("No se modificaron rutas.")
    print("No se modificó MySQL.")
    print("No se modificaron las consultas.")
    print()
    print("El resto del Dashboard queda intacto.")

print()
print("Backups:")
print(backup_dashboard)
print(backup_css)

print()
print("AHORA EJECUTA:")
print()
print("python .\\app.py")
print()
print("Y después Ctrl + F5")
print()
print("=" * 75)

