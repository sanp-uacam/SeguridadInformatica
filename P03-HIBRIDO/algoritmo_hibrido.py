"""
Práctica - Cifrado Híbrido RSA + AES-256
------------------------------------------
Idea general del esquema:

  1. Se genera un par de claves RSA (2048 bits) que representan al
     RECEPTOR del mensaje.
  2. Para cada mensaje se genera una clave AES-256 "de un solo uso"
     (clave de sesión) y un IV aleatorio de 16 bytes.
  3. El mensaje se cifra con AES-256 en modo CBC (con relleno PKCS7).
  4. La clave AES y el IV -que son pequeños- se cifran con la clave
     pública RSA usando el esquema OAEP.
  5. El receptor usa su clave privada RSA para recuperar la clave AES
     y el IV, y con eso descifra el mensaje original.

Por qué un esquema híbrido:
  RSA es seguro pero solo puede cifrar bloques de datos pequeños
  (limitados por el tamaño de la clave) y es mucho más lento que un
  cifrador simétrico. AES es rápido y puede cifrar mensajes de
  cualquier longitud. Combinando ambos se obtiene lo mejor de los dos:
  velocidad (AES) + facilidad de intercambio de claves sin canal
  secreto previo (RSA).

Nota sobre el IV:
  Un IV para AES-CBC debe medir exactamente el tamaño de bloque de
  AES, que es de 16 bytes (128 bits), sin importar el tamaño de la
  clave (128, 192 o 256 bits). Por eso aquí se usa un IV de 16 bytes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives import padding as relleno_simetrico
from cryptography.hazmat.primitives.asymmetric import padding as relleno_asimetrico
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# ---------------------------------------------------------------------------
# Parámetros del esquema
# ---------------------------------------------------------------------------
BITS_RSA = 2048          # Tamaño recomendado actual para RSA (>= 2048 bits)
BYTES_CLAVE_AES = 32     # 32 bytes = 256 bits -> AES-256
BYTES_IV = 16            # Tamaño de bloque de AES = 128 bits = 16 bytes


@dataclass
class PaqueteCifrado:
    """Todo lo que el emisor le manda al receptor por un canal inseguro."""
    mensaje_cifrado: bytes
    clave_sesion_cifrada: bytes
    iv_cifrado: bytes


# ---------------------------------------------------------------------------
# Generación de claves
# ---------------------------------------------------------------------------
def generar_par_de_claves_rsa() -> tuple[RSAPrivateKey, RSAPublicKey]:
    """Genera el par de claves RSA del receptor."""
    privada = rsa.generate_private_key(public_exponent=65537, key_size=BITS_RSA)
    publica = privada.public_key()
    return privada, publica


def generar_clave_de_sesion() -> bytes:
    """Clave AES-256 aleatoria, distinta para cada mensaje."""
    return os.urandom(BYTES_CLAVE_AES)


def generar_vector_inicializacion() -> bytes:
    """IV aleatorio de 16 bytes, requerido por AES-CBC."""
    return os.urandom(BYTES_IV)


# ---------------------------------------------------------------------------
# Capa simétrica (AES-256-CBC)
# ---------------------------------------------------------------------------
def cifrar_con_aes(texto_plano: bytes, clave: bytes, iv: bytes) -> bytes:
    rellenador = relleno_simetrico.PKCS7(algorithms.AES.block_size).padder()
    texto_con_relleno = rellenador.update(texto_plano) + rellenador.finalize()

    motor = Cipher(algorithms.AES(clave), modes.CBC(iv))
    cifrador = motor.encryptor()
    return cifrador.update(texto_con_relleno) + cifrador.finalize()


def descifrar_con_aes(texto_cifrado: bytes, clave: bytes, iv: bytes) -> bytes:
    motor = Cipher(algorithms.AES(clave), modes.CBC(iv))
    descifrador = motor.decryptor()
    texto_con_relleno = descifrador.update(texto_cifrado) + descifrador.finalize()

    quitador_relleno = relleno_simetrico.PKCS7(algorithms.AES.block_size).unpadder()
    return quitador_relleno.update(texto_con_relleno) + quitador_relleno.finalize()


# ---------------------------------------------------------------------------
# Capa asimétrica (RSA-OAEP), usada solo para envolver la clave y el IV
# ---------------------------------------------------------------------------
def _esquema_oaep() -> relleno_asimetrico.OAEP:
    return relleno_asimetrico.OAEP(
        mgf=relleno_asimetrico.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )


def envolver_con_rsa(datos: bytes, clave_publica: RSAPublicKey) -> bytes:
    return clave_publica.encrypt(datos, _esquema_oaep())


def desenvolver_con_rsa(datos_cifrados: bytes, clave_privada: RSAPrivateKey) -> bytes:
    return clave_privada.decrypt(datos_cifrados, _esquema_oaep())


# ---------------------------------------------------------------------------
# Flujo completo: emisor y receptor
# ---------------------------------------------------------------------------
def emisor_preparar_envio(mensaje: str, clave_publica_receptor: RSAPublicKey) -> PaqueteCifrado:
    """El emisor arma el paquete que se enviará por un canal no confiable."""
    clave_sesion = generar_clave_de_sesion()
    iv = generar_vector_inicializacion()

    mensaje_cifrado = cifrar_con_aes(mensaje.encode("utf-8"), clave_sesion, iv)
    clave_sesion_cifrada = envolver_con_rsa(clave_sesion, clave_publica_receptor)
    iv_cifrado = envolver_con_rsa(iv, clave_publica_receptor)

    return PaqueteCifrado(
        mensaje_cifrado=mensaje_cifrado,
        clave_sesion_cifrada=clave_sesion_cifrada,
        iv_cifrado=iv_cifrado,
    )


def receptor_recuperar_mensaje(paquete: PaqueteCifrado, clave_privada_receptor: RSAPrivateKey) -> str:
    """El receptor deshace el paquete y recupera el texto original."""
    clave_sesion = desenvolver_con_rsa(paquete.clave_sesion_cifrada, clave_privada_receptor)
    iv = desenvolver_con_rsa(paquete.iv_cifrado, clave_privada_receptor)
    mensaje_bytes = descifrar_con_aes(paquete.mensaje_cifrado, clave_sesion, iv)
    return mensaje_bytes.decode("utf-8")


# ---------------------------------------------------------------------------
# Demostración + pruebas automáticas
# ---------------------------------------------------------------------------
def _demo_basica() -> None:
    print("=" * 70)
    print("DEMOSTRACIÓN: cifrado y descifrado híbrido RSA + AES-256")
    print("=" * 70)

    privada, publica = generar_par_de_claves_rsa()
    mensaje_original = "Hola, este es un mensaje secreto con acentos: ñoño áéíóú 123."

    paquete = emisor_preparar_envio(mensaje_original, publica)
    mensaje_recuperado = receptor_recuperar_mensaje(paquete, privada)

    print(f"Mensaje original     : {mensaje_original}")
    print(f"Mensaje recuperado   : {mensaje_recuperado}")
    print(f"¿Coinciden?          : {mensaje_original == mensaje_recuperado}")
    print(f"Bytes cifrados (AES) : {len(paquete.mensaje_cifrado)} bytes")
    print(f"Clave AES cifrada    : {len(paquete.clave_sesion_cifrada)} bytes (con RSA-2048)")
    print(f"IV cifrado           : {len(paquete.iv_cifrado)} bytes (con RSA-2048)")


def _prueba(nombre: str, condicion: bool) -> None:
    estado = "OK " if condicion else "FALLÓ"
    print(f"[{estado}] {nombre}")


def _pruebas_automaticas() -> None:
    print()
    print("=" * 70)
    print("PRUEBAS AUTOMÁTICAS")
    print("=" * 70)

    privada, publica = generar_par_de_claves_rsa()

    # 1. Mensaje corto
    m1 = "Hi"
    p1 = emisor_preparar_envio(m1, publica)
    _prueba("Mensaje corto se recupera igual", receptor_recuperar_mensaje(p1, privada) == m1)

    # 2. Mensaje con espacios, acentos y símbolos
    m2 = "Contraseña: 123$%& - áéíóúñ ¿Todo bien?"
    p2 = emisor_preparar_envio(m2, publica)
    _prueba("Mensaje con acentos/símbolos se recupera igual", receptor_recuperar_mensaje(p2, privada) == m2)

    # 3. Mensaje largo
    m3 = "Lorem ipsum dolor sit amet. " * 200
    p3 = emisor_preparar_envio(m3, publica)
    _prueba("Mensaje largo se recupera igual", receptor_recuperar_mensaje(p3, privada) == m3)

    # 4. Cada ejecución genera datos distintos (misma clave pública, mismo mensaje)
    p4a = emisor_preparar_envio("mismo mensaje", publica)
    p4b = emisor_preparar_envio("mismo mensaje", publica)
    _prueba(
        "Dos cifrados del mismo mensaje son distintos entre sí",
        p4a.mensaje_cifrado != p4b.mensaje_cifrado
        and p4a.clave_sesion_cifrada != p4b.clave_sesion_cifrada,
    )

    # 5. Descifrar con una clave privada distinta debe fallar
    otra_privada, _ = generar_par_de_claves_rsa()
    p5 = emisor_preparar_envio("mensaje protegido", publica)
    fallo_esperado = False
    try:
        receptor_recuperar_mensaje(p5, otra_privada)
    except Exception:
        fallo_esperado = True
    _prueba("Descifrar con clave privada incorrecta falla", fallo_esperado)

    # 6. Alterar el texto cifrado debe romper el descifrado
    p6 = emisor_preparar_envio("mensaje intacto", publica)
    bytes_alterados = bytearray(p6.mensaje_cifrado)
    bytes_alterados[0] ^= 0xFF  # se cambia un solo bit/byte
    p6_alterado = PaqueteCifrado(
        mensaje_cifrado=bytes(bytes_alterados),
        clave_sesion_cifrada=p6.clave_sesion_cifrada,
        iv_cifrado=p6.iv_cifrado,
    )
    fallo_o_basura = False
    try:
        resultado = receptor_recuperar_mensaje(p6_alterado, privada)
        fallo_o_basura = resultado != "mensaje intacto"
    except Exception:
        fallo_o_basura = True
    _prueba("Alterar el ciphertext produce error o mensaje corrupto", fallo_o_basura)


if __name__ == "__main__":
    _demo_basica()
    _pruebas_automaticas()
