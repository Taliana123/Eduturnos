from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent
CSS = BASE / "static" / "css" / "estilos.css"
BACKUP = BASE / "static" / "css" / "estilos.css.backup_diseno"

if not CSS.exists():
    print("[ERROR] No existe static/css/estilos.css")
    raise SystemExit(1)

# Copia de seguridad
shutil.copy2(CSS, BACKUP)
print(f"COPIA DE SEGURIDAD: {BACKUP}")

texto = CSS.read_text(encoding="utf-8")

MARCADOR = "EDUTURNOS - NORMALIZACION VISUAL GLOBAL"

if MARCADOR in texto:
    print("El diseño global ya estaba aplicado.")
    raise SystemExit(0)

CSS_NUEVO = r"""

/* =========================================================
   EDUTURNOS - NORMALIZACION VISUAL GLOBAL
   ========================================================= */

/* ---------------------------------------------------------
   BASE DE FORMULARIOS
   --------------------------------------------------------- */

.formulario form:not(.inline-form),
.form-card form:not(.inline-form),
.stack-form,
.form-uniform {
    width: 100%;
    box-sizing: border-box;
}

.formulario form:not(.inline-form),
.form-card form:not(.inline-form) {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

/* ---------------------------------------------------------
   ETIQUETAS
   --------------------------------------------------------- */

/*
   Cada título queda arriba de su campo.
   Esto evita casos como:
   "Código institucional6 dígitosSede institucional"
*/

.formulario form:not(.inline-form) label,
.form-card form:not(.inline-form) label,
.stack-form label,
.form-uniform label {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;

    width: 100%;
    min-width: 0;

    gap: 7px;

    color: #1e293b;

    font-size: 14px;
    font-weight: 600;

    line-height: 1.35;

    box-sizing: border-box;
}

/* ---------------------------------------------------------
   CAMPOS
   --------------------------------------------------------- */

.formulario input:not([type="checkbox"]):not([type="radio"]),
.formulario select,
.formulario textarea,

.form-card input:not([type="checkbox"]):not([type="radio"]),
.form-card select,
.form-card textarea,

.stack-form input:not([type="checkbox"]):not([type="radio"]),
.stack-form select,
.stack-form textarea,

.form-uniform input:not([type="checkbox"]):not([type="radio"]),
.form-uniform select,
.form-uniform textarea {
    width: 100%;
    min-width: 0;
    box-sizing: border-box;

    min-height: 46px;

    padding: 11px 14px;

    border: 1px solid #cbd5e1;
    border-radius: 9px;

    background: #ffffff;

    color: #1e293b;

    font-family: inherit;
    font-size: 15px;
    font-weight: 400;

    line-height: 1.3;

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        background-color 0.2s ease;
}

.formulario textarea,
.form-card textarea,
.stack-form textarea,
.form-uniform textarea {
    min-height: 110px;
    resize: vertical;
}

.formulario input:focus,
.formulario select:focus,
.formulario textarea:focus,

.form-card input:focus,
.form-card select:focus,
.form-card textarea:focus,

.stack-form input:focus,
.stack-form select:focus,
.stack-form textarea:focus,

.form-uniform input:focus,
.form-uniform select:focus,
.form-uniform textarea:focus {
    outline: none;

    border-color: #2563eb;

    box-shadow:
        0 0 0 3px rgba(37, 99, 235, 0.12);
}

/* ---------------------------------------------------------
   PLACEHOLDERS
   --------------------------------------------------------- */

input::placeholder,
textarea::placeholder {
    color: #94a3b8;
    opacity: 1;
}

/* ---------------------------------------------------------
   GRUPOS DE CAMPOS
   --------------------------------------------------------- */

.form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
    width: 100%;
    box-sizing: border-box;
}

.form-grid > label,
.form-grid > .campo,
.form-grid > .form-field {
    width: 100%;
    min-width: 0;
}

/* ---------------------------------------------------------
   ENCABEZADOS
   --------------------------------------------------------- */

.section-heading,
.form-heading,
.formulario .section-heading,
.form-card .section-heading {
    width: 100%;
    margin: 0 0 20px 0;

    box-sizing: border-box;
}

.section-heading h1,
.form-heading h1,
.section-heading h2,
.form-heading h2 {
    margin: 0 0 8px 0;

    color: #0f172a;

    line-height: 1.2;

    font-weight: 700;
}

.section-heading p,
.form-heading p {
    margin: 0;

    color: #64748b;

    line-height: 1.55;
}

/* ---------------------------------------------------------
   TARJETAS / CUADROS
   --------------------------------------------------------- */

.tarjeta,
.form-card {
    box-sizing: border-box;
}

.form-card {
    width: 100%;
    max-width: 820px;

    margin-left: auto;
    margin-right: auto;
}

/* ---------------------------------------------------------
   BOTONES
   --------------------------------------------------------- */

.boton {
    min-height: 46px;

    padding: 11px 18px;

    border-radius: 9px;

    font-family: inherit;
    font-size: 15px;
    font-weight: 600;

    line-height: 1.2;

    cursor: pointer;

    box-sizing: border-box;

    transition:
        transform 0.15s ease,
        box-shadow 0.2s ease,
        background-color 0.2s ease,
        border-color 0.2s ease;
}

.boton:hover {
    transform: translateY(-1px);
}

.boton:active {
    transform: translateY(0);
}

.boton-full {
    width: 100%;
}

/* ---------------------------------------------------------
   ZONA DE BOTONES
   --------------------------------------------------------- */

.form-actions,
.formulario .acciones,
.form-card .acciones,
.acciones-formulario {
    display: flex;

    flex-wrap: wrap;

    gap: 10px;

    align-items: center;

    width: 100%;

    margin-top: 4px;
}

.form-actions .boton,
.formulario .acciones .boton,
.form-card .acciones .boton,
.acciones-formulario .boton {
    margin: 0;
}

/* ---------------------------------------------------------
   ENLACES DEL FORMULARIO
   --------------------------------------------------------- */

.form-top-actions {
    display: flex;

    align-items: center;

    justify-content: flex-start;

    width: 100%;

    margin-bottom: 12px;
}

.link-back,
.enlace-atras {
    display: inline-flex;

    align-items: center;

    min-height: 36px;

    color: #2563eb;

    font-size: 14px;

    font-weight: 500;

    text-decoration: none;
}

.link-back:hover,
.enlace-atras:hover {
    text-decoration: underline;
}

/* ---------------------------------------------------------
   INSCRIPCIONES / SECCIONES
   --------------------------------------------------------- */

.seccion-formulario,
.form-section {
    width: 100%;
    box-sizing: border-box;

    margin-top: 22px;
}

.seccion-formulario + .seccion-formulario,
.form-section + .form-section {
    margin-top: 28px;
}

/* ---------------------------------------------------------
   CHECKBOX Y RADIO
   --------------------------------------------------------- */

form:not(.inline-form) label:has(input[type="checkbox"]),
form:not(.inline-form) label:has(input[type="radio"]) {
    flex-direction: row;

    align-items: center;

    gap: 9px;

    font-weight: 500;
}

form:not(.inline-form) input[type="checkbox"],
form:not(.inline-form) input[type="radio"] {
    width: auto;
    min-height: auto;
}

/* ---------------------------------------------------------
   MENSAJES Y AYUDAS
   --------------------------------------------------------- */

.form-help,
.ayuda,
.texto-ayuda,
.formulario small,
.form-card small {
    color: #64748b;

    font-size: 13px;

    line-height: 1.45;
}

/* ---------------------------------------------------------
   RESPONSIVE
   --------------------------------------------------------- */

@media (max-width: 760px) {

    .form-grid {
        grid-template-columns: 1fr;
        gap: 16px;
    }

    .formulario form:not(.inline-form),
    .form-card form:not(.inline-form) {
        gap: 16px;
    }

    .form-actions,
    .formulario .acciones,
    .form-card .acciones,
    .acciones-formulario {
        flex-direction: column;
        align-items: stretch;
    }

    .form-actions .boton,
    .formulario .acciones .boton,
    .form-card .acciones .boton,
    .acciones-formulario .boton {
        width: 100%;
    }
}

/* ---------------------------------------------------------
   ESPACIADO CONSISTENTE
   --------------------------------------------------------- */

.formulario h1,
.formulario h2,
.formulario h3 {
    letter-spacing: normal;
}

.formulario hr,
.form-card hr {
    width: 100%;

    margin: 22px 0;

    border: 0;

    border-top: 1px solid #e2e8f0;
}
"""

CSS.write_text(
    texto.rstrip() + CSS_NUEVO + "\n",
    encoding="utf-8"
)

print()
print("==============================================")
print("DISEÑO GLOBAL APLICADO CORRECTAMENTE")
print("==============================================")
print()
print("Se mejoraron:")
print("- alineación de títulos y campos")
print("- separación entre campos")
print("- tamaño uniforme de inputs")
print("- tamaño uniforme de botones")
print("- tarjetas y formularios")
print("- encabezados")
print("- acciones")
print("- diseño responsive")
print()
print("No se modificaron archivos HTML ni Jinja.")
print("No se modificaron las listas desplegables.")
print("No se modificaron rutas ni base de datos.")
print()