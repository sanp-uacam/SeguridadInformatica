"""Pruebas unitarias de las reglas y autenticacion."""

import hashlib
import unittest

from utils.auth import (
    authenticate_user,
    hash_password,
    register_user,
    validate_password,
)


class PasswordValidationTests(unittest.TestCase):
    def test_accepts_valid_password(self):
        self.assertTrue(validate_password("sergio", "R0ca!Azul").valid)

    def test_rejects_short_password(self):
        self.assertFalse(validate_password("ana", "A1!bc").valid)

    def test_rejects_missing_uppercase(self):
        self.assertFalse(validate_password("ana", "clave1!x").valid)

    def test_rejects_missing_lowercase(self):
        self.assertFalse(validate_password("ana", "CLAVE1!X").valid)

    def test_rejects_missing_number(self):
        self.assertFalse(validate_password("ana", "Clave!xx").valid)

    def test_rejects_missing_special_character(self):
        self.assertFalse(validate_password("ana", "Clave123").valid)

    def test_rejects_username_case_insensitively(self):
        result = validate_password("Sergio", "MiSergio1!")
        self.assertFalse(result.valid)
        self.assertIn("No debe incluir el nombre de usuario.", result.errors)


class HashAndAuthenticationTests(unittest.TestCase):
    def test_hash_is_sha256_hexadecimal(self):
        expected = hashlib.sha256("R0ca!Azul".encode("utf-8")).hexdigest()
        self.assertEqual(hash_password("R0ca!Azul"), expected)
        self.assertEqual(len(expected), 64)

    def test_registration_stores_hash_not_plaintext(self):
        users = {}
        success, _ = register_user(users, "sergio", "R0ca!Azul")
        self.assertTrue(success)
        self.assertNotEqual(users["sergio"], "R0ca!Azul")
        self.assertEqual(users["sergio"], hash_password("R0ca!Azul"))

    def test_duplicate_user_is_rejected(self):
        users = {"sergio": hash_password("R0ca!Azul")}
        success, _ = register_user(users, "sergio", "Otra1!Clave")
        self.assertFalse(success)

    def test_correct_credentials_authenticate(self):
        users = {"sergio": hash_password("R0ca!Azul")}
        self.assertTrue(authenticate_user(users, "sergio", "R0ca!Azul"))

    def test_wrong_password_is_rejected(self):
        users = {"sergio": hash_password("R0ca!Azul")}
        self.assertFalse(authenticate_user(users, "sergio", "Incorrecta1!"))

    def test_unknown_user_is_rejected(self):
        self.assertFalse(authenticate_user({}, "nadie", "Clave1!x"))


if __name__ == "__main__":
    unittest.main()
