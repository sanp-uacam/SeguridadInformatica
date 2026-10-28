# ====== descifrado.py ======

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import unpad

def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada):
    descifrador_rsa = PKCS1_OAEP.new(RSA_Privada)
    paquete = descifrador_rsa.decrypt(iv_cifrado_RSA)
    clave_aes, iv = paquete[:32], paquete[32:48]

    descifrador_aes = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_padded = descifrador_aes.decrypt(mensajeCifrado_AES)
    return unpad(mensaje_padded, AES.block_size).decode('utf-8')



with open("privada.pem", "rb") as f:
    RSA_Privada = RSA.import_key(f.read())

# --- Leer los archivos  ---
with open("paquete.bin", "rb") as f:
    iv_cifrado_RSA = f.read()

with open("mensaje_cifrado.bin", "rb") as f:
    mensajeCifrado_AES = f.read()

mensaje_original = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)
print("Mensaje descifrado:", mensaje_original)