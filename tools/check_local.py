import sys
import mysql.connector
from config import Config
try:
    cnx = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        connection_timeout=3,
    )
except Exception as exc:
    print(f"MYSQL_ERROR: {exc}")
    sys.exit(1)
try:
    cur = cnx.cursor()
    cur.execute("SHOW DATABASES LIKE %s", (Config.MYSQL_DATABASE,))
    exists = cur.fetchone() is not None
    if not exists:
        print("MYSQL_OK_DB_MISSING")
        sys.exit(10)
    cur.execute(f"USE `{Config.MYSQL_DATABASE}`")
    cur.execute("SHOW TABLES LIKE 'usuarios'")
    if cur.fetchone() is None:
        print("MYSQL_OK_SCHEMA_MISSING")
        sys.exit(10)
    print("MYSQL_OK_DB_OK")
    sys.exit(0)
finally:
    try: cur.close()
    except Exception: pass
    cnx.close()
