"""RSA didáctico: valores pequeños impuestos por la práctica 02."""
from math import gcd

P, Q = 67, 83
CIFRADO = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]


def euclides_extendido(a, b):
    """Devuelve mcd, x, y tales que a*x + b*y = mcd."""
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b:
        cociente = a // b
        a, b = b, a % b
        x0, x1 = x1, x0 - cociente * x1
        y0, y1 = y1, y0 - cociente * y1
    return a, x0, y0


def resolver():
    n = P * Q
    phi = (P - 1) * (Q - 1)
    candidatos, intentos = [], []
    for valor in range(2, phi):
        divisor = gcd(valor, phi)
        intentos.append((valor, divisor))
        if divisor == 1:
            candidatos.append(valor)
            if len(candidatos) == 4:
                break
    e = candidatos[3]
    divisor, x, y = euclides_extendido(e, phi)
    if divisor != 1:
        raise ValueError("No existe inverso modular.")
    d = x % phi
    numeros = [pow(c, d, n) for c in CIFRADO]
    mensaje = "".join(chr(numero) for numero in numeros)
    recifrado = [pow(numero, e, n) for numero in numeros]
    return dict(n=n, phi=phi, intentos=intentos, candidatos=candidatos,
                e=e, d=d, x=x, y=y, numeros=numeros, mensaje=mensaje,
                recifrado=recifrado)
