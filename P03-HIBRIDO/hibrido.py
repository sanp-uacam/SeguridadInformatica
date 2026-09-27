# Algoritmo Hibrido AES + RSA
# Seguridad Informatica - Imparte: Sergio Noh Puch
# Alumno: Angel Antonio Perez Reyes

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

import rsa_simple

TAM_LLAVE_AES = 32   # 32 bytes = 256 bits -> AES-256
TAM_IV = AES.block_size   # 16 bytes. El IV SIEMPRE mide lo mismo que el bloque.


def Cifrado_AES_enviar_mensaje(mensaje, iv, key=None):
    """Funcion auxiliar: cifra un mensaje con AES-CBC usando el IV dado.

    Si no se pasa una llave, genera una aleatoria de 32 bytes.
    Devuelve (llave_usada, mensaje_cifrado_en_base64).
    """
    if key is None:
        key = get_random_bytes(TAM_LLAVE_AES)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    cifrado = cipher.encrypt(pad(mensaje.encode('utf-8'), AES.block_size))

    return key, base64.b64encode(cifrado).decode('utf-8')


def get_Msj_And_Key(RSA_Publica, mensaje="Mensaje"):
    """Emisor: cifra el mensaje con AES y protege la llave AES con RSA.

    1. Genera IV aleatorio
    2. Genera llave AES aleatoria y cifra el mensaje (AES-CBC)
    3. Cifra llave AES e IV con la clave publica RSA del receptor

    Devuelve (iv_cifrado_RSA, mensajeCifrado_AES).

    iv_cifrado_RSA es un diccionario que empaqueta el IV y la llave AES,
    ambos cifrados con RSA. El enunciado permite esto explicitamente:
    "o empaquetarlo junto con la clave cifrada".
    """
    iv = get_random_bytes(TAM_IV)
    key, mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, iv)

    iv_cifrado_RSA = {
        "iv":  rsa_simple.cifrar_bytes(iv,  RSA_Publica),
        "key": rsa_simple.cifrar_bytes(key, RSA_Publica),
    }

    return iv_cifrado_RSA, mensajeCifrado_AES


def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada):
    """Receptor: recupera llave AES e IV con RSA, y descifra el mensaje.

    Devuelve el texto plano original.
    """
    iv = rsa_simple.descifrar_bytes(iv_cifrado_RSA["iv"],  RSA_Privada)
    key = rsa_simple.descifrar_bytes(iv_cifrado_RSA["key"], RSA_Privada)

    cifrado = base64.b64decode(mensajeCifrado_AES)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    return unpad(cipher.decrypt(cifrado), AES.block_size).decode('utf-8')
