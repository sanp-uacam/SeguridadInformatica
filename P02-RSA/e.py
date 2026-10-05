from math import gcd

y_n = int(input("Ingresa φ(n): "))
candidatos = []

for e in range(2, y_n):
	if gcd(e, y_n) == 1:
		candidatos.append(e)

cuarto_e_seleccionado = candidatos[3] if len(candidatos) > 3 else None
print("Cuarto candidato para e:", cuarto_e_seleccionado)

print("Candidatos para e:")
print(", ".join(str(e) for e in candidatos))

