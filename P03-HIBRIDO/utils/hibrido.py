"""Cifrado híbrido RSA-OAEP + AES-256-CBC con autenticación HMAC."""

from __future__ import annotations

import getpass
import os
from pathlib import Path
from typing import TypeAlias

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

AES_KEY_SIZE = 32
AES_IV_SIZE = 16
HMAC_SIZE = 32
_OAEP_LABEL = b"rsa-aes-hibrido-v1"
_HKDF_INFO = b"rsa-aes-hibrido-hmac-v1"

PublicKeyInput: TypeAlias = rsa.RSAPublicKey | bytes | str | Path
PrivateKeyInput: TypeAlias = rsa.RSAPrivateKey | bytes | str | Path


def _leer_datos(valor: bytes | str | Path) -> bytes:
    if isinstance(valor, bytes):
        return valor
    if isinstance(valor, str) and "-----BEGIN" in valor:
        return valor.encode("utf-8")
    ruta = Path(valor)
    if ruta.exists():
        return ruta.read_bytes()
    raise ValueError("No se encontró el archivo que contiene la clave PEM")


def _clave_publica(valor: PublicKeyInput) -> rsa.RSAPublicKey:
    if isinstance(valor, rsa.RSAPublicKey):
        return valor
    clave = serialization.load_pem_public_key(_leer_datos(valor))
    if not isinstance(clave, rsa.RSAPublicKey):
        raise TypeError("Se esperaba una clave pública RSA")
    return clave


def _clave_privada(valor: PrivateKeyInput) -> rsa.RSAPrivateKey:
    if isinstance(valor, rsa.RSAPrivateKey):
        return valor
    clave = serialization.load_pem_private_key(_leer_datos(valor), password=None)
    if not isinstance(clave, rsa.RSAPrivateKey):
        raise TypeError("Se esperaba una clave privada RSA")
    return clave


def _oaep() -> asymmetric_padding.OAEP:
    return asymmetric_padding.OAEP(
        mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=_OAEP_LABEL,
    )


def _clave_hmac(clave_aes: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(), length=HMAC_SIZE, salt=None, info=_HKDF_INFO
    ).derive(clave_aes)


def Cifrado_AES_enviar_mensaje(
    mensaje: str | bytes, iv: bytes, clave_aes: bytes
) -> bytes:
    """Cifra con AES-256-CBC y devuelve ``ciphertext || HMAC``.

    La clave es necesaria: un IV es público y no puede sustituir a una clave.
    """
    if not isinstance(mensaje, (str, bytes)):
        raise TypeError("mensaje debe ser str o bytes")
    if not isinstance(iv, bytes) or len(iv) != AES_IV_SIZE:
        raise ValueError("El IV de AES-CBC debe medir exactamente 16 bytes")
    if not isinstance(clave_aes, bytes) or len(clave_aes) != AES_KEY_SIZE:
        raise ValueError("La clave AES-256 debe medir exactamente 32 bytes")

    plano = mensaje.encode("utf-8") if isinstance(mensaje, str) else mensaje
    rellenador = padding.PKCS7(algorithms.AES.block_size).padder()
    plano_rellenado = rellenador.update(plano) + rellenador.finalize()
    cifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv)).encryptor()
    cifrado = cifrador.update(plano_rellenado) + cifrador.finalize()

    autenticador = hmac.HMAC(_clave_hmac(clave_aes), hashes.SHA256())
    autenticador.update(iv + cifrado)
    return cifrado + autenticador.finalize()


def get_Msj_And_Key(
    RSA_Publica: PublicKeyInput, mensaje: str | bytes | None = None
) -> tuple[bytes, bytes]:
    """Cifra un mensaje y crea el sobre RSA con ``clave AES || IV``.

    Si no se proporciona ``mensaje``, se solicita por consola.
    """
    publica = _clave_publica(RSA_Publica)
    if publica.key_size < 2048:
        raise ValueError("La clave pública RSA debe tener al menos 2048 bits")
    if mensaje is None:
        mensaje = getpass.getpass("Mensaje a cifrar: ")

    clave_aes = os.urandom(AES_KEY_SIZE)
    iv = os.urandom(AES_IV_SIZE)
    mensaje_cifrado = Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)
    secretos_cifrados = publica.encrypt(clave_aes + iv, _oaep())
    return secretos_cifrados, mensaje_cifrado


def decifrar_mensaje(
    mensajeCifrado_AES: bytes,
    iv_cifrado_RSA: bytes,
    RSA_Privada: PrivateKeyInput,
) -> str:
    """Abre el sobre RSA, autentica y descifra el mensaje."""
    privada = _clave_privada(RSA_Privada)
    secretos = privada.decrypt(iv_cifrado_RSA, _oaep())
    if len(secretos) != AES_KEY_SIZE + AES_IV_SIZE:
        raise ValueError("El sobre RSA no contiene una clave y un IV válidos")
    if len(mensajeCifrado_AES) < HMAC_SIZE + algorithms.AES.block_size // 8:
        raise ValueError("El mensaje cifrado está incompleto")

    clave_aes, iv = secretos[:AES_KEY_SIZE], secretos[AES_KEY_SIZE:]
    cifrado = mensajeCifrado_AES[:-HMAC_SIZE]
    etiqueta = mensajeCifrado_AES[-HMAC_SIZE:]
    autenticador = hmac.HMAC(_clave_hmac(clave_aes), hashes.SHA256())
    autenticador.update(iv + cifrado)
    try:
        autenticador.verify(etiqueta)
    except InvalidSignature as exc:
        raise ValueError("El mensaje fue alterado o la clave no es correcta") from exc

    descifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv)).decryptor()
    rellenado = descifrador.update(cifrado) + descifrador.finalize()
    quitarelleno = padding.PKCS7(algorithms.AES.block_size).unpadder()
    try:
        plano = quitarelleno.update(rellenado) + quitarelleno.finalize()
        return plano.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("El contenido descifrado no es texto UTF-8 válido") from exc
