from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent
CSS = BASE / "static" / "css" / "estilos.css"
BACKUP = BASE / "static" / "css" / "estilos.css.backup_formularios"

if not CSS.exists():
    print("[ERROR] No existe static/css/estilos.css")
    raise SystemExit(1)

# Copia de seguridad
shutil.copy2(CSS, BACKUP)

texto = CSS.read_text(encoding="utf-8")

MARCADOR = "EDUTURNOS - FORMULARIOS ORDENADOS"

if MARCADOR in texto:
    print("El ajuste ya está aplicado.")
    raise SystemExit(0)

CSS_NUEVO = r"""

/* =========================================================
   EDUTURNOS - FORMULARIOS ORDENADOS
   ========================================================= */

/*
   Todos los grupos de campos tendrán:
   TITULO
   ↓
   CUADRO

   Los campos de una misma fila quedan perfectamente
   alineados entre sí.
*/

.form-grid {
    display: grid !important;

    grid-template-columns:
        repeat(3, minmax(0, 1fr)) !important;

    column-gap: 20px !important;
    row-gap: 20px !important;

    width: 100% !important;
    align-items: start !important;

    box-sizing: border-box !important;
}

/* Cada campo ocupa su propia columna */
.form-grid > label,
.form-grid > .campo,
.form-grid > .form-field {
    display: flex !important;

    flex-direction: column !important;

    align-items: stretch !important;
    justify-content: flex-start !important;

    width: 100% !important;
    min-width: 0 !important;

    margin: 0 !important;
    padding: 0 !important;

    gap: 7px !important;

    box-sizing: border-box !important;

    font-size: 14px !important;
    line-height: 1.35 !important;
    font-weight: 600 !important;
}

/* Título de cada campo */
.form-grid > label > small,
.form-grid > label small {
    display: inline !important;

    margin: 0 !important;

    font-size: 13px !important;
    line-height: 1.2 !important;

    font-weight: 400 !important;
}

/* Todos los cuadros exactamente alineados */
.form-grid > label > input,
.form-grid > label > select,
.form-grid > label > textarea,
.form-grid > .campo > input,
.form-grid > .campo > select,
.form-grid > .campo > textarea,
.form-grid > .form-field > input,
.form-grid > .form-field > select,
.form-grid > .form-field > textarea {
    display: block !important;

    width: 100% !important;
    max-width: 100% !important;

    min-height: 46px !important;

    margin: 0 !important;

    box-sizing: border-box !important;

    padding: 11px 14px !important;

    border: 1px solid #cbd5e1 !important;
    border-radius: 9px !important;

    background: #ffffff !important;

    color: #1e293b !important;

    font-family: inherit !important;
    font-size: 15px !important;
    font-weight: 400 !important;

    line-height: 1.3 !important;
}

/* El campo de texto no debe cambiar de posición */
.form-grid input,
.form-grid select,
.form-grid textarea {
    vertical-align: top !important;
}

/* Campos de una fila que ocupen todo el ancho */
.form-grid .campo-completo,
.form-grid .campo-full,
.form-grid .full-width {
    grid-column: 1 / -1 !important;
}

/* Espaciado uniforme entre el bloque explicativo y los campos */
.personal-login {
    width: 100% !important;
    box-sizing: border-box !important;
}

.personal-login h3 {
    margin: 0 0 8px 0 !important;

    line-height: 1.2 !important;
}

.personal-login p {
    margin: 0 0 20px 0 !important;

    line-height: 1.5 !important;
}

/* Formularios generales del sistema */
form.stack-form,
form.form-uniform {
    width: 100% !important;

    display: flex !important;

    flex-direction: column !important;

    gap: 18px !important;

    box-sizing: border-box !important;
}

/* Cada label simple queda alineado */
form.stack-form > label,
form.form-uniform > label {
    display: flex !important;

    flex-direction: column !important;

    align-items: stretch !important;

    width: 100% !important;

    gap: 7px !important;

    margin: 0 !important;
    padding: 0 !important;

    box-sizing: border-box !important;

    line-height: 1.35 !important;
}

/* Todos los campos simples con la misma altura */
form.stack-form > label > input,
form.stack-form > label > select,
form.stack-form > label > textarea,
form.form-uniform > label > input,
form.form-uniform > label > select,
form.form-uniform > label > textarea {
    width: 100% !important;

    min-height: 46px !important;

    margin: 0 !important;

    box-sizing: border-box !important;
}

/* Botones al final de los formularios */
form.stack-form > button,
form.form-uniform > button {
    margin-top: 2px !important;
}

/* ---------------------------------------------------------
   RESPONSIVE
   --------------------------------------------------------- */

@media (max-width: 900px) {

    .form-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;
    }
}

@media (max-width: 620px) {

    .form-grid {
        grid-template-columns: 1fr !important;

        gap: 16px !important;
    }
}
"""

CSS.write_text(
    texto.rstrip() + "\n" + CSS_NUEVO + "\n",
    encoding="utf-8"
)

# Quitar "6 dígitos" del título del campo solamente.
login = BASE / "templates" / "auth" / "login.html"

if login.exists():
    contenido = login.read_text(encoding="utf-8")

    contenido_nuevo = contenido.replace(
        "<small>6 dÃ­gitos</small>",
        ""
    )

    contenido_nuevo = contenido_nuevo.replace(
        "<small>6 dígitos</small>",
        ""
    )

    contenido_nuevo = contenido_nuevo.replace(
        "<small>6 digitos</small>",
        ""
    )

    if contenido_nuevo != contenido:
        login.write_text(
            contenido_nuevo,
            encoding="utf-8"
        )
        print("CORREGIDO: login.html")
    else:
        print("login.html: no fue necesario modificar el texto.")

print()
print("=" * 60)
print("FORMULARIOS ORDENADOS CORRECTAMENTE")
print("=" * 60)
print()
print("CSS actualizado.")
print("Copia de seguridad creada.")
print("Los títulos quedan arriba de sus cuadros.")
print("Los cuadros quedan alineados.")
print("Las columnas tienen el mismo ancho.")
print("Los espacios son uniformes.")
print("Se eliminó '6 dígitos' del título del código.")
print()