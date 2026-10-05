"""
Pruebas para el algoritmo hibrido de la practica 3

"""

from practica03_cifrado import (
    generar_par_claves_rsa,
    get_Msj_And_Key,
    decifrar_mensaje,
    Cifrado_AES_enviar_mensaje,
)
import os

resultados = []


def prueba(nombre, condicion):
    estado = "PASÓ" if condicion else "FALLÓ"
    resultados.append((nombre, condicion))
    print(f"[{estado}] {nombre}")


def main():
    print("=" * 70)
    print(" SUITE DE PRUEBAS - Algoritmo Híbrido RSA+AES")
    print("=" * 70)

    RSA_Privada, RSA_Publica = generar_par_claves_rsa()
    RSA_Privada2, RSA_Publica2 = generar_par_claves_rsa()  # par "de otro usuario"

    # 1) Round-trip básico
    msg = "Hola mundo"
    iv_c, msg_c = get_Msj_And_Key(msg, RSA_Publica)
    recuperado = decifrar_mensaje(msg_c, iv_c, RSA_Privada)
    prueba("Round-trip mensaje corto", recuperado == msg)

    # 2) Mensaje largo (varios bloques AES)
    msg_largo = "A" * 5000 + " fin del mensaje largo"
    iv_c, msg_c = get_Msj_And_Key(msg_largo, RSA_Publica)
    recuperado = decifrar_mensaje(msg_c, iv_c, RSA_Privada)
    prueba("Round-trip mensaje largo (5KB+)", recuperado == msg_largo)

    # 3) Mensaje vacío
    iv_c, msg_c = get_Msj_And_Key("", RSA_Publica)
    recuperado = decifrar_mensaje(msg_c, iv_c, RSA_Privada)
    prueba("Round-trip mensaje vacío", recuperado == "")

    # 4) Caracteres Unicode / acentos / emojis
    msg_unicode = "Contraseña: ñÑáéíóú 🔐🔑 中文测试"
    iv_c, msg_c = get_Msj_And_Key(msg_unicode, RSA_Publica)
    recuperado = decifrar_mensaje(msg_c, iv_c, RSA_Privada)
    prueba("Round-trip con Unicode/emojis", recuperado == msg_unicode)

    # 5) Cada cifrado usa clave AES e IV distintos (no determinismo)
    iv_c1, msg_c1 = get_Msj_And_Key("mismo mensaje", RSA_Publica)
    iv_c2, msg_c2 = get_Msj_And_Key("mismo mensaje", RSA_Publica)
    prueba("Dos cifrados del mismo mensaje son distintos (IV/clave aleatorios)",
           msg_c1 != msg_c2 and iv_c1 != iv_c2)

    # 6) La clave privada incorrecta NO debe poder descifrar
    iv_c, msg_c = get_Msj_And_Key("secreto", RSA_Publica)
    fallo_esperado = False
    try:
        decifrar_mensaje(msg_c, iv_c, RSA_Privada2)  # clave de "otro usuario"
    except (ValueError, TypeError):
        fallo_esperado = True
    prueba("Clave privada incorrecta no puede descifrar (lanza error)", fallo_esperado)

    # 7) Mensaje cifrado manipulado (bit-flipping) -> debe fallar el padding  o producir texto corrupto; demuestra la falta de integridad de CBC puro
    iv_c, msg_c = get_Msj_And_Key("mensaje integro", RSA_Publica)
    msg_c_manipulado = bytearray(msg_c)
    msg_c_manipulado[0] ^= 0xFF  # invierte el primer byte
    corrupcion_detectada = False
    try:
        resultado = decifrar_mensaje(bytes(msg_c_manipulado), iv_c, RSA_Privada)
        corrupcion_detectada = (resultado != "mensaje integro")
    except ValueError:
        corrupcion_detectada = True  # error de padding: también cuenta como detectado
    prueba("Manipulación del ciphertext altera/rompe el resultado", corrupcion_detectada)

    # 8) Función auxiliar Cifrado_AES_enviar_mensaje es determinista dado el mismo IV/clave
    clave_test = os.urandom(32)
    iv_test = os.urandom(16)
    c1 = Cifrado_AES_enviar_mensaje("Mensaje", iv_test, clave_test)
    c2 = Cifrado_AES_enviar_mensaje("Mensaje", iv_test, clave_test)
    prueba("Cifrado_AES_enviar_mensaje es determinista con mismo IV/clave", c1 == c2)

    print("\n" + "=" * 70)
    total = len(resultados)
    exitosas = sum(1 for _, ok in resultados if ok)
    print(f" RESULTADO: {exitosas}/{total} pruebas pasaron")
    print("=" * 70)

    if exitosas != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
