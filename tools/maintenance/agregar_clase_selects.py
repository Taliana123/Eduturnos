from pathlib import Path
import re

for ruta in Path("templates").rglob("*.html"):
    texto = ruta.read_text(encoding="utf-8")
    original = texto

    def agregar_clase(m):
        etiqueta = m.group(0)

        if "eduturnos-select" in etiqueta:
            return etiqueta

        if re.search(r'\bclass\s*=', etiqueta):
            etiqueta = re.sub(
                r'class\s*=\s*["\']([^"\']*)["\']',
                lambda c: 'class="' + c.group(1) + ' eduturnos-select"',
                etiqueta,
                count=1
            )
        else:
            etiqueta = etiqueta.replace("<select", '<select class="eduturnos-select"', 1)

        return etiqueta

    texto = re.sub(r"<select\b[^>]*>", agregar_clase, texto, flags=re.IGNORECASE)

    if texto != original:
        ruta.write_text(texto, encoding="utf-8")
        print("CORREGIDO:", ruta)

print("PROCESO TERMINADO")
