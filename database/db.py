from contextlib import contextmanager
import threading

import mysql.connector
from flask import current_app


_POOLS = {}
_LOCK = threading.Lock()


def _pool():
    key = (
        current_app.config["MYSQL_HOST"],
        current_app.config["MYSQL_PORT"],
        current_app.config["MYSQL_USER"],
        current_app.config["MYSQL_DATABASE"],
    )

    if key not in _POOLS:
        with _LOCK:
            if key not in _POOLS:
                _POOLS[key] = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="eduturnos_pool_%s" % abs(hash(key)),
                    pool_size=current_app.config.get("MYSQL_POOL_SIZE", 10),
                    host=current_app.config["MYSQL_HOST"],
                    port=current_app.config["MYSQL_PORT"],
                    user=current_app.config["MYSQL_USER"],
                    password=current_app.config["MYSQL_PASSWORD"],
                    database=current_app.config["MYSQL_DATABASE"],
                    autocommit=False,
                )

    return _POOLS[key]


@contextmanager
def conexion():
    cnx = _pool().get_connection()

    try:
        yield cnx
    finally:
        cnx.close()


def comprobar_conexion():
    with conexion() as cnx:
        cur = cnx.cursor()

        try:
            cur.execute("SELECT 1")
            return cur.fetchone() == (1,)
        finally:
            cur.close()


def consultar(sql, params=(), uno=False):
    with conexion() as cnx:
        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute(sql, params)
            rows = cur.fetchall()

            if uno:
                return rows[0] if rows else None

            return rows

        finally:
            cur.close()


def ejecutar(sql, params=()):
    with conexion() as cnx:
        cur = cnx.cursor()

        try:
            cur.execute(sql, params)
            cnx.commit()
            return cur.lastrowid

        except Exception:
            cnx.rollback()
            raise

        finally:
            cur.close()


@contextmanager
def transaccion():
    cnx = _pool().get_connection()

    try:
        yield cnx
        cnx.commit()

    except Exception:
        cnx.rollback()
        raise

    finally:
        cnx.close()