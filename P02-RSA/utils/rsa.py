"""Utilidades RSA didácticas y generación de claves seguras."""

from __future__ import annotations

import math

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def get_public_private_keys(p: int, q: int, pos: int) -> tuple[int, int, int]:
    """Construye un par RSA didáctico a partir de dos primos pequeños.

    Esta función solo sirve para aprender y probar la aritmética de RSA.
    """
    if p <= 1 or q <= 1 or pos <= 0:
        raise ValueError("p, q y pos deben ser enteros positivos válidos")

    phi = (p - 1) * (q - 1)
    n = p * q
    candidatos = (e for e in range(2, phi) if math.gcd(e, phi) == 1)
    try:
        e = next(e for indice, e in enumerate(candidatos, 1) if indice == pos)
    except StopIteration as exc:
        raise ValueError("pos no corresponde a un exponente público válido") from exc

    d = pow(e, -1, phi)
    return e, d, n


def encrypt(public: int, private: int, n: int, message: int) -> int:
    """Cifra un entero con RSA didáctico (``private`` se conserva por API)."""
    del private
    if not 0 <= message < n:
        raise ValueError("El mensaje debe cumplir 0 <= mensaje < n")
    return pow(message, public, n)


def descrypt(public: int, private: int, n: int, encrypted: int) -> int:
    """Descifra un entero con RSA didáctico (nombre legado del proyecto)."""
    del public
    if not 0 <= encrypted < n:
        raise ValueError("El criptograma debe cumplir 0 <= criptograma < n")
    return pow(encrypted, private, n)


decrypt = descrypt


def generar_claves_rsa(tamano: int = 2048) -> tuple[rsa.RSAPublicKey, rsa.RSAPrivateKey]:
    """Genera un par RSA seguro para el algoritmo híbrido."""
    if tamano < 2048:
        raise ValueError("La clave RSA debe tener al menos 2048 bits")
    privada = rsa.generate_private_key(public_exponent=65537, key_size=tamano)
    return privada.public_key(), privada


def serializar_claves_rsa(
    publica: rsa.RSAPublicKey, privada: rsa.RSAPrivateKey
) -> tuple[str, str]:
    """Convierte un par RSA a PEM para mostrarlo o guardarlo.

    La clave privada se devuelve sin contraseña solo para la demostración del
    ejercicio. En un sistema real debe almacenarse cifrada y nunca imprimirse.
    """
    publica_pem = publica.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    privada_pem = privada.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return publica_pem.decode("ascii"), privada_pem.decode("ascii")
