from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad

def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada):
    # 1 y 2. Descifrar el paquete (Clave AES + IV) usando RSA Privada
    cipher_rsa = PKCS1_OAEP.new(RSA_Privada)
    paquete_descifrado = cipher_rsa.decrypt(iv_cifrado_RSA)

    # Separar la clave AES (32 bytes) y el IV (16 bytes)
    clave_aes = paquete_descifrado[:32]
    iv = paquete_descifrado[32:]

    # 3. Descifrar el mensaje con AES recuperado
    cipher_aes = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_padded = cipher_aes.decrypt(mensajeCifrado_AES)
    mensaje_original = unpad(mensaje_padded, AES.block_size).decode('utf-8')

    return mensaje_original

# --- EJECUCION ---
with open("privada.pem", "rb") as f:
    clave_privada = RSA.import_key(f.read())

with open("paquete.bin", "rb") as f:
    iv_cifrado_RSA = f.read()

with open("mensaje_cifrado.bin", "rb") as f:
    mensajeCifrado_AES = f.read()

mensaje_recuperado = decifrar_mensaje(
    mensajeCifrado_AES,
    iv_cifrado_RSA,
    clave_privada
)

print(f"Mensaje descifrado: '{mensaje_recuperado}'")
