# Mauricio A. Sonda Cahuich

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import os


def encode(key, text):
    # Encripta 'text' con AES-CBC. Devuelve (iv_b64, texto_cifrado_b64)
    cipher = AES.new(key, AES.MODE_CBC)
    text_bytes = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    text_encrypted = base64.b64encode(text_bytes).decode('utf-8')
    return iv, text_encrypted


def decode(key, iv, text):
    # Descifra 'text' usando la misma clave e iv con los que se cifró.
    iv_bytes = base64.b64decode(iv)
    text_bytes = base64.b64decode(text)
    cipher = AES.new(key, AES.MODE_CBC, iv_bytes)
    pt = unpad(cipher.decrypt(text_bytes), AES.block_size)
    return pt.decode('utf-8')


def getKey(size=32):
    # Genera una clave aleatoria de 32 bytes (32 = AES-256).
    return get_random_bytes(size)


def get_or_create_key(path='secret.key', size=32):
    """
    Recupera la clave AES guardada en 'path'. Si no existe, la crea y la guarda. 
    Esto es porque una clave nueva en cada ejecución haría imposible descifrar datos guardados en ejecuciones anteriores."""
    if os.path.exists(path):
        with open(path, 'rb') as f:
            key = f.read()
        if len(key) in (16, 24, 32):
            return key
    key = getKey(size)
    with open(path, 'wb') as f:
        f.write(key)
    return key
