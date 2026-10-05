"""Práctica 3: AES-256-CBC + RSA-OAEP + HMAC-SHA256.

Las tres funciones solicitadas son métodos de AlgoritmoHibrido.
El objeto conserva las claves necesarias para la función auxiliar de dos
argumentos. Cada envío híbrido utiliza un contexto nuevo e independiente.
"""
import argparse
import base64
import hashlib
import secrets

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

VERSION = b"P2H1"


def _oaep():
    return rsa_padding.OAEP(mgf=rsa_padding.MGF1(hashes.SHA256()),
                            algorithm=hashes.SHA256(), label=VERSION)


def _iv_cbc(material_iv):
    if not isinstance(material_iv, bytes) or len(material_iv) != 32:
        raise ValueError("El material IV debe ser bytes de longitud 32.")
    # AES tiene bloques de 16 bytes, aunque su clave mida 32 bytes.
    return hashlib.sha256(material_iv).digest()[:16]


class AlgoritmoHibrido:
    """Contexto local; no comparte claves globales entre emisores."""

    def __init__(self):
        self._clave_aes = secrets.token_bytes(32)
        self._clave_mac = secrets.token_bytes(32)
        self._ivs_usados = set()

    def Cifrado_AES_enviar_mensaje(self, mensaje, iv):
        """Devuelve ciphertext || HMAC (32 bytes); iv es material de 32 bytes.

        Usa las claves del objeto. Para transportarlas al receptor debe
        utilizarse get_Msj_And_Key. No reutilizar un IV en este contexto.
        """
        if not isinstance(mensaje, str):
            raise TypeError("El mensaje debe ser texto (str).")
        iv_real = _iv_cbc(iv)
        if iv_real in self._ivs_usados:
            raise ValueError("No se permite reutilizar el IV con la misma clave.")
        self._ivs_usados.add(iv_real)
        rellenador = padding.PKCS7(128).padder()
        datos = rellenador.update(mensaje.encode("utf-8")) + rellenador.finalize()
        cifrador = Cipher(algorithms.AES(self._clave_aes), modes.CBC(iv_real)).encryptor()
        cifrado = cifrador.update(datos) + cifrador.finalize()
        autenticador = hmac.HMAC(self._clave_mac, hashes.SHA256())
        autenticador.update(VERSION + iv + cifrado)
        return cifrado + autenticador.finalize()

    def get_Msj_And_Key(self, RSA_Publica, mensaje=None):
        """Devuelve (sobre_RSA, ciphertext_AES_con_HMAC).

        Sin mensaje opcional, lo solicita por teclado como en el enunciado.
        El sobre RSA incluye versión, clave AES, material IV y clave HMAC.
        """
        if not isinstance(RSA_Publica, rsa.RSAPublicKey) or RSA_Publica.key_size < 2048:
            raise ValueError("Se requiere una clave pública RSA de al menos 2048 bits.")
        if mensaje is None:
            mensaje = input("Mensaje: ")
        sesion = AlgoritmoHibrido()
        iv = secrets.token_bytes(32)
        mensajeCifrado_AES = sesion.Cifrado_AES_enviar_mensaje(mensaje, iv)
        paquete = VERSION + sesion._clave_aes + iv + sesion._clave_mac
        iv_cifrado_RSA = RSA_Publica.encrypt(paquete, _oaep())
        return iv_cifrado_RSA, mensajeCifrado_AES

    @staticmethod
    def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada):
        """Verifica integridad antes de descifrar. Error externo uniforme."""
        try:
            if not isinstance(RSA_Privada, rsa.RSAPrivateKey) or RSA_Privada.key_size < 2048:
                raise ValueError()
            if not isinstance(mensajeCifrado_AES, bytes) or not isinstance(iv_cifrado_RSA, bytes):
                raise ValueError()
            if len(iv_cifrado_RSA) != (RSA_Privada.key_size + 7) // 8:
                raise ValueError()
            if len(mensajeCifrado_AES) < 48 or (len(mensajeCifrado_AES) - 32) % 16:
                raise ValueError()
            paquete = RSA_Privada.decrypt(iv_cifrado_RSA, _oaep())
            if len(paquete) != 100 or paquete[:4] != VERSION:
                raise ValueError()
            clave_aes, iv, clave_mac = paquete[4:36], paquete[36:68], paquete[68:100]
            cifrado, etiqueta = mensajeCifrado_AES[:-32], mensajeCifrado_AES[-32:]
            autenticador = hmac.HMAC(clave_mac, hashes.SHA256())
            autenticador.update(VERSION + iv + cifrado)
            autenticador.verify(etiqueta)
            descifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(_iv_cbc(iv))).decryptor()
            datos = descifrador.update(cifrado) + descifrador.finalize()
            quitar_relleno = padding.PKCS7(128).unpadder()
            plano = quitar_relleno.update(datos) + quitar_relleno.finalize()
            return plano.decode("utf-8")
        except (ValueError, TypeError, InvalidSignature):
            raise ValueError("No se pudo autenticar o descifrar el mensaje.") from None


# Alias de métodos ligados: permiten las llamadas exactas del enunciado.
_contexto = AlgoritmoHibrido()
get_Msj_And_Key = _contexto.get_Msj_And_Key
decifrar_mensaje = AlgoritmoHibrido.decifrar_mensaje
Cifrado_AES_enviar_mensaje = _contexto.Cifrado_AES_enviar_mensaje


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mensaje", help="Texto a cifrar; se pide por teclado si se omite.")
    args = parser.parse_args()
    RSA_Privada = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    RSA_Publica = RSA_Privada.public_key()
    iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(RSA_Publica, args.mensaje)
    print("RSA: 3072 bits | AES: 256 bits CBC | HMAC: SHA-256")
    print("Sobre RSA (Base64):", base64.b64encode(iv_cifrado_RSA).decode())
    print("AES + HMAC (Base64):", base64.b64encode(mensajeCifrado_AES).decode())
    print("Mensaje recuperado:", decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada))


if __name__ == "__main__":
    main()
