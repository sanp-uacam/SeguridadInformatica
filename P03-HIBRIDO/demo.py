"""Demostracion de cifrado y recuperacion del mensaje de ejemplo."""

from rsa_aes_hybrid import decifrar_mensaje, generar_par_claves_rsa, get_Msj_And_Key


def main() -> None:
    original = "Mensaje de prueba para el algoritmo hibrido RSA-AES"
    clave_privada, clave_publica = generar_par_claves_rsa()
    iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(clave_publica, original)
    recuperado = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, clave_privada)
    print("Practica de cifrado hibrido RSA-AES")
    print(f"Mensaje original: {original}")
    print(f"Tamano del paquete RSA: {len(iv_cifrado_RSA)} bytes")
    print(f"Tamano del mensaje cifrado: {len(mensajeCifrado_AES)} bytes")
    print(f"Mensaje recuperado: {recuperado}")
    print(f"Resultado: {'CORRECTO' if recuperado == original else 'ERROR'}")


if __name__ == "__main__":
    main()
