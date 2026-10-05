"""
Práctica 3 - Algoritmo Híbrido RSA_AES
Universidad Autónoma de Campeche - Facultad de Ingeniería
Seguridad Informática
"""

import os
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256

# Parámetros de diseño (ver documentación para la justificación completa)
AES_KEY_SIZE = 32      # 32 bytes = 256 bits -> AES-256
AES_BLOCK_SIZE = 16    # 16 bytes = 128 bits -> tamaño de bloque e IV de AES (fijo por el estándar, NO depende del tamaño de clave)
RSA_KEY_SIZE = 2048    



# Utilidad: generación del par de claves RSA del receptor
def generar_par_claves_rsa(bits: int = RSA_KEY_SIZE):
    """Genera un par de claves RSA (privada, pública)."""
    clave_privada = RSA.generate(bits)
    clave_publica = clave_privada.publickey()
    return clave_privada, clave_publica



# a) get_Msj_And_Key(mensaje, RSA_Publica)
def get_Msj_And_Key(mensaje: str, RSA_Publica):
    clave_aes = os.urandom(AES_KEY_SIZE)
    iv = os.urandom(AES_BLOCK_SIZE)

    # 3. Cifrar el mensaje con AES-CBC
    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)

    # 4-5. Empaquetar clave+IV y cifrar con RSA-OAEP (clave pública del receptor)
    cipher_rsa = PKCS1_OAEP.new(RSA_Publica, hashAlgo=SHA256)
    paquete = clave_aes + iv                      # 32 + 16 = 48 bytes
    iv_cifrado_RSA = cipher_rsa.encrypt(paquete)   # cabe holgado en RSA-2048

    return iv_cifrado_RSA, mensajeCifrado_AES


# c) Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)
def Cifrado_AES_enviar_mensaje(mensaje: str, iv: bytes, clave_aes: bytes) -> bytes:

    cipher = AES.new(clave_aes, AES.MODE_CBC, iv)
    datos = mensaje.encode("utf-8")
    datos_con_padding = pad(datos, AES.block_size)
    return cipher.encrypt(datos_con_padding)



# b) decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)
def decifrar_mensaje(mensajeCifrado_AES: bytes, iv_cifrado_RSA: bytes, RSA_Privada) -> str:
    cipher_rsa = PKCS1_OAEP.new(RSA_Privada, hashAlgo=SHA256)
    paquete = cipher_rsa.decrypt(iv_cifrado_RSA)

    clave_aes = paquete[:AES_KEY_SIZE]
    iv = paquete[AES_KEY_SIZE:AES_KEY_SIZE + AES_BLOCK_SIZE]

    cipher_aes = AES.new(clave_aes, AES.MODE_CBC, iv)
    datos_con_padding = cipher_aes.decrypt(mensajeCifrado_AES)
    datos = unpad(datos_con_padding, AES.block_size)

    return datos.decode("utf-8")


# Helpers de presentación (para inspeccionar los datos "en tránsito")
def a_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


# Demostración / uso exactamente como en el enunciado
if __name__ == "__main__":
    print("=" * 70)
    print(" DEMO: Algoritmo Híbrido RSA + AES ")
    print("=" * 70)

    # Generar par de claves RSA del receptor
    RSA_Privada, RSA_Publica = generar_par_claves_rsa()
    print(f"\n[+] Par de claves RSA generado ({RSA_KEY_SIZE} bits)")

    mensaje_original = "Este es un mensaje secreto para la práctica de Seguridad Informática."
    print(f"[+] Mensaje original: {mensaje_original!r}")

    # --- Emisor: cifra el mensaje y la clave/IV ---
    iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(mensaje_original, RSA_Publica)

    print(f"\n[+] Paquete (clave AES + IV) cifrado con RSA ({len(iv_cifrado_RSA)} bytes):")
    print(f"    {a_base64(iv_cifrado_RSA)[:80]}...")
    print(f"[+] Mensaje cifrado con AES ({len(mensajeCifrado_AES)} bytes):")
    print(f"    {a_base64(mensajeCifrado_AES)}")

    # --- Receptor: descifra ---
    mensaje_recuperado = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)
    print(f"\n[+] Mensaje descifrado: {mensaje_recuperado!r}")

    assert mensaje_recuperado == mensaje_original, "¡El mensaje descifrado no coincide!"
    print("\n[OK] El mensaje descifrado coincide con el original.")

    # --- Uso independiente de la función auxiliar ---
    print("\n" + "-" * 70)
    print(" Uso independiente de Cifrado_AES_enviar_mensaje ")
    print("-" * 70)
    clave_aes_demo = os.urandom(AES_KEY_SIZE)
    iv_demo = os.urandom(AES_BLOCK_SIZE)
    cifrado_demo = Cifrado_AES_enviar_mensaje("Mensaje", iv_demo, clave_aes_demo)
    print(f"[+] 'Mensaje' cifrado con AES-CBC: {a_base64(cifrado_demo)}")