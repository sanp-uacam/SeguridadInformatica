import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Permite ejecutar este archivo directamente desde la carpeta tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.login_app import LoginApp, validate_credentials, validate_password


class ValidateCredentialsTests(unittest.TestCase):
    def test_empty_username_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_credentials("", "ValidPassword!")

    def test_empty_password_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_credentials("usuario", "")

    def test_empty_fields_raise_value_error(self):
        with self.assertRaises(ValueError):
            validate_credentials("", "")

    def test_whitespace_fields_raise_value_error(self):
        with self.assertRaises(ValueError):
            validate_credentials("   ", "   ")

    def test_non_empty_credentials_are_valid(self):
        validate_credentials("usuario", "ValidPassword!")

    def test_each_blank_field_raises_value_error(self):
        for blank in ("", "   ", "\t\n"):
            for username, password in (
                (blank, "ClaveFuerte!9"),
                ("usuario", blank),
                (blank, blank),
            ):
                with self.subTest(username=username, password=password):
                    with self.assertRaisesRegex(ValueError, "no pueden estar vacíos"):
                        validate_credentials(username, password)


class ValidatePasswordTests(unittest.TestCase):
    def test_password_meets_requirements(self):
        errors = validate_password("usuario", "ClaveFuerte!9")

        self.assertEqual(errors, [])

    def test_password_does_not_meet_requirements(self):
        errors = validate_password("usuario", "123")

        self.assertTrue(errors)

    def test_empty_credentials_raise_value_error(self):
        with self.assertRaises(ValueError):
            validate_password("", "")

    def test_each_blank_field_raises_value_error(self):
        for blank in ("", "   ", "\t\n"):
            for username, password in (
                (blank, "ClaveFuerte!9"),
                ("usuario", blank),
            ):
                with self.subTest(username=username, password=password):
                    with self.assertRaises(ValueError):
                        validate_password(username, password)


class LoginTests(unittest.TestCase):
    @patch("utils.login_app.messagebox.showerror")
    def test_blank_credentials_stop_login(self, showerror):
        for blank in ("", "   ", "\t\n"):
            for username, password in (
                (blank, "ClaveFuerte!9"),
                ("usuario", blank),
                (blank, blank),
            ):
                with self.subTest(username=username, password=password):
                    # Evita abrir ventanas o acceder al archivo de usuarios.
                    app = LoginApp.__new__(LoginApp)
                    app.user_entry = Mock()
                    app.user_entry.get.return_value = username
                    app.pass_entry = Mock()
                    app.pass_entry.get.return_value = password
                    app.users = Mock()
                    app.hash_password = Mock()
                    app.open_dashboard = Mock()
                    showerror.reset_mock()

                    app.login()

                    showerror.assert_called_once_with(
                        "Error", "El usuario y la contraseña no pueden estar vacíos."
                    )
                    app.users.get.assert_not_called()
                    app.hash_password.assert_not_called()
                    app.open_dashboard.assert_not_called()


if __name__ == "__main__":
    unittest.main()
