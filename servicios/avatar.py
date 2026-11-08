import json

from database.db import consultar, ejecutar


AVATAR_CHOICES = {
    "character": {
        "title": "Personaje",
        "options": [
            {"value": "feminine", "label": "Femenino", "swatch": "#ad6c94"},
            {"value": "masculine", "label": "Masculino", "swatch": "#4777b7"},
            {"value": "neutral", "label": "Neutro", "swatch": "#68866f"},
        ],
    },
    "ageStyle": {
        "title": "Edad",
        "options": [
            {"value": "child", "label": "Infantil", "swatch": "#80a8d7"},
            {"value": "teen", "label": "Joven", "swatch": "#709b84"},
            {"value": "adult", "label": "Adulto", "swatch": "#b18b67"},
        ],
    },
    "hairstyle": {
        "title": "Peinado",
        "options": [
            {"value": "short", "label": "Corto", "swatch": "#30384d"},
            {"value": "long", "label": "Largo", "swatch": "#30384d"},
            {"value": "wavy", "label": "Ondulado", "swatch": "#30384d"},
            {"value": "curly", "label": "Rizado", "swatch": "#30384d"},
            {"value": "bun", "label": "Recogido", "swatch": "#30384d"},
            {"value": "straight", "label": "Liso", "swatch": "#30384d"},
        ],
    },
    "hairColor": {
        "title": "Color de cabello",
        "options": [
            {"value": "#282331", "label": "Negro", "swatch": "#282331"},
            {"value": "#69432f", "label": "Castaño", "swatch": "#69432f"},
            {"value": "#c99537", "label": "Rubio", "swatch": "#c99537"},
            {"value": "#a84d35", "label": "Pelirrojo", "swatch": "#a84d35"},
            {"value": "#858795", "label": "Gris", "swatch": "#858795"},
            {"value": "#4c6a9c", "label": "Azul", "swatch": "#4c6a9c"},
        ],
    },
    "skinColor": {
        "title": "Tono de piel",
        "options": [
            {"value": "#f5d6bd", "label": "Claro", "swatch": "#f5d6bd"},
            {"value": "#efc19a", "label": "Cálido", "swatch": "#efc19a"},
            {"value": "#d99c72", "label": "Canela", "swatch": "#d99c72"},
            {"value": "#b87855", "label": "Bronce", "swatch": "#b87855"},
            {"value": "#89583f", "label": "Moreno", "swatch": "#89583f"},
            {"value": "#603f35", "label": "Oscuro", "swatch": "#603f35"},
        ],
    },
    "eyeColor": {
        "title": "Color de ojos",
        "options": [
            {"value": "#493124", "label": "Café", "swatch": "#493124"},
            {"value": "#497454", "label": "Verde", "swatch": "#497454"},
            {"value": "#4b78a5", "label": "Azul", "swatch": "#4b78a5"},
            {"value": "#9a7040", "label": "Miel", "swatch": "#9a7040"},
        ],
    },
    "outfit": {
        "title": "Vestimenta",
        "options": [
            {"value": "shirt", "label": "Camiseta", "swatch": "#2875c7"},
            {"value": "hoodie", "label": "Sudadera", "swatch": "#3d8b72"},
            {"value": "uniform", "label": "Uniforme", "swatch": "#794f9c"},
            {"value": "jacket", "label": "Chaqueta", "swatch": "#34445d"},
            {"value": "sweater", "label": "Suéter", "swatch": "#c77a46"},
        ],
    },
    "shirtColor": {
        "title": "Color de ropa",
        "options": [
            {"value": "#2875c7", "label": "Azul", "swatch": "#2875c7"},
            {"value": "#3d8b72", "label": "Verde", "swatch": "#3d8b72"},
            {"value": "#794f9c", "label": "Violeta", "swatch": "#794f9c"},
            {"value": "#e2a53a", "label": "Dorado", "swatch": "#e2a53a"},
            {"value": "#c45252", "label": "Coral", "swatch": "#c45252"},
            {"value": "#34445d", "label": "Marino", "swatch": "#34445d"},
        ],
    },
    "accessory": {
        "title": "Accesorios",
        "options": [
            {"value": "none", "label": "Ninguno", "swatch": "#e7edf5"},
            {"value": "glasses", "label": "Gafas", "swatch": "#53708e"},
            {"value": "cap", "label": "Gorra", "swatch": "#d74c46"},
            {"value": "headband", "label": "Diadema", "swatch": "#b85d83"},
        ],
    },
}

DEFAULT_AVATAR = {
    "character": "neutral",
    "ageStyle": "teen",
    "hairstyle": "short",
    "hairColor": "#282331",
    "skinColor": "#efc19a",
    "eyeColor": "#493124",
    "outfit": "hoodie",
    "shirtColor": "#2875c7",
    "accessory": "none",
}


def avatar_inicial(id_usuario):
    """Genera una combinación estable y variada para una cuenta nueva."""
    user_id = int(id_usuario)
    if user_id < 1:
        raise ValueError("El usuario debe tener un identificador válido.")

    avatar = dict(DEFAULT_AVATAR)
    fields = ("character", "ageStyle", "hairstyle", "hairColor", "skinColor", "eyeColor", "outfit", "shirtColor", "accessory")
    for offset, field in enumerate(fields, start=1):
        options = AVATAR_CHOICES[field]["options"]
        avatar[field] = options[(user_id * (offset * 2 + 1) + offset) % len(options)]["value"]
    return avatar


def normalizar_avatar(value):
    if not isinstance(value, dict) or set(value) != set(DEFAULT_AVATAR):
        raise ValueError("La configuración del personaje no tiene el formato esperado.")

    normalized = {}
    for field, default in DEFAULT_AVATAR.items():
        allowed = {option["value"] for option in AVATAR_CHOICES[field]["options"]}
        choice = value.get(field)
        if not isinstance(choice, str) or choice not in allowed:
            raise ValueError("Una de las opciones del personaje no es válida.")
        normalized[field] = choice
    return normalized


def _leer_avatar(id_usuario):
    row = consultar(
        "SELECT avatar_json FROM avatares_usuario WHERE id_usuario=%s",
        (id_usuario,),
        uno=True,
    )
    if not row:
        return None

    stored = row["avatar_json"]
    if isinstance(stored, str):
        stored = json.loads(stored)
    return normalizar_avatar(stored)


def obtener_o_crear_avatar(id_usuario):
    user_id = int(id_usuario)
    avatar = _leer_avatar(user_id)
    if avatar is not None:
        return avatar

    initial = avatar_inicial(user_id)
    ejecutar(
        "INSERT IGNORE INTO avatares_usuario (id_usuario, avatar_json) VALUES (%s, %s)",
        (user_id, json.dumps(initial, separators=(",", ":"))),
    )
    avatar = _leer_avatar(user_id)
    if avatar is None:
        raise RuntimeError("No fue posible guardar el personaje inicial.")
    return avatar


def guardar_avatar(id_usuario, value):
    user_id = int(id_usuario)
    avatar = normalizar_avatar(value)
    ejecutar(
        "INSERT INTO avatares_usuario (id_usuario, avatar_json) VALUES (%s, %s) "
        "ON DUPLICATE KEY UPDATE avatar_json=VALUES(avatar_json)",
        (user_id, json.dumps(avatar, separators=(",", ":"))),
    )
    return avatar
