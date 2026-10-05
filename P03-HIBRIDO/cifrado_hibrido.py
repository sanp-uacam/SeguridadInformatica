"""Implementacion de cifrado hibrido RSA-OAEP + AES-256-CBC.

La API conserva los nombres solicitados en la practica. ``iv_cifrado_RSA`` es
un sobre binario que contiene, por separado, la clave AES y el IV cifrados con
RSA. El mensaje AES incluye una etiqueta HMAC para detectar modificaciones.
"""

from __future__ import annotations

import hmac as stdlib_hmac
import os
import struct
from dataclasses import dataclass
from typing import Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


MAGIC = b"RAH1"
AES_KEY_SIZE = 32
AES_BLOCK_SIZE = 16
HMAC_SIZE = 32

PublicKey = Union[rsa.RSAPublicKey, bytes, str]
PrivateKey = Union[rsa.RSAPrivateKey, bytes, str]


class ErrorCifrado(ValueError):
    """Indica que el sobre es invalido, fue alterado o no puede descifrarse."""


@dataclass(frozen=True)
class ParClavesRSA:
    publica_pem: bytes
    privada_pem: bytes


def generar_claves_rsa(tamano: int = 3072) -> ParClavesRSA:
    """Genera un par RSA y lo devuelve en formato PEM."""
    if tamano < 2048:
        raise ValueError("La clave RSA debe tener al menos 2048 bits")
    privada = rsa.generate_private_key(public_exponent=65537, key_size=tamano)
    privada_pem = privada.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    publica_pem = privada.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return ParClavesRSA(publica_pem=publica_pem, privada_pem=privada_pem)


def _cargar_publica(clave: PublicKey) -> rsa.RSAPublicKey:
    if isinstance(clave, rsa.RSAPublicKey):
        return clave
    datos = clave.encode("utf-8") if isinstance(clave, str) else clave
    resultado = serialization.load_pem_public_key(datos)
    if not isinstance(resultado, rsa.RSAPublicKey):
        raise TypeError("Se esperaba una clave publica RSA")
    return resultado


def _cargar_privada(clave: PrivateKey) -> rsa.RSAPrivateKey:
    if isinstance(clave, rsa.RSAPrivateKey):
        return clave
    datos = clave.encode("utf-8") if isinstance(clave, str) else clave
    resultado = serialization.load_pem_private_key(datos, password=None)
    if not isinstance(resultado, rsa.RSAPrivateKey):
        raise TypeError("Se esperaba una clave privada RSA")
    return resultado


def _oaep() -> asym_padding.OAEP:
    return asym_padding.OAEP(
        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )


def _clave_hmac(clave_aes: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"practica03-rsa-aes-cbc-hmac",
    ).derive(clave_aes)


def Cifrado_AES_enviar_mensaje(
    Mensaje: Union[str, bytes], iv: bytes, clave_AES: bytes
) -> bytes:
    """Cifra con AES-256-CBC y devuelve ``HMAC || texto_cifrado``.

    La clave es un parametro necesario aunque la firma abreviada de la consigna
    no la muestre. El IV de AES-CBC debe medir exactamente 16 bytes.
    """
    if len(clave_AES) != AES_KEY_SIZE:
        raise ValueError("La clave AES debe medir 32 bytes")
    if len(iv) != AES_BLOCK_SIZE:
        raise ValueError("El IV de AES-CBC debe medir 16 bytes")

    datos = Mensaje.encode("utf-8") if isinstance(Mensaje, str) else Mensaje
    rellenador = padding.PKCS7(algorithms.AES.block_size).padder()
    datos_rellenados = rellenador.update(datos) + rellenador.finalize()
    cifrador = Cipher(algorithms.AES(clave_AES), modes.CBC(iv)).encryptor()
    texto_cifrado = cifrador.update(datos_rellenados) + cifrador.finalize()

    autenticador = hmac.HMAC(_clave_hmac(clave_AES), hashes.SHA256())
    autenticador.update(iv + texto_cifrado)
    return autenticador.finalize() + texto_cifrado


def _empaquetar(clave_cifrada: bytes, iv_cifrado: bytes) -> bytes:
    return (
        MAGIC
        + struct.pack(">II", len(clave_cifrada), len(iv_cifrado))
        + clave_cifrada
        + iv_cifrado
    )


def _desempaquetar(sobre: bytes) -> tuple[bytes, bytes]:
    if len(sobre) < 12 or not stdlib_hmac.compare_digest(sobre[:4], MAGIC):
        raise ErrorCifrado("Formato de sobre no reconocido")
    largo_clave, largo_iv = struct.unpack(">II", sobre[4:12])
    if largo_clave == 0 or largo_iv == 0 or len(sobre) != 12 + largo_clave + largo_iv:
        raise ErrorCifrado("Longitudes invalidas en el sobre")
    inicio_iv = 12 + largo_clave
    return sobre[12:inicio_iv], sobre[inicio_iv:]


def get_Msj_And_Key(
    RSA_Publica: PublicKey, Mensaje: Union[str, bytes]
) -> tuple[bytes, bytes]:
    """Genera material aleatorio y cifra el mensaje para el receptor.

    Retorna ``(iv_cifrado_RSA, mensajeCifrado_AES)``. El primer elemento
    contiene tanto la clave AES cifrada como el IV cifrado.
    """
    publica = _cargar_publica(RSA_Publica)
    clave_aes = os.urandom(AES_KEY_SIZE)
    iv = os.urandom(AES_BLOCK_SIZE)
    mensaje_cifrado = Cifrado_AES_enviar_mensaje(Mensaje, iv, clave_aes)
    clave_cifrada = publica.encrypt(clave_aes, _oaep())
    iv_cifrado = publica.encrypt(iv, _oaep())
    return _empaquetar(clave_cifrada, iv_cifrado), mensaje_cifrado


def decifrar_mensaje(
    mensajeCifrado_AES: bytes,
    iv_cifrado_RSA: bytes,
    RSA_Privada: PrivateKey,
) -> str:
    """Abre el sobre RSA, autentica y descifra el mensaje AES."""
    privada = _cargar_privada(RSA_Privada)
    clave_cifrada, iv_cifrado = _desempaquetar(iv_cifrado_RSA)
    try:
        clave_aes = privada.decrypt(clave_cifrada, _oaep())
        iv = privada.decrypt(iv_cifrado, _oaep())
    except ValueError as exc:
        raise ErrorCifrado("No fue posible abrir el sobre RSA") from exc

    if len(clave_aes) != AES_KEY_SIZE or len(iv) != AES_BLOCK_SIZE:
        raise ErrorCifrado("Material criptografico con longitud invalida")
    if len(mensajeCifrado_AES) <= HMAC_SIZE:
        raise ErrorCifrado("Mensaje cifrado incompleto")

    etiqueta = mensajeCifrado_AES[:HMAC_SIZE]
    texto_cifrado = mensajeCifrado_AES[HMAC_SIZE:]
    autenticador = hmac.HMAC(_clave_hmac(clave_aes), hashes.SHA256())
    autenticador.update(iv + texto_cifrado)
    try:
        autenticador.verify(etiqueta)
    except InvalidSignature as exc:
        raise ErrorCifrado("La autenticidad del mensaje no es valida") from exc

    descifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv)).decryptor()
    datos_rellenados = descifrador.update(texto_cifrado) + descifrador.finalize()
    quitarelleno = padding.PKCS7(algorithms.AES.block_size).unpadder()
    try:
        datos = quitarelleno.update(datos_rellenados) + quitarelleno.finalize()
        return datos.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise ErrorCifrado("El contenido descifrado no es valido") from exc

