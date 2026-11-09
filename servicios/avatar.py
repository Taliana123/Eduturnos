import json
import re
from functools import lru_cache
from pathlib import Path

from database.db import consultar, ejecutar


HUMATION_SLOTS = ("head", "body", "bottom", "item", "glasses")
HUMATION_COLORS = ("hair", "clothes", "bottom", "skin", "stroke")
AVATAR_FIELDS = {"seed", "gender", "selections", "colors", "background"}
AVATAR_GENDERS = {"mujer", "hombre", "nina", "nino"}
_AVATAR_FIELDS_WITHOUT_GENDER = AVATAR_FIELDS - {"gender"}
_HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")
_SEED = re.compile(r"[A-Za-z0-9._:-]{1,128}\Z")

_HAIR_COLORS = ("#4A3728", "#282331", "#6B4934", "#A84D35", "#858795")
_SKIN_COLORS = ("#F4C9A8", "#E9B889", "#CF9368", "#AD7655", "#81573F", "#603F35")
_CLOTHES_COLORS = ("#6C91C2", "#4D806D", "#98688D", "#C18C49", "#52758A")


@lru_cache(maxsize=1)
def _official_parts():
    path = Path(__file__).resolve().parents[1] / "static" / "vendor" / "humation-parts.json"
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("No está disponible el catálogo local de piezas oficiales de Humation.") from exc

    if not isinstance(catalog, dict) or set(catalog) != set(HUMATION_SLOTS):
        raise RuntimeError("El catálogo local de piezas de Humation no tiene el formato esperado.")

    parts = {}
    for slot in HUMATION_SLOTS:
        entries = catalog[slot]
        if not isinstance(entries, list):
            raise RuntimeError(f"El catálogo de Humation para {slot} no es válido.")
        ids = {
            entry.get("id")
            for entry in entries
            if isinstance(entry, dict) and isinstance(entry.get("id"), str)
        }
        if not ids:
            raise RuntimeError(f"El catálogo de Humation no contiene piezas para {slot}.")
        parts[slot] = ids
    return parts


def _valid_user_id(id_usuario):
    user_id = int(id_usuario)
    if user_id < 1:
        raise ValueError("El usuario debe tener un identificador válido.")
    return user_id


def avatar_inicial(id_usuario):
    user_id = _valid_user_id(id_usuario)
    return {
        "seed": f"eduturnos-{user_id}",
        "gender": None,
        "selections": {},
        "colors": {
            "hair": _HAIR_COLORS[user_id % len(_HAIR_COLORS)],
            "skin": _SKIN_COLORS[user_id % len(_SKIN_COLORS)],
            "clothes": _CLOTHES_COLORS[user_id % len(_CLOTHES_COLORS)],
        },
        "background": "transparent",
    }


def normalizar_avatar(value):
    if not isinstance(value, dict) or set(value) not in (AVATAR_FIELDS, _AVATAR_FIELDS_WITHOUT_GENDER):
        raise ValueError("La configuración del personaje no tiene el formato esperado.")

    gender = value.get("gender")
    if gender is not None and (not isinstance(gender, str) or gender not in AVATAR_GENDERS):
        raise ValueError("El género del personaje no es válido.")

    seed = value.get("seed")
    if not isinstance(seed, str) or not _SEED.fullmatch(seed):
        raise ValueError("La semilla del personaje no es válida.")

    selections = value.get("selections")
    if not isinstance(selections, dict) or not set(selections).issubset(HUMATION_SLOTS):
        raise ValueError("Las piezas del personaje no son válidas.")
    allowed_parts = _official_parts()
    normalized_selections = {}
    for slot, part_id in selections.items():
        if not isinstance(part_id, str) or part_id not in allowed_parts[slot]:
            raise ValueError("Una de las piezas no pertenece al catálogo oficial de Humation.")
        normalized_selections[slot] = part_id

    colors = value.get("colors")
    if not isinstance(colors, dict) or not set(colors).issubset(HUMATION_COLORS):
        raise ValueError("Los colores del personaje no son válidos.")
    normalized_colors = {}
    for slot, color in colors.items():
        if not isinstance(color, str) or not _HEX_COLOR.fullmatch(color):
            raise ValueError("Uno de los colores del personaje no es válido.")
        normalized_colors[slot] = color.upper()

    background = value.get("background")
    if background != "transparent" and (
        not isinstance(background, str) or not _HEX_COLOR.fullmatch(background)
    ):
        raise ValueError("El fondo del personaje no es válido.")

    return {
        "seed": seed,
        "gender": gender,
        "selections": normalized_selections,
        "colors": normalized_colors,
        "background": background.upper() if isinstance(background, str) and background != "transparent" else "transparent",
    }


def _convertir_avatar_anterior(value, id_usuario):
    legacy_fields = {
        "character",
        "ageStyle",
        "hairstyle",
        "hairColor",
        "skinColor",
        "eyeColor",
        "outfit",
        "shirtColor",
        "accessory",
    }
    if not isinstance(value, dict) or set(value) != legacy_fields:
        return None

    migrated = avatar_inicial(id_usuario)
    color_map = {
        "hair": value.get("hairColor"),
        "skin": value.get("skinColor"),
        "clothes": value.get("shirtColor"),
    }
    for slot, color in color_map.items():
        if isinstance(color, str) and _HEX_COLOR.fullmatch(color):
            migrated["colors"][slot] = color.upper()
    return migrated


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
    try:
        return normalizar_avatar(stored)
    except ValueError:
        migrated = _convertir_avatar_anterior(stored, id_usuario)
        if migrated is None:
            raise
        ejecutar(
            "UPDATE avatares_usuario SET avatar_json=%s WHERE id_usuario=%s",
            (json.dumps(migrated, separators=(",", ":")), id_usuario),
        )
        return migrated


def obtener_o_crear_avatar(id_usuario):
    user_id = _valid_user_id(id_usuario)
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
    user_id = _valid_user_id(id_usuario)
    avatar = normalizar_avatar(value)
    ejecutar(
        "INSERT INTO avatares_usuario (id_usuario, avatar_json) VALUES (%s, %s) "
        "ON DUPLICATE KEY UPDATE avatar_json=VALUES(avatar_json)",
        (user_id, json.dumps(avatar, separators=(",", ":"))),
    )
    return avatar
