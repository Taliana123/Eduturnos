from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "templates" / "auth" / "registro.html"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/auth/registro.html")
    raise SystemExit(1)

texto = ARCHIVO.read_text(encoding="utf-8")

MARCADOR_INICIO = "<!-- EDUTURNOS_ROLES_COMPACTOS -->"
MARCADOR_FIN = "<!-- FIN EDUTURNOS_ROLES_COMPACTOS -->"

CSS = r"""
<!-- EDUTURNOS_ROLES_COMPACTOS -->

<style id="eduturnos-roles-compactos">

/* =========================================================
   EDUTURNOS - ROLES COMPACTOS
   ========================================================= */

/* Contenedor */
.registro-contenedor {
    max-width: 980px !important;
    padding: 28px !important;
}

/* Encabezado */
.registro-encabezado {
    margin-bottom: 22px !important;
}

/* Cuadrícula */
.registro-grid {
    display: grid !important;

    grid-template-columns:
        repeat(6, minmax(0, 1fr)) !important;

    gap: 16px !important;

    align-items: stretch !important;
}

/* Tarjetas */
.registro-opcion {
    grid-column: span 2 !important;

    min-height: 155px !important;

    padding: 18px !important;

    border-radius: 11px !important;

    box-shadow:
        0 2px 6px rgba(15, 23, 42, 0.05) !important;
}

/* Cuarta tarjeta */
.registro-opcion:nth-child(4) {
    grid-column: 2 / span 2 !important;
}

/* Quinta tarjeta */
.registro-opcion:nth-child(5) {
    grid-column: 4 / span 2 !important;
}

/* Contenido */
.registro-opcion-contenido {
    width: 100% !important;
}

/* Títulos */
.registro-opcion h3 {
    min-height: 0 !important;

    margin: 0 0 7px 0 !important;

    font-size: 17px !important;

    line-height: 1.2 !important;
}

/* Descripciones */
.registro-opcion p {
    min-height: 48px !important;

    margin: 0 !important;

    font-size: 13.5px !important;

    line-height: 1.4 !important;
}

/* Botones */
.registro-boton {
    min-height: 40px !important;

    margin-top: 12px !important;

    padding: 9px 14px !important;

    font-size: 14px !important;

    border-radius: 8px !important;
}

/* Volver */
.registro-volver {
    margin-top: 22px !important;

    padding-top: 18px !important;
}

/* =========================================================
   TABLET
   ========================================================= */

@media (max-width: 850px) {

    .registro-contenedor {
        padding: 24px !important;
    }

    .registro-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;

        gap: 14px !important;
    }

    .registro-opcion,
    .registro-opcion:nth-child(4),
    .registro-opcion:nth-child(5) {
        grid-column: auto !important;
    }

    .registro-opcion {
        min-height: 150px !important;
    }
}

/* =========================================================
   CELULAR
   ========================================================= */

@media (max-width: 600px) {

    .registro-contenedor {
        padding: 20px !important;
    }

    .registro-grid {
        grid-template-columns: 1fr !important;

        gap: 13px !important;
    }

    .registro-opcion,
    .registro-opcion:nth-child(4),
    .registro-opcion:nth-child(5) {
        grid-column: auto !important;

        min-height: 0 !important;
    }

    .registro-opcion p {
        min-height: 0 !important;
    }
}

</style>

<!-- FIN EDUTURNOS_ROLES_COMPACTOS -->
"""

patron = re.compile(
    re.escape(MARCADOR_INICIO)
    + r".*?"
    + re.escape(MARCADOR_FIN),
    re.IGNORECASE | re.DOTALL
)

if patron.search(texto):
    texto = patron.sub(CSS.strip(), texto)
    print("ACTUALIZADO: tarjetas de roles compactas.")
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

    print("AGREGADO: tarjetas de roles compactas.")

ARCHIVO.write_text(
    texto,
    encoding="utf-8"
)

print()
print("=" * 60)
print("ROLES COMPACTADOS")
print("=" * 60)
print()
print("Las tarjetas son más pequeñas.")
print("Se redujo el espacio interno.")
print("Los botones son más compactos.")
print("Se conserva la distribución 3 arriba + 2 abajo.")
print("El diseño sigue siendo responsive.")