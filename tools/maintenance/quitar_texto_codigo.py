from pathlib import Path
import re

archivos = [
    Path("templates/auth/login.html"),
    Path("templates/auth/registro_portal.html"),
]

for ruta in archivos:

    if not ruta.exists():
        continue

    texto = ruta.read_text(encoding="utf-8")
    original = texto

    # Quitar placeholder del campo codigo_institucional
    def limpiar_input(match):
        etiqueta = match.group(0)

        tiene_codigo = (
            re.search(
                r'\bname\s*=\s*["\']codigo_institucional["\']',
                etiqueta,
                re.IGNORECASE
            )
            or
            re.search(
                r'\bid\s*=\s*["\']codigo_institucional["\']',
                etiqueta,
                re.IGNORECASE
            )
        )

        if not tiene_codigo:
            return etiqueta

        # Eliminar cualquier placeholder de ese input
        etiqueta = re.sub(
            r'\s+placeholder\s*=\s*["\'][^"\']*["\']',
            '',
            etiqueta,
            flags=re.IGNORECASE
        )

        return etiqueta

    texto = re.sub(
        r'<input\b[^>]*>',
        limpiar_input,
        texto,
        flags=re.IGNORECASE
    )

    if texto != original:
        ruta.write_text(texto, encoding="utf-8")
        print(f"CORREGIDO: {ruta}")
    else:
        print(f"SIN CAMBIOS: {ruta}")

print()
print("LISTO.")
print("El campo Código institucional conserva su validación,")
print("pero ya no tendrá texto de ejemplo dentro del cuadro.")