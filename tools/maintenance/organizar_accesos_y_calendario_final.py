from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")
DASHBOARD = ROOT / "templates" / "dashboard.html"
CALENDARIO = ROOT / "templates" / "calendario" / "index.html"

print()
print("=" * 76)
print("EDUTURNOS - ORGANIZACION FINAL DE ACCESOS Y CALENDARIO")
print("=" * 76)
print()


# ============================================================
# FUNCIONES
# ============================================================

def limpiar_marca(texto, marker):
    patron = rf'<style[^>]*id=["\']{re.escape(marker)}["\'][^>]*>.*?</style>'
    return re.sub(
        patron,
        "",
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )


def insertar_head(texto, bloque):
    pos = texto.lower().rfind("</head>")

    if pos != -1:
        return (
            texto[:pos]
            + "\n"
            + bloque
            + "\n"
            + texto[pos:]
        )

    return texto + "\n" + bloque


# ============================================================
# 1. DASHBOARD
# ============================================================

if not DASHBOARD.exists():
    print("ERROR: no existe:")
    print(DASHBOARD)
    raise SystemExit

backup_dashboard = DASHBOARD.with_name(
    "dashboard.html.backup_accesos_diseno_final"
)

if not backup_dashboard.exists():
    shutil.copy2(
        DASHBOARD,
        backup_dashboard
    )

dashboard = DASHBOARD.read_text(
    encoding="utf-8"
)

# ------------------------------------------------------------
# Eliminar solamente nuestra corrección visual anterior
# de accesos.
# ------------------------------------------------------------

dashboard = limpiar_marca(
    dashboard,
    "EDUTURNOS_ACCESOS_DISENO_FINAL"
)

# También quitamos bloques anteriores que expresamente
# estaban afectando quick-card.
for marker in [
    "EDUTURNOS_ACCESOS_ORIGINAL",
    "EDUTURNOS_ENLACES_DASHBOARD_RESTAURADOS",
]:
    dashboard = limpiar_marca(
        dashboard,
        marker
    )


# ------------------------------------------------------------
# CSS DEL DASHBOARD
# ------------------------------------------------------------

CSS_DASHBOARD = r"""
<style id="EDUTURNOS_ACCESOS_DISENO_FINAL">

/* ==========================================================
   ACCESOS / ACCIONES RÁPIDAS
   Diseño visual basado en la referencia solicitada.
   Solo afecta quick-card y quick-grid.
   ========================================================== */


/* CONTENEDOR DE ACCIONES RÁPIDAS */
.quick-grid {

    display: grid !important;

    grid-template-columns:
        repeat(4, minmax(0, 1fr)) !important;

    gap: 14px !important;

    width: 100% !important;

    margin-top: 16px !important;

    align-items: stretch !important;
}


/* ==========================================================
   RECUADRO INDIVIDUAL
   ========================================================== */

a.quick-card {

    display: flex !important;

    flex-direction: column !important;

    align-items: flex-start !important;

    justify-content: flex-start !important;

    box-sizing: border-box !important;

    width: 100% !important;

    min-height: 186px !important;

    padding: 18px !important;

    background: #ffffff !important;

    background-color: #ffffff !important;

    color: #1f2933 !important;

    border: 1px solid #dce4ec !important;

    border-radius: 12px !important;

    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;

    text-decoration: none !important;

    overflow: hidden !important;

    transform: none !important;

    transition:
        box-shadow .15s ease,
        border-color .15s ease !important;
}


/* HOVER DEL RECUADRO */
a.quick-card:hover {

    background: #ffffff !important;

    background-color: #ffffff !important;

    color: #1f2933 !important;

    border-color: #d5dee8 !important;

    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;

    transform: none !important;

    text-decoration: none !important;
}


/* ==========================================================
   ETIQUETA SUPERIOR
   Ejemplo: Citas / Calendario / Avisos / Solicitudes
   ========================================================== */

.quick-card .quick-icon {

    display: inline-flex !important;

    align-items: center !important;

    justify-content: center !important;

    width: auto !important;

    min-height: 30px !important;

    margin: 0 0 12px 0 !important;

    padding: 6px 10px !important;

    background: #eaf2ff !important;

    color: #1769aa !important;

    border: 0 !important;

    border-radius: 8px !important;

    font-size: 12px !important;

    font-weight: 700 !important;

    line-height: 1 !important;

    box-shadow: none !important;
}


/* ==========================================================
   TÍTULO DE LA TARJETA
   ========================================================== */

.quick-card strong {

    display: block !important;

    width: 100% !important;

    margin: 0 0 8px 0 !important;

    padding: 0 !important;

    background: transparent !important;

    color: #111827 !important;

    border: 0 !important;

    box-shadow: none !important;

    font-size: 17px !important;

    font-weight: 700 !important;

    line-height: 1.25 !important;
}


/* ==========================================================
   DESCRIPCIÓN
   ========================================================== */

.quick-card > span:not(.quick-icon) {

    display: block !important;

    width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    background: transparent !important;

    color: #5f6b76 !important;

    border: 0 !important;

    box-shadow: none !important;

    font-size: 13px !important;

    font-weight: 400 !important;

    line-height: 1.45 !important;
}


/* ==========================================================
   ENLACE INFERIOR
   ========================================================== */

.quick-card small {

    display: block !important;

    width: 100% !important;

    margin-top: auto !important;

    padding: 14px 0 0 0 !important;

    background: transparent !important;

    color: #1769aa !important;

    border: 0 !important;

    box-shadow: none !important;

    font-size: 12px !important;

    font-weight: 700 !important;

    line-height: 1.2 !important;
}


/* ==========================================================
   ASEGURAR QUE NINGÚN ESTILO GLOBAL LAS CONVIERTA EN BOTONES
   ========================================================== */

a.quick-card,
a.quick-card:hover,
a.quick-card:focus,
a.quick-card:visited {

    color: #1f2933 !important;

    text-decoration: none !important;

}


/* El texto inferior sigue azul */
a.quick-card small {

    color: #1769aa !important;
}


/* La etiqueta superior sigue azul */
a.quick-card .quick-icon {

    color: #1769aa !important;
}


/* ==========================================================
   TABLET
   ========================================================== */

@media (max-width: 950px) {

    .quick-grid {

        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;

    }
}


/* ==========================================================
   CELULAR
   ========================================================== */

@media (max-width: 600px) {

    .quick-grid {

        grid-template-columns:
            1fr !important;

        gap: 12px !important;
    }

    a.quick-card {

        min-height: 150px !important;

        padding: 16px !important;
    }
}

</style>
"""


dashboard = insertar_head(
    dashboard,
    CSS_DASHBOARD
)

DASHBOARD.write_text(
    dashboard,
    encoding="utf-8"
)


print("OK - Dashboard actualizado.")
print("OK - Accesos organizados en cuatro recuadros.")


# ============================================================
# 2. CALENDARIO
# ============================================================

if not CALENDARIO.exists():
    print("ERROR: no existe:")
    print(CALENDARIO)
    raise SystemExit

backup_calendario = CALENDARIO.with_name(
    "index.html.backup_calendario_botones_final"
)

if not backup_calendario.exists():
    shutil.copy2(
        CALENDARIO,
        backup_calendario
    )

calendario = CALENDARIO.read_text(
    encoding="utf-8"
)


# ------------------------------------------------------------
# Limpiar nuestros estilos anteriores de organización.
# ------------------------------------------------------------

for marker in [
    "EDUTURNOS_LAYOUT_ATRAS_V8",
    "EDUTURNOS_ATRAS_TODOS_V7",
    "EDUTURNOS_CALENDARIO_CONTROLES_FINAL",
]:
    calendario = limpiar_marca(
        calendario,
        marker
    )


# ============================================================
# 3. ASEGURAR CLASE DEL BOTÓN HOY
# ============================================================

# Buscar cualquier enlace cuyo texto visible sea Hoy.
patron_hoy = re.compile(
    r'<a\b([^>]*)>\s*Hoy\s*</a>',
    flags=re.IGNORECASE | re.DOTALL
)


def agregar_clase_hoy(match):

    attrs = match.group(1)

    clase = re.search(
        r'\bclass\s*=\s*["\']([^"\']*)["\']',
        attrs,
        flags=re.IGNORECASE
    )

    if clase:

        clases = clase.group(1)

        if "eduturnos-hoy" not in clases:

            nuevas = (
                clases.strip()
                + " eduturnos-hoy"
            )

            attrs = (
                attrs[:clase.start(1)]
                + nuevas
                + attrs[clase.end(1):]
            )

    else:

        attrs += ' class="eduturnos-hoy"'

    return f"<a{attrs}>Hoy</a>"


calendario = patron_hoy.sub(
    agregar_clase_hoy,
    calendario
)


# ============================================================
# 4. CSS CALENDARIO
# ============================================================

CSS_CALENDARIO = r"""
<style id="EDUTURNOS_CALENDARIO_CONTROLES_FINAL">

/* ==========================================================
   PARTE SUPERIOR DEL CALENDARIO
   Atrás + Ver citas + Nueva cita
   TODOS EN LA MISMA LÍNEA
   ========================================================== */

.edc-header {

    display: flex !important;

    align-items: center !important;

    justify-content: space-between !important;

    gap: 16px !important;

    width: 100% !important;
}


/* Información */
.edc-header-info {

    flex: 1 1 auto !important;

    min-width: 0 !important;
}


/* Grupo de botones */
.edc-header-actions {

    display: flex !important;

    align-items: center !important;

    justify-content: flex-end !important;

    gap: 8px !important;

    flex: 0 0 auto !important;

    flex-wrap: nowrap !important;

    white-space: nowrap !important;

    margin: 0 !important;

    padding: 0 !important;
}


/* TODOS LOS BOTONES SUPERIORES DEL CALENDARIO */
.edc-header-actions a,
.edc-header-actions .boton,
.edc-header-actions .edc-back {

    display: inline-flex !important;

    align-items: center !important;

    justify-content: center !important;

    flex: 0 0 auto !important;

    height: 34px !important;

    min-height: 34px !important;

    margin: 0 !important;

    padding: 7px 12px !important;

    box-sizing: border-box !important;

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


/* Hover */
.edc-header-actions a:hover,
.edc-header-actions .boton:hover,
.edc-header-actions .edc-back:hover {

    background: #145b91 !important;

    background-color: #145b91 !important;

    color: #ffffff !important;

    border-color: #145b91 !important;
}


/* ==========================================================
   BARRA DEL MES
   ========================================================== */

.edc-month-toolbar {

    display: flex !important;

    align-items: center !important;

    width: 100% !important;

    min-height: 42px !important;

    gap: 8px !important;
}


/* Botón anterior */
.edc-month-toolbar a:not(.eduturnos-hoy) {

    flex: 0 0 auto !important;
}


/* Título del mes */
.edc-month-title {

    flex: 1 1 auto !important;

    margin: 0 !important;

    text-align: center !important;
}


/* ==========================================================
   HOY - ESQUINA DERECHA
   ========================================================== */

.edc-month-toolbar a.eduturnos-hoy {

    flex: 0 0 auto !important;

    margin-left: auto !important;

    display: inline-flex !important;

    align-items: center !important;

    justify-content: center !important;

    height: 34px !important;

    min-height: 34px !important;

    padding: 7px 12px !important;

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


/* Hover Hoy */
.edc-month-toolbar a.eduturnos-hoy:hover {

    background: #145b91 !important;

    background-color: #145b91 !important;

    color: #ffffff !important;

    border-color: #145b91 !important;
}


/* ==========================================================
   RESPONSIVE
   ========================================================== */

@media (max-width: 760px) {

    .edc-header {

        align-items: flex-start !important;

        flex-direction: column !important;

    }

    .edc-header-actions {

        width: 100% !important;

        justify-content: flex-start !important;

        flex-wrap: wrap !important;

    }

    .edc-month-toolbar {

        flex-wrap: nowrap !important;

    }
}

</style>
"""


calendario = insertar_head(
    calendario,
    CSS_CALENDARIO
)

CALENDARIO.write_text(
    calendario,
    encoding="utf-8"
)


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 76)
print("CAMBIOS TERMINADOS")
print("=" * 76)
print()
print("DASHBOARD")
print("✓ Accesos organizados")
print("✓ Citas dentro de su recuadro")
print("✓ Calendario dentro de su recuadro")
print("✓ Notificaciones dentro de su recuadro")
print("✓ Solicitudes dentro de su recuadro")
print("✓ Aspecto limpio y ordenado")
print()
print("CALENDARIO")
print("✓ ← Atrás")
print("✓ Ver citas")
print("✓ + Nueva cita")
print("  quedan en la misma línea")
print("✓ Hoy queda en la esquina derecha")
print()
print("NO SE TOCÓ:")
print("✓ MySQL")
print("✓ routes/calendario.py")
print("✓ lógica de citas")
print("✓ datos")
print("✓ permisos")
print("✓ demás secciones del Dashboard")
print()
print("Backups creados:")
print(backup_dashboard)
print(backup_calendario)
print()
print("Ahora ejecuta:")
print("python .\\app.py")
print()
print("Después pulsa Ctrl + F5.")
print("=" * 76)

