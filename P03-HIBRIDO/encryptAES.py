from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

def encode(key, text):
    cipher = AES.new(key, AES.MODE_CBC)
    tex_bytes = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
    # iv y texto cifrado codificados en base64 para facilitar almacenamiento y transporte
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    text_encript = base64.b64encode(tex_bytes).decode('utf-8')
    return iv, text_encript

def decode(key, iv_b64, text_encript_b64):
    iv = base64.b64decode(iv_b64)
    ciphertext = base64.b64decode(text_encript_b64)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_bytes.decode('utf-8')

def Cifrado_AES_enviar_mensaje(mensaje, iv, key):
    """
    Función auxiliar (inciso c de la práctica):
    Cifra un mensaje con AES en modo CBC usando el IV y la clave proporcionados.
    """
    if isinstance(iv, str):
        iv = base64.b64decode(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    tex_bytes = cipher.encrypt(pad(mensaje.encode('utf-8'), AES.block_size))
    return base64.b64encode(tex_bytes).decode('utf-8')