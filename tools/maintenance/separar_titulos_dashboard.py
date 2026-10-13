from pathlib import Path
import re

ruta = Path("templates/dashboard.html")

if not ruta.exists():
    print("[ERROR] No existe templates/dashboard.html")
    raise SystemExit(1)

texto = ruta.read_text(encoding="utf-8")

MARCADOR_INICIO = "EDUTURNOS - ESPACIADO TITULOS DASHBOARD"
MARCADOR_FIN = "FIN EDUTURNOS - ESPACIADO TITULOS DASHBOARD"

CSS = r"""
<!-- EDUTURNOS - ESPACIADO TITULOS DASHBOARD -->

<style>

/* =========================================================
   ESPACIADO DE TITULOS DEL DASHBOARD
   ========================================================= */

/* DOCENTE */
.dashboard-head-info .badge {
    display: inline-block !important;
    margin-bottom: 14px !important;
}

.dashboard-head-info h1 {
    margin-top: 0 !important;
    margin-bottom: 12px !important;
}

.dashboard-head-info p {
    margin-top: 0 !important;
}

/* ACCESOS */
.dashboard-card-head .badge {
    display: inline-block !important;
    margin-bottom: 13px !important;
}

.dashboard-card-head h2 {
    margin-top: 0 !important;
    margin-bottom: 11px !important;
}

.dashboard-card-head p {
    margin-top: 0 !important;
}

/* CUENTA */
.dashboard-account-card .dashboard-card-head {
    margin-bottom: 17px !important;
}

.dashboard-account-card .dashboard-card-head .badge {
    margin-bottom: 13px !important;
}

.dashboard-account-card .dashboard-card-head h2 {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

.dashboard-account-text {
    margin-top: 0 !important;
    margin-bottom: 20px !important;
}

/* Un poco más de aire antes de los indicadores */
.dashboard-head {
    margin-bottom: 28px !important;
}

/* Separación entre indicadores y Accesos */
.dashboard-kpis {
    margin-bottom: 28px !important;
}

/* Separación dentro de Acciones rápidas */
.dashboard-actions-card .dashboard-card-head {
    margin-bottom: 24px !important;
}

</style>

<!-- FIN EDUTURNOS - ESPACIADO TITULOS DASHBOARD -->
"""

# Si ya existe el bloque, reemplazarlo
patron = re.compile(
    r'<!-- EDUTURNOS - ESPACIADO TITULOS DASHBOARD -->'
    r'.*?'
    r'<!-- FIN EDUTURNOS - ESPACIADO TITULOS DASHBOARD -->',
    re.IGNORECASE | re.DOTALL
)

if patron.search(texto):
    texto = patron.sub(CSS.strip(), texto)
    print("ACTUALIZADO: espaciado de títulos del dashboard.")
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

    print("AGREGADO: espaciado de títulos del dashboard.")

ruta.write_text(texto, encoding="utf-8")

print()
print("=" * 60)
print("ESPACIADO DEL DASHBOARD ACTUALIZADO")
print("=" * 60)
print()
print("Docente tiene más separación antes de Hola.")
print("Accesos tiene más separación antes de Acciones rápidas.")
print("Cuenta tiene más separación antes de Mi cuenta.")
print("También se mejoró el espacio entre secciones.")