from flask import Blueprint, redirect

soporte_bp = Blueprint("soporte", __name__, url_prefix="/soporte")


@soporte_bp.get("/")
def index():
    return redirect(
        "mailto:coliejjfh@hotmail.com"
        "?subject=Ayuda%20con%20EDUTURNOS"
        "&body=Hola%2C%20necesito%20ayuda%20con%20EDUTURNOS"
    )
