import json, tempfile, unittest
from pathlib import Path
from utils.password_rules import validate_password
from utils.users_db import UserRepository, hash_password

class HashPracticeTests(unittest.TestCase):
    def test_sha256(self): self.assertEqual(len(hash_password("Q!7mR#2z")), 64)
    def test_rules(self):
        self.assertEqual(validate_password("sergio", "Q!7mR#2z"), [])
        self.assertTrue(validate_password("sergio", "Sergio123!"))
    def test_storage_and_login(self):
        with tempfile.TemporaryDirectory() as folder:
            path, repo = Path(folder) / "users.json", UserRepository(Path(folder) / "users.json")
            self.assertTrue(repo.register("sergio", "Q!7mR#2z")); self.assertTrue(repo.authenticate("sergio", "Q!7mR#2z")); self.assertFalse(repo.authenticate("sergio", "incorrecta"))
            self.assertNotIn("Q!7mR#2z", json.loads(path.read_text(encoding="utf-8")).__str__())

if __name__ == "__main__": unittest.main(verbosity=2)
