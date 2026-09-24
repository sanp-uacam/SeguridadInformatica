"""Demostración: python main.py --mensaje \"Hola mundo\""""
import argparse
from base64 import b64encode
from utils.hibrido import generar_claves, get_Msj_And_Key, decifrar_mensaje


def main():
    parser = argparse.ArgumentParser(description='Práctica 03: cifrado híbrido RSA y AES')
    parser.add_argument('--mensaje', help='Texto; si se omite, se pide por consola.')
    args = parser.parse_args()
    mensaje = args.mensaje if args.mensaje is not None else input('Mensaje a cifrar: ')
    publica, privada = generar_claves()
    sobre, cifrado = get_Msj_And_Key(publica, mensaje)
    recuperado = decifrar_mensaje(cifrado, sobre, privada)
    print('PRACTICA 03 - HIBRIDO | Alfredo J Cruz Miss')
    print('RSA: 2048 bits, OAEP con SHA-256')
    print('AES: clave de 32 bytes, CBC, IV de 16 bytes, relleno PKCS#7')
    print('Sobre RSA: clave AES (32 bytes) + IV (16 bytes)')
    print('iv_cifrado_RSA (Base64):', b64encode(sobre).decode('ascii'))
    print('mensajeCifrado_AES (Base64):', b64encode(cifrado).decode('ascii'))
    print('Mensaje original:', mensaje)
    print('Mensaje recuperado:', recuperado)
    print('Verificacion:', 'CORRECTA' if mensaje == recuperado else 'FALLO')


if __name__ == '__main__':
    main()
