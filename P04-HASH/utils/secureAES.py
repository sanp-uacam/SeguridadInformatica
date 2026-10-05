from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

def encode(key, text):
    cipher = AES.new(key, AES.MODE_CBC)
    text_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
    vi = base64.b64encode(cipher.iv).decode('utf-8')
    text_encrypted = base64.b64encode(text_bytes).decode('utf-8')
    return vi, text_encrypted

def decode(key, iv, text):
    iv = base64.b64decode(iv)
    text = base64.b64decode(text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(text), AES.block_size)
    return pt.decode('utf-8')

def getKey(size):
    return get_random_bytes(size)