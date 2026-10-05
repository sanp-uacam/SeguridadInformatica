"""Persistencia local: solo se almacena el SHA-256 de la contrasena."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class UserRepository:
    def __init__(self, file_path: str | Path): self.file_path = Path(file_path)
    def _load(self):
        if not self.file_path.exists(): return {}
        try:
            with self.file_path.open(encoding="utf-8") as file: return json.load(file)
        except (json.JSONDecodeError, OSError): return {}
    def _save(self, users):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as file: json.dump(users, file, ensure_ascii=False, indent=2)
    def register(self, username: str, password: str) -> bool:
        users, key = self._load(), username.casefold()
        if key in users: return False
        users[key] = {"username": username, "password_hash": hash_password(password)}
        self._save(users); return True
    def authenticate(self, username: str, password: str) -> bool:
        record = self._load().get(username.casefold())
        return bool(record and record.get("password_hash") == hash_password(password))
