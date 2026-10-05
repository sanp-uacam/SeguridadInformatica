import math
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import getPrime

# Generación de claves RSA 
def generar_claves_rsa():
    # Generar primos aleatorios 
    p = getPrime(10)
    q = getPrime(10)
    
    # Que no sean identicos
    while p == q:
        q = getPrime(10)

    n = p * q
    phi_n = (p - 1) * (q - 1)

    candidatos = [i for i in range(2, phi_n) if math.gcd(i, phi_n) == 1]
    e = candidatos[4]
    d = pow(e, -1, phi_n)
    
    return (e, n), (d, n)

# Función de cifrado AES
def Cifrado_AES_enviar_mensaje(mensaje, clave_aes, iv):
    cipher = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_bytes = mensaje.encode('utf-8')
    return cipher.encrypt(pad(mensaje_bytes, AES.block_size))

# Cifrado RSA
def get_Msj_And_Key(RSA_Publica, mensaje):
    e_pub, n_pub = RSA_Publica
    
    clave_aes = get_random_bytes(32)
    iv = get_random_bytes(16)  
    
    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, clave_aes, iv)
    
    clave_aes_cifrada_RSA = [pow(byte, e_pub, n_pub) for byte in clave_aes]
    iv_cifrado_RSA = [pow(byte, e_pub, n_pub) for byte in iv]
    
    return iv_cifrado_RSA, clave_aes_cifrada_RSA, mensajeCifrado_AES

# Función de descifrado RSA y AES
def decifrar_mensaje(mensajeCifrado_AES, clave_aes_cifrada_RSA, iv_cifrado_RSA, RSA_Privada):
    d_priv, n_priv = RSA_Privada
    
    iv_descifrado = bytes([pow(c, d_priv, n_priv) for c in iv_cifrado_RSA])
    clave_aes_descifrada = bytes([pow(c, d_priv, n_priv) for c in clave_aes_cifrada_RSA])
    
    cipher = AES.new(clave_aes_descifrada, AES.MODE_CBC, iv_descifrado)
    mensaje_bytes = unpad(cipher.decrypt(mensajeCifrado_AES), AES.block_size)
    
    return mensaje_bytes.decode('utf-8')