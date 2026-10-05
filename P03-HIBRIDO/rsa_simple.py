# RSA de la Practica 2 - Angel Antonio Perez Reyes
# Adaptado como modulo para el algoritmo hibrido


def mcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def euclides_extendido(a, b):
    """Devuelve (mcd, x, y) tal que a*x + b*y = mcd."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = euclides_extendido(b, a % b)
    return g, y1, x1 - (a // b) * y1


def generar_llaves(p=67, q=83, num_candidato=4):
    """Genera el par de llaves RSA igual que en la practica 2.

    Con p=67 y q=83 -> n=5561, e=17, d=4457
    """
    n = p * q
    phi = (p - 1) * (q - 1)

    contador = 0
    numero = 2
    e = 0
    while contador < num_candidato:
        if mcd(numero, phi) == 1:
            contador += 1
            e = numero
        numero += 1

    g, x, y = euclides_extendido(e, phi)
    d = x % phi

    return (e, n), (d, n)


def cifrar_bytes(datos, publica):
    """Cifra una secuencia de bytes con RSA, byte por byte.

    Solo funciona si n > 255. Con n=5561 se cumple.
    Devuelve una lista de enteros.
    """
    e, n = publica
    if n <= 255:
        raise ValueError("n debe ser mayor a 255 para cifrar bytes")
    return [pow(b, e, n) for b in datos]


def descifrar_bytes(cifrado, privada):
    """Operacion inversa de cifrar_bytes. Devuelve bytes."""
    d, n = privada
    return bytes(pow(c, d, n) for c in cifrado)
