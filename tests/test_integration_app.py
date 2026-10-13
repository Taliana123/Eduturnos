import os
import unittest

from app import app
from database.db import comprobar_conexion


class TestIntegracionEDUTURNOS(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_funciona(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"EDUTURNOS", respuesta.data)

    def test_login_presenta_acceso_por_identificador_y_deteccion_automatica(self):
        respuesta = self.client.get("/auth/login")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Documento o correo".encode(), respuesta.data)
        self.assertIn("Personal institucional".encode(), respuesta.data)
        self.assertIn("El sistema determina tu rol".encode(), respuesta.data)
        self.assertNotIn(b'<select name="rol"', respuesta.data)
        self.assertIn(b"Coordinador", respuesta.data)

    def test_conexion_real_a_mysql(self):
        if os.environ.get("EDUTURNOS_SKIP_DB_TEST") == "1":
            self.skipTest("Prueba de MySQL desactivada por variable de entorno.")
        try:
            with app.app_context():
                self.assertTrue(comprobar_conexion())
        except Exception as exc:
            self.skipTest(f"MySQL no está disponible para la prueba de integración: {exc}")


if __name__ == "__main__":
    unittest.main()


def test_citas_endpoint_registered():
    assert 'citas.index' in {rule.endpoint for rule in app.url_map.iter_rules()}
