
from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import hashes, padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization


# Variables constantes globales
RSA_KEY_SIZE = 2048          
AES_KEY_SIZE_BYTES = 32      # 32 bytes = AES-256
AES_BLOCK_SIZE_BYTES = 16    # tamaño de bloque fijo de AES
IV_SIZE_BYTES = 32           # tamaño de IV mayor para hacer la practica

# Derivo el IV de 32 bytes a 16 bytes para AES-CBC
def _derivar_iv_aes(iv_extendido: bytes) -> bytes:
   
    if len(iv_extendido) != IV_SIZE_BYTES:
        raise ValueError(
            f"El IV (extendido) debe medir {IV_SIZE_BYTES} bytes, "
            f"se recibieron {len(iv_extendido)} bytes."
        )
    return iv_extendido[:AES_BLOCK_SIZE_BYTES]


@dataclass
class PaqueteCifrado:
    mensajeCifrado_AES: bytes        # texto cifrado
    iv_cifrado_RSA: bytes            # IV cifrado
    clave_aes_cifrada_RSA: bytes     # clave simétrica AES


# claves RSA
def generar_par_claves_rsa(key_size: int = RSA_KEY_SIZE):
    
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    clave_publica = clave_privada.public_key()
    return clave_privada, clave_publica


# cifrado AES-CBC
def Cifrado_AES_enviar_mensaje(mensaje: str, clave_aes: bytes, iv: bytes) -> bytes:
   
    iv_aes = _derivar_iv_aes(iv)  # revisa longitud de 32 bytes y deriva a 16
    if len(clave_aes) not in (16, 24, 32):
        raise ValueError("La clave AES debe medir 16, 24 o 32 bytes.")

    mensaje_bytes = mensaje.encode("utf-8")

    # Aplicar padding PKCS7 para que el mensaje sea múltiplo de 16 bytes
    padder = sym_padding.PKCS7(AES_BLOCK_SIZE_BYTES * 8).padder()
    datos_con_padding = padder.update(mensaje_bytes) + padder.finalize()

    # Cifrar con AES-CBC con el IV derivado (16 bytes)
    cifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv_aes))
    encryptor = cifrador.encryptor()
    mensajeCifrado_AES = encryptor.update(datos_con_padding) + encryptor.finalize()

    return mensajeCifrado_AES


# descifrado AES-CBC
def _descifrar_aes_cbc(mensajeCifrado_AES: bytes, clave_aes: bytes, iv: bytes) -> str:
   
    iv_aes = _derivar_iv_aes(iv)

    cifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv_aes))
    decryptor = cifrador.decryptor()
    datos_con_padding = decryptor.update(mensajeCifrado_AES) + decryptor.finalize()

    unpadder = sym_padding.PKCS7(AES_BLOCK_SIZE_BYTES * 8).unpadder()
    mensaje_bytes = unpadder.update(datos_con_padding) + unpadder.finalize()

    return mensaje_bytes.decode("utf-8")


# helpers para cifrado/descifrado
def _oaep_padding() -> asym_padding.OAEP:
    """
    OAEP (Optimal Asymmetric Encryption Padding) con SHA-256 es el esquema
    de padding recomendado para RSA en cifrado; PKCS1v15 "clásico" para
    cifrado está desaconsejado por vulnerabilidades tipo Bleichenbacher.
    """
    return asym_padding.OAEP(
        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )


def _rsa_cifrar(datos: bytes, rsa_publica) -> bytes:
    return rsa_publica.encrypt(datos, _oaep_padding())


def _rsa_descifrar(datos_cifrados: bytes, rsa_privada) -> bytes:
    return rsa_privada.decrypt(datos_cifrados, _oaep_padding())


# get_Msj_And_Key(RSA_Publica)
def get_Msj_And_Key(mensaje: str, rsa_publica) -> PaqueteCifrado:
    
    # Clave simétrica AES-256 aleatoria y segura
    clave_aes = os.urandom(AES_KEY_SIZE_BYTES)

    # IV aleatorio de 32 bytes, Cifrado_AES_enviar_mensaje deriva aquí internamente los 16 bytes reales que usa AES-CBC.
    iv = os.urandom(IV_SIZE_BYTES)

    # Cifrar el mensaje con AES-CBC (reutilizando la función auxiliar c)
    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, clave_aes, iv)

    # Cifrar la clave AES con la clave pública RSA del receptor
    clave_aes_cifrada_RSA = _rsa_cifrar(clave_aes, rsa_publica)

    # Cifrar el IV extendido (32 bytes) con RSA igual
    iv_cifrado_RSA = _rsa_cifrar(iv, rsa_publica)

    return PaqueteCifrado(
        mensajeCifrado_AES=mensajeCifrado_AES,
        iv_cifrado_RSA=iv_cifrado_RSA,
        clave_aes_cifrada_RSA=clave_aes_cifrada_RSA,
    )


# decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)
def decifrar_mensaje(
    mensajeCifrado_AES: bytes,
    iv_cifrado_RSA: bytes,
    clave_aes_cifrada_RSA: bytes,
    rsa_privada,
) -> str:
    
    # Descifrar el IV con RSA (se recupera el IV extendido de 32 bytes)
    iv = _rsa_descifrar(iv_cifrado_RSA, rsa_privada)

    # Descifrar la clave AES con RSA
    clave_aes = _rsa_descifrar(clave_aes_cifrada_RSA, rsa_privada)

    # _descifrar_aes_cbc deriva internamente el IV real de 16 bytes a partir del IV de 32
    mensaje_original = _descifrar_aes_cbc(mensajeCifrado_AES, clave_aes, iv)

    return mensaje_original


# para guardar/cargar claves desde disco o para las pruebas
def clave_privada_a_pem(clave_privada, password: bytes | None = None) -> bytes:
    algoritmo_cifrado = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )
    return clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=algoritmo_cifrado,
    )


def clave_publica_a_pem(clave_publica) -> bytes:
    return clave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )



# Main
if __name__ == "__main__":

    print(" Algoritmo Híbrido RSA + AES - Mauricio Sonda")

    # receptor generando su par de claves RSA
    privada_receptor, publica_receptor = generar_par_claves_rsa()

    mensaje_original = "Mensaje secreto para la práctica 3 - Mau"
    print(f"\nMensaje original:\n  {mensaje_original}")

    # emisor: cifra el mensaje con la clave pública del receptor
    paquete = get_Msj_And_Key(mensaje_original, publica_receptor)
    print(f"\nMensaje cifrado (AES, en hex):\n  {paquete.mensajeCifrado_AES.hex()}")
    print(f"\nClave AES cifrada (RSA, en hex, primeros 60 chars):"
          f"\n  {paquete.clave_aes_cifrada_RSA.hex()[:60]}...")
    print(f"\nIV cifrado (RSA, en hex, primeros 60 chars):"
          f"\n  {paquete.iv_cifrado_RSA.hex()[:60]}...")

    # receptor: descifra el paquete con su clave privada
    mensaje_recuperado = decifrar_mensaje(
        paquete.mensajeCifrado_AES,
        paquete.iv_cifrado_RSA,
        paquete.clave_aes_cifrada_RSA,
        privada_receptor,
    )
    print(f"\nMensaje descifrado:\n  {mensaje_recuperado}")

    assert mensaje_recuperado == mensaje_original
    print("\nEl mensaje descifrado es el mismo que el original")
