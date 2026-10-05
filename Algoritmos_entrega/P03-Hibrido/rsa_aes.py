from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64


# ==========================================================
# FUNCIÓN AUXILIAR AES
# ==========================================================

def Cifrado_AES_enviar_mensaje(Mensaje, iv, clave_AES):
    """
    Cifra un mensaje utilizando AES-256 en modo CBC.
    """

    cipher_AES = AES.new(
        clave_AES,
        AES.MODE_CBC,
        iv
    )

    mensaje_bytes = Mensaje.encode("utf-8")

    # AES requiere que los datos sean múltiplos de 16 bytes
    mensaje_padding = pad(
        mensaje_bytes,
        AES.block_size
    )

    mensaje_cifrado = cipher_AES.encrypt(
        mensaje_padding
    )

    return mensaje_cifrado


# ==========================================================
# GENERAR MENSAJE Y CLAVES
# ==========================================================

def get_Msj_And_Key(RSA_Publica):

    print("\n======================================")
    print("       CIFRADO HÍBRIDO RSA + AES")
    print("======================================")

    # ------------------------------------------------------
    # 1. Pedir mensaje
    # ------------------------------------------------------

    mensaje = input("\nEscribe el mensaje que deseas cifrar: ")

    # ------------------------------------------------------
    # 2. Generar clave AES de 32 bytes
    # AES-256 = 256 bits = 32 bytes
    # ------------------------------------------------------

    clave_AES = get_random_bytes(32)

    print("\n[1] Clave AES generada")
    print("Clave AES:")
    print(clave_AES.hex())

    print("\nTamaño clave AES:")
    print(len(clave_AES), "bytes")

    # ------------------------------------------------------
    # 3. Generar IV
    # AES CBC requiere exactamente 16 bytes
    # ------------------------------------------------------

    iv = get_random_bytes(16)

    print("\n[2] Vector de Inicialización generado")
    print("IV:")
    print(iv.hex())

    print("\nTamaño IV:")
    print(len(iv), "bytes")

    # ------------------------------------------------------
    # 4. Cifrar mensaje usando AES
    # ------------------------------------------------------

    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(
        mensaje,
        iv,
        clave_AES
    )

    print("\n[3] Mensaje cifrado con AES-CBC")

    print(
        base64.b64encode(
            mensajeCifrado_AES
        ).decode()
    )

    # ------------------------------------------------------
    # 5. Preparar RSA
    # ------------------------------------------------------

    cipher_RSA = PKCS1_OAEP.new(
        RSA_Publica
    )

    # ------------------------------------------------------
    # 6. Cifrar clave AES con RSA
    # ------------------------------------------------------

    clave_AES_cifrada_RSA = cipher_RSA.encrypt(
        clave_AES
    )

    print("\n[4] Clave AES cifrada con RSA")

    print(
        base64.b64encode(
            clave_AES_cifrada_RSA
        ).decode()
    )

    # ------------------------------------------------------
    # 7. Cifrar IV con RSA
    # ------------------------------------------------------

    iv_cifrado = cipher_RSA.encrypt(
        iv
    )

    print("\n[5] IV cifrado con RSA")

    print(
        base64.b64encode(
            iv_cifrado
        ).decode()
    )

    # ------------------------------------------------------
    # Empaquetamos clave AES cifrada + IV cifrado
    # ------------------------------------------------------

    iv_cifrado_RSA = {
        "clave_AES_RSA": clave_AES_cifrada_RSA,
        "iv_RSA": iv_cifrado
    }

    return iv_cifrado_RSA, mensajeCifrado_AES


# ==========================================================
# DESCIFRAR MENSAJE
# ==========================================================

def decifrar_mensaje(
        mensajeCifrado_AES,
        iv_cifrado_RSA,
        RSA_Privada
):

    print("\n======================================")
    print("            DESCIFRADO")
    print("======================================")

    # ------------------------------------------------------
    # Preparar RSA con clave privada
    # ------------------------------------------------------

    cipher_RSA = PKCS1_OAEP.new(
        RSA_Privada
    )

    # ------------------------------------------------------
    # 1. Recuperar IV
    # ------------------------------------------------------

    iv = cipher_RSA.decrypt(
        iv_cifrado_RSA["iv_RSA"]
    )

    print("\n[1] IV descifrado correctamente")

    print("IV:")
    print(iv.hex())

    # ------------------------------------------------------
    # 2. Recuperar clave AES
    # ------------------------------------------------------

    clave_AES = cipher_RSA.decrypt(
        iv_cifrado_RSA["clave_AES_RSA"]
    )

    print("\n[2] Clave AES descifrada correctamente")

    print("Clave AES:")
    print(clave_AES.hex())

    # ------------------------------------------------------
    # 3. Descifrar mensaje AES
    # ------------------------------------------------------

    cipher_AES = AES.new(
        clave_AES,
        AES.MODE_CBC,
        iv
    )

    mensaje_padding = cipher_AES.decrypt(
        mensajeCifrado_AES
    )

    mensaje_original = unpad(
        mensaje_padding,
        AES.block_size
    )

    mensaje_original = mensaje_original.decode(
        "utf-8"
    )

    print("\n[3] Mensaje descifrado:")

    print("\n--------------------------------------")
    print(mensaje_original)
    print("--------------------------------------")

    return mensaje_original


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

def main():

    print("======================================")
    print("    ALGORITMO HÍBRIDO RSA + AES")
    print("======================================")

    # ------------------------------------------------------
    # Generar claves RSA
    # ------------------------------------------------------

    print("\nGenerando claves RSA...")

    RSA_Privada = RSA.generate(2048)

    RSA_Publica = RSA_Privada.publickey()

    print("Claves RSA generadas correctamente.")

    print("\nTamaño RSA:")
    print(RSA_Privada.size_in_bits(), "bits")

    # ------------------------------------------------------
    # Mostrar clave pública
    # ------------------------------------------------------

    print("\n===== CLAVE PÚBLICA RSA =====")

    print(
        RSA_Publica.export_key().decode()
    )

    # ------------------------------------------------------
    # CIFRADO
    # ------------------------------------------------------

    iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(
        RSA_Publica
    )

    # ------------------------------------------------------
    # DESCIFRADO
    # ------------------------------------------------------

    mensaje_recuperado = decifrar_mensaje(
        mensajeCifrado_AES,
        iv_cifrado_RSA,
        RSA_Privada
    )

    # ------------------------------------------------------
    # PRUEBA
    # ------------------------------------------------------

    print("\n======================================")
    print("       PRUEBA FINAL COMPLETADA")
    print("======================================")

    print("\nMensaje recuperado:")

    print(mensaje_recuperado)


# ==========================================================
# EJECUTAR
# ==========================================================

if __name__ == "__main__":
    main()