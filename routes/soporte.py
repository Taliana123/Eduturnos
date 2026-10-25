from flask import Blueprint, render_template

from routes.helpers import login_requerido, usuario_actual

soporte_bp = Blueprint("soporte", __name__, url_prefix="/soporte")


@soporte_bp.get("/")
@login_requerido
def index():
    usuario = usuario_actual()
    return render_template("soporte/index.html", usuario=usuario)
