"""Pruebas de persistencia JSON."""

import json
import tempfile
import unittest
from pathlib import Path

from utils.saveJson import cargar_diccionario, guardar_diccionario


class JsonPersistenceTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "users.json"
            expected = {"alan": "a" * 64}
            self.assertTrue(guardar_diccionario(expected, path))
            self.assertEqual(cargar_diccionario(path), expected)

    def test_missing_file_returns_empty_dictionary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            self.assertEqual(cargar_diccionario(path), {})

    def test_invalid_json_returns_empty_dictionary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "users.json"
            path.write_text("{invalid", encoding="utf-8")
            self.assertEqual(cargar_diccionario(path), {})

    def test_plaintext_password_is_not_written_when_given_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "users.json"
            guardar_diccionario({"alan": "b" * 64}, path)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["alan"], "b" * 64)


if __name__ == "__main__":
    unittest.main()
