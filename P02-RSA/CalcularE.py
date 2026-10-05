import math

# Datos iniciales
p = 67
q = 83
phi = (p - 1) * (q - 1)  # 5412

candidatos_validos = []

# Evaluar valores de e a partir de 2 para documentar el descarte
for e in range(2, phi):
    mcd = math.gcd(e, phi)
    if mcd == 1:
        candidatos_validos.append(e)
        print(f"e = {e:2d} -> mcd({e}, {phi}) = {mcd}  [CANDIDATO #{len(candidatos_validos)} ACEPTADO]")
        if len(candidatos_validos) == 4:
            break
    else:
        print(f"e = {e:2d} -> mcd({e}, {phi}) = {mcd}  (Descartado)")

print("\n--- RESULTADO ---")
print(f"El 4to candidato seleccionado para e es: {candidatos_validos[-1]}")