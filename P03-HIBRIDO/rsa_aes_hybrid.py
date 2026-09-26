"""Implementacion didactica de un esquema hibrido RSA-AES.

El nombre iv_cifrado_RSA se conserva por compatibilidad con el enunciado.
Internamente guarda un paquete RSA-OAEP que contiene AES_key || IV, porque
un RSA de 2048 bits no puede cifrar ambos bloques de 32 bytes por separado
con OAEP-SHA256 sin exceder su limite de tamano.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Union

from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

AES_KEY_BYTES = 32
IV_BYTES = 16  # AES siempre usa bloques de 16 bytes; CBC exige un IV de ese tamano.
OAEP_SHA256 = OAEP(mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)


@dataclass(frozen=True)
class PaqueteHibrido:
    """Datos que el emisor entrega al receptor."""

    iv_cifrado_RSA: bytes
    mensajeCifrado_AES: bytes


def generar_par_claves_rsa() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """Genera un par RSA de 2048 bits para las pruebas o el receptor."""
    privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return privada, privada.public_key()


def Cifrado_AES_enviar_mensaje(mensaje: Union[str, bytes], iv: bytes, clave_aes: bytes) -> bytes:
    """Cifra un mensaje usando AES-256-CBC y padding PKCS7.

    La clave se recibe como parametro adicional porque AES no puede cifrar
    correctamente sin ella. El IV proporcionado debe medir 16 bytes.
    """
    if len(clave_aes) != AES_KEY_BYTES:
        raise ValueError("La clave AES debe tener exactamente 32 bytes.")
    if len(iv) != IV_BYTES:
        raise ValueError("El IV de AES-CBC debe tener exactamente 16 bytes.")
    plano = mensaje.encode("utf-8") if isinstance(mensaje, str) else mensaje
    relleno = padding.PKCS7(algorithms.AES.block_size).padder()
    plano_con_relleno = relleno.update(plano) + relleno.finalize()
    cifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv)).encryptor()
    return cifrador.update(plano_con_relleno) + cifrador.finalize()


def get_Msj_And_Key(RSA_Publica: rsa.RSAPublicKey, mensaje: Union[str, bytes] = "Mensaje") -> tuple[bytes, bytes]:
    """Genera AES-256, cifra el mensaje y protege clave e IV con RSA-OAEP.

    Retorna (iv_cifrado_RSA, mensajeCifrado_AES), tal como solicita la practica.
    El primer valor contiene la concatenacion clave_AES || IV protegida por RSA.
    """
    clave_aes = os.urandom(AES_KEY_BYTES)
    iv = os.urandom(IV_BYTES)
    mensaje_cifrado = Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)
    paquete_secreto = clave_aes + iv
    iv_cifrado_rsa = RSA_Publica.encrypt(paquete_secreto, OAEP_SHA256)
    return iv_cifrado_rsa, mensaje_cifrado


def decifrar_mensaje(
    mensajeCifrado_AES: bytes, iv_cifrado_RSA: bytes, RSA_Privada: rsa.RSAPrivateKey
) -> str:
    """Recupera clave e IV con RSA-OAEP y devuelve el texto original."""
    paquete_secreto = RSA_Privada.decrypt(iv_cifrado_RSA, OAEP_SHA256)
    if len(paquete_secreto) != AES_KEY_BYTES + IV_BYTES:
        raise ValueError("Paquete RSA invalido: clave AES e IV incompletos.")
    clave_aes = paquete_secreto[:AES_KEY_BYTES]
    iv = paquete_secreto[AES_KEY_BYTES:]
    descifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv)).decryptor()
    plano_con_relleno = descifrador.update(mensajeCifrado_AES) + descifrador.finalize()
    quitador = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plano = quitador.update(plano_con_relleno) + quitador.finalize()
    return plano.decode("utf-8")


def guardar_clave_publica_pem(clave: rsa.RSAPublicKey) -> bytes:
    return clave.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)


def guardar_clave_privada_pem(clave: rsa.RSAPrivateKey) -> bytes:
    return clave.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
