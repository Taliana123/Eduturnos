# ============================================================
# ROLES Y VALIDACIONES DE EDUTURNOS
# ============================================================

import re

DOMINIO_GMAIL = "@gmail.com"
DOMINIO_INSTITUCIONAL = "@jjfh.edu.co"


# ============================================================
# VALIDAR NOMBRES / APELLIDOS (solo letras, espacios y tildes)
# ============================================================

_NOMBRE_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚÑÜáéíóúñü ]+$")


def es_nombre_valido(texto: str) -> bool:
    texto = (texto or "").strip()
    return bool(texto) and bool(_NOMBRE_REGEX.fullmatch(texto))


# ============================================================
# VALIDAR CAMPOS NUMÉRICOS (documento, teléfono, código, etc.)
# ============================================================

def es_solo_digitos(texto: str) -> bool:
    texto = (texto or "").strip()
    return bool(texto) and texto.isdigit()


def es_documento_valido(texto: str) -> bool:
    texto = (texto or "").strip()
    return texto.isascii() and texto.isdigit() and len(texto) <= 30


# ============================================================
# PORTALES
# ============================================================

PORTALES = {
    "estudiante": {
        "label": "Estudiante",
        "rol": "Estudiante",
        "identificador": "documento",
        "descripcion": "Consulta tus citaciones y calendario.",
        "requiere_codigo": False,
        "requiere_sede": False,
    },

    "acudiente": {
        "label": "Padre / Madre / Acudiente",
        "rol": "Acudiente",
        "identificador": "documento",
        "descripcion": "Consulta y confirma las citaciones de tus estudiantes asociados.",
        "requiere_codigo": False,
        "requiere_sede": False,
    },

    "docente": {
        "label": "Docente",
        "rol": "Docente",
        "identificador": "correo",
        "descripcion": "Correo institucional + contraseña + código personal + sede.",
        "requiere_codigo": True,
        "requiere_sede": True,
    },

    "coordinador": {
        "label": "Coordinador",
        "rol": "Administrador / Coordinador",
        "identificador": "correo",
        "descripcion": "Acceso institucional de coordinación.",
        "requiere_codigo": True,
        "requiere_sede": True,
    },

    "rector": {
        "label": "Rector",
        "rol": "Rector",
        "identificador": "correo",
        "descripcion": "Acceso institucional de rectoría.",
        "requiere_codigo": True,
        "requiere_sede": True,
    },
}


# ============================================================
# ROLES PARA LOGIN
# ============================================================

ROLES_LOGIN = [
    ("Estudiante", "Estudiante"),
    ("Acudiente", "Acudiente"),
    ("Docente", "Docente"),
    ("Coordinador", "Administrador / Coordinador"),
    ("Rector", "Rector"),
]


# ============================================================
# SEDES INSTITUCIONALES
# ============================================================

SEDES_INSTITUCIONALES = [
    (
        1,
        "Sede Principal (Las Américas)",
        "Ciudadela Las Américas, sector Picaleña (Cra. 15A Sur #2-01)",
        "238596",
    ),
    (
        2,
        "Sede Arboleda Campestre",
        "Calle 152 #21 Sur - 22, urbanización Arboleda Campestre",
        "418257",
    ),
    (
        3,
        "Sede Picaleña",
        "Barrio Picaleña, sobre la vía nacional",
        "724305",
    ),
    (
        4,
        "Sede Bello Horizonte",
        "Barrio Bello Horizonte (Km 3 vía Picaleña)",
        "351864",
    ),
    (
        5,
        "Sede Secundino Porras Cruz",
        "Zona sur de Ibagué, parte alta del barrio Picaleña",
        "563812",
    ),
    (
        6,
        "Sede San Francisco Club",
        "Calle 113 con Carrera 48 Sur",
        "896421",
    ),
    (
        7,
        "Sede San Martín",
        "Vereda San Martín",
        "602137",
    ),
]


# ============================================================
# VALIDAR CORREO INSTITUCIONAL
# ============================================================

def es_correo_institucional(correo: str) -> bool:
    return es_correo_de_dominio(correo, DOMINIO_INSTITUCIONAL)


def es_correo_gmail(correo: str) -> bool:
    return es_correo_de_dominio(correo, DOMINIO_GMAIL)


def es_correo_de_dominio(correo: str, dominio: str) -> bool:
    correo = (correo or "").strip().lower()
    dominio = (dominio or "").strip().lower()
    if not dominio.startswith("@"):
        dominio = f"@{dominio}"

    return (
        correo.count("@") == 1
        and len(correo) > len(dominio)
        and correo.endswith(dominio)
        and not any(caracter.isspace() for caracter in correo)
    )


def dominio_correo_para_rol(rol: str) -> str | None:
    rol = (rol or "").strip().casefold()
    if rol in {"estudiante", "acudiente"}:
        return DOMINIO_GMAIL
    if rol in {"docente", "rector", "administrador / coordinador"}:
        return DOMINIO_INSTITUCIONAL
    return None


def es_correo_valido_para_rol(rol: str, correo: str) -> bool:
    dominio = dominio_correo_para_rol(rol)
    return dominio is None or es_correo_de_dominio(correo, dominio)


# ============================================================
# VALIDAR FORMATO DEL CÓDIGO
# ============================================================

def es_codigo_institucional_valido(codigo: str) -> bool:
    codigo = (codigo or "").strip()

    return (
        len(codigo) == 6
        and codigo.isdigit()
    )


# ============================================================
# OBTENER CÓDIGO DE UNA SEDE
# ============================================================

def obtener_codigo_sede(sede_id):
    try:
        sede_id = int(sede_id)
    except (TypeError, ValueError):
        return None

    for sede in SEDES_INSTITUCIONALES:
        if sede[0] == sede_id:
            return sede[3]

    return None


# ============================================================
# VALIDAR CÓDIGO SEGÚN LA SEDE
# ============================================================

def validar_codigo_sede(sede_id, codigo) -> bool:
    codigo = (codigo or "").strip()

    if not es_codigo_institucional_valido(codigo):
        return False

    codigo_correcto = obtener_codigo_sede(sede_id)

    if not codigo_correcto:
        return False

    return codigo == codigo_correcto


# ============================================================
# OBTENER INFORMACIÓN DE UNA SEDE
# ============================================================

def obtener_sede(sede_id):
    try:
        sede_id = int(sede_id)
    except (TypeError, ValueError):
        return None

    for sede in SEDES_INSTITUCIONALES:
        if sede[0] == sede_id:
            return {
                "id": sede[0],
                "nombre": sede[1],
                "direccion": sede[2],
                "codigo": sede[3],
            }

    return None