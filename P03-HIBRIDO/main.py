"""Demostración visible del cifrado híbrido (solo con fines educativos)."""

from utils import (
    decifrar_mensaje,
    generar_claves_rsa,
    get_Msj_And_Key,
    serializar_claves_rsa,
)


if __name__ == "__main__":
    RSA_Publica, RSA_Privada = generar_claves_rsa()
    publica_pem, _privada_pem = serializar_claves_rsa(RSA_Publica, RSA_Privada)

    print("\n=== CLAVE PÚBLICA RSA CREADA ===")
    print(publica_pem)
    print("=== CLAVE PRIVADA RSA CREADA ===")
    print("********************...")

    iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(RSA_Publica)

    print("\n=== CLAVE AES + IV CIFRADOS CON RSA (hexadecimal) ===")
    print(iv_cifrado_RSA.hex())
    print("\n=== MENSAJE CIFRADO CON AES + HMAC (hexadecimal) ===")
    print(mensajeCifrado_AES.hex())

    mensaje = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)
    print("\n=== MENSAJE DESCIFRADO ===")
    print(mensaje)
