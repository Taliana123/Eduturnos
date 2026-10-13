from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent
CSS = BASE / "static" / "css" / "estilos.css"
BACKUP = BASE / "static" / "css" / "estilos.css.backup_forzado"

if not CSS.exists():
    print("[ERROR] No existe:")
    print(CSS)
    raise SystemExit(1)

shutil.copy2(CSS, BACKUP)
print(f"COPIA DE SEGURIDAD: {BACKUP}")

texto = CSS.read_text(encoding="utf-8")

MARCADOR = "EDUTURNOS - DISENO GLOBAL FORZADO"

if MARCADOR in texto:
    print("El ajuste ya está instalado.")
    raise SystemExit(0)

CSS_FORZADO = r"""

/* =========================================================
   EDUTURNOS - DISENO GLOBAL FORZADO
   ========================================================= */

/* ---------- CONTENEDOR GENERAL ---------- */

main.contenedor {
    box-sizing: border-box;
}

main.contenedor .formulario,
main.contenedor .form-card,
main.contenedor .tarjeta {
    box-sizing: border-box;
}

/* ---------- FORMULARIOS ---------- */

main.contenedor form:not(.inline-form) {
    box-sizing: border-box;

    width: 100%;

    display: flex;
    flex-direction: column;

    gap: 18px;
}

/* ---------- TITULO DEL CAMPO ---------- */

main.contenedor form:not(.inline-form) label {
    box-sizing: border-box;

    width: 100%;

    display: flex !important;
    flex-direction: column !important;

    align-items: stretch !important;
    justify-content: flex-start !important;

    gap: 7px !important;

    margin: 0 !important;
    padding: 0 !important;

    color: #1e293b !important;

    font-family: inherit !important;
    font-size: 14px !important;
    font-weight: 600 !important;

    line-height: 1.35 !important;
}

/* ---------- CAMPOS ---------- */

main.contenedor form:not(.inline-form) input:not([type="checkbox"]):not([type="radio"]),
main.contenedor form:not(.inline-form) select,
main.contenedor form:not(.inline-form) textarea {
    display: block !important;

    box-sizing: border-box !important;

    width: 100% !important;
    max-width: 100% !important;

    min-height: 46px !important;

    margin: 0 !important;

    padding: 11px 14px !important;

    border: 1px solid #cbd5e1 !important;
    border-radius: 9px !important;

    background: #ffffff !important;

    color: #1e293b !important;

    font-family: inherit !important;
    font-size: 15px !important;
    font-weight: 400 !important;

    line-height: 1.35 !important;

    box-sizing: border-box !important;
}

main.contenedor form:not(.inline-form) textarea {
    min-height: 110px !important;
    resize: vertical;
}

/* ---------- FOCUS ---------- */

main.contenedor form:not(.inline-form) input:not([type="checkbox"]):not([type="radio"]):focus,
main.contenedor form:not(.inline-form) select:focus,
main.contenedor form:not(.inline-form) textarea:focus {
    outline: none !important;

    border-color: #2563eb !important;

    box-shadow:
        0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}

/* ---------- CHECKBOX / RADIO ---------- */

main.contenedor form:not(.inline-form) label:has(input[type="checkbox"]),
main.contenedor form:not(.inline-form) label:has(input[type="radio"]) {
    flex-direction: row !important;

    align-items: center !important;

    gap: 9px !important;
}

main.contenedor form:not(.inline-form) input[type="checkbox"],
main.contenedor form:not(.inline-form) input[type="radio"] {
    width: auto !important;
    min-height: auto !important;
    margin: 0 !important;
}

/* ---------- BOTONES ---------- */

main.contenedor form:not(.inline-form) button:not(.nav-button),
main.contenedor form:not(.inline-form) .boton {
    box-sizing: border-box;

    min-height: 46px;

    margin: 0;

    padding: 11px 18px;

    border-radius: 9px;

    font-family: inherit;
    font-size: 15px;
    font-weight: 600;

    line-height: 1.2;

    cursor: pointer;
}

/* Botón de ancho completo cuando ya usa esa clase */
main.contenedor form:not(.inline-form) .boton-full {
    width: 100% !important;
}

/* ---------- TITULOS ---------- */

main.contenedor h1,
main.contenedor h2,
main.contenedor h3 {
    line-height: 1.2 !important;
}

main.contenedor h1 {
    margin-top: 0 !important;
    margin-bottom: 10px !important;
}

main.contenedor h2,
main.contenedor h3 {
    margin-top: 0 !important;
    margin-bottom: 8px !important;
}

/* ---------- DESCRIPCIONES ---------- */

main.contenedor .section-heading,
main.contenedor .form-heading {
    width: 100%;

    margin-bottom: 20px;
}

main.contenedor .section-heading p,
main.contenedor .form-heading p {
    margin: 0;

    line-height: 1.55;
}

/* ---------- TARJETAS ---------- */

main.contenedor .form-card,
main.contenedor .tarjeta {
    box-sizing: border-box;

    width: 100%;
}

main.contenedor .form-card {
    max-width: 820px;

    margin-left: auto;
    margin-right: auto;
}

/* ---------- ESPACIOS ENTRE SECCIONES ---------- */

main.contenedor .section-heading + form,
main.contenedor .form-heading + form {
    margin-top: 0;
}

/* ---------- BOTONES AGRUPADOS ---------- */

main.contenedor .form-actions,
main.contenedor .acciones,
main.contenedor .acciones-formulario {
    box-sizing: border-box;

    width: 100%;

    display: flex;

    flex-wrap: wrap;

    align-items: center;

    gap: 10px;

    margin-top: 2px;
}

/* ---------- ENLACE VOLVER ---------- */

main.contenedor .form-top-actions {
    width: 100%;

    display: flex;

    align-items: center;

    margin-bottom: 12px;
}

/* ---------- RESPONSIVE ---------- */

@media (max-width: 760px) {

    main.contenedor form:not(.inline-form) {
        gap: 15px;
    }

    main.contenedor .form-actions,
    main.contenedor .acciones,
    main.contenedor .acciones-formulario {
        flex-direction: column;
        align-items: stretch;
    }

    main.contenedor .form-actions .boton,
    main.contenedor .acciones .boton,
    main.contenedor .acciones-formulario .boton {
        width: 100%;
    }
}

/* ---------- FIN ---------- */
"""

CSS.write_text(
    texto.rstrip() + "\n" + CSS_FORZADO + "\n",
    encoding="utf-8"
)

print()
print("=" * 60)
print("DISEÑO GLOBAL FORZADO APLICADO")
print("=" * 60)
print()
print("Los títulos de los campos quedarán arriba.")
print("Los cuadros quedarán debajo del título.")
print("Todos los campos tendrán el mismo ancho.")
print("Todos tendrán alturas y separaciones uniformes.")
print("Los botones quedarán alineados.")
print("El cambio afecta los formularios de todo EDUTURNOS.")
print()