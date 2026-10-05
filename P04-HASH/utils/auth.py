"""Reglas de contrasena, hash SHA-256 y autenticacion."""

from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass


MIN_PASSWORD_LENGTH = 8
SPECIAL_CHARACTER = re.compile(r"[^A-Za-z0-9\s]")


@dataclass(frozen=True)
class PasswordValidation:
    """Resultado de validar una contrasena."""

    valid: bool
    errors: tuple[str, ...]


def hash_password(password: str) -> str:
    """Devuelve el resumen hexadecimal SHA-256 de ``password`` en UTF-8."""

    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def validate_password(username: str, password: str) -> PasswordValidation:
    """Valida las reglas escritas en el pizarron de la practica."""

    errors: list[str] = []
    normalized_username = username.strip().casefold()
    normalized_password = password.casefold()

    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append("Debe contener al menos 8 caracteres.")
    if not any(character.isupper() for character in password):
        errors.append("Debe incluir al menos una letra mayuscula.")
    if not any(character.islower() for character in password):
        errors.append("Debe incluir al menos una letra minuscula.")
    if not any(character.isdigit() for character in password):
        errors.append("Debe incluir al menos un numero.")
    if SPECIAL_CHARACTER.search(password) is None:
        errors.append("Debe incluir al menos un caracter especial.")
    if normalized_username and normalized_username in normalized_password:
        errors.append("No debe incluir el nombre de usuario.")

    return PasswordValidation(valid=not errors, errors=tuple(errors))


def verify_password(password: str, stored_hash: str) -> bool:
    """Compara el hash calculado con el almacenado evitando comparacion directa."""

    candidate_hash = hash_password(password)
    return hmac.compare_digest(candidate_hash, stored_hash)


def register_user(users: dict[str, str], username: str, password: str) -> tuple[bool, str]:
    """Valida y agrega un usuario al diccionario sin guardar texto plano."""

    clean_username = username.strip()
    if not clean_username:
        return False, "El nombre de usuario es obligatorio."
    if clean_username in users:
        return False, "El nombre de usuario ya existe."

    validation = validate_password(clean_username, password)
    if not validation.valid:
        return False, "\n".join(validation.errors)

    users[clean_username] = hash_password(password)
    return True, "Usuario registrado correctamente."


def authenticate_user(users: dict[str, str], username: str, password: str) -> bool:
    """Comprueba que el usuario exista y que su hash coincida."""

    clean_username = username.strip()
    stored_hash = users.get(clean_username)
    return stored_hash is not None and verify_password(password, stored_hash)
