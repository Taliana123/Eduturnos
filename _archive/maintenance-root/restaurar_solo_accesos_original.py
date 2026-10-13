from pathlib import Path
import shutil
import re

ROOT = Path(r"F:\edu_Final")
DASHBOARD = ROOT / "templates" / "dashboard.html"

# Respaldos posibles del dashboard anteriores a los cambios de botones.
BACKUPS = [
    ROOT / "templates" / "dashboard.html.backup_organizado",
    ROOT / "templates" / "dashboard.html.backup_solo_interno",
    ROOT / "templates" / "dashboard.html.backup_enlaces_restaurados",
]

MARCADOR = "EDUTURNOS_ACCESOS_RESTAURADOS_EXACTAMENTE"


def extraer_seccion_accesos(texto):
    """
    Busca la sección que contiene "Accesos" y "Acciones rápidas".
    Devuelve únicamente el bloque de sección.
    """

    # Buscar una etiqueta de sección que contenga Accesos.
    patrones = [
        r'<section\b[^>]*>.*?<[^>]*>\s*Accesos\s*</[^>]*>.*?</section>',
        r'<section\b[^>]*>.*?>\s*<[^>]+>\s*Accesos\s*</[^>]+>.*?</section>',
    ]

    for patron in patrones:
        m = re.search(
            patron,
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )
        if m:
            bloque = m.group(0)

            if "Acciones rápidas" in bloque or "Acciones r" in bloque:
                return bloque

    # Método alternativo: localizar "Acciones rápidas" y subir
    # hasta la sección contenedora más cercana.
    m = re.search(
        r'Acciones\s+r[aá]pidas',
        texto,
        flags=re.IGNORECASE
    )

    if not m:
        return None

    antes = texto[:m.start()]

    inicio = antes.rfind("<section")

    if inicio == -1:
        return None

    fin = texto.find("</section>", m.end())

    if fin == -1:
        return None

    return texto[inicio:fin + len("</section>")]


def insertar_clase_restaurada(bloque):
    """
    Añade una clase al contenedor de la sección sin cambiar
    su estructura interna.
    """

    m = re.match(
        r'(<section\b)([^>]*)>',
        bloque,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not m:
        return bloque

    apertura = m.group(0)

    clase = re.search(
        r'\bclass\s*=\s*["\']([^"\']*)["\']',
        apertura,
        flags=re.IGNORECASE
    )

    if clase:
        clases = clase.group(1)

        if MARCADOR not in clases:
            nuevas = clases.strip() + " " + MARCADOR

            apertura_nueva = (
                apertura[:clase.start(1)]
                + nuevas
                + apertura[clase.end(1):]
            )

    else:
        apertura_nueva = apertura[:-1] + (
            f' class="{MARCADOR}">'
        )

    return apertura_nueva + bloque[len(apertura):]


def main():

    print()
    print("=" * 75)
    print("EDUTURNOS - RESTAURAR SOLO ACCESOS")
    print("=" * 75)
    print()

    if not DASHBOARD.exists():
        print("ERROR: no existe:")
        print(DASHBOARD)
        return

    # --------------------------------------------------------
    # Buscar el respaldo que contiene la versión anterior.
    # --------------------------------------------------------

    respaldo = None

    for candidato in BACKUPS:
        if candidato.exists():
            try:
                texto_respaldo = candidato.read_text(
                    encoding="utf-8"
                )

                bloque_respaldo = extraer_seccion_accesos(
                    texto_respaldo
                )

                if bloque_respaldo:
                    respaldo = candidato
                    break

            except Exception:
                continue

    if respaldo is None:
        print()
        print("ERROR: no encontré un respaldo anterior")
        print("que contenga la sección Accesos.")
        print()
        print("No se modificó dashboard.html.")
        return

    print("Respaldo encontrado:")
    print(respaldo)

    # --------------------------------------------------------
    # Leer dashboard actual.
    # --------------------------------------------------------

    actual = DASHBOARD.read_text(
        encoding="utf-8"
    )

    bloque_actual = extraer_seccion_accesos(
        actual
    )

    if not bloque_actual:
        print()
        print("ERROR: no encontré la sección Accesos")
        print("en el dashboard actual.")
        print()
        print("No se modificó dashboard.html.")
        return

    print()
    print("Sección actual encontrada correctamente.")

    # --------------------------------------------------------
    # Backup del estado actual antes de reemplazar SOLO
    # esta sección.
    # --------------------------------------------------------

    backup_actual = DASHBOARD.with_name(
        "dashboard.html.backup_antes_restaurar_accesos"
    )

    if not backup_actual.exists():
        shutil.copy2(
            DASHBOARD,
            backup_actual
        )

        print()
        print("Backup del dashboard actual creado:")
        print(backup_actual)

    # --------------------------------------------------------
    # Restaurar el bloque exacto del respaldo.
    # --------------------------------------------------------

    bloque_restaurado = insertar_clase_restaurada(
        bloque_respaldo
    )

    nuevo = actual.replace(
        bloque_actual,
        bloque_restaurado,
        1
    )

    # --------------------------------------------------------
    # CSS SOLO para esta sección.
    # Evita que enlaces normales vuelvan a verse
    # como botones, PERO NO TOCA EL RESTO DEL DASHBOARD.
    # --------------------------------------------------------

    CSS = r"""
<style id="EDUTURNOS_ACCESOS_SOLO_RESTAURADO">

/* ==========================================================
   SOLO ACCESOS / ACCIONES RÁPIDAS
   Estado visual anterior a los cambios de botones.
   ========================================================== */

section.EDUTURNOS_ACCESOS_RESTAURADOS a:not(.boton):not(.btn):not([role="button"]),
section.EDUTURNOS_ACCESOS_RESTAURADOS a:not(.boton):not(.btn):not([role="button"]):visited {

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

    opacity: 1 !important;
}

/* Títulos Citas / Calendario / Notificaciones / Solicitudes */
section.EDUTURNOS_ACCESOS_RESTAURADOS h2 a,
section.EDUTURNOS_ACCESOS_RESTAURADOS h3 a,
section.EDUTURNOS_ACCESOS_RESTAURADOS h4 a {

    background: transparent !important;
    background-color: transparent !important;

    color: inherit !important;

    border: none !important;

    box-shadow: none !important;

    padding: 0 !important;
    margin: 0 !important;

    min-height: 0 !important;
    height: auto !important;

    font-weight: inherit !important;
}

/* Descripciones */
section.EDUTURNOS_ACCESOS_RESTAURADOS p a {

    background: transparent !important;
    background-color: transparent !important;

    color: inherit !important;

    border: none !important;

    padding: 0 !important;
    margin: 0 !important;

    min-height: 0 !important;
    height: auto !important;

    box-shadow: none !important;
}

/* Enlaces "Ver citas", "Abrir calendario", etc. */
section.EDUTURNOS_ACCESOS_RESTAURADOS
a:not(.boton):not(.btn):not([role="button"]):hover {

    background: transparent !important;
    background-color: transparent !important;

    color: inherit !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;

    text-decoration: underline !important;
}

/* ==========================================================
   LOS RECUADROS DE ACCESO SE MANTIENEN
   ========================================================== */

section.EDUTURNOS_ACCESOS_RESTAURADOS
.dashboard-card,
section.EDUTURNOS_ACCESOS_RESTAURADOS
.quick-card {

    position: relative;
    overflow: hidden;
}


/* ==========================================================
   BOTONES REALES DENTRO DE ESTA SECCIÓN
   ========================================================== */

section.EDUTURNOS_ACCESOS_RESTAURADOS
a.boton,
section.EDUTURNOS_ACCESOS_RESTAURADOS
a.btn,
section.EDUTURNOS_ACCESOS_RESTAURADOS
button {

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border-color: #1769aa !important;
}


section.EDUTURNOS_ACCESOS_RESTAURADOS
a.boton:hover,
section.EDUTURNOS_ACCESOS_RESTAURADOS
a.btn:hover,
section.EDUTURNOS_ACCESOS_RESTAURADOS
button:hover {

    background: #145b91 !important;
    background-color: #145b91 !important;

    color: #ffffff !important;

    border-color: #145b91 !important;
}

</style>
"""

    # Quitar versión anterior de este CSS.
    nuevo = re.sub(
        r'<style[^>]*id=["\']EDUTURNOS_ACCESOS_SOLO_RESTAURADO["\'][^>]*>.*?</style>',
        "",
        nuevo,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Insertar antes de </head>.
    posicion = nuevo.lower().rfind("</head>")

    if posicion != -1:
        nuevo = (
            nuevo[:posicion]
            + "\n"
            + CSS
            + "\n"
            + nuevo[posicion:]
        )
    else:
        nuevo += "\n" + CSS

    # --------------------------------------------------------
    # Guardar.
    # --------------------------------------------------------

    DASHBOARD.write_text(
        nuevo,
        encoding="utf-8"
    )

    print()
    print("=" * 75)
    print("RESTAURACIÓN TERMINADA")
    print("=" * 75)
    print()
    print("Se restauró SOLO:")
    print("✓ Accesos")
    print("✓ Acciones rápidas")
    print("✓ Recuadro de Citas")
    print("✓ Recuadro de Calendario")
    print("✓ Recuadro de Notificaciones")
    print("✓ Recuadro de Solicitudes")
    print()
    print("Volvieron al aspecto anterior:")
    print("✓ Citas")
    print("✓ Calendario")
    print("✓ Avisos / Notificaciones")
    print("✓ Solicitudes")
    print("✓ Ver citas →")
    print("✓ Abrir calendario →")
    print("✓ Ver notificaciones →")
    print("✓ Ver solicitudes →")
    print()
    print("El resto del Dashboard NO fue reemplazado.")
    print("Los botones reales NO fueron eliminados.")
    print()
    print("Backup del estado anterior:")
    print(backup_actual)
    print()
    print("Ahora ejecuta:")
    print("python .\\app.py")
    print()
    print("Después: Ctrl + F5")
    print()
    print("=" * 75)


if __name__ == "__main__":
    main()
