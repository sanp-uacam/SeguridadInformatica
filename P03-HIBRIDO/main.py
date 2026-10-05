"""Demostracion ejecutable de la practica."""

import argparse
import base64

from cifrado_hibrido import decifrar_mensaje, generar_claves_rsa, get_Msj_And_Key


def main() -> None:
    parser = argparse.ArgumentParser(description="Demostracion RSA + AES-256-CBC")
    parser.add_argument("mensaje", nargs="?", default="Mensaje confidencial de prueba")
    args = parser.parse_args()

    claves = generar_claves_rsa()
    sobre, cifrado = get_Msj_And_Key(claves.publica_pem, args.mensaje)
    recuperado = decifrar_mensaje(cifrado, sobre, claves.privada_pem)

    print("Sobre RSA (Base64):", base64.b64encode(sobre).decode("ascii"))
    print("Mensaje AES (Base64):", base64.b64encode(cifrado).decode("ascii"))
    print("Mensaje recuperado:", recuperado)


if __name__ == "__main__":
    main()

