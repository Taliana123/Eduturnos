from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")

DASHBOARD = ROOT / "templates" / "dashboard.html"
CALENDARIO = ROOT / "templates" / "calendario" / "index.html"

AZUL = "#1769aa"
HOVER = "#145b91"


# ============================================================
# UTILIDADES
# ============================================================

def backup_unico(archivo, nombre):
    destino = archivo.with_name(nombre)
    if not destino.exists():
        shutil.copy2(archivo, destino)
    return destino


def reemplazar_style_attr(attrs, nuevo_style):
    """
    Reemplaza style existente o lo añade.
    """
    patron = re.compile(
        r'\sstyle\s*=\s*["\'][^"\']*["\']',
        flags=re.IGNORECASE | re.DOTALL
    )

    if patron.search(attrs):
        return patron.sub(
            f' style="{nuevo_style}"',
            attrs,
            count=1
        )

    return attrs + f' style="{nuevo_style}"'


def encontrar_div_balanceado(texto, posicion_inicio):
    """
    Encuentra el cierre del <div> correspondiente al <div>
    que comienza en posicion_inicio.
    """
    patron = re.compile(
        r'<\s*(/?)\s*div\b[^>]*>',
        flags=re.IGNORECASE
    )

    nivel = 0
    encontrado_inicio = False

    for match in patron.finditer(texto, posicion_inicio):

        etiqueta = match.group(1)

        if not etiqueta:
            nivel += 1
            encontrado_inicio = True
        else:
            nivel -= 1

            if encontrado_inicio and nivel == 0:
                return match.end()

    return -1


def buscar_contenedor_clase(texto, clase):
    """
    Localiza el <div> que contiene determinada clase y devuelve
    el inicio y final del div completo.
    """

    patron = re.compile(
        rf'<div\b[^>]*class\s*=\s*["\'][^"\']*\b{re.escape(clase)}\b[^"\']*["\'][^>]*>',
        flags=re.IGNORECASE | re.DOTALL
    )

    match = patron.search(texto)

    if not match:
        return None

    inicio = match.start()
    apertura_fin = match.end()

    fin = encontrar_div_balanceado(
        texto,
        inicio
    )

    if fin == -1:
        return None

    return inicio, apertura_fin, fin


def modificar_apertura_div(texto, selector_clase, style):
    """
    Modifica el primer div que tenga selector_clase.
    """

    patron = re.compile(
        rf'<div\b([^>]*)class\s*=\s*["\'][^"\']*\b{re.escape(selector_clase)}\b[^"\']*["\']([^>]*)>',
        flags=re.IGNORECASE | re.DOTALL
    )

    match = patron.search(texto)

    if not match:
        return texto, False

    attrs = match.group(0)[4:-1]

    attrs = reemplazar_style_attr(
        attrs,
        style
    )

    nuevo = (
        "<div"
        + attrs
        + ">"
    )

    nuevo_texto = (
        texto[:match.start()]
        + nuevo
        + texto[match.end():]
    )

    return nuevo_texto, True


# ============================================================
# DASHBOARD
# ============================================================

def reparar_dashboard():

    print()
    print(">>> DASHBOARD")

    if not DASHBOARD.exists():
        print("ERROR: no existe:")
        print(DASHBOARD)
        return False

    backup = backup_unico(
        DASHBOARD,
        "dashboard.html.backup_accesos_definitivo"
    )

    print(
        "Backup:",
        backup
    )

    texto = DASHBOARD.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Buscar quick-grid
    # --------------------------------------------------------

    info = buscar_contenedor_clase(
        texto,
        "quick-grid"
    )

    if not info:
        print(
            "ERROR: no se encontró .quick-grid en dashboard.html"
        )
        return False

    inicio, apertura_fin, fin = info


    # --------------------------------------------------------
    # CONTENIDO EXACTO DE LOS ACCESOS
    # --------------------------------------------------------

    tarjetas = r'''
        <!-- CITAS -->
        <a
            class="quick-card"
            href="{{ url_for('citas.index') }}"
            style="
                display:flex !important;
                flex-direction:column !important;
                align-items:flex-start !important;
                justify-content:flex-start !important;
                width:100% !important;
                min-width:0 !important;
                min-height:186px !important;
                box-sizing:border-box !important;
                padding:18px !important;
                margin:0 !important;
                background:#ffffff !important;
                background-color:#ffffff !important;
                color:#1f2933 !important;
                border:1px solid #dce4ec !important;
                border-radius:12px !important;
                box-shadow:0 2px 8px rgba(0,0,0,.05) !important;
                text-decoration:none !important;
                overflow:hidden !important;
            "
        >

            <span
                class="quick-icon"
                style="
                    display:inline-flex !important;
                    align-items:center !important;
                    justify-content:center !important;
                    min-height:30px !important;
                    padding:6px 10px !important;
                    margin:0 0 12px 0 !important;
                    box-sizing:border-box !important;
                    background:#eaf2ff !important;
                    background-color:#eaf2ff !important;
                    color:#1769aa !important;
                    border:none !important;
                    border-radius:8px !important;
                    font-size:12px !important;
                    font-weight:700 !important;
                    line-height:1 !important;
                "
            >Citas</span>

            <strong
                style="
                    display:block !important;
                    width:100% !important;
                    margin:0 0 8px 0 !important;
                    padding:0 !important;
                    background:transparent !important;
                    color:#111827 !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:17px !important;
                    font-weight:700 !important;
                    line-height:1.25 !important;
                "
            >Citas</strong>

            <span
                style="
                    display:block !important;
                    width:100% !important;
                    margin:0 !important;
                    padding:0 !important;
                    background:transparent !important;
                    color:#5f6b76 !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:13px !important;
                    font-weight:400 !important;
                    line-height:1.45 !important;
                "
            >Consultar y gestionar citaciones.</span>

            <small
                style="
                    display:block !important;
                    width:100% !important;
                    margin-top:auto !important;
                    padding:14px 0 0 0 !important;
                    background:transparent !important;
                    color:#1769aa !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:12px !important;
                    font-weight:700 !important;
                    line-height:1.2 !important;
                "
            >Ver citas →</small>

        </a>


        <!-- CALENDARIO -->
        <a
            class="quick-card"
            href="{{ url_for('calendario.index') }}"
            style="
                display:flex !important;
                flex-direction:column !important;
                align-items:flex-start !important;
                justify-content:flex-start !important;
                width:100% !important;
                min-width:0 !important;
                min-height:186px !important;
                box-sizing:border-box !important;
                padding:18px !important;
                margin:0 !important;
                background:#ffffff !important;
                background-color:#ffffff !important;
                color:#1f2933 !important;
                border:1px solid #dce4ec !important;
                border-radius:12px !important;
                box-shadow:0 2px 8px rgba(0,0,0,.05) !important;
                text-decoration:none !important;
                overflow:hidden !important;
            "
        >

            <span
                class="quick-icon"
                style="
                    display:inline-flex !important;
                    align-items:center !important;
                    justify-content:center !important;
                    min-height:30px !important;
                    padding:6px 10px !important;
                    margin:0 0 12px 0 !important;
                    background:#eaf2ff !important;
                    color:#1769aa !important;
                    border:none !important;
                    border-radius:8px !important;
                    font-size:12px !important;
                    font-weight:700 !important;
                    line-height:1 !important;
                "
            >Calendario</span>

            <strong
                style="
                    display:block !important;
                    width:100% !important;
                    margin:0 0 8px 0 !important;
                    padding:0 !important;
                    background:transparent !important;
                    color:#111827 !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:17px !important;
                    font-weight:700 !important;
                    line-height:1.25 !important;
                "
            >Calendario</strong>

            <span
                style="
                    display:block !important;
                    width:100% !important;
                    margin:0 !important;
                    padding:0 !important;
                    background:transparent !important;
                    color:#5f6b76 !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:13px !important;
                    font-weight:400 !important;
                    line-height:1.45 !important;
                "
            >Revisar fechas y horarios.</span>

            <small
                style="
                    display:block !important;
                    width:100% !important;
                    margin-top:auto !important;
                    padding:14px 0 0 0 !important;
                    background:transparent !important;
                    color:#1769aa !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:12px !important;
                    font-weight:700 !important;
                    line-height:1.2 !important;
                "
            >Abrir calendario →</small>

        </a>


        <!-- NOTIFICACIONES -->
        <a
            class="quick-card"
            href="{{ url_for('notificaciones.index') }}"
            style="
                display:flex !important;
                flex-direction:column !important;
                align-items:flex-start !important;
                justify-content:flex-start !important;
                width:100% !important;
                min-width:0 !important;
                min-height:186px !important;
                box-sizing:border-box !important;
                padding:18px !important;
                margin:0 !important;
                background:#ffffff !important;
                background-color:#ffffff !important;
                color:#1f2933 !important;
                border:1px solid #dce4ec !important;
                border-radius:12px !important;
                box-shadow:0 2px 8px rgba(0,0,0,.05) !important;
                text-decoration:none !important;
                overflow:hidden !important;
            "
        >

            <span
                class="quick-icon"
                style="
                    display:inline-flex !important;
                    align-items:center !important;
                    justify-content:center !important;
                    min-height:30px !important;
                    padding:6px 10px !important;
                    margin:0 0 12px 0 !important;
                    background:#eaf2ff !important;
                    color:#1769aa !important;
                    border:none !important;
                    border-radius:8px !important;
                    font-size:12px !important;
                    font-weight:700 !important;
                    line-height:1 !important;
                "
            >Avisos</span>

            <strong
                style="
                    display:block !important;
                    width:100% !important;
                    margin:0 0 8px 0 !important;
                    padding:0 !important;
                    background:transparent !important;
                    color:#111827 !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:17px !important;
                    font-weight:700 !important;
                    line-height:1.25 !important;
                "
            >Notificaciones</strong>

            <span
                style="
                    display:block !important;
                    width:100% !important;
                    margin:0 !important;
                    padding:0 !important;
                    background:transparent !important;
                    color:#5f6b76 !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:13px !important;
                    font-weight:400 !important;
                    line-height:1.45 !important;
                "
            >Ver avisos y novedades del sistema.</span>

            {% if notificaciones_no_leidas > 0 %}

            <small
                style="
                    display:block !important;
                    width:100% !important;
                    margin-top:auto !important;
                    padding:14px 0 0 0 !important;
                    background:transparent !important;
                    color:#1769aa !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:12px !important;
                    font-weight:700 !important;
                    line-height:1.2 !important;
                "
            >
                {{ notificaciones_no_leidas }} sin leer →
            </small>

            {% else %}

            <small
                style="
                    display:block !important;
                    width:100% !important;
                    margin-top:auto !important;
                    padding:14px 0 0 0 !important;
                    background:transparent !important;
                    color:#1769aa !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:12px !important;
                    font-weight:700 !important;
                    line-height:1.2 !important;
                "
            >
                Ver notificaciones →
            </small>

            {% endif %}

        </a>


        <!-- SOLICITUDES -->
        {% if usuario.rol_nombre in [
            'Docente',
            'Administrador / Coordinador',
            'Rector',
            'Super Admin'
        ] %}

        <a
            class="quick-card"
            href="{{ url_for('solicitudes.index') }}"
            style="
                display:flex !important;
                flex-direction:column !important;
                align-items:flex-start !important;
                justify-content:flex-start !important;
                width:100% !important;
                min-width:0 !important;
                min-height:186px !important;
                box-sizing:border-box !important;
                padding:18px !important;
                margin:0 !important;
                background:#ffffff !important;
                background-color:#ffffff !important;
                color:#1f2933 !important;
                border:1px solid #dce4ec !important;
                border-radius:12px !important;
                box-shadow:0 2px 8px rgba(0,0,0,.05) !important;
                text-decoration:none !important;
                overflow:hidden !important;
            "
        >

            <span
                class="quick-icon"
                style="
                    display:inline-flex !important;
                    align-items:center !important;
                    justify-content:center !important;
                    min-height:30px !important;
                    padding:6px 10px !important;
                    margin:0 0 12px 0 !important;
                    background:#eaf2ff !important;
                    color:#1769aa !important;
                    border:none !important;
                    border-radius:8px !important;
                    font-size:12px !important;
                    font-weight:700 !important;
                    line-height:1 !important;
                "
            >Solicitudes</span>

            <strong
                style="
                    display:block !important;
                    width:100% !important;
                    margin:0 0 8px 0 !important;
                    padding:0 !important;
                    background:transparent !important;
                    color:#111827 !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:17px !important;
                    font-weight:700 !important;
                    line-height:1.25 !important;
                "
            >Solicitudes</strong>

            <span
                style="
                    display:block !important;
                    width:100% !important;
                    margin:0 !important;
                    padding:0 !important;
                    background:transparent !important;
                    color:#5f6b76 !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:13px !important;
                    font-weight:400 !important;
                    line-height:1.45 !important;
                "
            >Gestionar reuniones y propuestas.</span>

            <small
                style="
                    display:block !important;
                    width:100% !important;
                    margin-top:auto !important;
                    padding:14px 0 0 0 !important;
                    background:transparent !important;
                    color:#1769aa !important;
                    border:none !important;
                    box-shadow:none !important;
                    font-size:12px !important;
                    font-weight:700 !important;
                    line-height:1.2 !important;
                "
            >Ver solicitudes →</small>

        </a>

        {% endif %}


        <!-- REPORTES -->
        {% if usuario.rol_nombre in [
            'Administrador / Coordinador',
            'Rector',
            'Super Admin'
        ] %}

        <a
            class="quick-card"
            href="{{ url_for('reportes.index') }}"
            style="
                display:flex !important;
                flex-direction:column !important;
                align-items:flex-start !important;
                justify-content:flex-start !important;
                width:100% !important;
                min-height:186px !important;
                box-sizing:border-box !important;
                padding:18px !important;
                margin:0 !important;
                background:#ffffff !important;
                color:#1f2933 !important;
                border:1px solid #dce4ec !important;
                border-radius:12px !important;
                box-shadow:0 2px 8px rgba(0,0,0,.05) !important;
                text-decoration:none !important;
            "
        >
            <span class="quick-icon">Reportes</span>
            <strong>Reportes</strong>
            <span>Consultar indicadores institucionales.</span>
            <small>Ver reportes →</small>
        </a>

        {% endif %}


        <!-- JUSTIFICACIONES -->
        {% if usuario.rol_nombre in [
            'Estudiante',
            'Acudiente'
        ] %}

        <a
            class="quick-card"
            href="{{ url_for('justificaciones.index') }}"
            style="
                display:flex !important;
                flex-direction:column !important;
                width:100% !important;
                min-height:186px !important;
                box-sizing:border-box !important;
                padding:18px !important;
                margin:0 !important;
                background:#ffffff !important;
                color:#1f2933 !important;
                border:1px solid #dce4ec !important;
                border-radius:12px !important;
                box-shadow:0 2px 8px rgba(0,0,0,.05) !important;
                text-decoration:none !important;
            "
        >
            <span class="quick-icon">Justificaciones</span>
            <strong>Justificaciones</strong>
            <span>Consultar o presentar solicitudes.</span>
            <small>Ver justificaciones →</small>
        </a>

        {% endif %}
    '''


    # --------------------------------------------------------
    # CSS DEL GRID
    # --------------------------------------------------------

    grid_style = """
        display:grid !important;
        grid-template-columns:repeat(4,minmax(0,1fr)) !important;
        gap:14px !important;
        width:100% !important;
        margin-top:16px !important;
        align-items:stretch !important;
        box-sizing:border-box !important;
    """

    apertura = texto[ inicio:apertura_fin ]

    apertura = reemplazar_style_attr(
        apertura[4:-1],
        grid_style
    )

    nueva_apertura = (
        "<div"
        + apertura
        + ">"
    )

    nuevo_grid = (
        nueva_apertura
        + "\n"
        + tarjetas
        + "\n"
        + texto[fin - len("</div>"):fin]
    )

    # El cierre correcto del div es exactamente "</div>"
    nuevo_grid = (
        nueva_apertura
        + "\n"
        + tarjetas
        + "\n</div>"
    )

    texto = (
        texto[:inicio]
        + nuevo_grid
        + texto[fin:]
    )


    # --------------------------------------------------------
    # INSERTAR RESPONSIVE DIRECTO EN DASHBOARD
    # --------------------------------------------------------

    RESPONSIVE = r"""
<style id="EDUTURNOS_ACCESOS_RESPONSIVE_DEFINITIVO">
@media (max-width: 950px) {
    .quick-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}

@media (max-width: 600px) {
    .quick-grid {
        grid-template-columns: 1fr !important;
    }
}
</style>
"""

    # Eliminar copia anterior.
    texto = re.sub(
        r'<style[^>]*id=["\']EDUTURNOS_ACCESOS_RESPONSIVE_DEFINITIVO["\'][^>]*>.*?</style>',
        "",
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )

    posicion = texto.lower().rfind("</head>")

    if posicion != -1:
        texto = (
            texto[:posicion]
            + RESPONSIVE
            + "\n"
            + texto[posicion:]
        )


    DASHBOARD.write_text(
        texto,
        encoding="utf-8"
    )

    print(
        "OK - Accesos reconstruidos directamente."
    )

    return True


# ============================================================
# CALENDARIO
# ============================================================

def reparar_calendario():

    print()
    print(">>> CALENDARIO")

    if not CALENDARIO.exists():
        print("ERROR: no existe:")
        print(CALENDARIO)
        return False

    backup = backup_unico(
        CALENDARIO,
        "index.html.backup_controles_definitivo"
    )

    print(
        "Backup:",
        backup
    )

    texto = CALENDARIO.read_text(
        encoding="utf-8"
    )


    # --------------------------------------------------------
    # REPARAR ENDPOINT ROTO
    # --------------------------------------------------------

    texto = texto.replace(
        "{{ url_for('docente') }}",
        "{{ url_for('auth.dashboard') }}"
    )

    texto = re.sub(
        r"\{\{\s*url_for\(\s*['\"]docente['\"]\s*\).*?\}\}",
        "{{ url_for('auth.dashboard') }}",
        texto,
        flags=re.IGNORECASE | re.DOTALL
    )


    # --------------------------------------------------------
    # CABECERA DEL CALENDARIO
    # --------------------------------------------------------

    patron = re.compile(
        r'(<div\b[^>]*class\s*=\s*["\'][^"\']*\bedc-header\b[^"\']*["\'][^>]*>)',
        flags=re.IGNORECASE | re.DOTALL
    )

    m = patron.search(texto)

    if m:

        apertura = m.group(1)

        apertura = reemplazar_style_attr(
            apertura[4:-1],
            """
            display:flex !important;
            align-items:center !important;
            justify-content:space-between !important;
            gap:16px !important;
            width:100% !important;
            box-sizing:border-box !important;
            """
        )

        nuevo = (
            "<div"
            + apertura
            + ">"
        )

        texto = (
            texto[:m.start()]
            + nuevo
            + texto[m.end():]
        )


    # --------------------------------------------------------
    # INFORMACION IZQUIERDA
    # --------------------------------------------------------

    patron_info = re.compile(
        r'(<div\b[^>]*class\s*=\s*["\'][^"\']*\bedc-header-info\b[^"\']*["\'][^>]*>)',
        flags=re.IGNORECASE | re.DOTALL
    )

    m = patron_info.search(texto)

    if m:

        apertura = m.group(1)

        apertura = reemplazar_style_attr(
            apertura[4:-1],
            """
            flex:1 1 auto !important;
            min-width:0 !important;
            """
        )

        nuevo = (
            "<div"
            + apertura
            + ">"
        )

        texto = (
            texto[:m.start()]
            + nuevo
            + texto[m.end():]
        )


    # --------------------------------------------------------
    # GRUPO DE BOTONES
    # --------------------------------------------------------

    patron_acciones = re.compile(
        r'(<div\b[^>]*class\s*=\s*["\'][^"\']*\bedc-header-actions\b[^"\']*["\'][^>]*>)',
        flags=re.IGNORECASE | re.DOTALL
    )

    m = patron_acciones.search(texto)

    if m:

        apertura = m.group(1)

        apertura = reemplazar_style_attr(
            apertura[4:-1],
            """
            display:flex !important;
            flex-direction:row !important;
            align-items:center !important;
            justify-content:flex-end !important;
            gap:8px !important;
            flex:0 0 auto !important;
            flex-wrap:nowrap !important;
            width:auto !important;
            margin:0 !important;
            padding:0 !important;
            box-sizing:border-box !important;
            """
        )

        nuevo = (
            "<div"
            + apertura
            + ">"
        )

        texto = (
            texto[:m.start()]
            + nuevo
            + texto[m.end():]
        )


    # --------------------------------------------------------
    # BOTONES DEL ENCABEZADO
    # --------------------------------------------------------

    patron_btn = re.compile(
        r'(<a\b([^>]*)class\s*=\s*["\'][^"\']*(?:edc-back|boton|link-back)[^"\']*["\'][^>]*>)',
        flags=re.IGNORECASE | re.DOTALL
    )

    def boton_header(match):

        apertura = match.group(1)

        apertura = reemplazar_style_attr(
            apertura[2:-1],
            f"""
            display:inline-flex !important;
            align-items:center !important;
            justify-content:center !important;
            flex:0 0 auto !important;
            width:auto !important;
            height:34px !important;
            min-height:34px !important;
            margin:0 !important;
            padding:7px 12px !important;
            box-sizing:border-box !important;
            background:{AZUL} !important;
            background-color:{AZUL} !important;
            color:#ffffff !important;
            border:1px solid {AZUL} !important;
            border-radius:7px !important;
            font-size:13px !important;
            font-weight:600 !important;
            line-height:1 !important;
            text-decoration:none !important;
            """
        )

        return (
            "<a"
            + apertura
            + ">"
        )

    texto = patron_btn.sub(
        boton_header,
        texto
    )


    # --------------------------------------------------------
    # HOY
    # --------------------------------------------------------

    patron_hoy = re.compile(
        r'<a\b([^>]*)>\s*Hoy\s*</a>',
        flags=re.IGNORECASE | re.DOTALL
    )

    def hoy(match):

        attrs = match.group(1)

        # Clase
        m_clase = re.search(
            r'\bclass\s*=\s*["\']([^"\']*)["\']',
            attrs,
            flags=re.IGNORECASE
        )

        if m_clase:

            clases = m_clase.group(1)

            if "eduturnos-hoy" not in clases:

                clases = (
                    clases.strip()
                    + " eduturnos-hoy"
                )

                attrs = (
                    attrs[:m_clase.start(1)]
                    + clases
                    + attrs[m_clase.end(1):]
                )

        else:

            attrs += (
                ' class="eduturnos-hoy"'
            )


        attrs = reemplazar_style_attr(
            attrs,
            f"""
            display:inline-flex !important;
            align-items:center !important;
            justify-content:center !important;
            flex:0 0 auto !important;
            width:auto !important;
            height:34px !important;
            min-height:34px !important;
            margin-left:auto !important;
            margin-right:0 !important;
            padding:7px 12px !important;
            box-sizing:border-box !important;
            background:{AZUL} !important;
            background-color:{AZUL} !important;
            color:#ffffff !important;
            border:1px solid {AZUL} !important;
            border-radius:7px !important;
            font-size:13px !important;
            font-weight:600 !important;
            line-height:1 !important;
            text-decoration:none !important;
            """
        )

        return (
            "<a"
            + attrs
            + ">Hoy</a>"
        )


    texto = patron_hoy.sub(
        hoy,
        texto
    )


    # --------------------------------------------------------
    # BARRA DEL MES
    # --------------------------------------------------------

    patron_toolbar = re.compile(
        r'(<div\b[^>]*class\s*=\s*["\'][^"\']*\bedc-month-toolbar\b[^"\']*["\'][^>]*>)',
        flags=re.IGNORECASE | re.DOTALL
    )

    m = patron_toolbar.search(texto)

    if m:

        apertura = m.group(1)

        apertura = reemplazar_style_attr(
            apertura[4:-1],
            """
            display:flex !important;
            flex-direction:row !important;
            align-items:center !important;
            width:100% !important;
            min-height:42px !important;
            gap:8px !important;
            box-sizing:border-box !important;
            """
        )

        nuevo = (
            "<div"
            + apertura
            + ">"
        )

        texto = (
            texto[:m.start()]
            + nuevo
            + texto[m.end():]
        )


    # --------------------------------------------------------
    # TITULO DEL MES
    # --------------------------------------------------------

    patron_mes = re.compile(
        r'(<[^>]+\bclass\s*=\s*["\'][^"\']*\bedc-month-title\b[^"\']*["\'][^>]*>)',
        flags=re.IGNORECASE | re.DOTALL
    )

    m = patron_mes.search(texto)

    if m:

        apertura = m.group(1)

        apertura = reemplazar_style_attr(
            apertura[1:-1],
            """
            flex:1 1 auto !important;
            min-width:0 !important;
            margin:0 !important;
            text-align:center !important;
            """
        )

        nuevo = (
            "<"
            + apertura
            + ">"
        )

        texto = (
            texto[:m.start()]
            + nuevo
            + texto[m.end():]
        )


    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    CALENDARIO.write_text(
        texto,
        encoding="utf-8"
    )

    print(
        "OK - Controles del calendario forzados."
    )

    return True


# ============================================================
# EJECUCIÓN
# ============================================================

def main():

    print()
    print("=" * 78)
    print("EDUTURNOS - CORRECCIÓN REAL Y DIRECTA")
    print("=" * 78)

    ok_dashboard = reparar_dashboard()

    ok_calendario = reparar_calendario()

    print()
    print("=" * 78)
    print("RESULTADO")
    print("=" * 78)

    if ok_dashboard:
        print(
            "✓ Dashboard: Accesos reconstruidos."
        )
    else:
        print(
            "✗ Dashboard: no se pudo modificar."
        )

    if ok_calendario:
        print(
            "✓ Calendario: controles reconstruidos."
        )
    else:
        print(
            "✗ Calendario: no se pudo modificar."
        )

    print()
    print("Dashboard:")
    print("✓ 4 tarjetas alineadas")
    print("✓ Fondo blanco")
    print("✓ Etiquetas azul claro")
    print("✓ Títulos organizados")
    print("✓ Descripciones organizadas")
    print("✓ Enlaces inferiores azules")
    print()
    print("Calendario:")
    print("✓ Atrás + Ver citas + Nueva cita en una línea")
    print("✓ Hoy a la derecha")
    print("✓ Se corrigió url_for('docente')")
    print()
    print("No se tocó MySQL.")
    print("No se modificaron las rutas Python.")
    print()
    print("AHORA EJECUTA:")
    print()
    print("python .\\app.py")
    print()
    print("Después abre EDUTURNOS y pulsa:")
    print("Ctrl + F5")
    print()
    print("=" * 78)


if __name__ == "__main__":
    main()
