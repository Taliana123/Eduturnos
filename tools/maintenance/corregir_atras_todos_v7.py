from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")
TEMPLATES = ROOT / "templates"

AZUL = "#1769aa"
HOVER = "#145b91"
BLANCO = "#ffffff"

ESTILO = (
    f"background:{AZUL} !important;"
    f"background-color:{AZUL} !important;"
    f"color:{BLANCO} !important;"
    f"border:1px solid {AZUL} !important;"
    f"border-radius:7px !important;"
    f"display:inline-flex !important;"
    f"align-items:center !important;"
    f"justify-content:center !important;"
    f"min-height:34px !important;"
    f"padding:7px 12px !important;"
    f"text-decoration:none !important;"
    f"font-weight:600 !important;"
    f"box-shadow:none !important;"
)

CSS = f"""
<style id="EDUTURNOS_ATRAS_TODOS_V7">

/* SOLO LOS BOTONES ATRÁS */
a.eduturnos-atras,
a.link-back,
a.edc-back {{
    background:{AZUL} !important;
    background-color:{AZUL} !important;
    color:{BLANCO} !important;
    border:1px solid {AZUL} !important;
    border-radius:7px !important;
    text-decoration:none !important;
    display:inline-flex !important;
    align-items:center !important;
    justify-content:center !important;
    min-height:34px !important;
    padding:7px 12px !important;
    font-weight:600 !important;
    box-shadow:none !important;
}}

a.eduturnos-atras:hover,
a.link-back:hover,
a.edc-back:hover {{
    background:{HOVER} !important;
    background-color:{HOVER} !important;
    color:{BLANCO} !important;
    border-color:{HOVER} !important;
}}

a.eduturnos-atras *,
a.link-back *,
a.edc-back * {{
    color:{BLANCO} !important;
}}

</style>
"""


def limpiar_version_anterior(texto):
    patrones = [
        r'<style[^>]*id=["\']EDUTURNOS_ATRAS_TODOS_V7["\'][^>]*>.*?</style>',
    ]

    for patron in patrones:
        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    return texto


def convertir_atras(texto):
    """
    Encuentra cualquier:
    <a ...>← Atrás</a>

    y le añade la clase eduturnos-atras
    y el estilo directo.
    """

    patron = re.compile(
        r'<a\b([^>]*)>\s*←\s*Atrás\s*</a>',
        re.IGNORECASE
    )

    cantidad = 0

    def reemplazar(match):
        nonlocal cantidad

        attrs = match.group(1)

        # Añadir clase.
        m_clase = re.search(
            r'\bclass\s*=\s*["\']([^"\']*)["\']',
            attrs,
            flags=re.IGNORECASE
        )

        if m_clase:
            clases = m_clase.group(1)

            if "eduturnos-atras" not in clases:
                nuevas_clases = (
                    clases.strip()
                    + " eduturnos-atras"
                )

                attrs = (
                    attrs[:m_clase.start(1)]
                    + nuevas_clases
                    + attrs[m_clase.end(1):]
                )
        else:
            attrs += ' class="eduturnos-atras"'

        # Añadir estilo directo.
        m_style = re.search(
            r'\bstyle\s*=\s*["\']([^"\']*)["\']',
            attrs,
            flags=re.IGNORECASE
        )

        if m_style:
            estilo_actual = m_style.group(1)

            nuevo_estilo = (
                estilo_actual.rstrip("; ")
                + ";"
                + ESTILO
            )

            attrs = (
                attrs[:m_style.start(1)]
                + nuevo_estilo
                + attrs[m_style.end(1):]
            )
        else:
            attrs += f' style="{ESTILO}"'

        cantidad += 1

        return f"<a{attrs}>← Atrás</a>"

    return patron.sub(reemplazar, texto), cantidad


def agregar_css(texto):
    texto = limpiar_version_anterior(texto)

    posicion = texto.lower().rfind("</head>")

    if posicion != -1:
        return (
            texto[:posicion]
            + "\n"
            + CSS
            + "\n"
            + texto[posicion:]
        )

    posicion = texto.lower().rfind("</body>")

    if posicion != -1:
        return (
            texto[:posicion]
            + "\n"
            + CSS
            + "\n"
            + texto[posicion:]
        )

    return texto + "\n" + CSS


def main():

    print()
    print("=" * 72)
    print("EDUTURNOS - CORREGIR TODOS LOS BOTONES ATRÁS")
    print("=" * 72)
    print()

    archivos = list(TEMPLATES.rglob("*.html"))

    encontrados = 0
    archivos_modificados = 0

    for archivo in archivos:

        if ".backup" in archivo.name.lower():
            continue

        try:
            original = archivo.read_text(
                encoding="utf-8"
            )
        except Exception:
            continue

        nuevo = original

        # Convertir TODOS los ← Atrás.
        nuevo, cantidad = convertir_atras(nuevo)

        # Añadir CSS solo de botón Atrás.
        nuevo = agregar_css(nuevo)

        if nuevo != original:

            backup = archivo.with_name(
                archivo.name + ".backup_atras_v7"
            )

            if not backup.exists():
                shutil.copy2(archivo, backup)

            archivo.write_text(
                nuevo,
                encoding="utf-8"
            )

            archivos_modificados += 1
            encontrados += cantidad

            print(
                "OK:",
                archivo.relative_to(ROOT),
                "| botones Atrás:",
                cantidad
            )

    print()
    print("=" * 72)
    print("CORRECCIÓN TERMINADA")
    print("=" * 72)
    print()
    print("Botones Atrás corregidos:", encontrados)
    print("Plantillas modificadas:", archivos_modificados)
    print()
    print("Fondo :", AZUL)
    print("Letra :", BLANCO)
    print("Hover :", HOVER)
    print()
    print("Esto corrige también:")
    print("← Atrás de Solicitudes de cita")
    print("← Atrás de Citas")
    print("← Atrás de Calendario")
    print("← Atrás de formularios")
    print("← Atrás de cualquier otra página")
    print()
    print("No se modifican textos normales ni títulos.")
    print("=" * 72)


if __name__ == "__main__":
    main()
