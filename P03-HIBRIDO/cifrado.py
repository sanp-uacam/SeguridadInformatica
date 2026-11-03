from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

def Cifrado_AES_enviar_mensaje(mensaje, iv, key):
    cipher_aes = AES.new(key, AES.MODE_CBC, iv)
    mensaje_cifrado = cipher_aes.encrypt(pad(mensaje.encode('utf-8'), AES.block_size))
    return mensaje_cifrado

def get_Msj_And_Key(RSA_Publica, mensaje_texto):
    # 1 y 2. Generar clave AES (32 bytes) y IV (16 bytes para CBC)
    clave_aes = get_random_bytes(32)
    iv = get_random_bytes(16)

    # 3. Cifrar el mensaje con AES
    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje_texto, iv, clave_aes)

    # 4 y 5. Empaquetar y cifrar la clave AES y el IV con RSA
    paquete_simetrico = clave_aes + iv
    cipher_rsa = PKCS1_OAEP.new(RSA_Publica)
    iv_cifrado_RSA = cipher_rsa.encrypt(paquete_simetrico)

    return iv_cifrado_RSA, mensajeCifrado_AES

# --- EJECUCION ---
with open("publica.pem", "rb") as f:
    clave_publica = RSA.import_key(f.read())

mensaje = "Hola Universidad Autonoma de Campeche, soy Fernando"
print(f"Mensaje a cifrar: '{mensaje}'")

iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(clave_publica, mensaje)

with open("paquete.bin", "wb") as f:
    f.write(iv_cifrado_RSA)

with open("mensaje_cifrado.bin", "wb") as f:
    f.write(mensajeCifrado_AES)

print("¡Listo! Archivos 'paquete.bin' y 'mensaje_cifrado.bin' enviados.")
