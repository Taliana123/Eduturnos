import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import app
from servicios.email import enviar_correo_recuperacion, correo_configurado

with app.app_context():
    if not correo_configurado() or app.config.get("MAIL_MODE") != "smtp":
        raise SystemExit("El correo SMTP no está configurado. Ejecuta CONFIGURAR_CORREO.bat primero.")
    destinatario = input("Correo que recibirá la prueba: ").strip()
    if not destinatario:
        raise SystemExit("Debes indicar un correo de destino.")
    codigo = "123456"
    enviar_correo_recuperacion(destinatario, codigo)
    print("Correo de prueba enviado correctamente.")
