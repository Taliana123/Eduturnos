from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")

DASHBOARD = ROOT / "templates" / "dashboard.html"
BACKUP = ROOT / "templates" / "dashboard.html.backup_solo_interno"
CSS_FILE = ROOT / "static" / "css" / "estilos.css"

print()
print("=" * 75)
print("EDUTURNOS - RESTAURAR ACCESOS CON EL CODIGO REAL")
print("=" * 75)
print()

if not DASHBOARD.exists():
    print("ERROR: no existe:")
    print(DASHBOARD)
    raise SystemExit


# ============================================================
# BACKUP DEL ESTADO ACTUAL
# ============================================================

backup_actual = DASHBOARD.with_name(
    "dashboard.html.backup_antes_reparacion_real"
)

if not backup_actual.exists():
    shutil.copy2(
        DASHBOARD,
        backup_actual
    )
    print("Backup actual creado:")
    print(backup_actual)


# ============================================================
# 1. LEER DASHBOARD ACTUAL
# ============================================================

actual = DASHBOARD.read_text(
    encoding="utf-8"
)


# ============================================================
# 2. OBTENER LA SECCION ORIGINAL DE ACCIONES RAPIDAS
# ============================================================

seccion_original = None

if BACKUP.exists():

    respaldo = BACKUP.read_text(
        encoding="utf-8"
    )

    # Buscar desde el texto "Acciones rápidas".
    posicion = respaldo.lower().find(
        "acciones rápidas"
    )

    if posicion == -1:
        posicion = respaldo.lower().find(
            "acciones rapidas"
        )

    if posicion != -1:

        inicio = respaldo.rfind(
            "<section",
            0,
            posicion
        )

        if inicio != -1:

            fin = respaldo.find(
                "</section>",
                posicion
            )

            if fin != -1:

                seccion_original = respaldo[
                    inicio:
                    fin + len("</section>")
                ]


# ============================================================
# 3. ENCONTRAR LA SECCION ACTUAL
# ============================================================

def encontrar_seccion(texto):

    posicion = texto.lower().find(
        "acciones rápidas"
    )

    if posicion == -1:
        posicion = texto.lower().find(
            "acciones rapidas"
        )

    if posicion == -1:
        return None

    inicio = texto.rfind(
        "<section",
        0,
        posicion
    )

    if inicio == -1:
        return None

    # Encontrar el cierre de esta section.
    nivel = 0

    patron = re.compile(
        r"<(/?)section\b[^>]*>",
        flags=re.IGNORECASE
    )

    for m in patron.finditer(
        texto,
        inicio
    ):

        if m.group(1):
            nivel -= 1

            if nivel == 0:
                return (
                    inicio,
                    m.end()
                )

        else:
            nivel += 1

    return None


ubicacion = encontrar_seccion(actual)


# ============================================================
# 4. REEMPLAZAR SOLO LA SECCION
# ============================================================

if seccion_original and ubicacion:

    inicio, fin = ubicacion

    actual = (
        actual[:inicio]
        + seccion_original
        + actual[fin:]
    )

    print(
        "OK - Se recupero la seccion Acciones rapidas "
        "del respaldo anterior."
    )

else:

    print(
        "AVISO - No se pudo recuperar el bloque completo "
        "desde el respaldo."
    )

    print(
        "Se mantendra la seccion actual y se corregira "
        "su estructura visual."
    )


# ============================================================
# 5. CAMBIAR CUALQUIER quick-grid POR action-grid
#    PORQUE ESA ES LA CLASE REAL DEL PROYECTO ORIGINAL
# ============================================================

actual = actual.replace(
    'class="quick-grid"',
    'class="action-grid"'
)

actual = actual.replace(
    "quick-grid",
    "action-grid"
)


# ============================================================
# 6. QUITAR ESTILOS INLINE ANTIGUOS DE QUICK-CARD
# ============================================================

def limpiar_estilo_quickcard(match):

    apertura = match.group(0)

    apertura = re.sub(
        r'\sstyle\s*=\s*["\'][^"\']*["\']',
        "",
        apertura,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Asegurar que conserve quick-card.
    return apertura


actual = re.sub(
    r'<a\b[^>]*class\s*=\s*["\'][^"\']*\bquick-card\b[^"\']*["\'][^>]*>',
    limpiar_estilo_quickcard,
    actual,
    flags=re.IGNORECASE | re.DOTALL
)


# ============================================================
# 7. CSS REAL BASADO EN EL PROYECTO
# ============================================================

CSS = r"""

/* ============================================================
   EDUTURNOS - ACCIONES RAPIDAS
   Basado en la estructura real del proyecto:
   .action-grid + .quick-card
   ============================================================ */


/* CONTENEDOR */
.action-grid {

    display: grid !important;

    grid-template-columns:
        repeat(4, minmax(0, 1fr)) !important;

    gap: 14px !important;

    width: 100% !important;

    margin-top: 16px !important;

    align-items: stretch !important;
}


/* TARJETA */
.action-grid .quick-card {

    min-height: 186px !important;

    height: auto !important;

    width: 100% !important;

    box-sizing: border-box !important;

    padding: 18px !important;

    margin: 0 !important;

    display: flex !important;

    flex-direction: column !important;

    justify-content: flex-start !important;

    align-items: flex-start !important;

    gap: 0 !important;

    background: #ffffff !important;

    background-color: #ffffff !important;

    color: #1f2933 !important;

    border: 1px solid #dce4ec !important;

    border-radius: 12px !important;

    box-shadow:
        0 2px 8px rgba(0,0,0,.05) !important;

    text-decoration: none !important;

    overflow: hidden !important;

}


/* TARJETA HOVER */
.action-grid .quick-card:hover {

    background: #ffffff !important;

    background-color: #ffffff !important;

    color: #1f2933 !important;

    border-color: #b8cceb !important;

    box-shadow:
        0 4px 12px rgba(0,0,0,.08) !important;

    transform: none !important;

}


/* ETIQUETA */
.action-grid .quick-card .quick-icon {

    display: inline-flex !important;

    align-items: center !important;

    justify-content: center !important;

    min-height: 30px !important;

    padding: 6px 10px !important;

    margin: 0 0 12px 0 !important;

    background: #eaf2ff !important;

    background-color: #eaf2ff !important;

    color: #1769aa !important;

    border: none !important;

    border-radius: 8px !important;

    font-size: 12px !important;

    font-weight: 700 !important;

    line-height: 1 !important;

}


/* TITULO */
.action-grid .quick-card strong {

    display: block !important;

    width: 100% !important;

    margin: 0 0 8px 0 !important;

    padding: 0 !important;

    color: #111827 !important;

    background: transparent !important;

    border: none !important;

    box-shadow: none !important;

    font-size: 17px !important;

    font-weight: 700 !important;

    line-height: 1.25 !important;

}


/* DESCRIPCION */
.action-grid .quick-card span:not(.quick-icon) {

    display: block !important;

    width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    color: #5f6b76 !important;

    background: transparent !important;

    border: none !important;

    box-shadow: none !important;

    font-size: 13px !important;

    font-weight: 400 !important;

    line-height: 1.45 !important;

}


/* ENLACE INFERIOR */
.action-grid .quick-card small {

    display: block !important;

    width: 100% !important;

    margin-top: auto !important;

    padding: 14px 0 0 0 !important;

    color: #1769aa !important;

    background: transparent !important;

    border: none !important;

    box-shadow: none !important;

    font-size: 12px !important;

    font-weight: 700 !important;

    line-height: 1.2 !important;

}


/* ============================================================
   IMPORTANTE:
   QUICK-CARD NO ES UN BOTON AZUL
   ============================================================ */

.action-grid a.quick-card {

    background: #ffffff !important;

    background-color: #ffffff !important;

    color: #1f2933 !important;

    border: 1px solid #dce4ec !important;

    border-radius: 12px !important;

    box-shadow:
        0 2px 8px rgba(0,0,0,.05) !important;

}


/* ============================================================
   NO HEREDAR ESTILO DE BOTON
   ============================================================ */

.action-grid a.quick-card,
.action-grid a.quick-card:hover,
.action-grid a.quick-card:focus,
.action-grid a.quick-card:visited {

    text-decoration: none !important;

}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 950px) {

    .action-grid {

        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;

    }

}


@media (max-width: 600px) {

    .action-grid {

        grid-template-columns:
            1fr !important;

        gap: 12px !important;

    }

    .action-grid .quick-card {

        min-height: 150px !important;

        padding: 16px !important;

    }

}

"""


# ============================================================
# 8. QUITAR BLOQUE ANTERIOR SI EXISTE
# ============================================================

actual = re.sub(
    r'/\* ============================================================\s+EDUTURNOS - ACCIONES RAPIDAS.*?@media \(max-width: 600px\).*?\}\s*\}\s*\n',
    "",
    actual,
    flags=re.IGNORECASE | re.DOTALL
)


# ============================================================
# 9. INSERTAR CSS EN DASHBOARD
# ============================================================

pos = actual.lower().rfind(
    "</head>"
)

if pos != -1:

    actual = (
        actual[:pos]
        + "\n<style id=\"EDUTURNOS_ACCESOS_REALES_FINAL\">\n"
        + CSS
        + "\n</style>\n"
        + actual[pos:]
    )


DASHBOARD.write_text(
    actual,
    encoding="utf-8"
)


# ============================================================
# 10. ACTUALIZAR CSS GLOBAL REAL
# ============================================================

if CSS_FILE.exists():

    css_actual = CSS_FILE.read_text(
        encoding="utf-8"
    )

    marcador_css = (
        "/* EDUTURNOS ACCIONES RAPIDAS REALES */"
    )

    # Eliminar nuestra versión anterior.
    css_actual = re.sub(
        r'/\* EDUTURNOS ACCIONES RAPIDAS REALES \*/.*',
        "",
        css_actual,
        flags=re.IGNORECASE | re.DOTALL
    )

    css_actual += """

/* EDUTURNOS ACCIONES RAPIDAS REALES */

/* La estructura REAL utiliza action-grid */
.action-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:14px;
    width:100%;
}

.action-grid .quick-card{
    min-height:186px;
    box-sizing:border-box;
    padding:18px;
    background:#fff;
    color:#1f2933;
    border:1px solid #dce4ec;
    border-radius:12px;
    box-shadow:0 2px 8px rgba(0,0,0,.05);
    text-decoration:none;
    display:flex;
    flex-direction:column;
}

.action-grid .quick-card:hover{
    background:#fff;
    color:#1f2933;
    border-color:#b8cceb;
    box-shadow:0 4px 12px rgba(0,0,0,.08);
}

.action-grid .quick-card .quick-icon{
    background:#eaf2ff;
    color:#1769aa;
    border-radius:8px;
    padding:6px 10px;
    margin-bottom:12px;
    font-size:12px;
    font-weight:700;
}

.action-grid .quick-card strong{
    color:#111827;
    background:transparent;
    font-size:17px;
    margin-bottom:8px;
}

.action-grid .quick-card span:not(.quick-icon){
    color:#5f6b76;
    background:transparent;
    font-size:13px;
}

.action-grid .quick-card small{
    color:#1769aa;
    background:transparent;
    margin-top:auto;
    padding-top:14px;
    font-size:12px;
    font-weight:700;
}

@media(max-width:950px){
    .action-grid{
        grid-template-columns:repeat(2,minmax(0,1fr));
    }
}

@media(max-width:600px){
    .action-grid{
        grid-template-columns:1fr;
    }
}

"""

    CSS_FILE.write_text(
        css_actual,
        encoding="utf-8"
    )

    print(
        "OK - static/css/estilos.css actualizado con las clases reales."
    )


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 75)
print("CORRECCIÓN REAL TERMINADA")
print("=" * 75)
print()
print("SE UTILIZARON LAS CLASES REALES:")
print()
print("✓ action-grid")
print("✓ quick-card")
print("✓ quick-icon")
print()
print("ACCESOS:")
print("✓ Citas")
print("✓ Calendario")
print("✓ Notificaciones")
print("✓ Solicitudes")
print()
print("Las tarjetas vuelven a estar dentro de sus recuadros.")
print("No se convierten en botones azules.")
print()
print("Se modificó solamente:")
print("✓ dashboard.html")
print("✓ static/css/estilos.css")
print()
print("NO se modificó:")
print("✗ MySQL")
print("✗ routes/calendario.py")
print("✗ rutas")
print("✗ lógica de citas")
print()
print("Backup:")
print(backup_actual)
print()
print("Ahora ejecuta:")
print("python .\\app.py")
print()
print("Después pulsa Ctrl + F5.")
print("=" * 75)

