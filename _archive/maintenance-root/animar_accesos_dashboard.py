from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "templates" / "dashboard.html"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/dashboard.html")
    raise SystemExit(1)

texto = ARCHIVO.read_text(encoding="utf-8")

INICIO = "<!-- EDUTURNOS_ACCESOS_ANIMADOS -->"
FIN = "<!-- FIN EDUTURNOS_ACCESOS_ANIMADOS -->"

CSS = r"""
<!-- EDUTURNOS_ACCESOS_ANIMADOS -->

<style id="eduturnos-accesos-animados">

/* =========================================================
   EDUTURNOS - ACCESOS ELEGANTES Y ANIMADOS
   ========================================================= */

.dashboard-action-grid {
    display: grid !important;

    grid-template-columns:
        repeat(4, minmax(0, 1fr)) !important;

    gap: 18px !important;

    width: 100% !important;

    align-items: stretch !important;
}

/* =========================================================
   TARJETAS
   ========================================================= */

.dashboard-action {
    position: relative !important;

    isolation: isolate !important;

    overflow: hidden !important;

    min-height: 205px !important;

    padding: 20px !important;

    display: flex !important;

    flex-direction: column !important;

    justify-content: flex-start !important;

    border: 1px solid #dbe4ef !important;

    border-radius: 16px !important;

    background:
        linear-gradient(
            145deg,
            #ffffff 0%,
            #f8fbff 100%
        ) !important;

    box-shadow:
        0 5px 16px rgba(15, 23, 42, 0.06) !important;

    text-decoration: none !important;

    transform: translateY(0) !important;

    transition:
        transform 0.28s ease,
        box-shadow 0.28s ease,
        border-color 0.28s ease,
        background 0.28s ease !important;

    animation:
        entradaAcceso 0.55s ease both;
}

/* =========================================================
   ANIMACIÓN DE ENTRADA
   ========================================================= */

.dashboard-action:nth-child(1) {
    animation-delay: 0.05s;
}

.dashboard-action:nth-child(2) {
    animation-delay: 0.12s;
}

.dashboard-action:nth-child(3) {
    animation-delay: 0.19s;
}

.dashboard-action:nth-child(4) {
    animation-delay: 0.26s;
}

.dashboard-action:nth-child(5) {
    animation-delay: 0.33s;
}

.dashboard-action:nth-child(6) {
    animation-delay: 0.40s;
}

@keyframes entradaAcceso {

    from {
        opacity: 0;
        transform: translateY(14px) scale(0.98);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* =========================================================
   BRILLO SUTIL
   ========================================================= */

.dashboard-action::before {
    content: "";

    position: absolute;

    top: -80%;
    left: -35%;

    width: 35%;
    height: 260%;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.72),
            transparent
        );

    transform: rotate(18deg) translateX(-220%);

    transition:
        transform 0.65s ease;

    pointer-events: none;

    z-index: -1;
}

.dashboard-action:hover::before {
    transform:
        rotate(18deg)
        translateX(520%);
}

/* =========================================================
   HOVER
   ========================================================= */

.dashboard-action:hover {

    transform:
        translateY(-7px)
        scale(1.01) !important;

    border-color: #b8d3f8 !important;

    background:
        linear-gradient(
            145deg,
            #ffffff 0%,
            #f2f7ff 100%
        ) !important;

    box-shadow:
        0 14px 30px rgba(15, 23, 42, 0.12),
        0 0 0 1px rgba(37, 99, 235, 0.04) !important;
}

/* =========================================================
   ETIQUETA SUPERIOR
   ========================================================= */

.dashboard-action-top {
    display: flex !important;

    align-items: center !important;

    width: 100% !important;

    margin-bottom: 16px !important;
}

.dashboard-action-icon {

    position: relative !important;

    display: inline-flex !important;

    align-items: center !important;

    justify-content: center !important;

    min-height: 32px !important;

    padding: 7px 12px !important;

    border-radius: 9px !important;

    background:
        linear-gradient(
            135deg,
            #e9f2ff,
            #dceaff
        ) !important;

    color: #2563eb !important;

    font-size: 12px !important;

    font-weight: 700 !important;

    line-height: 1 !important;

    box-shadow:
        inset 0 0 0 1px rgba(37, 99, 235, 0.08) !important;

    transition:
        transform 0.28s ease,
        box-shadow 0.28s ease,
        background 0.28s ease !important;
}

.dashboard-action:hover
.dashboard-action-icon {

    transform:
        translateY(-2px)
        scale(1.04);

    background:
        linear-gradient(
            135deg,
            #dceaff,
            #cfe0ff
        ) !important;

    box-shadow:
        0 5px 12px rgba(37, 99, 235, 0.14) !important;
}

/* =========================================================
   TÍTULO
   ========================================================= */

.dashboard-action h3 {

    margin: 0 0 9px 0 !important;

    color: #0f172a !important;

    font-size: 19px !important;

    font-weight: 700 !important;

    line-height: 1.2 !important;

    letter-spacing: -0.01em !important;

    transition:
        transform 0.25s ease,
        color 0.25s ease !important;
}

.dashboard-action:hover h3 {

    transform: translateX(2px);

    color: #1d4ed8 !important;
}

/* =========================================================
   DESCRIPCIÓN
   ========================================================= */

.dashboard-action p {

    flex: 1 !important;

    margin: 0 !important;

    color: #64748b !important;

    font-size: 13.5px !important;

    line-height: 1.55 !important;
}

/* =========================================================
   ENLACE INFERIOR
   ========================================================= */

.dashboard-action-link {

    display: inline-flex !important;

    align-items: center !important;

    width: fit-content !important;

    margin-top: 17px !important;

    color: #2563eb !important;

    font-size: 13px !important;

    font-weight: 700 !important;

    line-height: 1.3 !important;

    transition:
        transform 0.25s ease,
        color 0.25s ease !important;
}

.dashboard-action:hover
.dashboard-action-link {

    transform: translateX(5px);

    color: #1d4ed8 !important;
}

/* =========================================================
   BORDE SUPERIOR DECORATIVO
   ========================================================= */

.dashboard-action::after {

    content: "";

    position: absolute;

    top: 0;
    left: 18px;
    right: 18px;

    height: 3px;

    border-radius: 0 0 8px 8px;

    background:
        linear-gradient(
            90deg,
            #2563eb,
            #60a5fa
        );

    opacity: 0.7;

    transform: scaleX(0.35);

    transform-origin: center;

    transition:
        transform 0.28s ease,
        opacity 0.28s ease;
}

.dashboard-action:hover::after {

    transform: scaleX(1);

    opacity: 1;
}

/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1000px) {

    .dashboard-action-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;
    }
}

@media (max-width: 600px) {

    .dashboard-action-grid {
        grid-template-columns: 1fr !important;
    }

    .dashboard-action {
        min-height: 175px !important;
    }
}

/* =========================================================
   REDUCIR MOVIMIENTO SI EL SISTEMA LO SOLICITA
   ========================================================= */

@media (prefers-reduced-motion: reduce) {

    .dashboard-action {
        animation: none !important;

        transition: none !important;
    }

    .dashboard-action::before,
    .dashboard-action::after {
        transition: none !important;
    }
}

</style>

<!-- FIN EDUTURNOS_ACCESOS_ANIMADOS -->
"""

patron = re.compile(
    re.escape(INICIO)
    + r".*?"
    + re.escape(FIN),
    re.IGNORECASE | re.DOTALL
)

if patron.search(texto):

    texto = patron.sub(
        CSS.strip(),
        texto
    )

    print("ACTUALIZADO: animación de accesos.")

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

    print("AGREGADO: animación de accesos.")

ARCHIVO.write_text(
    texto,
    encoding="utf-8"
)

print()
print("=" * 65)
print("ACCESOS DEL DASHBOARD MEJORADOS")
print("=" * 65)
print()
print("Tarjetas más elegantes.")
print("Animación de entrada.")
print("Efecto hover.")
print("Brillo sutil.")
print("Bordes animados.")
print("Enlaces animados.")
print("Diseño responsive.")
print()