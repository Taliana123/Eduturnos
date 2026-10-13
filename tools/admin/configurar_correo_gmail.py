import getpass
from pathlib import Path
import smtplib

ROOT = Path(__file__).resolve().parents[2]
ENV = ROOT / ".env"

print("=" * 60)
print("EDUTURNOS - CONFIGURAR GMAIL PARA RECUPERACION")
print("=" * 60)
print()
print("Necesitas Verificacion en 2 pasos y una contrasena de aplicacion de Google.")
print("La contrasena de aplicacion no es tu contrasena normal de Gmail.")
print()

correo = input("Correo de Gmail que enviara los codigos: ").strip()
app_password = getpass.getpass("Contrasena de aplicacion de Google: ").strip().replace(" ", "")

if "@" not in correo or "." not in correo.split("@", 1)[-1]:
    print("ERROR: escribe un correo valido.")
    raise SystemExit(1)
if len(app_password) != 16:
    print("ERROR: la contrasena de aplicacion debe tener 16 caracteres.")
    raise SystemExit(1)

# Test SMTP before saving configuration.
try:
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(correo, app_password)
    print("\nConexion con Gmail: OK")
except Exception as exc:
    print("\nERROR: no se pudo autenticar con Gmail.")
    print("Revisa Verificacion en 2 pasos y la contrasena de aplicacion.")
    print(f"Detalle tecnico: {exc}")
    raise SystemExit(2)

lines = []
if ENV.exists():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        key = line.split("=",1)[0].strip() if "=" in line else ""
        if key in {"MAIL_HOST","MAIL_PORT","MAIL_USERNAME","MAIL_PASSWORD","MAIL_FROM","MAIL_USE_TLS"}:
            continue
        lines.append(line)

lines.extend([
    "",
    "# Gmail configurado automaticamente para recuperacion de EDUTURNOS",
    "MAIL_HOST=smtp.gmail.com",
    "MAIL_PORT=587",
    f"MAIL_USERNAME={correo}",
    f"MAIL_PASSWORD={app_password}",
    f"MAIL_FROM={correo}",
    "MAIL_USE_TLS=1",
])
ENV.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
print("Configuracion guardada en .env")
print("EDUTURNOS ya puede enviar codigos de recuperacion por Gmail.")
