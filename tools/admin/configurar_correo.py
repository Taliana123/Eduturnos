from pathlib import Path
import getpass

ROOT = Path(__file__).resolve().parents[2]
ENV = ROOT / ".env"

print("=" * 60)
print("EDUTURNOS - CONFIGURACIÓN DE CORREO")
print("=" * 60)
print("Esta configuración se realiza UNA SOLA VEZ en el servidor/computador que envía los correos.")
print("Los usuarios finales nunca verán ni introducirán estos datos.")
print("Esta es la UNICA cuenta remitente; cada usuario recibirá el mensaje en su propio correo.\n")

sender = input("Correo remitente del sistema: ").strip()
password = getpass.getpass("Contraseña de aplicación SMTP (no se mostrará): ").strip().replace(" ", "")
port = input("Puerto SMTP [587]: ").strip() or "587"

if not sender or not password:
    raise SystemExit("Faltan datos del remitente.")

host = "smtp.gmail.com"
use_tls = "1" if port != "465" else "0"
use_ssl = "1" if port == "465" else "0"

existing = {}
if ENV.exists():
    for raw in ENV.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        existing[k.strip()] = v.strip()

existing.update({
    "MAIL_MODE": "smtp",
    "MAIL_HOST": host,
    "MAIL_PORT": port,
    "MAIL_USE_TLS": use_tls,
    "MAIL_USE_SSL": use_ssl,
    "MAIL_USERNAME": sender,
    "MAIL_PASSWORD": password,
    "MAIL_FROM": sender,
})

ordered = [
    "MAIL_MODE", "MAIL_HOST", "MAIL_PORT", "MAIL_USE_TLS", "MAIL_USE_SSL",
    "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM",
]
seen = set()
lines = []
for key in ordered:
    if key in existing:
        lines.append(f"{key}={existing[key]}")
        seen.add(key)
for key, value in existing.items():
    if key not in seen:
        lines.append(f"{key}={value}")

ENV.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\nConfiguración guardada en .env")
print("No se muestra la contraseña por seguridad.")
