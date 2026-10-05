import base64
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import encryptAES
import local_db

def get_Msj_And_Key(RSA_Publica):
    """
    A)
    1.- Genera clave AES (32 bytes).
    2.- Cifra el mensaje con AES en modo CBC.
    3.- Empaqueta clave AES + IV y los cifra con RSA pública.
    """
    #1.- Clave AES simétrica (32 bytes = 256 bits)
    clave_aes = get_random_bytes(32)
    
    #2 y 3.- Cifrado del mensaje en AES
    mensaje_plano = "Mensaje confidencial - Seguridad Informática UACAM"
    iv_b64, mensajeCifrado_AES = encryptAES.encode(clave_aes, mensaje_plano)
    iv_bytes = base64.b64decode(iv_b64)

    #4 y 5.- Empaquetar clave AES + IV y cifrar con la clave pública RSA usando OAEP
    datos_sesion = clave_aes + iv_bytes
    cipher_rsa = PKCS1_OAEP.new(RSA_Publica)
    iv_cifrado_bytes = cipher_rsa.encrypt(datos_sesion)
    
    iv_cifrado_RSA = base64.b64encode(iv_cifrado_bytes).decode('utf-8')
    
    return iv_cifrado_RSA, mensajeCifrado_AES

def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada):
    """
    B)
    1.- Descifra el bloque RSA con la clave privada para recuperar AES Key e IV.
    2.- Descifra el mensaje AES usando la clave recuperada y el IV.
    """
    #1 y 2.- Descifrado RSA
    cipher_rsa = PKCS1_OAEP.new(RSA_Privada)
    datos_cifrados = base64.b64decode(iv_cifrado_RSA)
    datos_sesion = cipher_rsa.decrypt(datos_cifrados)

    clave_aes_recuperada = datos_sesion[:32]
    iv_bytes_recuperado = datos_sesion[32:]
    iv_b64_recuperado = base64.b64encode(iv_bytes_recuperado).decode('utf-8')

    #3.- Descifrado AES
    mensaje_original = encryptAES.decode(clave_aes_recuperada, iv_b64_recuperado, mensajeCifrado_AES)
    return mensaje_original

if __name__ == "__main__":
    par_rsa = RSA.generate(2048)
    RSA_Privada = par_rsa
    RSA_Publica = par_rsa.publickey()

    #Emisor genera mensaje cifrado y sobre digital RSA
    iv_cifrado, mensajeCifrado = get_Msj_And_Key(RSA_Publica)

    print("== CIFRADO ==")
    print("IV y Clave AES cifrados con RSA (Base64):")
    print(iv_cifrado)
    print("\nMensaje cifrado con AES (Base64):")
    print(mensajeCifrado)

    #Guardar datos en archivo JSON local
    data = {
        "mensaje": mensajeCifrado,
        "iv_cifrado_RSA": iv_cifrado
    }
    local_db.save(data, "mensaje_oculto.json")
    print("\nDatos guardados exitosamente en 'mensaje_oculto.json'.")

    #Receptor descifra el mensaje
    mensaje_descifrado = decifrar_mensaje(mensajeCifrado, iv_cifrado, RSA_Privada)
    print("\n== DESCIFRADO ==")
    print("Texto original:")
    print(mensaje_descifrado)

    #Demostración de la función auxiliar (Inciso c)
    clave_prueba = get_random_bytes(32)
    iv_prueba = get_random_bytes(16)
    cifrado_aux = encryptAES.Cifrado_AES_enviar_mensaje("Mensaje adicional", iv_prueba, clave_prueba)
    print(f"\nPrueba auxiliar Cifrado_AES_enviar_mensaje: {cifrado_aux}")