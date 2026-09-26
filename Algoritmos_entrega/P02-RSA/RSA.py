from math import gcd

# Datos iniciales
p = 67
q = 83

print("===== ALGORITMO RSA =====")

# Paso 1: calcular n
n = p * q

print("\nPASO 1")
print("p =", p)
print("q =", q)
print("n = p * q")
print("n =", n)

# Paso 2: calcular phi(n)
phi = (p - 1) * (q - 1)

print("\nPASO 2")
print("phi(n) = (p - 1) * (q - 1)")
print("phi(n) =", phi)

# Paso 3: encontrar el cuarto candidato válido para e
print("\nPASO 3")
print("Buscando candidatos para e...")

candidatos = []

for numero in range(2, phi):

    mcd = gcd(numero, phi)

    print(
        "e =", numero,
        "| MCD(", numero, ",", phi, ") =", mcd
    )

    if mcd == 1:
        candidatos.append(numero)

        print(
            ">>> Candidato válido número",
            len(candidatos),
            ":", numero
        )

    if len(candidatos) == 4:
        break

e = candidatos[3]

print("\nLos cuatro candidatos son:")
print(candidatos)

print("\ne elegido =", e)

# Paso 4: encontrar d
print("\nPASO 4")

d = pow(e, -1, phi)

print("d =", d)
print(
    "Comprobación:",
    e,
    "*",
    d,
    "mod",
    phi,
    "=",
    (e * d) % phi
)

print("\nClave pública:")
print("(e, n) =", (e, n))

print("\nClave privada:")
print("(d, n) =", (d, n))

# Paso 5: mensaje cifrado
mensaje_cifrado = [
    1058,
    2597,
    4955,
    4201,
    3162,
    4343,
    2754,
    2497,
    336,
    2597
]

print("\nPASO 5")
print("Descifrando mensaje...")

mensaje = ""

for c in mensaje_cifrado:

    # Fórmula RSA
    m = pow(c, d, n)

    # Convertir resultado ASCII a letra
    caracter = chr(m)

    print(
        "C =", c,
        "->",
        "M =", m,
        "->",
        repr(caracter)
    )

    mensaje += caracter

print("\n======================")
print("MENSAJE DESCIFRADO:")
print(mensaje)
print("======================")