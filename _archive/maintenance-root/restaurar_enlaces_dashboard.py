from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")
ARCHIVO = ROOT / "templates" / "dashboard.html"

print()
print("=" * 72)
print("EDUTURNOS - RESTAURAR ENLACES DE ACCESO DEL DASHBOARD")
print("=" * 72)
print()

if not ARCHIVO.exists():
    print("ERROR: no existe:")
    print(ARCHIVO)
    raise SystemExit

# ============================================================
# BACKUP
# ============================================================

backup = ARCHIVO.with_name(
    "dashboard.html.backup_enlaces_restaurados"
)

if not backup.exists():
    shutil.copy2(ARCHIVO, backup)
    print("Backup creado:")
    print(backup)
else:
    print("Backup ya existente:")
    print(backup)

texto = ARCHIVO.read_text(encoding="utf-8")


# ============================================================
# CSS SOLO PARA LOS ENLACES NORMALES DE LAS TARJETAS
# ============================================================

CSS = r"""
<style id="EDUTURNOS_ENLACES_DASHBOARD_RESTAURADOS">

/* =========================================================
   ENLACES NORMALES DE ACCESOS
   NO SON BOTONES
   ========================================================= */

.dashboard-card a.dashboard-normal-link,
.dashboard-card a.dashboard-card-link,
.quick-card a.dashboard-normal-link,
.quick-card a.dashboard-card-link {

    background: transparent !important;
    background-color: transparent !important;

    color: #ffffff !important;

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

/* TÍTULOS */
.dashboard-card h2 a.dashboard-normal-link,
.dashboard-card h3 a.dashboard-normal-link,
.dashboard-card h4 a.dashboard-normal-link,
.quick-card h2 a.dashboard-normal-link,
.quick-card h3 a.dashboard-normal-link,
.quick-card h4 a.dashboard-normal-link {

    background: transparent !important;
    background-color: transparent !important;

    color: #ffffff !important;

    border: none !important;

    padding: 0 !important;

    margin: 0 !important;

    height: auto !important;
    min-height: 0 !important;

    box-shadow: none !important;
}

/* DESCRIPCIONES */
.dashboard-card p a.dashboard-normal-link,
.quick-card p a.dashboard-normal-link {

    background: transparent !important;
    background-color: transparent !important;

    color: #ffffff !important;

    border: none !important;

    padding: 0 !important;

    margin: 0 !important;

    height: auto !important;
    min-height: 0 !important;

    box-shadow: none !important;
}

/* HOVER SIN ASPECTO DE BOTÓN */
.dashboard-card a.dashboard-normal-link:hover,
.dashboard-card a.dashboard-card-link:hover,
.quick-card a.dashboard-normal-link:hover,
.quick-card a.dashboard-card-link:hover {

    background: transparent !important;
    background-color: transparent !important;

    color: #ffffff !important;

    border: none !important;

    box-shadow: none !important;
}

/* TEXTO INTERNO */
.dashboard-card a.dashboard-normal-link *,
.dashboard-card a.dashboard-card-link *,
.quick-card a.dashboard-normal-link *,
.quick-card a.dashboard-card-link * {

    color: #ffffff !important;
}

</style>
"""


# ============================================================
# QUITAR CSS ANTERIOR QUE CONVERTÍA ESTOS EN BOTONES
# ============================================================

patrones_css = [
    r'<style[^>]*id=["\']EDUTURNOS_ENLACES_DASHBOARD_RESTAURADOS["\'][^>]*>.*?</style>',
]

for patron in patrones_css:
    texto = re.sub(
        patron,
        "",
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )


# ============================================================
# TEXTOS QUE REPRESENTAN LAS TARJETAS
# ============================================================

nombres = [
    "Citas",
    "Calendario",
    "Avisos",
    "Notificaciones",
    "Solicitudes"
]


# ============================================================
# MODIFICAR ENLACES DE DASHBOARD
# ============================================================

def modificar_enlace(match):
    attrs = match.group(1)
    contenido = match.group(2)

    # No tocar el botón real "boton" ni btn.
    clases_match = re.search(
        r'\bclass\s*=\s*["\']([^"\']*)["\']',
        attrs,
        flags=re.IGNORECASE
    )

    if clases_match:
        clases = clases_match.group(1)

        # Quitar clases que les daban apariencia de botón.
        clases_lista = clases.split()

        clases_lista = [
            c for c in clases_lista
            if c.lower() not in {
                "boton",
                "btn",
                "btn-primary",
                "btn-secondary",
                "btn-success",
                "btn-danger",
                "btn-warning",
                "btn-info",
                "btn-dark",
                "btn-light"
            }
        ]

        if "dashboard-normal-link" not in clases_lista:
            clases_lista.append("dashboard-normal-link")

        nuevas_clases = " ".join(clases_lista)

        attrs = (
            attrs[:clases_match.start(1)]
            + nuevas_clases
            + attrs[clases_match.end(1):]
        )

    else:
        attrs += ' class="dashboard-normal-link"'

    # Eliminar estilos inline que puedan convertirlo en botón.
    attrs = re.sub(
        r'\sstyle\s*=\s*["\'][^"\']*["\']',
        "",
        attrs,
        flags=re.IGNORECASE
    )

    return f"<a{attrs}>{contenido}</a>"


# ------------------------------------------------------------
# Buscar todos los <a> y comprobar su contenido.
# ------------------------------------------------------------

patron_a = re.compile(
    r"<a\b([^>]*)>(.*?)</a>",
    flags=re.IGNORECASE | re.DOTALL
)

contador = 0


def procesar_a(match):

    global contador

    attrs = match.group(1)
    contenido = match.group(2)

    texto_visible = re.sub(
        r"<[^>]+>",
        "",
        contenido
    ).strip().lower()

    # Solo enlaces que pertenecen a las tarjetas o tienen
    # los textos concretos mostrados en el Dashboard.
    pertenece = any(
        nombre.lower() in texto_visible
        for nombre in nombres
    )

    # También modificar enlaces de acciones de tarjeta.
    acciones = [
        "Ver citas",
        "Ver citas →",
        "Abrir calendario",
        "Abrir calendario →",
        "Ver notificaciones",
        "Ver notificaciones →",
        "Ver solicitudes",
        "Ver solicitudes →"
    ]

    es_accion = any(
        accion.lower() in texto_visible
        for accion in acciones
    )

    # Solo dentro de clases/contenedores de dashboard.
    es_dashboard = any(
        clase in attrs.lower()
        for clase in [
            "dashboard-card",
            "quick-card",
            "quick-link",
            "dashboard-action",
            "dashboard-actions"
        ]
    )

    if pertenece or es_accion or es_dashboard:
        # Evitar modificar enlaces que claramente son botones
        # reales de formularios.
        if not re.search(
            r'class\s*=\s*["\'][^"\']*\b(link-back|edc-back)\b',
            attrs,
            flags=re.IGNORECASE
        ):
            contador += 1
            return modificar_enlace(match)

    return match.group(0)


texto = patron_a.sub(
    procesar_a,
    texto
)


# ============================================================
# INSERTAR CSS
# ============================================================

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


# ============================================================
# GUARDAR
# ============================================================

ARCHIVO.write_text(
    texto,
    encoding="utf-8"
)


print()
print("=" * 72)
print("RESTAURACIÓN TERMINADA")
print("=" * 72)
print()
print("Enlaces modificados:", contador)
print()
print("Estas secciones vuelven a ser enlaces normales:")
print("✓ Citas")
print("✓ Calendario")
print("✓ Notificaciones / Avisos")
print("✓ Solicitudes")
print("✓ Ver citas")
print("✓ Abrir calendario")
print("✓ Ver notificaciones")
print("✓ Ver solicitudes")
print()
print("Fondo: transparente")
print("Texto: blanco")
print()
print("Los botones REALES no se modificaron.")
print()
print("Backup:")
print(backup)
print()
print("Ahora ejecuta:")
print("python .\\app.py")
print()
print("Después presiona Ctrl + F5 en el navegador.")
print("=" * 72)

