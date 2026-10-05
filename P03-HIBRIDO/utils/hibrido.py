"""AES-256-CBC y RSA-OAEP/SHA-256. Implementación educativa sin autenticación."""
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def generar_claves():
    privada = RSA.generate(2048)
    return privada.public_key(), privada


def Cifrado_AES_enviar_mensaje(mensaje, iv, clave_AES):
    """La clave explícita evita depender de variables globales ocultas."""
    if len(clave_AES) != 32:
        raise ValueError("La clave AES debe tener 32 bytes.")
    if len(iv) != AES.block_size:
        raise ValueError("El IV de AES-CBC debe tener 16 bytes.")
    cifrador = AES.new(clave_AES, AES.MODE_CBC, iv=iv)
    return cifrador.encrypt(pad(mensaje.encode('utf-8'), AES.block_size))


def get_Msj_And_Key(RSA_Publica, mensaje=None):
    """Devuelve (iv_cifrado_RSA, mensajeCifrado_AES).

    El primer valor es un sobre RSA con clave AES (32 bytes) + IV (16 bytes).
    Si se omite el mensaje, se solicita por consola, como en la firma del PDF.
    """
    if mensaje is None:
        mensaje = input("Mensaje a cifrar: ")
    if RSA_Publica.size_in_bits() < 2048:
        raise ValueError("Se requiere una clave RSA de al menos 2048 bits.")
    clave = get_random_bytes(32)
    iv = get_random_bytes(AES.block_size)
    mensaje_cifrado = Cifrado_AES_enviar_mensaje(mensaje, iv, clave)
    sobre = PKCS1_OAEP.new(RSA_Publica.public_key(), hashAlgo=SHA256).encrypt(clave + iv)
    return sobre, mensaje_cifrado


def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada):
    """Recupera clave e IV del sobre y devuelve el texto UTF-8 original."""
    if not RSA_Privada.has_private():
        raise ValueError("Se requiere la clave privada RSA.")
    try:
        sobre = PKCS1_OAEP.new(RSA_Privada, hashAlgo=SHA256).decrypt(iv_cifrado_RSA)
        if len(sobre) != 48:
            raise ValueError("Sobre de longitud incorrecta.")
        clave, iv = sobre[:32], sobre[32:]
        descifrador = AES.new(clave, AES.MODE_CBC, iv=iv)
        datos = unpad(descifrador.decrypt(mensajeCifrado_AES), AES.block_size)
        return datos.decode('utf-8')
    except (ValueError, TypeError, UnicodeError) as error:
        raise ValueError("No se pudo descifrar: clave o datos incorrectos.") from error
