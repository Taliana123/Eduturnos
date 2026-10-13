from pathlib import Path

ruta = Path("static/css/estilos.css")

if not ruta.exists():
    print("[ERROR] No existe static/css/estilos.css")
    raise SystemExit(1)

texto = ruta.read_text(encoding="utf-8")

css = r"""

/* =========================================================
   EDUTURNOS - LISTAS: TEXTO NORMAL
   ========================================================= */

select {
    font-weight: 400 !important;
}

select option {
    font-weight: 400 !important;
}
"""

# Evita agregar el mismo bloque varias veces
if "EDUTURNOS - LISTAS: TEXTO NORMAL" not in texto:
    texto += css
    ruta.write_text(texto, encoding="utf-8")
    print("CORRECTO: se quitó la negrita de las listas.")
else:
    print("CORRECTO: el ajuste ya estaba aplicado.")