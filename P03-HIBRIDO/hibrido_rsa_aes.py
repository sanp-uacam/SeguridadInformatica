"""
Practica 3 - Algoritmo Hibrido RSA + AES
Universidad Autonoma de Campeche - Facultad de Ingenieria
Seguridad Informatica

Implementacion con la libreria PyCryptodome (paquete Crypto).
"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes



# Generacion de claves RSA

def generar_claves_rsa(bits=2048):
    """Genera un par de claves RSA (publica, privada)."""
    clave_privada = RSA.generate(bits)
    clave_publica = clave_privada.publickey()
    return clave_publica, clave_privada


# c) Funcion auxiliar de cifrado AES-CBC

def Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes):
    """
    Cifra 'mensaje' (str) con AES en modo CBC usando 'clave_aes'
    (32 bytes) y el 'iv' (16 bytes) proporcionados.
    Devuelve los bytes cifrados.
    """
    cipher = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_bytes = mensaje.encode("utf-8")
    mensaje_padded = pad(mensaje_bytes, AES.block_size)
    return cipher.encrypt(mensaje_padded)



# a) Generacion de clave/IV, cifrado AES del mensaje y cifrado
#    RSA de la clave+IV

def get_Msj_And_Key(RSA_Publica, mensaje="Mensaje por defecto"):
    """
    Entrada:  clave publica RSA del receptor (y el mensaje a enviar).
    Proceso:
        1. Genera una clave AES-256 (32 bytes) aleatoria.
        2. Genera un IV aleatorio de 16 bytes (tamano de bloque de AES).
        3. Cifra el mensaje con AES-CBC usando clave e IV.
        4-5. Empaqueta clave_aes + iv y cifra el paquete con RSA-OAEP
             usando la clave publica del receptor.
    Salida: (iv_cifrado_RSA, mensajeCifrado_AES)
        iv_cifrado_RSA contiene el paquete cifrado con RSA
        (clave AES + IV), tal como permite la especificacion
        ("empaquetarlo junto con la clave cifrada").
    """
    # 1. Clave AES simetrica (256 bits)
    clave_aes = get_random_bytes(32)

    # 2. IV de 16 bytes (128 bits = tamano de bloque de AES)
    iv = get_random_bytes(16)

    # 3. Cifrado AES-CBC del mensaje
    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)

    # 4-5. Empaquetar clave + IV y cifrar con RSA-OAEP
    paquete = clave_aes + iv  # 32 + 16 = 48 bytes
    cipher_rsa = PKCS1_OAEP.new(RSA_Publica)
    iv_cifrado_RSA = cipher_rsa.encrypt(paquete)

    return iv_cifrado_RSA, mensajeCifrado_AES



# b) Descifrado del paquete RSA y del mensaje AES

def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada):
    """
    Entrada: mensaje cifrado AES, paquete (clave+IV) cifrado con RSA,
             clave privada RSA del receptor.
    Proceso:
        1-2. Descifra el paquete con RSA-OAEP para recuperar la
             clave AES y el IV originales.
        3. Descifra el mensaje con AES-CBC usando clave e IV.
    Salida: mensaje original en texto plano.
    """
    # 1-2. Descifrar paquete RSA -> clave_aes + iv
    cipher_rsa = PKCS1_OAEP.new(RSA_Privada)
    paquete = cipher_rsa.decrypt(iv_cifrado_RSA)
    clave_aes = paquete[:32]
    iv = paquete[32:48]

    # 3. Descifrar mensaje con AES-CBC
    cipher_aes = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_padded = cipher_aes.decrypt(mensajeCifrado_AES)
    mensaje = unpad(mensaje_padded, AES.block_size)

    return mensaje.decode("utf-8")



# Pruebas

if __name__ == "__main__":
    print("=" * 65)
    print(" PRACTICA 3 - ALGORITMO HIBRIDO RSA + AES")
    print("=" * 65)

    # Prueba 1: flujo completo 
    RSA_Publica, RSA_Privada = generar_claves_rsa(2048)
    print("\n[1] Par de claves RSA generado (2048 bits)")

    mensaje_original = "Este es un mensaje confidencial de prueba."
    print(f"[2] Mensaje original      : {mensaje_original}")

    iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(RSA_Publica, mensaje_original)
    print(f"[3] Mensaje cifrado (AES) : {mensajeCifrado_AES.hex()[:60]}...")
    print(f"[4] Paquete cifrado (RSA) : {iv_cifrado_RSA.hex()[:60]}...")

    mensaje_recuperado = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)
    print(f"[5] Mensaje descifrado    : {mensaje_recuperado}")

    assert mensaje_original == mensaje_recuperado
    print("\n[OK] Prueba 1 exitosa: el mensaje descifrado coincide con el original.")

    # Prueba 2: funcion auxiliar de cifrado directo 
    print("\n--- Prueba 2: Cifrado_AES_enviar_mensaje('Mensaje', iv) ---")
    clave_prueba = get_random_bytes(32)
    iv_prueba = get_random_bytes(16)
    cifrado_prueba = Cifrado_AES_enviar_mensaje("Mensaje", iv_prueba, clave_prueba)
    print(f"IV usado          : {iv_prueba.hex()}")
    print(f"Mensaje cifrado   : {cifrado_prueba.hex()}")

    # Prueba 3: prueba ante clave privada incorrecta ---
    print("\n--- Prueba 3: descifrado con clave privada incorrecta ---")
    try:
        _, otra_privada = generar_claves_rsa(2048)
        decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, otra_privada)
        print("[FALLO] No debio poder descifrar con una clave distinta.")
    except Exception as e:
        print(f"[OK] Error esperado al usar clave privada incorrecta: {type(e).__name__}")

    # Prueba 4: mensajes de distinta longitud (padding)
    print("\n--- Prueba 4: mensajes de longitudes variadas ---")
    for texto in ["", "A", "Hola mundo", "X" * 100]:
        iv_r, msg_c = get_Msj_And_Key(RSA_Publica, texto)
        recuperado = decifrar_mensaje(msg_c, iv_r, RSA_Privada)
        estado = "OK" if recuperado == texto else "FALLO"
        print(f"  len={len(texto):4d}  -> {estado}")

    print("\n" + "=" * 65)
    print(" TODAS LAS PRUEBAS FINALIZADAS")
    print("=" * 65)
