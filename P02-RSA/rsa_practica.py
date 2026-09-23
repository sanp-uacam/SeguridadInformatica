from math import gcd
p, q = 67, 83
n = p * q
phi = (p - 1) * (q - 1)
candidatos = [i for i in range(2, phi) if gcd(i, phi) == 1]
e = candidatos[3]  # Cuarto candidato
d = pow(e, -1, phi)
cifrados = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]
descifrados = [pow(c, d, n) for c in cifrados]
mensaje = "".join(chr(m) for m in descifrados)
print("n =", n)
print("phi(n) =", phi)
print("Primeros candidatos de e =", candidatos[:4])
print("e =", e)
print("d =", d)
print("Comprobacion =", (e * d) % phi)
print("Clave publica =", (e, n))
print("Clave privada =", (d, n))
print("Bloques descifrados =", descifrados)
print("Mensaje =", mensaje)
