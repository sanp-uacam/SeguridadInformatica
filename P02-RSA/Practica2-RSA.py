import math

p, q = 67, 83
n = p * q
phi = (p - 1) * (q - 1)

# Buscar candidatos de e
candidatos = []
e = 2
while len(candidatos) < 4:
    if math.gcd(e, phi) == 1:
        candidatos.append(e)
    e += 1
e = candidatos[3]  # el 4to candidato

# Extended Euclid para hallar d
def ext_gcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = ext_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

_, x, _ = ext_gcd(e, phi)
d = x % phi

# Descifrar
cifrado = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]
descifrado = [pow(c, d, n) for c in cifrado]
mensaje = ''.join(chr(m) for m in descifrado)

print("n =", n, "| phi =", phi, "| e =", e, "| d =", d)
print("Numeros descifrados :", descifrado)
print("Mensaje :", mensaje)