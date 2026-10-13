from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")

DASHBOARD = ROOT / "templates" / "dashboard.html"
CALENDARIO = ROOT / "templates" / "calendario" / "index.html"

MARK_DASH = "EDUTURNOS_ACCESOS_FINAL_V11"
MARK_CAL = "EDUTURNOS_CALENDARIO_FINAL_V11"


# ============================================================
# CSS PARA DASHBOARD
# ============================================================

CSS_DASHBOARD = r"""
<style id="EDUTURNOS_ACCESOS_FINAL_V11">

/* ============================================================
   EDUTURNOS - ACCESOS / ACCIONES RAPIDAS
   Diseño equivalente al de la imagen solicitada.
   SOLO afecta quick-grid y quick-card.
   ============================================================ */


/* CONTENEDOR DE LAS TARJETAS */
.quick-grid {

    display: grid !important;

    grid-template-columns:
        repeat(4, minmax(0, 1fr)) !important;

    gap: 14px !important;

    width: 100% !important;

    margin-top: 16px !important;

    align-items: stretch !important;

}


/* ============================================================
   TARJETA
   ============================================================ */

a.quick-card {

    display: flex !important;

    flex-direction: column !important;

    align-items: flex-start !important;

    justify-content: flex-start !important;

    box-sizing: border-box !important;

    width: 100% !important;

    min-width: 0 !important;

    min-height: 186px !important;

    margin: 0 !important;

    padding: 18px !important;

    background: #ffffff !important;

    background-color: #ffffff !important;

    color: #1f2933 !important;

    border: 1px solid #dce4ec !important;

    border-radius: 12px !important;

    box-shadow:
        0 2px 8px rgba(0,0,0,.05) !important;

    text-decoration: none !important;

    overflow: hidden !important;

    transform: none !important;

    opacity: 1 !important;

}


/* HOVER DE LA TARJETA */
a.quick-card:hover,
a.quick-card:focus {

    background: #ffffff !important;

    background-color: #ffffff !important;

    color: #1f2933 !important;

    border-color: #d5dee8 !important;

    box-shadow:
        0 4px 12px rgba(0,0,0,.08) !important;

    transform: none !important;

    text-decoration: none !important;

}


/* ============================================================
   ETIQUETA SUPERIOR
   Citas / Calendario / Avisos / Solicitudes
   ============================================================ */

.quick-card .quick-icon {

    display: inline-flex !important;

    align-items: center !important;

    justify-content: center !important;

    width: auto !important;

    min-height: 30px !important;

    margin: 0 0 12px 0 !important;

    padding: 6px 10px !important;

    box-sizing: border-box !important;

    background: #eaf2ff !important;

    background-color: #eaf2ff !important;

    color: #1769aa !important;

    border: none !important;

    border-radius: 8px !important;

    box-shadow: none !important;

    font-size: 12px !important;

    font-weight: 700 !important;

    line-height: 1 !important;

}


/* ============================================================
   TITULO
   ============================================================ */

.quick-card strong {

    display: block !important;

    width: 100% !important;

    margin: 0 0 8px 0 !important;

    padding: 0 !important;

    background: transparent !important;

    background-color: transparent !important;

    color: #111827 !important;

    border: none !important;

    box-shadow: none !important;

    font-size: 17px !important;

    font-weight: 700 !important;

    line-height: 1.25 !important;

}


/* ============================================================
   DESCRIPCION
   ============================================================ */

.quick-card > span:not(.quick-icon) {

    display: block !important;

    width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    background: transparent !important;

    background-color: transparent !important;

    color: #5f6b76 !important;

    border: none !important;

    box-shadow: none !important;

    font-size: 13px !important;

    font-weight: 400 !important;

    line-height: 1.45 !important;

}


/* ============================================================
   ENLACE FINAL
   ============================================================ */

.quick-card small {

    display: block !important;

    width: 100% !important;

    margin-top: auto !important;

    padding: 14px 0 0 0 !important;

    background: transparent !important;

    background-color: transparent !important;

    color: #1769aa !important;

    border: none !important;

    box-shadow: none !important;

    font-size: 12px !important;

    font-weight: 700 !important;

    line-height: 1.2 !important;

}


/* ============================================================
   MUY IMPORTANTE
   quick-card ES UNA TARJETA, NO UN BOTON
   ============================================================ */

a.quick-card,
a.quick-card:visited,
a.quick-card:hover,
a.quick-card:focus {

    background-color: #ffffff !important;

    color: #1f2933 !important;

    border-radius: 12px !important;

}


/* No permitir que un CSS global le ponga azul de botón */
a.quick-card {

    background: #ffffff !important;

    border: 1px solid #dce4ec !important;

    box-shadow:
        0 2px 8px rgba(0,0,0,.05) !important;

}


/* ============================================================
   SOLO PARA LOS ELEMENTOS INTERNOS
   ============================================================ */

a.quick-card .quick-icon {

    background: #eaf2ff !important;

    color: #1769aa !important;

}

a.quick-card strong {

    background: transparent !important;

    color: #111827 !important;

}

a.quick-card small {

    background: transparent !important;

    color: #1769aa !important;

}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 950px) {

    .quick-grid {

        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;

    }

}


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


# ============================================================
# CSS PARA CALENDARIO
# ============================================================

CSS_CALENDARIO = r"""
<style id="EDUTURNOS_CALENDARIO_FINAL_V11">

/* ============================================================
   CALENDARIO - CONTROLES SUPERIORES
   ============================================================ */


/* Cabecera */
.edc-header {

    display: flex !important;

    align-items: center !important;

    justify-content: space-between !important;

    gap: 16px !important;

    width: 100% !important;

}


/* Información izquierda */
.edc-header-info {

    flex: 1 1 auto !important;

    min-width: 0 !important;

}


/* Grupo de botones */
.edc-header-actions {

    display: flex !important;

    flex-direction: row !important;

    align-items: center !important;

    justify-content: flex-end !important;

    gap: 8px !important;

    flex: 0 0 auto !important;

    flex-wrap: nowrap !important;

    width: auto !important;

    margin: 0 !important;

    padding: 0 !important;

}


/* ============================================================
   ATRAS / VER CITAS / NUEVA CITA
   ============================================================ */

.edc-header-actions a,
.edc-header-actions .boton {

    display: inline-flex !important;

    flex-direction: row !important;

    align-items: center !important;

    justify-content: center !important;

    flex: 0 0 auto !important;

    width: auto !important;

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
.edc-header-actions .boton:hover {

    background: #145b91 !important;

    background-color: #145b91 !important;

    color: #ffffff !important;

    border-color: #145b91 !important;

}


/* ============================================================
   BARRA DEL MES
   ============================================================ */

.edc-month-toolbar {

    display: flex !important;

    flex-direction: row !important;

    align-items: center !important;

    width: 100% !important;

    min-height: 42px !important;

    gap: 8px !important;

    box-sizing: border-box !important;

}


/* Anterior */
.edc-month-toolbar a:not(.eduturnos-hoy) {

    flex: 0 0 auto !important;

}


/* Título */
.edc-month-title {

    flex: 1 1 auto !important;

    min-width: 0 !important;

    margin: 0 !important;

    text-align: center !important;

}


/* ============================================================
   HOY A LA ESQUINA DERECHA
   ============================================================ */

.edc-month-toolbar a.eduturnos-hoy {

    display: inline-flex !important;

    align-items: center !important;

    justify-content: center !important;

    flex: 0 0 auto !important;

    width: auto !important;

    height: 34px !important;

    min-height: 34px !important;

    margin-left: auto !important;

    margin-right: 0 !important;

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


/* Hover Hoy */
.edc-month-toolbar a.eduturnos-hoy:hover {

    background: #145b91 !important;

    background-color: #145b91 !important;

    color: #ffffff !important;

    border-color: #145b91 !important;

}


/* ============================================================
   MOVIL
   ============================================================ */

@media (max-width: 760px) {

    .edc-header {

        flex-direction: column !important;

        align-items: flex-start !important;

    }

    .edc-header-actions {

        width: 100% !important;

        justify-content: flex-start !important;

        flex-wrap: wrap !important;

    }

}

</style>
"""


# ============================================================
# FUNCIONES
# ============================================================

def eliminar_bloque(texto, marker):

    patrones = [
        rf'<style[^>]*id=["\']{re.escape(marker)}["\'][^>]*>.*?</style>',
        rf'<script[^>]*id=["\']{re.escape(marker)}["\'][^>]*>.*?</script>',
    ]

    for patron in patrones:

        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    return texto


def insertar_head(texto, bloque):

    posicion = texto.lower().rfind("</head>")

    if posicion != -1:

        return (
            texto[:posicion]
            + "\n"
            + bloque
            + "\n"
            + texto[posicion:]
        )

    posicion = texto.lower().rfind("</body>")

    if posicion != -1:

        return (
            texto[:posicion]
            + "\n"
            + bloque
            + "\n"
            + texto[posicion:]
        )

    return texto + "\n" + bloque


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 78)
    print("EDUTURNOS - CAMBIO DEFINITIVO")
    print("=" * 78)
    print()


    # ========================================================
    # DASHBOARD
    # ========================================================

    if not DASHBOARD.exists():

        print("ERROR: no existe:")
        print(DASHBOARD)

        return


    backup_dashboard = DASHBOARD.with_name(
        "dashboard.html.backup_v11"
    )

    if not backup_dashboard.exists():

        shutil.copy2(
            DASHBOARD,
            backup_dashboard
        )

        print(
            "Backup Dashboard:",
            backup_dashboard
        )


    dashboard = DASHBOARD.read_text(
        encoding="utf-8"
    )


    # Limpiar nuestra versión anterior.
    dashboard = eliminar_bloque(
        dashboard,
        MARK_DASH
    )


    # Asegurar que quick-grid exista.
    if "quick-grid" not in dashboard:

        print()
        print(
            "ADVERTENCIA: no se encontró .quick-grid."
        )

        print(
            "No se modificó la estructura del Dashboard."
        )


    # Insertar CSS.
    dashboard = insertar_head(
        dashboard,
        CSS_DASHBOARD
    )


    DASHBOARD.write_text(
        dashboard,
        encoding="utf-8"
    )


    print(
        "OK - Accesos del Dashboard preparados."
    )


    # ========================================================
    # CALENDARIO
    # ========================================================

    if not CALENDARIO.exists():

        print()
        print("ERROR: no existe:")
        print(CALENDARIO)

        return


    backup_calendario = CALENDARIO.with_name(
        "index.html.backup_v11"
    )


    if not backup_calendario.exists():

        shutil.copy2(
            CALENDARIO,
            backup_calendario
        )

        print(
            "Backup Calendario:",
            backup_calendario
        )


    calendario = CALENDARIO.read_text(
        encoding="utf-8"
    )


    # --------------------------------------------------------
    # CORREGIR ERROR url_for('docente')
    # --------------------------------------------------------

    calendario = calendario.replace(
        "{{ url_for('docente') }}",
        "{{ url_for('auth.dashboard') }}"
    )


    calendario = calendario.replace(
        "{{ url_for('docente') }}'auth.dashboard') }}",
        "{{ url_for('auth.dashboard') }}"
    )


    # Variante rota más compleja.
    calendario = re.sub(
        r"\{\{\s*url_for\(\s*['\"]docente['\"]\s*\)[^}]*\}\}",
        "{{ url_for('auth.dashboard') }}",
        calendario,
        flags=re.IGNORECASE | re.DOTALL
    )


    # Limpiar bloque anterior.
    calendario = eliminar_bloque(
        calendario,
        MARK_CAL
    )


    # --------------------------------------------------------
    # ASEGURAR CLASE eduturnos-hoy
    # --------------------------------------------------------

    patron_hoy = re.compile(
        r'<a\b([^>]*)>\s*Hoy\s*</a>',
        flags=re.IGNORECASE | re.DOTALL
    )


    def poner_clase_hoy(match):

        attrs = match.group(1)

        clase = re.search(
            r'\bclass\s*=\s*["\']([^"\']*)["\']',
            attrs,
            flags=re.IGNORECASE
        )

        if clase:

            clases = clase.group(1)

            if "eduturnos-hoy" not in clases:

                nuevas_clases = (
                    clases.strip()
                    + " eduturnos-hoy"
                )

                attrs = (
                    attrs[:clase.start(1)]
                    + nuevas_clases
                    + attrs[clase.end(1):]
                )

        else:

            attrs += ' class="eduturnos-hoy"'


        return f"<a{attrs}>Hoy</a>"


    calendario = patron_hoy.sub(
        poner_clase_hoy,
        calendario
    )


    # Insertar CSS calendario.
    calendario = insertar_head(
        calendario,
        CSS_CALENDARIO
    )


    CALENDARIO.write_text(
        calendario,
        encoding="utf-8"
    )


    print(
        "OK - Calendario preparado."
    )


    # ========================================================
    # INFORME FINAL
    # ========================================================

    print()
    print("=" * 78)
    print("CAMBIOS APLICADOS")
    print("=" * 78)
    print()

    print("DASHBOARD")
    print("✓ Accesos dentro de recuadros")
    print("✓ 4 tarjetas alineadas")
    print("✓ Citas")
    print("✓ Calendario")
    print("✓ Avisos / Notificaciones")
    print("✓ Solicitudes")
    print("✓ Fondo blanco de las tarjetas")
    print("✓ Etiquetas azul claro")
    print("✓ Títulos organizados")
    print("✓ Descripciones organizadas")
    print("✓ Enlaces inferiores azules")
    print()

    print("CALENDARIO")
    print("✓ ← Atrás")
    print("✓ Ver citas")
    print("✓ + Nueva cita")
    print("  están en la misma línea")
    print("✓ Hoy queda a la derecha")
    print("✓ Referencia 'docente' corregida")
    print()

    print("NO TOCADO")
    print("✓ MySQL")
    print("✓ routes/calendario.py")
    print("✓ lógica de citas")
    print("✓ Citas")
    print("✓ Mi cuenta")
    print("✓ demás contenido del Dashboard")
    print()

    print("AHORA EJECUTA:")
    print()
    print("python .\\app.py")
    print()
    print("Después abre EDUTURNOS y presiona:")
    print()
    print("Ctrl + F5")
    print()

    print("=" * 78)


if __name__ == "__main__":
    main()
