from math import gcd

# Datos
p = 67
q = 83
e = 17  # Cuarto candidato

# Calcular n
n = p * q

# Calcular φ(n)
phi_n = (p - 1) * (q - 1)

print("="*50)
print(f"p = {p}")
print(f"q = {q}")
print(f"n = p × q = {p} × {q} = {n}")
print(f"φ(n) = (p-1)(q-1) = {p-1} × {q-1} = {phi_n}")
print("="*50)

# Validar que e y φ(n) sean coprimos
if gcd(e, phi_n) != 1:
    print(f"Error: e={e} y φ(n)={phi_n} no son coprimos")
    exit()

print(f"e = {e}")

# Buscar d donde (e * d) mod φ(n) = 1
d = None
for i in range(1, phi_n):
    if (e * i) % phi_n == 1:
        d = i
        break

if d is None:
    print("No se encontró d")
    exit()

print(f"d = {d}")
print("\n" + "="*50)
print("CLAVE PUBLICA")
print(f"(e, n) = ({e}, {n})")
print("="*50)
print("CLAVE PRIVADA")
print(f"(d, n) = ({d}, {n})")
print("="*50)

# Verificación
print(f"\nVerificación: ({e} × {d}) mod {phi_n} = {(e * d) % phi_n}")

# Descifrar el mensaje que dio el profe
print("\n" + "="*50)
print("DESCIFRANDO MENSAJE")
print("="*50)

cifrado = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]
mensaje = ""

for c in cifrado:
    m = pow(c, d, n)
    mensaje += chr(m)
    print(f"{c} -> {m} -> {chr(m)}")

print("\nMensaje descifrado:", mensaje)
