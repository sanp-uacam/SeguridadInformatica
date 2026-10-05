"""Pruebas de hash, reglas, persistencia y autenticación sin datos reales."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from utils import login_app as app


class PruebasLogin(unittest.TestCase):
    def test_vector_sha256(self):
        self.assertEqual(app.hash_password("abc"),
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_password_valida(self):
        self.assertTrue(all(ok for _, ok in app.password_rules("alumno", "Clave!507")))

    def test_password_debil(self):
        self.assertFalse(all(ok for _, ok in app.password_rules("alumno", "alumno123")))

    def test_numeros_consecutivos(self):
        for value in ("Abc!1234", "Abc!9876"):
            self.assertTrue(app.has_consecutive_numbers(value))
        self.assertFalse(app.has_consecutive_numbers("Abc!5075"))

    def test_usuario_en_password(self):
        self.assertFalse(app.password_rules(" Alumno ", "ALUMNO!507a")[-1][1])

    def test_persistencia_solo_hash(self):
        instance = app.LoginApp.__new__(app.LoginApp)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "users.json"
            with patch.object(app, "DATABASE_PATH", path):
                self.assertEqual(instance.load_users(), {})
                instance.users = {"Alumno": app.hash_password("Clave!507")}
                instance.save_users()
                self.assertNotIn("Clave!507", path.read_text())
                self.assertEqual(instance.load_users(), instance.users)
                self.assertEqual(json.loads(path.read_text()), instance.users)

    def test_login_correcto_e_incorrecto(self):
        instance = app.LoginApp.__new__(app.LoginApp)
        instance.users = {"Alumno": app.hash_password("Clave!507")}
        instance.user_entry = Mock()
        instance.pass_entry = Mock()
        instance.user_entry.get.return_value = " alumno "
        with patch.object(app.messagebox, "showinfo") as ok, patch.object(app.messagebox, "showerror") as error:
            instance.pass_entry.get.return_value = "Clave!507"
            instance.login()
            ok.assert_called_once()
            error.assert_not_called()
            ok.reset_mock()
            instance.pass_entry.get.return_value = "Incorrecta!507"
            instance.login()
            error.assert_called_once()
            ok.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
