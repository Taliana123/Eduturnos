from pathlib import Path
import re
import shutil

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "templates" / "dashboard.html"
BACKUP = BASE / "templates" / "dashboard.html.backup_solo_interno"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/dashboard.html")
    raise SystemExit(1)

# Copia de seguridad
shutil.copy2(ARCHIVO, BACKUP)

texto = ARCHIVO.read_text(encoding="utf-8")

# =========================================================
# QUITAR EL ESTILO ANIMADO ANTERIOR
# =========================================================

texto = re.sub(
    r'<!-- EDUTURNOS_ACCESOS_ANIMADOS -->.*?<!-- FIN EDUTURNOS_ACCESOS_ANIMADOS -->',
    '',
    texto,
    flags=re.IGNORECASE | re.DOTALL
)

# =========================================================
# ESTILO SOLO INTERNO DE LAS TARJETAS
# =========================================================

INICIO = "<!-- EDUTURNOS_ACCESOS_SOLO_INTERNO -->"
FIN = "<!-- FIN EDUTURNOS_ACCESOS_SOLO_INTERNO -->"

CSS = r"""
<!-- EDUTURNOS_ACCESOS_SOLO_INTERNO -->

<style id="eduturnos-accesos-solo-interno">

/* =========================================================
   SOLO CONTENIDO INTERIOR DE LAS TARJETAS
   ========================================================= */

.dashboard-action {
    min-height: 185px !important;
    padding: 19px !important;

    /* Sin animaciones externas */
    transform: none !important;
    transition: none !important;
}

/* Etiqueta pequeña */
.dashboard-action-icon {
    padding: 6px 10px !important;

    font-size: 12px !important;

    margin: 0 !important;
}

/* Espacio entre etiqueta y título */
.dashboard-action-top {
    margin-bottom: 14px !important;
}

/* Título */
.dashboard-action h3 {
    margin: 0 0 8px 0 !important;

    font-size: 18px !important;

    line-height: 1.25 !important;

    font-weight: 700 !important;

    transform: none !important;
}

/* Descripción */
.dashboard-action p {
    margin: 0 !important;

    font-size: 13.5px !important;

    line-height: 1.5 !important;
}

/* Enlace inferior */
.dashboard-action-link {
    margin-top: 15px !important;

    font-size: 13px !important;

    font-weight: 600 !important;

    transform: none !important;
}

/* No mover la tarjeta al pasar el mouse */
.dashboard-action:hover {
    transform: none !important;
}

/* No desplazar título/enlace */
.dashboard-action:hover h3,
.dashboard-action:hover .dashboard-action-link {
    transform: none !important;
}

/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 600px) {

    .dashboard-action {
        min-height: 170px !important;
    }
}

</style>

<!-- FIN EDUTURNOS_ACCESOS_SOLO_INTERNO -->
"""

# Reemplazar si ya existe
patron = re.compile(
    re.escape(INICIO)
    + r".*?"
    + re.escape(FIN),
    re.IGNORECASE | re.DOTALL
)

if patron.search(texto):
    texto = patron.sub(CSS.strip(), texto)
else:
    posicion = texto.lower().rfind("{% endblock %}")

    if posicion == -1:
        print("[ERROR] No se encontró {% endblock %}")
        raise SystemExit(1)

    texto = (
        texto[:posicion]
        + "\n"
        + CSS
        + "\n"
        + texto[posicion:]
    )

ARCHIVO.write_text(
    texto,
    encoding="utf-8"
)

print()
print("=" * 65)
print("DASHBOARD RESTAURADO")
print("=" * 65)
print()
print("Se eliminó la animación exterior.")
print("Las tarjetas conservarán su tamaño y posición.")
print("El estilo ahora afecta solamente el contenido interno.")
print("Títulos, descripciones y enlaces quedaron organizados.")
print()
print(f"Copia de seguridad: {BACKUP}")