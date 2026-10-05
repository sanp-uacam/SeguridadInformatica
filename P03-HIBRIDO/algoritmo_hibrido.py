"""
=============================================================================
 Seguridad Informatica - Practica 3: Algoritmo Hibrido RSA + AES
 Universidad Autonoma de Campeche - Facultad de Ingenieria

 Alumno: Kerin Del Jesus Gonzalez Maas
 Grado: 7   Grupo: "A"
 Maestro: Sergio A. Noh Puch
=============================================================================

 QUE ES UN CIFRADO HIBRIDO
 -------------------------
 RSA es lento y solo puede cifrar mensajes mas pequenos que su modulo, por lo
 que no sirve para cifrar archivos o textos largos. AES es muy rapido y maneja
 cualquier tamano, pero necesita que emisor y receptor compartan la misma clave
 secreta, y transmitir esa clave por un canal inseguro es justo el problema.

 La solucion hibrida combina lo mejor de ambos:
   - El MENSAJE se cifra con AES  (rapido, sin limite de tamano).
   - La CLAVE AES se cifra con RSA (resuelve el intercambio de la clave).

 Es exactamente el esquema que usan TLS/HTTPS, PGP y la mensajeria cifrada.

 -----------------------
 
"""

from __future__ import annotations

import base64
import json
import os
import secrets
from dataclasses import dataclass, asdict

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption,
    load_pem_private_key, load_pem_public_key,
)

# ---------------------------------------------------------------------------
# PARAMETROS DE DISENO (justificados en la documentacion)
# ---------------------------------------------------------------------------
TAM_CLAVE_AES = 32      # 32 bytes = 256 bits  -> AES-256
TAM_BLOQUE_AES = 16     # 16 bytes = 128 bits  -> tamano de bloque e IV en CBC
TAM_CLAVE_RSA = 2048    # bits; minimo recomendado por NIST hasta 2030
EXPONENTE_RSA = 65537   # exponente publico estandar (F4)


# ===========================================================================
#  PADDING PKCS#7  (implementado a mano para mostrar como funciona)
# ===========================================================================
def aplicar_padding(datos: bytes) -> bytes:
    """
    AES-CBC solo cifra bloques completos de 16 bytes. PKCS#7 rellena el
    ultimo bloque repitiendo el numero de bytes que faltan.

    Ejemplo: si faltan 3 bytes se agrega  \\x03\\x03\\x03
    Si el mensaje ya es multiplo de 16 se agrega un bloque entero de 16
    bytes con valor \\x10, para que el relleno siempre sea reversible.
    """
    faltan = TAM_BLOQUE_AES - (len(datos) % TAM_BLOQUE_AES)
    return datos + bytes([faltan]) * faltan


def quitar_padding(datos: bytes) -> bytes:
    """Elimina el relleno PKCS#7 validando que sea coherente."""
    if not datos or len(datos) % TAM_BLOQUE_AES != 0:
        raise ValueError("Los datos cifrados no son multiplo del tamano de bloque.")

    n = datos[-1]
    if n < 1 or n > TAM_BLOQUE_AES:
        raise ValueError("Padding PKCS#7 invalido: longitud fuera de rango.")
    if datos[-n:] != bytes([n]) * n:
        raise ValueError("Padding PKCS#7 invalido: bytes de relleno inconsistentes.")
    return datos[:-n]


# ===========================================================================
#  CLAVES RSA
# ===========================================================================
def generar_par_rsa(bits: int = TAM_CLAVE_RSA):
    """Genera el par de claves RSA del receptor."""
    privada = rsa.generate_private_key(public_exponent=EXPONENTE_RSA, key_size=bits)
    return privada.public_key(), privada


def guardar_claves(publica, privada, carpeta: str = ".") -> None:
    """Exporta las claves a archivos .pem (formato estandar)."""
    with open(os.path.join(carpeta, "clave_publica.pem"), "wb") as f:
        f.write(publica.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
    with open(os.path.join(carpeta, "clave_privada.pem"), "wb") as f:
        f.write(privada.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))


def cargar_clave_publica(ruta: str):
    with open(ruta, "rb") as f:
        return load_pem_public_key(f.read())


def cargar_clave_privada(ruta: str):
    with open(ruta, "rb") as f:
        return load_pem_private_key(f.read(), password=None)


def _cifrar_rsa(datos: bytes, clave_publica) -> bytes:
    """
    Cifra con RSA usando relleno OAEP.
    OAEP agrega aleatoriedad al mensaje antes de cifrarlo, de modo que cifrar
    dos veces el mismo dato produce resultados distintos. Sin OAEP (RSA "en
    crudo") el cifrado seria determinista y un atacante podria reconocer
    valores repetidos.
    """
    return clave_publica.encrypt(
        datos,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def _descifrar_rsa(datos: bytes, clave_privada) -> bytes:
    return clave_privada.decrypt(
        datos,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


# ===========================================================================
#  PAQUETE CIFRADO
# ===========================================================================
@dataclass
class PaqueteCifrado:
    """
    Representa lo que viaja por el canal inseguro. Se codifica en Base64 para
    poder transmitirlo como texto (JSON, correo, etc.) sin corromper los bytes.
    """
    iv_cifrado_RSA: str
    clave_AES_cifrada_RSA: str
    mensajeCifrado_AES: str

    def a_json(self, indentado: bool = True) -> str:
        return json.dumps(asdict(self), indent=2 if indentado else None)

    @staticmethod
    def desde_json(texto: str) -> "PaqueteCifrado":
        return PaqueteCifrado(**json.loads(texto))

    def tamanos(self) -> dict:
        """Tamano real en bytes de cada componente (util para las pruebas)."""
        return {
            "iv_cifrado_RSA": len(base64.b64decode(self.iv_cifrado_RSA)),
            "clave_AES_cifrada_RSA": len(base64.b64decode(self.clave_AES_cifrada_RSA)),
            "mensajeCifrado_AES": len(base64.b64decode(self.mensajeCifrado_AES)),
        }


# ===========================================================================
#  FUNCION c) DEL ENUNCIADO
# ===========================================================================
def Cifrado_AES_enviar_mensaje(mensaje, iv: bytes, clave_aes: bytes) -> bytes:
    """
    Cifra un mensaje con AES-256 en modo CBC usando el IV proporcionado.

    Modo CBC: cada bloque se combina con XOR contra el bloque cifrado anterior
    antes de cifrarse. El primer bloque usa el IV como "bloque anterior". Gracias
    a esto, dos bloques de texto plano identicos producen cifrados distintos,
    a diferencia del modo ECB.
    """
    if len(iv) != TAM_BLOQUE_AES:
        raise ValueError(
            f"El IV de AES-CBC debe medir {TAM_BLOQUE_AES} bytes, se recibieron {len(iv)}."
        )
    if len(clave_aes) != TAM_CLAVE_AES:
        raise ValueError(
            f"La clave AES-256 debe medir {TAM_CLAVE_AES} bytes, se recibieron {len(clave_aes)}."
        )

    if isinstance(mensaje, str):
        mensaje = mensaje.encode("utf-8")

    bloques = aplicar_padding(mensaje)
    cifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv)).encryptor()
    return cifrador.update(bloques) + cifrador.finalize()


def Descifrado_AES_recibir_mensaje(cifrado: bytes, iv: bytes, clave_aes: bytes) -> bytes:
    """Operacion inversa de Cifrado_AES_enviar_mensaje."""
    descifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv)).decryptor()
    bloques = descifrador.update(cifrado) + descifrador.finalize()
    return quitar_padding(bloques)


# ===========================================================================
#  FUNCION a) DEL ENUNCIADO
# ===========================================================================
def get_Msj_And_Key(RSA_Publica, mensaje: str) -> PaqueteCifrado:
    """
    Lado EMISOR. Recibe la clave publica RSA del receptor y el mensaje.

    Proceso:
      1. Genera una clave AES aleatoria de 32 bytes (clave de sesion).
      2. Genera un IV aleatorio de 16 bytes.
      3. Cifra el mensaje con AES-256-CBC.
      4. Cifra la clave AES con RSA-OAEP.
      5. Cifra el IV con RSA-OAEP.

    Devuelve el paquete listo para enviarse por el canal inseguro.
    """
    # secrets usa el generador criptografico del sistema operativo,
    # a diferencia de random que es predecible y no sirve para claves.
    clave_aes = secrets.token_bytes(TAM_CLAVE_AES)
    iv = secrets.token_bytes(TAM_BLOQUE_AES)

    mensaje_cifrado = Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)
    clave_cifrada = _cifrar_rsa(clave_aes, RSA_Publica)
    iv_cifrado = _cifrar_rsa(iv, RSA_Publica)

    return PaqueteCifrado(
        iv_cifrado_RSA=base64.b64encode(iv_cifrado).decode("ascii"),
        clave_AES_cifrada_RSA=base64.b64encode(clave_cifrada).decode("ascii"),
        mensajeCifrado_AES=base64.b64encode(mensaje_cifrado).decode("ascii"),
    )


# ===========================================================================
#  FUNCION b) DEL ENUNCIADO
# ===========================================================================
def decifrar_mensaje(mensajeCifrado_AES: str, iv_cifrado_RSA: str,
                     clave_AES_cifrada_RSA: str, RSA_Privada) -> str:
    """
    Lado RECEPTOR.

    Proceso:
      1. Descifra el IV con RSA usando la clave privada.
      2. Descifra la clave AES con RSA usando la clave privada.
      3. Descifra el mensaje con AES-CBC y retira el padding.
    """
    iv = _descifrar_rsa(base64.b64decode(iv_cifrado_RSA), RSA_Privada)
    clave_aes = _descifrar_rsa(base64.b64decode(clave_AES_cifrada_RSA), RSA_Privada)

    # Validacion defensiva: si los tamanos no cuadran, algo se manipulo.
    if len(iv) != TAM_BLOQUE_AES:
        raise ValueError("El IV recuperado no mide 16 bytes.")
    if len(clave_aes) != TAM_CLAVE_AES:
        raise ValueError("La clave AES recuperada no mide 32 bytes.")

    cifrado = base64.b64decode(mensajeCifrado_AES)
    if len(cifrado) % TAM_BLOQUE_AES != 0:
        raise ValueError("El criptograma AES esta truncado o corrupto.")

    claro = Descifrado_AES_recibir_mensaje(cifrado, iv, clave_aes)
    return claro.decode("utf-8")


# ===========================================================================
#  DEMOSTRACION INTERACTIVA
# ===========================================================================
def _linea(titulo: str = "") -> None:
    print("\n" + "=" * 68)
    if titulo:
        print(f" {titulo}")
        print("=" * 68)


def demostracion(mensaje: str) -> None:
    """Ejecuta el ciclo completo mostrando cada etapa."""
    _linea("ALGORITMO HIBRIDO RSA + AES")

    print("\n[ETAPA 0] Generando par de claves RSA del receptor...")
    publica, privada = generar_par_rsa()
    guardar_claves(publica, privada)
    print(f"  Par RSA de {TAM_CLAVE_RSA} bits generado.")
    print("  Guardado en: clave_publica.pem / clave_privada.pem")

    print("\n[ETAPA 1] Mensaje original (texto plano):")
    print(f"  {mensaje!r}")
    print(f"  Longitud: {len(mensaje.encode('utf-8'))} bytes")

    print("\n[ETAPA 2] EMISOR - get_Msj_And_Key()")
    paquete = get_Msj_And_Key(publica, mensaje)
    tam = paquete.tamanos()
    print(f"  Clave AES de {TAM_CLAVE_AES} bytes generada aleatoriamente.")
    print(f"  IV de {TAM_BLOQUE_AES} bytes generado aleatoriamente.")
    print(f"  Mensaje cifrado con AES-256-CBC  -> {tam['mensajeCifrado_AES']} bytes")
    print(f"  Clave AES cifrada con RSA-OAEP   -> {tam['clave_AES_cifrada_RSA']} bytes")
    print(f"  IV cifrado con RSA-OAEP          -> {tam['iv_cifrado_RSA']} bytes")

    print("\n[ETAPA 3] Paquete que viaja por el canal inseguro:")
    for campo, valor in asdict(paquete).items():
        recorte = valor if len(valor) <= 64 else valor[:61] + "..."
        print(f"  {campo}:\n    {recorte}")

    with open("paquete_cifrado.json", "w", encoding="utf-8") as f:
        f.write(paquete.a_json())
    print("\n  Paquete guardado en: paquete_cifrado.json")

    print("\n[ETAPA 4] RECEPTOR - decifrar_mensaje()")
    recuperado = decifrar_mensaje(
        paquete.mensajeCifrado_AES,
        paquete.iv_cifrado_RSA,
        paquete.clave_AES_cifrada_RSA,
        privada,
    )
    print(f"  Mensaje recuperado: {recuperado!r}")

    _linea()
    if recuperado == mensaje:
        print(" RESULTADO: CORRECTO - el mensaje recuperado es identico al original.")
    else:
        print(" RESULTADO: ERROR - los mensajes no coinciden.")
    print("=" * 68)


def main() -> None:
    print("=" * 68)
    print(" PRACTICA 3 - ALGORITMO HIBRIDO RSA + AES")
    print(" Seguridad Informatica - Facultad de Ingenieria, UACAM")
    print("=" * 68)
    print("\n [1] Ejecutar demostracion con mensaje de ejemplo")
    print(" [2] Ejecutar demostracion con mi propio mensaje")
    print(" [3] Salir")

    try:
        opcion = input("\n Opcion: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n Cancelado.")
        return

    if opcion == "1":
        demostracion("Mensaje secreto de la Practica 3: RSA + AES, "
                     "con acentos (áéíóú), ñ y simbolos @#$%.")
    elif opcion == "2":
        texto = input(" Escribe el mensaje a cifrar: ")
        if not texto:
            print(" No se escribio ningun mensaje.")
            return
        demostracion(texto)
    elif opcion == "3":
        print(" Hasta luego.")
    else:
        print(" Opcion no valida.")


if __name__ == "__main__":
    main()
