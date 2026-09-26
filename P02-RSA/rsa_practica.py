"""Practica RSA didactica con p=67, q=83 y los bloques dados en clase."""

from math import gcd

P = 67
Q = 83
CIPHERTEXT = (1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597)


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Devuelve (g, x, y), donde a*x + b*y = g = mcd(a,b)."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def modular_inverse(value: int, modulus: int) -> int:
    g, x, _ = extended_gcd(value, modulus)
    if g != 1:
        raise ValueError("El inverso modular no existe: los valores no son coprimos.")
    return x % modulus


def fourth_public_exponent(phi: int) -> tuple[int, list[tuple[int, int, bool]]]:
    """Busca el cuarto entero e, en orden ascendente, coprimo con phi."""
    candidates: list[tuple[int, int, bool]] = []
    valid_count = 0
    for e in range(2, phi):
        common_divisor = gcd(e, phi)
        valid = common_divisor == 1
        candidates.append((e, common_divisor, valid))
        if valid:
            valid_count += 1
            if valid_count == 4:
                return e, candidates
    raise ValueError("No se encontraron cuatro exponentes candidatos.")


def decrypt(ciphertext: tuple[int, ...], private_exponent: int, modulus: int) -> list[int]:
    return [pow(block, private_exponent, modulus) for block in ciphertext]


def solve() -> dict[str, object]:
    n = P * Q
    phi = (P - 1) * (Q - 1)
    e, candidates = fourth_public_exponent(phi)
    d = modular_inverse(e, phi)
    plaintext_values = decrypt(CIPHERTEXT, d, n)
    message = "".join(chr(value) for value in plaintext_values)
    return {"n": n, "phi": phi, "e": e, "d": d, "candidates": candidates,
            "plaintext_values": plaintext_values, "message": message}


def main() -> None:
    result = solve()
    print("PRACTICA 2 - ALGORITMO RSA")
    print(f"p = {P}; q = {Q}")
    print(f"n = {result['n']}")
    print(f"phi(n) = {result['phi']}")
    print("Candidatos e revisados (e, mcd, cumple):")
    for e, common_divisor, valid in result["candidates"]:
        print(f"  {e:>2}, {common_divisor:>2}, {'si' if valid else 'no'}")
    print(f"Clave publica: (e={result['e']}, n={result['n']})")
    print(f"Clave privada: (d={result['d']}, n={result['n']})")
    print(f"Valores descifrados: {result['plaintext_values']}")
    print(f"Mensaje: {result['message']}")


if __name__ == "__main__":
    main()
