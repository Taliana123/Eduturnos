from pathlib import Path

ruta = Path("templates/auth/registro.html")

if not ruta.exists():
    print("[ERROR] No existe templates/auth/registro.html")
    raise SystemExit(1)

texto = ruta.read_text(encoding="utf-8")

MARCADOR = "EDUTURNOS_MEJORA_FINAL_REGISTRO"

if MARCADOR in texto:
    print("El ajuste ya está aplicado.")
    raise SystemExit(0)

CSS = r"""
<!-- EDUTURNOS_MEJORA_FINAL_REGISTRO -->

<style>

    /* =====================================================
       MEJORA FINAL - REGISTRO
       ===================================================== */

    .registro-pagina {
        padding-top: 12px !important;
        padding-bottom: 30px !important;
    }

    .registro-contenedor {
        max-width: 1080px !important;

        padding: 34px !important;
    }

    .registro-encabezado {
        margin-bottom: 30px !important;
    }

    .registro-encabezado h1 {
        font-size: 30px !important;
        margin-bottom: 9px !important;
    }

    .registro-encabezado p {
        max-width: 820px !important;
        line-height: 1.55 !important;
    }

    /* =====================================================
       DISTRIBUCIÓN DE LAS 5 TARJETAS
       ===================================================== */

    .registro-grid {
        display: grid !important;

        grid-template-columns:
            repeat(6, minmax(0, 1fr)) !important;

        gap: 22px !important;

        width: 100% !important;

        align-items: stretch !important;
    }

    .registro-opcion {
        grid-column: span 2 !important;

        min-height: 205px !important;

        padding: 22px !important;

        display: flex !important;
        flex-direction: column !important;

        justify-content: space-between !important;

        margin: 0 !important;
    }

    /* Centrar las dos últimas */
    .registro-opcion:nth-child(4) {
        grid-column: 2 / span 2 !important;
    }

    .registro-opcion:nth-child(5) {
        grid-column: 4 / span 2 !important;
    }

    /* =====================================================
       TÍTULOS
       ===================================================== */

    .registro-opcion h3 {
        min-height: 46px !important;

        margin: 0 0 10px 0 !important;

        font-size: 18px !important;

        line-height: 1.25 !important;
    }

    /* =====================================================
       DESCRIPCIONES
       ===================================================== */

    .registro-opcion p {
        min-height: 70px !important;

        margin: 0 !important;

        line-height: 1.5 !important;
    }

    /* =====================================================
       BOTONES
       ===================================================== */

    .registro-boton {
        min-height: 46px !important;

        margin-top: 18px !important;
    }

    /* =====================================================
       VOLVER
       ===================================================== */

    .registro-volver {
        margin-top: 30px !important;

        padding-top: 22px !important;
    }

    /* =====================================================
       TABLET
       ===================================================== */

    @media (max-width: 900px) {

        .registro-grid {
            grid-template-columns:
                repeat(2, minmax(0, 1fr)) !important;

            gap: 18px !important;
        }

        .registro-opcion,
        .registro-opcion:nth-child(4),
        .registro-opcion:nth-child(5) {
            grid-column: auto !important;
        }

        .registro-opcion {
            min-height: 200px !important;
        }
    }

    /* =====================================================
       CELULAR
       ===================================================== */

    @media (max-width: 620px) {

        .registro-contenedor {
            padding: 22px !important;
        }

        .registro-grid {
            grid-template-columns: 1fr !important;

            gap: 16px !important;
        }

        .registro-opcion,
        .registro-opcion:nth-child(4),
        .registro-opcion:nth-child(5) {
            grid-column: auto !important;

            min-height: 0 !important;
        }

        .registro-opcion h3,
        .registro-opcion p {
            min-height: 0 !important;
        }

        .registro-encabezado h1 {
            font-size: 27px !important;
        }
    }

</style>

<!-- FIN EDUTURNOS_MEJORA_FINAL_REGISTRO -->
"""

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

ruta.write_text(texto, encoding="utf-8")

print()
print("=" * 60)
print("REGISTRO MEJORADO")
print("=" * 60)
print()
print("3 tarjetas arriba.")
print("2 tarjetas centradas abajo.")
print("Todas del mismo tamaño.")
print("Más separación y mejor alineación.")