"""Reglas de la práctica y cálculo de SHA-256. No necesita paquetes externos."""

import hashlib
import re


def generar_hash(contrasena):
    """UTF-8 convierte el texto a bytes; hexdigest devuelve 64 caracteres hex."""
    return hashlib.sha256(contrasena.encode("utf-8")).hexdigest()


def contiene_secuencia(texto):
    """Rechaza 3 caracteres consecutivos: abc, cba, 123, 321, etc."""
    texto = texto.casefold()
    for serie in ("abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnñopqrstuvwxyz", "0123456789"):
        for i in range(len(serie) - 2):
            tramo = serie[i:i + 3]
            if tramo in texto or tramo[::-1] in texto:
                return True
    return False


def reglas_contrasena(usuario, contrasena):
    """Lista de (descripción, cumple) compartida por la interfaz y el registro."""
    nombre = usuario.strip().casefold()
    return [
        ("Mínimo 8 caracteres", len(contrasena) >= 8),
        ("Al menos una mayúscula y una minúscula",
         any(c.isupper() for c in contrasena) and any(c.islower() for c in contrasena)),
        ("Al menos un carácter especial",
         any(not c.isalnum() and not c.isspace() for c in contrasena)),
        ("Sin secuencias de 3 letras o números", not contiene_secuencia(contrasena)),
        ("No incluye el nombre de usuario", bool(nombre) and nombre not in contrasena.casefold()),
        ("Sin espacios", bool(contrasena) and not any(c.isspace() for c in contrasena)),
    ]


def validar_usuario(usuario):
    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", usuario):
        raise ValueError("El usuario debe tener de 3 a 20 letras sin acentos, números o guion bajo.")
