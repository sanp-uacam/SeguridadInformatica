"""Práctica 2: cálculo y descifrado RSA con los datos del enunciado."""

from math import gcd

P, Q = 67, 83
CIFRADO = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]


def euclides_extendido(a, b):
    """Devuelve mcd, x, y y pasos, tales que a*x + b*y = mcd."""
    r0, r1, x0, x1, y0, y1 = a, b, 1, 0, 0, 1
    pasos = []
    while r1:
        cociente, resto = divmod(r0, r1)
        pasos.append((r0, cociente, r1, resto))
        r0, r1 = r1, resto
        x0, x1 = x1, x0 - cociente * x1
        y0, y1 = y1, y0 - cociente * y1
    return r0, x0, y0, pasos


def main():
    n = P * Q
    phi = (P - 1) * (Q - 1)
    print('PRACTICA 2 - RSA')
    print(f'p = {P}; q = {Q}')
    print(f'1. n = {P} * {Q} = {n}')
    print(f'2. phi(n) = {P - 1} * {Q - 1} = {phi}')
    print('\n3. Candidatos en orden ascendente desde 2:')
    candidatos = []
    for valor in range(2, phi):
        divisor = gcd(valor, phi)
        if divisor == 1:
            candidatos.append(valor)
        estado = f'candidato valido #{len(candidatos)}' if divisor == 1 else 'descartado'
        print(f'e = {valor:2}; mcd({valor:2}, {phi}) = {divisor:2}; {estado}')
        if len(candidatos) == 4:
            break
    e = candidatos[3]
    print(f'Cuarto candidato: e = {e}')
    divisor, x, y, pasos = euclides_extendido(e, phi)
    assert divisor == 1
    d = x % phi
    print('\n4. Euclides extendido e inverso modular:')
    for a, cociente, b, resto in pasos:
        print(f'{a} = {cociente} * {b} + {resto}')
    print(f'Bezout: {e} * ({x}) + {phi} * ({y}) = 1')
    print(f'd = {x} mod {phi} = {d}')
    print(f'Comprobacion: {e} * {d} = {e*d} = {(e*d-1)//phi} * {phi} + 1')
    print(f'Clave publica (e, n): ({e}, {n})')
    print(f'Clave privada (d, n): ({d}, {n})')
    print('\n5. Descifrado: m = c^d mod n; interpretacion ASCII')
    mensaje = []
    for c in CIFRADO:
        m = pow(c, d, n)
        caracter = chr(m)
        mensaje.append(caracter)
        print(f'{c:4}^{d} mod {n} = {m:2} -> {caracter!r}')
        assert pow(m, e, n) == c, 'El recifrado debe reproducir cada bloque'
    texto = ''.join(mensaje)
    assert candidatos == [5, 7, 13, 17]
    assert (n, phi, e, d) == (5561, 5412, 17, 4457)
    assert texto == 'HOLA MUNDO'
    print(f'\nMensaje: {texto}')
    print('Verificacion: los 10 bloques recifrados coinciden con el enunciado.')


if __name__ == '__main__':
    main()
