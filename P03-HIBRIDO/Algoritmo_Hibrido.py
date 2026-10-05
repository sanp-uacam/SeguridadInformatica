from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# Generación de par de llaves RSA 
def generar_llaves_rsa(bits=2048):
    clave_privada = RSA.generate(bits)
    clave_publica = clave_privada.publickey()
    return clave_privada, clave_publica

# a) get_Msj_And_Key: cifra el mensaje con AES y protege la clave+IV con RSA
def get_Msj_And_Key(mensaje: str, RSA_Publica):
    
    # 1. Clave AES-256 simétrica
    clave_aes = get_random_bytes(32)

    # 2. IV de 16 bytes (tamaño de bloque AES)
    iv = get_random_bytes(16)

    # 3. Cifrar el mensaje con AES-CBC (función auxiliar del inciso c)
    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)

    # 4. Cifrar (clave_aes + iv) con RSA usando la llave pública
    cifrador_rsa = PKCS1_OAEP.new(RSA_Publica)
    paquete_secreto = clave_aes + iv                 # 32 + 16 = 48 bytes
    iv_cifrado_RSA = cifrador_rsa.encrypt(paquete_secreto)

    return iv_cifrado_RSA, mensajeCifrado_AES

# b) decifrar_mensaje: recupera clave+IV con RSA y descifra el mensaje AES

def decifrar_mensaje(mensajeCifrado_AES: bytes, iv_cifrado_RSA: bytes, RSA_Privada):

    # 1. Descifrar el paquete (clave_aes + iv) con RSA
    descifrador_rsa = PKCS1_OAEP.new(RSA_Privada)
    paquete_secreto = descifrador_rsa.decrypt(iv_cifrado_RSA)

    # 2. Separar clave AES (32 bytes) e IV (16 bytes)
    clave_aes = paquete_secreto[:32]
    iv = paquete_secreto[32:48]

    # 3. Descifrar el mensaje con AES-CBC
    descifrador_aes = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_padded = descifrador_aes.decrypt(mensajeCifrado_AES)

    # 4. Quitar padding PKCS7
    mensaje_bytes = unpad(mensaje_padded, AES.block_size)

    return mensaje_bytes.decode("utf-8")

# c) Cifrado_AES_enviar_mensaje: función auxiliar de cifrado AES-CBC
def Cifrado_AES_enviar_mensaje(mensaje: str, iv: bytes, clave_aes: bytes) -> bytes:

    cifrador_aes = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_padded = pad(mensaje.encode("utf-8"), AES.block_size)
    return cifrador_aes.encrypt(mensaje_padded)

# Demostración 
if __name__ == "__main__":
    print("Demostración del algoritmo híbrido RSA + AES\n")

    # Simulamos al receptor generando su par de llaves
    clave_privada_receptor, clave_publica_receptor = generar_llaves_rsa()

    mensaje_original = "Este es un mensaje secreto para la práctica."
    print(f"Mensaje original:\n  {mensaje_original}\n")

    # Emisor: cifra el mensaje con la llave pública del receptor 
    iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(mensaje_original, clave_publica_receptor)
    print(f"Mensaje cifrado (AES, hex):\n  {mensajeCifrado_AES.hex()}\n")
    print(f"Clave+IV cifrados (RSA, hex):\n  {iv_cifrado_RSA.hex()}\n")

    # Receptor: descifra con su llave privada 
    mensaje_recuperado = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, clave_privada_receptor)
    print(f"Mensaje descifrado:\n  {mensaje_recuperado}\n")

    assert mensaje_recuperado == mensaje_original
    print("El mensaje descifrado coincide con el original.")