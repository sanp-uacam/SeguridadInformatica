"""
utils/password_policy.py
Hash SHA-256 y validación de los requisitos de contraseña
"""

import hashlib
import re


def hash_password(password: str) -> str:
    """Hashea la contraseña usando SHA-256"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


CARACTERES_ESPECIALES = r"!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`"


def _tiene_secuencia_numerica(password: str, longitud: int = 3) -> bool:
    """Detecta secuencias numéricas tipo 123 o 321"""
    texto = password
    for i in range(len(texto) - longitud + 1):
        fragmento = texto[i:i + longitud]
        if not fragmento.isdigit():
            continue
        valores = [int(d) for d in fragmento]
        ascendente = all(valores[j] + 1 == valores[j + 1] for j in range(len(valores) - 1))
        descendente = all(valores[j] - 1 == valores[j + 1] for j in range(len(valores) - 1))
        if ascendente or descendente:
            return True
    return False

def _incluye_usuario(password: str, username: str) -> bool:
    """
    Compara solo las letras del username contra solo las
    letras del password.
    """
    solo_letras = lambda t: re.sub(r"[^a-zA-Z]", "", t).lower()
    letras_usuario = solo_letras(username)
    letras_password = solo_letras(password)
    return bool(letras_usuario) and letras_usuario in letras_password

def validar_password(password: str, username: str) -> list:
    """Valida los requisitos de contraseña. Devuelve lista de errores."""
    errores = []

    if len(password) < 8:
        errores.append("Debe tener al menos 8 caracteres.")

    if not (re.search(r"[A-Z]", password) and re.search(r"[a-z]", password)):
        errores.append("Debe incluir mayúsculas y minúsculas.")

    if _tiene_secuencia_numerica(password):
        errores.append("No debe contener una secuencia numérica (ej. 123, 456).")

    if not re.search(f"[{CARACTERES_ESPECIALES}]", password):
        errores.append("Debe incluir al menos un carácter especial (ej. !@#$%).")

    if _incluye_usuario(password, username):
        errores.append("La contraseña no debe incluir el nombre de usuario.")

    return errores
