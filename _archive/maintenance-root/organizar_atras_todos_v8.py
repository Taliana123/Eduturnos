from pathlib import Path
import re
import shutil

ROOT = Path(r"F:\edu_Final")
TEMPLATES = ROOT / "templates"

MARCADOR = "EDUTURNOS_LAYOUT_ATRAS_V8"

CSS = r"""
<style id="EDUTURNOS_LAYOUT_ATRAS_V8">

/* =========================================================
   EDUTURNOS - ORGANIZACIÓN DEL BOTÓN ATRÁS
   El botón queda separado del título.
   ========================================================= */

/* Contenedor de navegación superior */
.page-navigation,
.form-top-actions,
.edc-header-actions {
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    width: 100% !important;
    margin-bottom: 14px !important;
}

/* Botón atrás */
.page-navigation .link-back,
.form-top-actions .link-back,
a.eduturnos-atras,
a.link-back,
a.edc-back {
    position: relative !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;

    float: none !important;
    clear: both !important;

    margin: 0 0 10px 0 !important;

    min-height: 34px !important;
    height: 34px !important;

    padding: 7px 12px !important;

    background: #1769aa !important;
    background-color: #1769aa !important;

    color: #ffffff !important;

    border: 1px solid #1769aa !important;
    border-radius: 7px !important;

    text-decoration: none !important;

    font-size: 13px !important;
    font-weight: 600 !important;
    line-height: 1 !important;

    box-shadow: none !important;
}

/* Título debajo del botón */
.page-navigation + h1,
.page-navigation + .section-heading,
.form-top-actions + .section-heading,
.edc-header-info {
    clear: both !important;
}

/* Cuando el botón está directamente antes del título */
a.eduturnos-atras + h1,
a.link-back + h1,
a.edc-back + h1 {
    margin-top: 8px !important;
}

/* Evitar superposición */
.page-head {
    position: relative !important;
}

.page-head .page-navigation {
    position: relative !important;
    z-index: 2 !important;
}

.page-head h1 {
    position: relative !important;
    z-index: 1 !important;
    clear: both !important;
}

/* En formularios */
.form-card .form-top-actions {
    margin-bottom: 16px !important;
}

.form-card .section-heading {
    clear: both !important;
}

/* En solicitudes, citas, calendario y páginas similares */
.edc-header {
    position: relative !important;
}

.edc-header .edc-header-actions {
    margin-bottom: 12px !important;
}

/* En pantallas pequeñas */
@media (max-width: 700px) {
    .page-navigation,
    .form-top-actions {
        margin-bottom: 12px !important;
    }

    .page-navigation .link-back,
    .form-top-actions .link-back,
    a.eduturnos-atras,
    a.link-back,
    a.edc-back {
        margin-bottom: 8px !important;
    }
}

</style>
"""


def limpiar_version(texto):
    patrones = [
        r'<style[^>]*id=["\']EDUTURNOS_LAYOUT_ATRAS_V8["\'][^>]*>.*?</style>',
    ]

    for patron in patrones:
        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL
        )

    return texto


def asegurar_clase_atras(attrs):
    m = re.search(
        r'\bclass\s*=\s*["\']([^"\']*)["\']',
        attrs,
        flags=re.IGNORECASE
    )

    if m:
        clases = m.group(1)

        if "eduturnos-atras" not in clases:
            nuevas = clases.strip() + " eduturnos-atras"

            attrs = (
                attrs[:m.start(1)]
                + nuevas
                + attrs[m.end(1):]
            )
    else:
        attrs += ' class="eduturnos-atras"'

    return attrs


def corregir_atras(texto):

    # Solo busca botones cuyo texto sea exactamente ← Atrás.
    patron = re.compile(
        r'<a\b([^>]*)>\s*←\s*Atrás\s*</a>',
        re.IGNORECASE
    )

    encontrados = 0

    def reemplazar(match):
        nonlocal encontrados

        attrs = asegurar_clase_atras(match.group(1))

        encontrados += 1

        return f'<a{attrs}>← Atrás</a>'

    texto = patron.sub(reemplazar, texto)

    return texto, encontrados


def insertar_css(texto):

    texto = limpiar_version(texto)

    pos = texto.lower().rfind("</head>")

    if pos != -1:
        return (
            texto[:pos]
            + "\n"
            + CSS
            + "\n"
            + texto[pos:]
        )

    return texto + "\n" + CSS


def main():

    print()
    print("=" * 72)
    print("EDUTURNOS - ORDENAR BOTONES ATRÁS")
    print("=" * 72)
    print()

    if not TEMPLATES.exists():
        print("ERROR: no existe:")
        print(TEMPLATES)
        return

    archivos = list(TEMPLATES.rglob("*.html"))

    total = 0
    modificados = 0

    for archivo in archivos:

        if ".backup" in archivo.name.lower():
            continue

        try:
            original = archivo.read_text(
                encoding="utf-8"
            )
        except Exception:
            continue

        nuevo, cantidad = corregir_atras(original)
        nuevo = insertar_css(nuevo)

        if nuevo != original:

            backup = archivo.with_name(
                archivo.name + ".backup_layout_atras_v8"
            )

            if not backup.exists():
                shutil.copy2(archivo, backup)

            archivo.write_text(
                nuevo,
                encoding="utf-8"
            )

            modificados += 1
            total += cantidad

            print(
                "OK:",
                archivo.relative_to(ROOT),
                "| Atrás:",
                cantidad
            )

    print()
    print("=" * 72)
    print("CORRECCIÓN TERMINADA")
    print("=" * 72)
    print()
    print("Botones Atrás encontrados:", total)
    print("Plantillas modificadas:", modificados)
    print()
    print("AHORA EL BOTÓN ATRÁS:")
    print("- queda separado del título")
    print("- queda arriba del título")
    print("- no se superpone")
    print("- mantiene azul #1769aa")
    print("- mantiene letra blanca")
    print()
    print("No se cambió el contenido de las páginas.")
    print()
    print("Reinicia Flask y usa Ctrl + F5.")
    print("=" * 72)


if __name__ == "__main__":
    main()
