from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import app
from servicios.google_calendar import procesar_cola_google


def main() -> int:
    with app.app_context():
        if not app.config.get("DB_BOOTSTRAP_OK"):
            app.logger.error("No se ejecutó la cola de Google Calendar: MySQL no está disponible.")
            return 1
        resultado = procesar_cola_google()
        print(
            "Google Calendar: "
            f"{resultado['procesadas']} procesadas, "
            f"{resultado['sincronizadas']} completadas, "
            f"{resultado['fallidas']} con error."
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
