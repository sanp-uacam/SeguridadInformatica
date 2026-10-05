# -*- coding: utf-8 -*-
"""
Práctica 2 - Algoritmo Híbrido RSA + AES
Universidad Autónoma de Campeche - Facultad de Ingeniería
Materia: Seguridad Informática

Implementa un esquema de cifrado híbrido:
  - AES-256 en modo CBC para cifrar el mensaje (rápido, apto para datos grandes).
  - RSA (OAEP) para cifrar la clave simétrica AES, resolviendo el problema de
    distribución de claves de los cifrados simétricos.

Nota de diseño respecto al enunciado original:
  El enunciado solicita un IV de 32 bytes. AES trabaja siempre con bloques de
  128 bits (16 bytes), sin importar el tamaño de la clave (128/192/256 bits),
  por lo que el IV en modo CBC debe medir exactamente 16 bytes; un valor de
  32 bytes no es válido para el algoritmo y provocaría un error en cualquier
  implementación estándar (PyCryptodome, OpenSSL, etc.). Por ello, en esta
  solución se usa IV = 16 bytes y la clave AES = 32 bytes (AES-256), tal como
  se documenta y justifica en el reporte adjunto.
"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

AES_KEY_SIZE = 32   # 256 bits
AES_IV_SIZE = 16    # tamaño de bloque de AES, fijo por especificación del algoritmo


# ---------------------------------------------------------------------------
# a) Generación de claves RSA (auxiliar, no pedida explícitamente pero
#    necesaria para poder probar el sistema de extremo a extremo).
# ---------------------------------------------------------------------------
def generar_par_rsa(bits=2048):
    """Genera un par de claves RSA (privada, pública)."""
    clave_privada = RSA.generate(bits)
    clave_publica = clave_privada.publickey()
    return clave_privada, clave_publica


# ---------------------------------------------------------------------------
# a) get_Msj_And_Key
# ---------------------------------------------------------------------------
def get_Msj_And_Key(mensaje: bytes, RSA_Publica):
    """
    Cifra 'mensaje' con AES-256-CBC usando una clave e IV generados al vuelo,
    y protege esa clave e IV cifrándolos con la clave pública RSA del receptor.

    Entrada:
        mensaje     -> bytes: texto plano a proteger
        RSA_Publica -> objeto RSA.RsaKey (clave pública del receptor)

    Salida (dict):
        iv_cifrado_RSA      -> IV cifrado con RSA-OAEP
        mensajeCifrado_AES  -> mensaje cifrado con AES-CBC
        clave_cifrada_RSA   -> clave AES cifrada con RSA-OAEP (necesaria para
                                que el receptor pueda descifrar; el enunciado
                                la agrupa conceptualmente junto con el IV)
    """
    # 1. Generar clave AES simétrica aleatoria (256 bits / 32 bytes)
    clave_aes = get_random_bytes(AES_KEY_SIZE)

    # 2. Generar Vector de Inicialización aleatorio (16 bytes, tamaño de bloque AES)
    iv = get_random_bytes(AES_IV_SIZE)

    # 3. Cifrar el mensaje con AES en modo CBC usando la clave generada y el IV
    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, clave_aes, iv)

    # 4. Cifrar la clave AES con RSA usando la clave pública del receptor
    cifrador_rsa = PKCS1_OAEP.new(RSA_Publica)
    clave_cifrada_RSA = cifrador_rsa.encrypt(clave_aes)

    # 5. Cifrar el IV con RSA
    iv_cifrado_RSA = cifrador_rsa.encrypt(iv)

    return {
        "iv_cifrado_RSA": iv_cifrado_RSA,
        "mensajeCifrado_AES": mensajeCifrado_AES,
        "clave_cifrada_RSA": clave_cifrada_RSA,
    }


# ---------------------------------------------------------------------------
# c) Cifrado_AES_enviar_mensaje (función auxiliar, definida antes de b)
#    porque get_Msj_And_Key depende de ella)
# ---------------------------------------------------------------------------
def Cifrado_AES_enviar_mensaje(mensaje: bytes, clave_aes: bytes, iv: bytes) -> bytes:
    """
    Cifra 'mensaje' con AES en modo CBC usando la clave y el IV proporcionados.
    Aplica relleno PKCS#7 porque CBC exige que la longitud del texto plano
    sea múltiplo del tamaño de bloque (16 bytes).
    """
    cifrador = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_padded = pad(mensaje, AES.block_size)
    return cifrador.encrypt(mensaje_padded)


def _descifrar_aes(mensajeCifrado_AES: bytes, clave_aes: bytes, iv: bytes) -> bytes:
    """Inverso de Cifrado_AES_enviar_mensaje."""
    descifrador = AES.new(clave_aes, AES.MODE_CBC, iv)
    mensaje_padded = descifrador.decrypt(mensajeCifrado_AES)
    return unpad(mensaje_padded, AES.block_size)


# ---------------------------------------------------------------------------
# b) decifrar_mensaje
# ---------------------------------------------------------------------------
def decifrar_mensaje(mensajeCifrado_AES: bytes, iv_cifrado_RSA: bytes,
                      clave_cifrada_RSA: bytes, RSA_Privada) -> bytes:
    """
    Revierte el proceso de get_Msj_And_Key.

    Entrada:
        mensajeCifrado_AES -> mensaje cifrado con AES
        iv_cifrado_RSA     -> IV cifrado con RSA
        clave_cifrada_RSA  -> clave AES cifrada con RSA
        RSA_Privada        -> clave privada RSA del receptor

    Salida: mensaje original en texto plano (bytes)
    """
    descifrador_rsa = PKCS1_OAEP.new(RSA_Privada)

    # 1. Descifrar el IV con RSA usando la clave privada
    iv = descifrador_rsa.decrypt(iv_cifrado_RSA)

    # 2. Descifrar la clave AES con RSA usando la clave privada
    clave_aes = descifrador_rsa.decrypt(clave_cifrada_RSA)

    # 3. Descifrar el mensaje con AES usando la clave recuperada y el IV
    mensaje_original = _descifrar_aes(mensajeCifrado_AES, clave_aes, iv)

    return mensaje_original


# ---------------------------------------------------------------------------
# Demostración de uso end-to-end
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Demostración del algoritmo híbrido RSA + AES ===\n")

    # Simulación: el receptor genera su par de claves RSA
    clave_privada_receptor, clave_publica_receptor = generar_par_rsa(2048)
    print("[*] Par de claves RSA-2048 generado para el receptor.")

    mensaje_original = b"Practica 2 - Seguridad Informatica - UACAM - Mensaje confidencial de prueba."
    print(f"[*] Mensaje original: {mensaje_original.decode()}")

    # Emisor cifra el mensaje con la clave publica del receptor
    paquete = get_Msj_And_Key(mensaje_original, clave_publica_receptor)
    print("\n[*] Paquete cifrado generado:")
    print(f"    - mensajeCifrado_AES ({len(paquete['mensajeCifrado_AES'])} bytes): "
          f"{paquete['mensajeCifrado_AES'].hex()[:64]}...")
    print(f"    - iv_cifrado_RSA ({len(paquete['iv_cifrado_RSA'])} bytes): "
          f"{paquete['iv_cifrado_RSA'].hex()[:64]}...")
    print(f"    - clave_cifrada_RSA ({len(paquete['clave_cifrada_RSA'])} bytes): "
          f"{paquete['clave_cifrada_RSA'].hex()[:64]}...")

    # Receptor descifra con su clave privada
    mensaje_recuperado = decifrar_mensaje(
        paquete["mensajeCifrado_AES"],
        paquete["iv_cifrado_RSA"],
        paquete["clave_cifrada_RSA"],
        clave_privada_receptor,
    )
    print(f"\n[*] Mensaje descifrado: {mensaje_recuperado.decode()}")

    assert mensaje_recuperado == mensaje_original, "ERROR: el mensaje no coincide"
    print("\n[OK] El mensaje descifrado coincide exactamente con el original.")
