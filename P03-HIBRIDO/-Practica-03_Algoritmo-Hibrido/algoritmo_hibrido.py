from base64 import b64encode, b64decode
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption,
)

AES_KEY_SIZE = 32      
AES_BLOCK_SIZE = 16    


def generar_claves_rsa():
    """Genera un par RSA de 2048 bits para el receptor."""
    privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    publica = privada.public_key()
    return publica, privada


def _rsa_cifrar(datos, clave_publica):
    return clave_publica.encrypt(
        datos,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def _rsa_descifrar(datos, clave_privada):
    return clave_privada.decrypt(
        datos,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes):
    """
    Cifra el mensaje con AES-256-CBC usando el IV proporcionado.
    Se usa PKCS7 para completar el último bloque.
    """
    if len(iv) != AES_BLOCK_SIZE:
        raise ValueError("El IV de AES-CBC debe tener exactamente 16 bytes.")
    if len(clave_aes) != AES_KEY_SIZE:
        raise ValueError("La clave debe tener exactamente 32 bytes para AES-256.")

    if isinstance(mensaje, str):
        mensaje = mensaje.encode("utf-8")

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(mensaje) + padder.finalize()

    cipher = Cipher(algorithms.AES(clave_aes), modes.CBC(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(padded) + encryptor.finalize()


def get_Msj_And_Key(RSA_Publica, mensaje):
    """
    1) Genera clave AES aleatoria de 32 bytes.
    2) Genera IV aleatorio de 16 bytes (AES-CBC).
    3) Cifra el mensaje con AES-256-CBC.
    4) Cifra clave AES e IV con RSA-OAEP.
    5) Devuelve los datos necesarios para el receptor.
    """
    clave_aes = os.urandom(AES_KEY_SIZE)
    iv = os.urandom(AES_BLOCK_SIZE)

    mensaje_cifrado_aes = Cifrado_AES_enviar_mensaje(
        mensaje, iv, clave_aes
    )

    clave_aes_cifrada_rsa = _rsa_cifrar(clave_aes, RSA_Publica)
    iv_cifrado_rsa = _rsa_cifrar(iv, RSA_Publica)

    return {
        "iv_cifrado_RSA": b64encode(iv_cifrado_rsa).decode("ascii"),
        "clave_AES_cifrada_RSA": b64encode(clave_aes_cifrada_rsa).decode("ascii"),
        "mensajeCifrado_AES": b64encode(mensaje_cifrado_aes).decode("ascii"),
    }


def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA,
                     clave_AES_cifrada_RSA, RSA_Privada):
    """
    1) Descifra el IV con RSA.
    2) Descifra la clave AES con RSA.
    3) Descifra el mensaje con AES-256-CBC.
    4) Quita el padding PKCS7.
    """
    iv_cifrado = b64decode(iv_cifrado_RSA)
    clave_aes_cifrada = b64decode(clave_AES_cifrada_RSA)
    mensaje_cifrado = b64decode(mensajeCifrado_AES)

    iv = _rsa_descifrar(iv_cifrado, RSA_Privada)
    clave_aes = _rsa_descifrar(clave_aes_cifrada, RSA_Privada)

    if len(iv) != AES_BLOCK_SIZE:
        raise ValueError("El IV recuperado no tiene 16 bytes.")
    if len(clave_aes) != AES_KEY_SIZE:
        raise ValueError("La clave AES recuperada no tiene 32 bytes.")

    cipher = Cipher(algorithms.AES(clave_aes), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(mensaje_cifrado) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    mensaje = unpadder.update(padded) + unpadder.finalize()

    return mensaje.decode("utf-8")


def guardar_claves(publica, privada):
    Path("clave_publica.pem").write_bytes(
        publica.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    )
    Path("clave_privada.pem").write_bytes(
        privada.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    )


def demo():
    print("=" * 60)
    print("ALGORITMO HIBRIDO RSA + AES")
    print("=" * 60)

    publica, privada = generar_claves_rsa()
    guardar_claves(publica, privada)

    mensaje = "Mensaje secreto de la práctica RSA + AES."

    print("\n[1] Mensaje original:")
    print(mensaje)

    paquete = get_Msj_And_Key(publica, mensaje)

    print("\n[2] Datos generados:")
    print(f"  IV cifrado con RSA:       {len(b64decode(paquete['iv_cifrado_RSA']))} bytes")
    print(f"  Clave AES cifrada RSA:    {len(b64decode(paquete['clave_AES_cifrada_RSA']))} bytes")
    print(f"  Mensaje cifrado AES:      {len(b64decode(paquete['mensajeCifrado_AES']))} bytes")

    mensaje_original = decifrar_mensaje(
        paquete["mensajeCifrado_AES"],
        paquete["iv_cifrado_RSA"],
        paquete["clave_AES_cifrada_RSA"],
        privada,
    )

    print("\n[3] Mensaje descifrado:")
    print(mensaje_original)

    assert mensaje_original == mensaje
    print("\n[OK] PRUEBA SUPERADA: el mensaje recuperado coincide con el original.")


if __name__ == "__main__":
    demo()
