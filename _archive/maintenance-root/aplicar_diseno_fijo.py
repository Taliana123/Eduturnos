from pathlib import Path
import shutil
import re

BASE = Path(__file__).resolve().parent

BASE_HTML = BASE / "templates" / "base.html"
LOGIN_HTML = BASE / "templates" / "auth" / "login.html"

BACKUP_BASE = BASE / "templates" / "base.html.backup_diseno_fijo"
BACKUP_LOGIN = BASE / "templates" / "auth" / "login.html.backup_diseno_fijo"


ESTILO_FIJO = r"""
<!-- EDUTURNOS_ESTILO_FIJO -->

<style id="eduturnos-estilo-fijo">

/* =========================================================
   EDUTURNOS - ESTILO VISUAL FIJO
   ========================================================= */

/* Todo calcula sus tamaños correctamente */
#contenido,
#contenido *,
#contenido *::before,
#contenido *::after {
    box-sizing: border-box;
}

/* =========================================================
   TARJETAS Y FORMULARIOS
   ========================================================= */

#contenido .formulario {
    width: 100% !important;
    padding: 20px 0 !important;
}

#contenido .form-card,
#contenido .tarjeta {
    width: 100% !important;
    max-width: 850px !important;

    margin-left: auto !important;
    margin-right: auto !important;

    padding: 30px !important;

    border-radius: 14px !important;
}

/* =========================================================
   ENCABEZADO
   ========================================================= */

#contenido .section-heading {
    width: 100% !important;

    margin: 0 0 26px 0 !important;

    padding: 0 !important;
}

#contenido .section-heading .badge {
    display: inline-block !important;
    margin-bottom: 10px !important;
}

#contenido .section-heading h1 {
    display: block !important;

    width: 100% !important;

    margin: 0 0 10px 0 !important;

    line-height: 1.2 !important;
}

#contenido .section-heading p {
    display: block !important;

    width: 100% !important;

    margin: 0 !important;

    line-height: 1.55 !important;
}

/* =========================================================
   FORMULARIO PRINCIPAL
   ========================================================= */

#contenido form.stack-form,
#contenido form.form-uniform {
    width: 100% !important;

    display: flex !important;

    flex-direction: column !important;

    gap: 20px !important;

    margin: 0 !important;
}

/* =========================================================
   CADA CAMPO
   ========================================================= */

#contenido form.stack-form > label,
#contenido form.form-uniform > label {
    width: 100% !important;

    display: flex !important;

    flex-direction: column !important;

    align-items: stretch !important;

    justify-content: flex-start !important;

    gap: 7px !important;

    margin: 0 !important;
    padding: 0 !important;

    line-height: 1.3 !important;

    font-size: 14px !important;
}

/* =========================================================
   CAMPOS DE TEXTO
   ========================================================= */

#contenido form.stack-form input:not([type="checkbox"]):not([type="radio"]),
#contenido form.stack-form select,
#contenido form.stack-form textarea,

#contenido form.form-uniform input:not([type="checkbox"]):not([type="radio"]),
#contenido form.form-uniform select,
#contenido form.form-uniform textarea {

    display: block !important;

    width: 100% !important;
    max-width: 100% !important;

    min-height: 46px !important;

    margin: 0 !important;

    padding: 11px 14px !important;

    border-radius: 9px !important;

    font-size: 15px !important;

    font-weight: 400 !important;

    line-height: 1.3 !important;
}

/* =========================================================
   PERSONAL INSTITUCIONAL
   ========================================================= */

#contenido .personal-login {
    width: 100% !important;

    margin: 4px 0 0 0 !important;

    padding: 22px !important;

    border: 1px solid #dbe3ee !important;

    border-radius: 12px !important;

    background: #f8fafc !important;
}

#contenido .personal-login h3 {
    display: block !important;

    width: 100% !important;

    margin: 0 0 8px 0 !important;

    padding: 0 !important;

    line-height: 1.2 !important;
}

#contenido .personal-login > p {
    display: block !important;

    width: 100% !important;

    margin: 0 0 22px 0 !important;

    line-height: 1.55 !important;
}

/* =========================================================
   LOS TRES CAMPOS:
   CÓDIGO | SEDE | JORNADA
   ========================================================= */

#contenido .personal-login .form-grid {

    display: grid !important;

    grid-template-columns:
        repeat(3, minmax(0, 1fr)) !important;

    column-gap: 20px !important;

    row-gap: 20px !important;

    width: 100% !important;

    align-items: start !important;

    margin: 0 !important;

    padding: 0 !important;
}

#contenido .personal-login .form-grid > label {

    width: 100% !important;

    min-width: 0 !important;

    display: flex !important;

    flex-direction: column !important;

    align-items: stretch !important;

    justify-content: flex-start !important;

    gap: 7px !important;

    margin: 0 !important;

    padding: 0 !important;

    line-height: 1.3 !important;

    font-size: 14px !important;

    font-weight: 600 !important;
}

/* =========================================================
   TÍTULOS DE CÓDIGO / SEDE / JORNADA
   ========================================================= */

#contenido .personal-login .form-grid > label:first-child,
#contenido .personal-login .form-grid > label:nth-child(2),
#contenido .personal-login .form-grid > label:nth-child(3) {

    align-self: start !important;
}

/* =========================================================
   QUITAR EL PEQUEÑO TEXTO DE APOYO DEL TÍTULO
   ========================================================= */

#contenido .personal-login label small {
    display: none !important;
}

/* =========================================================
   CAMPOS DE PERSONAL INSTITUCIONAL
   ========================================================= */

#contenido .personal-login input,
#contenido .personal-login select {

    width: 100% !important;

    min-width: 0 !important;

    min-height: 46px !important;

    margin: 0 !important;

    padding: 11px 14px !important;

    background: #ffffff !important;

    border-radius: 9px !important;

    font-size: 15px !important;

    font-weight: 400 !important;

    line-height: 1.3 !important;
}

/* =========================================================
   LISTAS
   ========================================================= */

#contenido select {
    font-weight: 400 !important;
}

#contenido select option {
    font-weight: 400 !important;
}

/* =========================================================
   BOTÓN
   ========================================================= */

#contenido form.stack-form > button,
#contenido form.form-uniform > button {

    width: 100% !important;

    min-height: 48px !important;

    margin: 2px 0 0 0 !important;

    padding: 12px 18px !important;

    border-radius: 9px !important;

    font-size: 15px !important;

    font-weight: 600 !important;
}

/* =========================================================
   ENLACES
   ========================================================= */

#contenido .form-links {

    display: flex !important;

    justify-content: center !important;

    align-items: center !important;

    flex-wrap: wrap !important;

    gap: 18px !important;

    width: 100% !important;

    margin-top: 20px !important;
}

#contenido .form-links a {
    line-height: 1.4 !important;
}

/* =========================================================
   OTROS FORMULARIOS DEL SITIO
   ========================================================= */

#contenido form:not(.inline-form) label {

    line-height: 1.3 !important;
}

#contenido form:not(.inline-form) {

    max-width: 100% !important;
}

/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 900px) {

    #contenido .personal-login .form-grid {

        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;
    }
}

@media (max-width: 600px) {

    #contenido .form-card,
    #contenido .tarjeta {

        padding: 20px !important;
    }

    #contenido .personal-login {

        padding: 18px !important;
    }

    #contenido .personal-login .form-grid {

        grid-template-columns: 1fr !important;

        gap: 16px !important;
    }

    #contenido .form-links {

        flex-direction: column !important;

        gap: 10px !important;
    }
}

/* =========================================================
   FIN ESTILO FIJO
   ========================================================= */

</style>
<!-- FIN EDUTURNOS_ESTILO_FIJO -->
"""


# ------------------------------------------------------------
# Comprobar archivos
# ------------------------------------------------------------

if not BASE_HTML.exists():
    print("[ERROR] No existe templates/base.html")
    raise SystemExit(1)

if not LOGIN_HTML.exists():
    print("[ERROR] No existe templates/auth/login.html")
    raise SystemExit(1)


# ------------------------------------------------------------
# Copias de seguridad
# ------------------------------------------------------------

shutil.copy2(BASE_HTML, BACKUP_BASE)
shutil.copy2(LOGIN_HTML, BACKUP_LOGIN)

print(f"COPIA: {BACKUP_BASE}")
print(f"COPIA: {BACKUP_LOGIN}")


# ------------------------------------------------------------
# Insertar estilo directamente en base.html
# ------------------------------------------------------------

base = BASE_HTML.read_text(encoding="utf-8")

# Si ya existe el estilo fijo, reemplazarlo.
patron_estilo = re.compile(
    r'<!-- EDUTURNOS_ESTILO_FIJO -->.*?<!-- FIN EDUTURNOS_ESTILO_FIJO -->',
    re.IGNORECASE | re.DOTALL
)

if patron_estilo.search(base):

    base = patron_estilo.sub(
        ESTILO_FIJO.strip(),
        base
    )

    print("ACTUALIZADO: estilo fijo existente en base.html")

else:

    if "</head>" not in base.lower():
        print("[ERROR] base.html no contiene </head>")
        raise SystemExit(1)

    posicion = base.lower().find("</head>")

    base = (
        base[:posicion]
        + "\n"
        + ESTILO_FIJO
        + "\n"
        + base[posicion:]
    )

    print("AGREGADO: estilo fijo directamente en base.html")


BASE_HTML.write_text(
    base,
    encoding="utf-8"
)


# ------------------------------------------------------------
# Quitar "6 dígitos" del login
# ------------------------------------------------------------

login = LOGIN_HTML.read_text(encoding="utf-8")

login_original = login

login = re.sub(
    r'\s*<small>\s*6\s*(?:dÃ­gitos|dígitos|digitos)\s*</small>',
    "",
    login,
    flags=re.IGNORECASE
)

if login != login_original:

    LOGIN_HTML.write_text(
        login,
        encoding="utf-8"
    )

    print("CORREGIDO: login.html")

else:

    print("login.html ya no contiene el pequeño texto de 6 dígitos.")


print()
print("=" * 65)
print("DISEÑO FIJO INSTALADO")
print("=" * 65)
print()
print("Los títulos quedan arriba de cada cuadro.")
print("Código, Sede y Jornada quedan alineados.")
print("Todos los cuadros tienen el mismo ancho.")
print("Todos tienen separación uniforme.")
print("Los botones quedan alineados.")
print("Las listas conservan su funcionamiento.")
print("El texto de '6 dígitos' fue ocultado del título.")
print()
print("Se creó copia de seguridad antes del cambio.")
print()