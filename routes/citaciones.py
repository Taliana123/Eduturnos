from flask import Blueprint, redirect, url_for

citaciones_bp=Blueprint("citaciones",__name__,url_prefix="/citaciones")

@citaciones_bp.route("/")
def lista():
    return redirect(url_for("citas.index"))

@citaciones_bp.route("/nueva")
def nueva():
    return redirect(url_for("citas.nueva"))

@citaciones_bp.post("/<int:cita_id>/estado")
def cambiar_estado(cita_id):
    from routes.citas import cambiar_estado as canonical
    return canonical(cita_id)
