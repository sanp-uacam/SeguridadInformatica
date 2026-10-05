from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

# ==========================================
# FUNCIONES ORIGINALES (Cifrado Simétrico AES)
# ==========================================

def encode(key, text):
    cipher = AES.new(key, AES.MODE_CBC)
    text_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
    vi = base64.b64encode(cipher.iv).decode('utf-8')
    text_encrypted = base64.b64encode(text_bytes).decode('utf-8')
    return vi, text_encrypted

def decode(key, iv, text):
    iv = base64.b64decode(iv)
    text = base64.b64decode(text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(text), AES.block_size)
    return pt.decode('utf-8')

def getKey(size):
    return get_random_bytes(size)

# ==========================================
# NUEVAS FUNCIONES (Criptografía Híbrida del Pizarrón)
# ==========================================

def generar_llaves_rsa():
    """Genera el par de llaves RSA (Pública y Privada) para el Receptor"""
    # Genera una llave de 2048 bits (estándar seguro)
    llave_privada = RSA.generate(2048)
    llave_publica = llave_privada.publickey()
    return llave_privada, llave_publica

def emisor_cifrar(mensaje, rsa_public_key):
    """
    Representa el flujo del 'Emisor' en el pizarrón:
    - Crea una llave AES.
    - Cifra el mensaje usando AES.
    - Cifra el VI y la Llave AES usando la llave pública RSA.
    """
    # 1. Generar llave simétrica temporal para este mensaje (16 bytes = 128 bits)
    llave_aes = getKey(16)
    
    # 2. Cifrar el mensaje con tu función original AES
    vi_b64, msj_cifrado_aes = encode(llave_aes, mensaje)
    
    # 3. Preparar los datos que deben protegerse con RSA (Llave + Vector de Inicialización)
    # Concatenamos la llave (16 bytes) con el VI convertido a bytes
    datos_a_proteger = llave_aes + vi_b64.encode('utf-8')
    
    # 4. Cifrar con la llave Pública del receptor usando RSA
    rsa_cipher = PKCS1_OAEP.new(rsa_public_key)
    datos_rsa_cifrados = rsa_cipher.encrypt(datos_a_proteger)
    
    # Devolver el "paquete" que viajaría por la red (todo en base64 para que sea legible)
    return {
        'datos_rsa': base64.b64encode(datos_rsa_cifrados).decode('utf-8'),
        'mensaje_cifrado_aes': msj_cifrado_aes
    }

def receptor_descifrar(paquete, rsa_private_key):
    """
    Representa el flujo del 'Receptor' en el pizarrón:
    - Descifra el VI y la Llave AES usando su llave privada RSA.
    - Descifra el mensaje usando la llave y el VI obtenidos.
    """
    # 1. Recuperar los datos cifrados con RSA desde el base64
    datos_rsa_cifrados = base64.b64decode(paquete['datos_rsa'])
    
    # 2. Descifrar usando la llave Privada del receptor
    rsa_cipher = PKCS1_OAEP.new(rsa_private_key)
    datos_descifrados = rsa_cipher.decrypt(datos_rsa_cifrados)
    
    # 3. Separar la llave AES y el VI (sabemos que la llave mide exactamente 16 bytes)
    llave_aes = datos_descifrados[:16]
    vi_b64 = datos_descifrados[16:].decode('utf-8')
    
    # 4. Descifrar el mensaje usando tu función original AES
    mensaje_original = decode(llave_aes, vi_b64, paquete['mensaje_cifrado_aes'])
    
    return mensaje_original