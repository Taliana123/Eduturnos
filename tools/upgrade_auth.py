from pathlib import Path
import mysql.connector
from config import Config

ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / "sql" / "auth_migration.sql"


def main():
    cnx = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
    )
    try:
        cur = cnx.cursor()
        sql = SQL_FILE.read_text(encoding="utf-8")
        for statement in [x.strip() for x in sql.split(";") if x.strip()]:
            cur.execute(statement)
        cnx.commit()
        print("OK: tabla codigos_acceso disponible.")
    finally:
        cur.close()
        cnx.close()


if __name__ == "__main__":
    main()
