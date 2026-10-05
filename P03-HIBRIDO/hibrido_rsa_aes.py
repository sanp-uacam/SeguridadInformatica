# Practica 2 - Algoritmo hibrido RSA + AES
# Seguridad Informatica
#
# La idea es combinar los dos tipos de cifrado: AES cifra el mensaje porque es
# rapido y no tiene limite de tamano, y RSA se encarga nada mas de la clave AES
# y del IV, que es lo unico que se necesita mandar de forma segura.

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

TAM_CLAVE_AES = 32   # 32 bytes = 256 bits (AES-256)
TAM_IV = 32          # la practica pide 32, aunque CBC solo usa 16
BLOQUE = 16

# Aqui se guarda la clave AES que genera get_Msj_And_Key, porque la firma de
# Cifrado_AES_enviar_mensaje("Mensaje", iv) no recibe la clave por ningun lado.
clave_actual = None


def generar_par_llaves(bits=2048):
    """Crea el par de llaves del receptor."""
    privada = RSA.generate(bits)
    return privada, privada.publickey()


def guardar_llaves(privada, ruta_priv="privada.pem", ruta_pub="publica.pem"):
    with open(ruta_priv, "wb") as f:
        f.write(privada.export_key())
    with open(ruta_pub, "wb") as f:
        f.write(privada.publickey().export_key())


def cargar_llave(ruta):
    with open(ruta, "rb") as f:
        return RSA.import_key(f.read())


def Cifrado_AES_enviar_mensaje(mensaje, iv, clave=None):
    """Cifra el mensaje con AES en modo CBC usando el IV que se le pase."""
    if isinstance(mensaje, str):
        mensaje = mensaje.encode("utf-8")
    if clave is None:
        clave = clave_actual

    # CBC necesita un IV de exactamente 16 bytes (el tamano de bloque), asi que
    # de los 32 que pide la practica nada mas se le pasan los primeros 16.
    cifrador = AES.new(clave, AES.MODE_CBC, iv[:BLOQUE])

    # el relleno hace falta porque CBC solo trabaja con bloques completos
    return cifrador.encrypt(pad(mensaje, BLOQUE))


def Descifrado_AES_recibir_mensaje(mensaje_cifrado, iv, clave=None):
    if clave is None:
        clave = clave_actual
    descifrador = AES.new(clave, AES.MODE_CBC, iv[:BLOQUE])
    return unpad(descifrador.decrypt(mensaje_cifrado), BLOQUE).decode("utf-8")


def get_Msj_And_Key(RSA_Publica, mensaje=None):
    """
    Lado del emisor. Genera la clave AES y el IV, cifra el mensaje con AES y
    despues cifra la clave y el IV con la clave publica del receptor.

    Regresa (iv_cifrado_RSA, mensajeCifrado_AES).
    """
    global clave_actual

    if mensaje is None:
        mensaje = input("Escribe el mensaje a cifrar: ")

    clave_aes = get_random_bytes(TAM_CLAVE_AES)
    iv = get_random_bytes(TAM_IV)
    clave_actual = clave_aes

    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)

    # El IV y la clave se mandan juntos en un solo cifrado RSA. Son 64 bytes en
    # total y en RSA-2048 con OAEP caben hasta 190, asi que no hay problema.
    rsa = PKCS1_OAEP.new(RSA_Publica, hashAlgo=SHA256)
    iv_cifrado_RSA = rsa.encrypt(iv + clave_aes)

    return iv_cifrado_RSA, mensajeCifrado_AES


def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada):
    """
    Lado del receptor. Primero abre el paquete RSA con la clave privada para
    sacar el IV y la clave AES, y con eso ya descifra el mensaje.
    """
    rsa = PKCS1_OAEP.new(RSA_Privada, hashAlgo=SHA256)
    paquete = rsa.decrypt(iv_cifrado_RSA)

    iv = paquete[:TAM_IV]
    clave_aes = paquete[TAM_IV:]

    return Descifrado_AES_recibir_mensaje(mensajeCifrado_AES, iv, clave_aes)
