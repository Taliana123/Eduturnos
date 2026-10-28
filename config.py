from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).resolve().parent / ".env")

def _first(*names, default=""):
    for name in names:
        value = os.getenv(name)
        if value is not None:
            return value
    return default


class Config:
    _raw_secret = _first("SECRET_KEY", default="")
    SECRET_KEY_INSECURE = not bool(_raw_secret)
    SECRET_KEY = _raw_secret or "dev-only-change-me"
    APP_ENV = _first("APP_ENV", default="development")
    TEMPLATES_AUTO_RELOAD = APP_ENV != "production"
    DEV_MODE = _first("DEV_MODE", default="0") == "1"
    TESTING = _first("TESTING", default="0") == "1"
    MYSQL_HOST = _first("MYSQL_HOST", "MYSQLHOST", default="127.0.0.1")
    MYSQL_PORT = int(_first("MYSQL_PORT", "MYSQLPORT", default="3306"))
    MYSQL_USER = _first("MYSQL_USER", "MYSQLUSER", default="root")
    MYSQL_PASSWORD = _first("MYSQL_PASSWORD", "MYSQLPASSWORD", default="")
    MYSQL_DATABASE = _first("MYSQL_DATABASE", "MYSQLDATABASE", default="eduturnos")
    MYSQL_POOL_SIZE = int(_first("MYSQL_POOL_SIZE", default="10"))
    APP_ORIGIN = _first("APP_ORIGIN", default="")
    SESSION_COOKIE_SECURE = _first("SESSION_COOKIE_SECURE", default="1" if APP_ENV == "production" else "0") == "1"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 365 * 24 * 60 * 60
    SESSION_REFRESH_EACH_REQUEST = True
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    # Correo: una única cuenta remitente del sistema. Los usuarios reciben en su propio correo.
    MAIL_HOST = _first("MAIL_HOST", "SMTP_HOST", default="smtp.gmail.com")
    MAIL_PORT = int(_first("MAIL_PORT", "SMTP_PORT", default="587"))
    MAIL_USERNAME = _first("MAIL_USERNAME", "SMTP_USER", default="")
    MAIL_PASSWORD = _first("MAIL_PASSWORD", "SMTP_PASSWORD", default="")
    MAIL_FROM = _first("MAIL_FROM", default=MAIL_USERNAME)
    MAIL_USE_TLS = _first("MAIL_USE_TLS", "SMTP_TLS", default="1") == "1"
    MAIL_USE_SSL = _first("MAIL_USE_SSL", default="1" if MAIL_PORT == 465 else "0") == "1"
    MAIL_TIMEOUT = int(_first("MAIL_TIMEOUT", default="20"))
    SUPPORT_EMAIL = _first("SUPPORT_EMAIL", default="coliejjfh@hotmail.com")
    GOOGLE_OAUTH_CLIENT_ID = _first("GOOGLE_OAUTH_CLIENT_ID", default="")
    GOOGLE_OAUTH_CLIENT_SECRET = _first("GOOGLE_OAUTH_CLIENT_SECRET", default="")
    GOOGLE_CALENDAR_ID = _first("GOOGLE_CALENDAR_ID", default="primary")
    GOOGLE_APPS_SCRIPT_URL = _first("GOOGLE_APPS_SCRIPT_URL", default="")
    GOOGLE_APPS_SCRIPT_SECRET = _first("GOOGLE_APPS_SCRIPT_SECRET", default="")
    GROQ_API_KEY = _first("GROQ_API_KEY", default="")
    GROQ_MODEL = _first("GROQ_MODEL", default="openai/gpt-oss-120b")
    BEEPY_DOMAINS = tuple(
        domain.strip().lower()
        for domain in _first(
            "BEEPY_DOMAINS",
            default=f"{_first('BEEPY_DOMAIN', default='seventy-excavator-designate.ngrok-free.dev')},eduturnos-jjfh.alwaysdata.net",
        ).split(",")
        if domain.strip()
    )
    BEEPY_DOMAIN = _first("BEEPY_DOMAIN", default=BEEPY_DOMAINS[0] if BEEPY_DOMAINS else "")
    BEEPY_ENABLED = _first("BEEPY_ENABLED", default="1") == "1"
    BEEPY_CHAT_URL = _first("BEEPY_CHAT_URL", default="https://www.beepychatbot.com/u/1nLBFlV/")
    _mail_mode = _first("MAIL_MODE", default="")
    MAIL_MODE = _mail_mode.lower() if _mail_mode else ("smtp" if MAIL_USERNAME and MAIL_PASSWORD and MAIL_FROM else ("console" if DEV_MODE else "disabled"))
    # Alias para compatibilidad con versiones anteriores.
    SMTP_HOST = MAIL_HOST
    SMTP_PORT = MAIL_PORT
    SMTP_USER = MAIL_USERNAME
    SMTP_PASSWORD = MAIL_PASSWORD
    SMTP_TLS = MAIL_USE_TLS
