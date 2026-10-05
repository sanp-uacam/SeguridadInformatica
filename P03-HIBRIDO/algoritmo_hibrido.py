"""Práctica RSA + AES-CBC. Python 3.10+ y cryptography.

El IV real de AES-CBC mide 16 bytes, no 32. El sobre RSA incluye
clave AES, IV y clave HMAC. No se utiliza estado global de sesión.
"""
import argparse
import base64
import secrets

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

VERSION = b"HRA1"
ERROR = "No se pudo descifrar: paquete inválido o clave incorrecta."


class ErrorDescifrado(ValueError):
    """Error público uniforme; no revela el motivo criptográfico concreto."""


def generar_claves_RSA():
    """Devuelve (clave pública, clave privada) RSA de 2048 bits."""
    privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return privada.public_key(), privada


def _oaep():
    return rsa_padding.OAEP(
        mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(), label=VERSION,
    )


def Cifrado_AES_enviar_mensaje(mensaje, iv, clave_AES=None):
    """Devuelve (clave_AES, ciphertext) en bytes, con padding PKCS7.

    Admite la llamada de dos argumentos de la guía: si no se proporciona
    clave, genera una de 32 bytes y la devuelve para no perderla. La clave
    retornada es local: NUNCA se transmite sin protección RSA.
    Esta función auxiliar no autentica el ciphertext; use get_Msj_And_Key
    para construir el paquete híbrido completo. Use un IV nuevo por cifrado.
    """
    if not isinstance(mensaje, str):
        raise TypeError("El mensaje debe ser texto (str).")
    if not isinstance(iv, bytes) or len(iv) != 16:
        raise ValueError("AES-CBC requiere un IV de exactamente 16 bytes.")
    if clave_AES is None:
        clave_AES = secrets.token_bytes(32)
    if not isinstance(clave_AES, bytes) or len(clave_AES) != 32:
        raise ValueError("AES-256 requiere una clave de exactamente 32 bytes.")
    padder = padding.PKCS7(128).padder()
    datos = padder.update(mensaje.encode("utf-8")) + padder.finalize()
    cifrador = Cipher(algorithms.AES(clave_AES), modes.CBC(iv)).encryptor()
    return clave_AES, cifrador.update(datos) + cifrador.finalize()


def get_Msj_And_Key(RSA_Publica, mensaje=None):
    """Devuelve (iv_cifrado_RSA, mensajeCifrado_AES), ambos bytes.

    Con un solo argumento solicita el mensaje por teclado. El argumento
    opcional mensaje permite pruebas y ejecución sin interacción.
    iv_cifrado_RSA = RSA-OAEP(clave_AES[32] || IV[16] || clave_HMAC[32]).
    mensajeCifrado_AES = HRA1[4] || ciphertext[N*16] || HMAC-SHA256[32].
    El HMAC cubre VERSION || sobre_RSA || ciphertext (encrypt-then-MAC).
    """
    if not isinstance(RSA_Publica, rsa.RSAPublicKey):
        raise TypeError("Se requiere un objeto de clave pública RSA.")
    if RSA_Publica.key_size < 2048:
        raise ValueError("RSA debe tener al menos 2048 bits.")
    if mensaje is None:
        mensaje = input("Escribe el mensaje: ")
    clave_AES = secrets.token_bytes(32)
    iv = secrets.token_bytes(16)
    clave_hmac = secrets.token_bytes(32)
    _, ciphertext = Cifrado_AES_enviar_mensaje(mensaje, iv, clave_AES)
    sobre = RSA_Publica.encrypt(clave_AES + iv + clave_hmac, _oaep())
    autenticador = hmac.HMAC(clave_hmac, hashes.SHA256())
    autenticador.update(VERSION + sobre + ciphertext)
    paquete = VERSION + ciphertext + autenticador.finalize()
    return sobre, paquete


def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada):
    """Verifica integridad ANTES de descifrar AES y devuelve texto UTF-8."""
    try:
        if not isinstance(RSA_Privada, rsa.RSAPrivateKey):
            raise ValueError()
        if RSA_Privada.key_size < 2048:
            raise ValueError()
        if not isinstance(mensajeCifrado_AES, bytes):
            raise ValueError()
        if not isinstance(iv_cifrado_RSA, bytes):
            raise ValueError()
        if len(iv_cifrado_RSA) != (RSA_Privada.key_size + 7) // 8:
            raise ValueError()
        paquete = mensajeCifrado_AES
        if len(paquete) < 52 or paquete[:4] != VERSION:
            raise ValueError()
        ciphertext, etiqueta = paquete[4:-32], paquete[-32:]
        if len(ciphertext) % 16 != 0:
            raise ValueError()
        material = RSA_Privada.decrypt(iv_cifrado_RSA, _oaep())
        if len(material) != 80:
            raise ValueError()
        clave_AES, iv, clave_hmac = material[:32], material[32:48], material[48:]
        autenticador = hmac.HMAC(clave_hmac, hashes.SHA256())
        autenticador.update(VERSION + iv_cifrado_RSA + ciphertext)
        autenticador.verify(etiqueta)
        descifrador = Cipher(algorithms.AES(clave_AES), modes.CBC(iv)).decryptor()
        datos = descifrador.update(ciphertext) + descifrador.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plano = unpadder.update(datos) + unpadder.finalize()
        return plano.decode("utf-8")
    except (ValueError, TypeError, InvalidSignature):
        raise ErrorDescifrado(ERROR) from None


def main():
    parser = argparse.ArgumentParser(description="Demostración híbrida RSA/AES-CBC")
    parser.add_argument("--mensaje", help="Texto a cifrar; si se omite se solicita")
    args = parser.parse_args()
    RSA_Publica, RSA_Privada = generar_claves_RSA()
    iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(RSA_Publica, args.mensaje)
    print("Sobre RSA (Base64):", base64.b64encode(iv_cifrado_RSA).decode("ascii"))
    print("Paquete AES (Base64):", base64.b64encode(mensajeCifrado_AES).decode("ascii"))
    original = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)
    print("Mensaje recuperado:", original)
    print("Verificación: descifrado e integridad correctos.")


if __name__ == "__main__":
    main()
