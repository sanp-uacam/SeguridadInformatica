import math

p = 67
q = 83
n = p * q

phi_n = (p - 1) * (q - 1)

print(f"p = {p}, q = {q}")
print(f"n = p * q = {n}")
print(f"φ(n) = (p - 1) * (q - 1) = {phi_n}\n")
candidatos_e = []

for candidato in range(2, phi_n):
    if math.gcd(candidato, phi_n) == 1:
        candidatos_e.append(candidato)
    if len(candidatos_e) == 4:
        break

e = candidatos_e[3] 

print(f"Primeros 4 candidatos encontrados con mcd(e, φ(n)) = 1: {candidatos_e}")
print(f"Clave pública seleccionada (4to candidato): e = {e}\n")

d = pow(e, -1, phi_n)

print(f"Clave privada calculada: d = {d}")
print(f"Comprobación (e * d) % φ(n): {(e * d) % phi_n}\n")

cifrado = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]
mensaje_descifrado = []

for c in cifrado:
    m = pow(c, d, n)
    letra = chr(m)
    mensaje_descifrado.append(letra)
    print(f"Cifrado: {c:4} -> ASCII: {m:3} -> Carácter: '{letra}'")

texto_final = "".join(mensaje_descifrado)
print(f"\nMensaje completo descifrado: \"{texto_final}\"")