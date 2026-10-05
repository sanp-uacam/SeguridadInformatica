# ====== cifrado.py ======

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

def Cifrado_AES_enviar_mensaje(mensaje, clave_aes, iv):
    cifrador = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_padded = pad(mensaje.encode('utf-8'), AES.block_size)
    return cifrador.encrypt(mensaje_padded)

def get_Msj_And_Key(mensaje, RSA_Publica):
    clave_aes = get_random_bytes(32)   # AES-256
    iv = get_random_bytes(16)          # tamaño de bloque de AES, siempre 16

    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, clave_aes, iv)

    cifrador_rsa = PKCS1_OAEP.new(RSA_Publica)
    paquete = clave_aes + iv
    iv_cifrado_RSA = cifrador_rsa.encrypt(paquete)

    return iv_cifrado_RSA, mensajeCifrado_AES



with open("publica_companero.pem", "rb") as f:
    RSA_Publica = RSA.import_key(f.read())

mensaje = input("Mensaje a cifrar: ")
iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(mensaje, RSA_Publica)


with open("paquete.bin", "wb") as f:
    f.write(iv_cifrado_RSA)

with open("mensaje_cifrado.bin", "wb") as f:
    f.write(mensajeCifrado_AES)

print("Listo: manda 'paquete.bin' y 'mensaje_cifrado.bin' ")