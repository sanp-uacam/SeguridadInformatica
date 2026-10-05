# Demostracion del algoritmo hibrido.
#   python demo.py "mensaje"   -> usa ese mensaje
#   python demo.py             -> lo pide por teclado

import sys

from hibrido_rsa_aes import decifrar_mensaje, generar_par_llaves, get_Msj_And_Key


def mostrar(nombre, datos):
    # se recorta el hexadecimal para que no llene la pantalla
    hexa = datos.hex()
    if len(hexa) > 96:
        hexa = hexa[:96] + "..."
    print("   ", nombre, ":", hexa, "(" + str(len(datos)), "bytes)")


mensaje = sys.argv[1] if len(sys.argv) > 1 else None

print("--- ALGORITMO HIBRIDO RSA-AES ---")

# el receptor crea sus llaves y publica la publica
print("\n1) El receptor genera sus llaves RSA de 2048 bits")
RSA_Privada, RSA_Publica = generar_par_llaves()

# el emisor cifra usando nada mas la clave publica
print("\n2) El emisor cifra con get_Msj_And_Key(RSA_Publica)")
iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(RSA_Publica, mensaje)
mostrar("iv_cifrado_RSA    ", iv_cifrado_RSA)
mostrar("mensajeCifrado_AES", mensajeCifrado_AES)

print("\n3) Eso es lo unico que viaja por el canal, sin la clave privada no se lee")

print("\n4) El receptor lo descifra con decifrar_mensaje()")
recuperado = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)
print("    Mensaje recuperado:", recuperado)
