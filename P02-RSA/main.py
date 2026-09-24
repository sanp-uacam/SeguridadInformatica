"""Ejecutar: python main.py"""
from utils.rsa import CIFRADO, P, Q, resolver


def main():
    r = resolver()
    print("PRACTICA 02 - RSA | Alfredo J Cruz Miss")
    print(f"1. n = {P} * {Q} = {r['n']}")
    print(f"2. phi(n) = ({P}-1) * ({Q}-1) = {r['phi']}")
    print("3. Candidatos en orden ascendente desde 2:")
    for valor, divisor in r['intentos']:
        print(f"   e={valor:2d}, mcd={divisor:2d}: "
              + ("valido" if divisor == 1 else "descartado"))
    print(f"   Validos: {r['candidatos']}; cuarto: e={r['e']}")
    print(f"4. Euclides: {r['e']}*({r['x']}) + {r['phi']}*({r['y']}) = 1")
    print(f"   d = {r['x']} mod {r['phi']} = {r['d']}")
    print(f"   e*d mod phi(n) = {(r['e'] * r['d']) % r['phi']}")
    print(f"   Clave publica (e,n): ({r['e']}, {r['n']})")
    print(f"   Clave privada (d,n): ({r['d']}, {r['n']})")
    print("5. Descifrado: m = c^d mod n; interpretacion ASCII")
    for c, numero in zip(CIFRADO, r['numeros']):
        print(f"   {c:4d} -> {numero:3d} -> {chr(numero)!r}")
    print(f"   Mensaje: {r['mensaje']}")
    print(f"6. Recifrado: {r['recifrado']}")
    print(f"   Coincide con el original: {r['recifrado'] == CIFRADO}")


if __name__ == "__main__":
    main()
