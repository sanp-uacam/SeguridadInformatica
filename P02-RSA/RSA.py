"""
Practica 2 - Algoritmo RSA

"""

import math

# ---------- Datos de entrada ----------
p = 67
q = 83

# ---------- Paso 1: Calcular n ----------
n = p * q
print(f"Paso 1: n = p * q = {p} * {q} = {n}")

# ---------- Paso 2: Calcular phi(n) ----------
phi = (p - 1) * (q - 1)
print(f"Paso 2: phi(n) = (p-1)*(q-1) = {p-1} * {q-1} = {phi}")

# ---------- Paso 3: Elegir e (el 4to candidato valido) ----------
candidatos = []
e_actual = 2
while len(candidatos) < 4:
    if math.gcd(e_actual, phi) == 1:
        candidatos.append(e_actual)
    e_actual += 1

print(f"Paso 3: candidatos validos encontrados (en orden): {candidatos}")
e = candidatos[3]  # el cuarto candidato (indice 3)
print(f"         e elegido = 4to candidato = {e}")

# ---------- Paso 4: Calcular d (inverso multiplicativo de e mod phi(n)) ----------
d = pow(e, -1, phi)
print(f"Paso 4: d (inverso de e mod phi(n)) = {d}")
print(f"         Comprobacion: (e * d) mod phi(n) = {(e * d) % phi} (debe ser 1)")

# ---------- Paso 5: Descifrar el mensaje ----------
mensaje_cifrado = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]

print("\nPaso 5: Descifrando mensaje...")
numeros_descifrados = []
for c in mensaje_cifrado:
    m = pow(c, d, n)  # exponenciacion modular rapida integrada en Python
    numeros_descifrados.append(m)
    print(f"  {c}^{d} mod {n} = {m}  -> caracter: '{chr(m)}'")

texto = "".join(chr(num) for num in numeros_descifrados)
print(f"\nMensaje descifrado: {texto}")

# ---------- Resumen de claves ----------
print("\nResultados finales:")
print(f"Clave publica:  (e={e}, n={n})")
print(f"Clave privada:  (d={d}, n={n})")
print(f"Mensaje descifrado: {texto}")