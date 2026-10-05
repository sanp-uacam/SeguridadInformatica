import math

n = int(input("Ingresa n: "))

p = 0
q = 0

for i in range(2, int(math.sqrt(n)) + 1):
    if n % i == 0:
        p = i
        q = n // i
        break

if p == 0:
    print("No se pudo factorizar (es primo) n")
else:
    print("p =", p)
    print("q =", q)

phi = (p - 1) * (q - 1)
print("phi =", phi)

print("\n--- Posibles candidatos para e ---")
candidatos_e = []
for posible_e in range(2, phi):
    if math.gcd(posible_e, phi) == 1:
        candidatos_e.append(posible_e)
    if len(candidatos_e) == 30:
        break

for idx, valor_e in enumerate(candidatos_e):
    print(f"[{idx + 1}] e = {valor_e}")

seleccion_e = int(input(f"\nElige el número de posición para 'e' (1-{len(candidatos_e)}): "))
if 1 <= seleccion_e <= len(candidatos_e):
    e = candidatos_e[seleccion_e - 1]
else:
    print("Opción inválida. Se seleccionará el candidato [1] por defecto.")
    e = candidatos_e[0]

print("\ne seleccionado =", e)

d = 0
for i in range(1, phi):
    if (e * i) % phi == 1:
        d = i
        break

if d == 0:
    print("No se pudo encontrar d")
else:
    print("d calculada automáticamente =", d)

comprobacion = (e * d) % phi
print("Comprobacion =", comprobacion)

if comprobacion == 1:
    print("\n¡RSA valido!")
    print("Clave publica =", (n, e))
    print("Clave privada =", (d, n))

    print("\n--- Proceso de Encriptación y Desencriptación (ejemplo) ---")
    m = 42
    print("Mensaje original (m) =", m)

    C = pow(m, e, n)  # C = m^e mod n
    print("Mensaje cifrado (C) =", C)

    m_descifrado = pow(C, d, n)  # m = C^d mod n
    print("Mensaje recuperado =", m_descifrado)

    ## descifrar el mensaje dado
    print("\n--- Descifrando mensaje de la práctica ---")
    mensaje_cifrado = "1058 2597 4955 4201 3162 4343 2754 2497 336 2597"
    bloques = mensaje_cifrado.split()

    texto_descifrado = ""
    for bloque in bloques:
        C_bloque = int(bloque)
        m_bloque = pow(C_bloque, d, n)  # m = C^d mod n
        print(f"{C_bloque} -> {m_bloque} -> {chr(m_bloque)}")
        texto_descifrado += chr(m_bloque)

    print("\nMensaje descifrado completo:", texto_descifrado)
