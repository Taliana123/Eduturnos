from pathlib import Path
import re

# ============================================================
# EDUTURNOS - CONFIGURACIÓN GLOBAL DE LISTAS
# ============================================================

BASE = Path(__file__).resolve().parent

TEMPLATES = BASE / "templates"
STATIC_CSS = BASE / "static" / "css"
STATIC_JS = BASE / "static" / "js"


CSS_FILE = STATIC_CSS / "listas_eduturnos.css"
JS_FILE = STATIC_JS / "listas_eduturnos.js"


CSS_CONTENT = r"""
/* =========================================================
   EDUTURNOS - LISTAS DESPLEGABLES
   ========================================================= */

select.eduturnos-lista {
    width: 100%;
    min-height: 46px;
    padding: 10px 42px 10px 14px;

    border: 1px solid #cbd5e1;
    border-radius: 10px;

    background-color: #ffffff;
    color: #1e293b;

    font-family: inherit;
    font-size: 15px;

    cursor: pointer;

    appearance: auto;
    -webkit-appearance: auto;
    -moz-appearance: auto;

    box-sizing: border-box;
}

select.eduturnos-lista:hover {
    border-color: #2563eb;
}

select.eduturnos-lista:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

/*
   Cuando la lista está en estado inicial:
   no se muestra ningún texto.
*/
select.eduturnos-lista.eduturnos-vacio {
    color: transparent;
}

/*
   Las opciones reales conservan su texto normal.
*/
select.eduturnos-lista option {
    color: #1e293b;
    background: #ffffff;
}

/*
   La opción vacía no debe tener texto.
*/
select.eduturnos-lista option[value=""] {
    color: transparent;
}

/*
   Campos deshabilitados.
*/
select.eduturnos-lista:disabled {
    background-color: #f8fafc;
    cursor: not-allowed;
    opacity: 0.8;
}
"""


JS_CONTENT = r"""
document.addEventListener("DOMContentLoaded", function () {

    const listas = document.querySelectorAll(
        "select.eduturnos-lista"
    );

    listas.forEach(function (select) {

        function actualizarEstado() {

            if (select.value === "") {
                select.classList.add("eduturnos-vacio");
            } else {
                select.classList.remove("eduturnos-vacio");
            }
        }

        actualizarEstado();

        select.addEventListener("change", function () {
            actualizarEstado();
        });
    });

});
"""


def agregar_clase_select(texto):
    """
    Agrega la clase eduturnos-lista a todos los select
    sin crear otro select ni duplicar elementos.
    """

    def reemplazar(match):
        atributos = match.group(1)

        # Si ya tiene la clase, no hacer nada.
        if re.search(
            r'\bclass\s*=\s*["\'][^"\']*\beduturnos-lista\b[^"\']*["\']',
            atributos,
            flags=re.IGNORECASE
        ):
            return "<select" + atributos + ">"

        # Si tiene class, agregar nuestra clase.
        patron_class = re.compile(
            r'(\bclass\s*=\s*["\'])([^"\']*)(["\'])',
            flags=re.IGNORECASE
        )

        if patron_class.search(atributos):
            atributos = patron_class.sub(
                lambda m: m.group(1)
                + m.group(2)
                + " eduturnos-lista"
                + m.group(3),
                atributos,
                count=1
            )
        else:
            atributos = atributos + ' class="eduturnos-lista"'

        return "<select" + atributos + ">"

    return re.sub(
        r"<select\b([^>]*)>",
        reemplazar,
        texto,
        flags=re.IGNORECASE
    )


def corregir_opciones_vacias(texto):
    """
    Convierte opciones iniciales tipo:
        Selecciona...
        Seleccione...
        Elige...
        Ninguno
        No definido
    en una opción realmente vacía.

    La opción queda disabled + hidden para evitar que aparezca
    como una opción seleccionable normal.
    """

    patrones = [
        r"Selecciona(?:r)?(?:\s+tu|\s+la|\s+el|\s+una|\s+un)?\s+[^<]*",
        r"Seleccione(?:\s+tu|\s+la|\s+el|\s+una|\s+un)?\s+[^<]*",
        r"Elige(?:\s+tu|\s+la|\s+el|\s+una|\s+un)?\s+[^<]*",
        r"Elegir(?:\s+tu|\s+la|\s+el|\s+una|\s+un)?\s+[^<]*",
        r"Ninguno",
        r"No definido",
    ]

    for patron in patrones:
        texto = re.sub(
            rf'<option([^>]*)>\s*{patron}\s*</option>',
            '<option value="" disabled hidden></option>',
            texto,
            flags=re.IGNORECASE
        )

    return texto


def eliminar_script_anterior(texto):
    """
    Elimina los scripts anteriores que intentaban crear
    desplegables personalizados y podían duplicar la interfaz.
    """

    rutas_antiguas = [
        "js/selects.js",
        "js/listas_eduturnos.js",
    ]

    for ruta in rutas_antiguas:
        patron = (
            r'<script[^>]+src=["\']'
            + re.escape("{{ url_for('static', filename='" + ruta + "') }}")
            + r'["\'][^>]*>\s*</script>'
        )

        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE
        )

    return texto


def agregar_recursos_base():
    """
    Hace que base.html cargue solamente el CSS y JS nuevos.
    """

    base_file = TEMPLATES / "base.html"

    if not base_file.exists():
        print("[ADVERTENCIA] No existe templates/base.html")
        return False

    texto = base_file.read_text(encoding="utf-8")

    original = texto

    # --------------------------------------------------------
    # Eliminar referencias antiguas
    # --------------------------------------------------------

    texto = eliminar_script_anterior(texto)

    # Eliminar posibles referencias anteriores al nuevo archivo
    texto = re.sub(
        r'<link[^>]+listas_eduturnos\.css[^>]*>\s*',
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
        r'<script[^>]+listas_eduturnos\.js[^>]*>\s*</script>\s*',
        "",
        texto,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Agregar CSS
    # --------------------------------------------------------

    etiqueta_css = (
        '<link rel="stylesheet" '
        'href="{{ url_for(\'static\', filename=\'css/listas_eduturnos.css\') }}">'
    )

    if "</head>" in texto:
        texto = texto.replace(
            "</head>",
            etiqueta_css + "\n</head>",
            1
        )
    else:
        print("[ADVERTENCIA] base.html no contiene </head>")

    # --------------------------------------------------------
    # Agregar JS
    # --------------------------------------------------------

    etiqueta_js = (
        '<script src="{{ url_for(\'static\', '
        "filename='js/listas_eduturnos.js') }}\"></script>"
    )

    if "</body>" in texto:
        texto = texto.replace(
            "</body>",
            etiqueta_js + "\n</body>",
            1
        )
    else:
        print("[ADVERTENCIA] base.html no contiene </body>")

    if texto != original:
        base_file.write_text(texto, encoding="utf-8")
        print("CORREGIDO: templates/base.html")
    else:
        print("base.html ya estaba configurado.")

    return True


def procesar_templates():
    """
    Aplica la clase a todos los select del proyecto.
    """

    if not TEMPLATES.exists():
        print("[ERROR] No existe la carpeta templates.")
        return

    archivos_modificados = 0
    listas_modificadas = 0

    for archivo in TEMPLATES.rglob("*.html"):

        try:
            texto = archivo.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"[ADVERTENCIA] No se pudo leer: {archivo}")
            continue

        original = texto

        cantidad_antes = len(
            re.findall(r"<select\b", texto, flags=re.IGNORECASE)
        )

        if cantidad_antes == 0:
            continue

        texto = agregar_clase_select(texto)
        texto = corregir_opciones_vacias(texto)

        if texto != original:

            archivo.write_text(texto, encoding="utf-8")

            archivos_modificados += 1
            listas_modificadas += cantidad_antes

            print(f"CORREGIDO: {archivo}")

    print()
    print(f"ARCHIVOS HTML MODIFICADOS: {archivos_modificados}")
    print(f"LISTAS DETECTADAS/MODIFICADAS: {listas_modificadas}")


def crear_archivos():

    STATIC_CSS.mkdir(
        parents=True,
        exist_ok=True
    )

    STATIC_JS.mkdir(
        parents=True,
        exist_ok=True
    )

    CSS_FILE.write_text(
        CSS_CONTENT.strip() + "\n",
        encoding="utf-8"
    )

    JS_FILE.write_text(
        JS_CONTENT.strip() + "\n",
        encoding="utf-8"
    )

    print(f"CREADO: {CSS_FILE}")
    print(f"CREADO: {JS_FILE}")


def main():

    print()
    print("=" * 60)
    print("EDUTURNOS - CONFIGURACIÓN DE LISTAS")
    print("=" * 60)
    print()

    crear_archivos()

    procesar_templates()

    agregar_recursos_base()

    print()
    print("=" * 60)
    print("PROCESO TERMINADO CORRECTAMENTE")
    print("=" * 60)
    print()
    print("Las listas conservarán un solo control.")
    print("No se crearán listas duplicadas.")
    print("Al inicio no mostrarán texto.")
    print("Al hacer clic aparecerán las opciones reales.")
    print("Después de seleccionar, aparecerá la opción elegida.")
    print()


if __name__ == "__main__":
    main()