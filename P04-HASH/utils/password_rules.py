"""Reglas de contrasena de la practica."""
import re

def _has_sequence(password: str) -> bool:
    value = password.casefold()
    for i in range(len(value) - 2):
        piece = value[i:i + 3]
        if piece.isalpha() or piece.isdigit():
            nums = [ord(c) for c in piece]
            if nums[1] - nums[0] == nums[2] - nums[1] and abs(nums[1] - nums[0]) == 1: return True
    return False

def validate_password(username: str, password: str) -> list[str]:
    errors = []
    if len(password) < 8: errors.append("Debe tener al menos 8 caracteres.")
    if not re.search(r"[A-Z]", password): errors.append("Debe incluir una mayuscula.")
    if not re.search(r"[a-z]", password): errors.append("Debe incluir una minuscula.")
    if not re.search(r"\d", password): errors.append("Debe incluir un numero.")
    if not re.search(r"[^A-Za-z0-9]", password): errors.append("Debe incluir un caracter especial.")
    if username and username.casefold() in password.casefold(): errors.append("No debe incluir el nombre de usuario.")
    if _has_sequence(password): errors.append("No debe contener secuencias alfabeticas o numericas de tres caracteres.")
    return errors
