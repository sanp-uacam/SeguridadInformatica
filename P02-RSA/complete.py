from math import gcd


def inverso_modular(e, phi_n):
	for d in range(1, phi_n):
		if (e * d) % phi_n == 1:
			return d
	return None


p = int(input("p: "))
q = int(input("q: "))
numero_candidato = int(input("Número del candidato elegido para e: "))

n = p * q
phi_n = (p - 1) * (q - 1)

candidatos_e = []
for e in range(2, phi_n):
	if gcd(e, phi_n) == 1:
		candidatos_e.append(e)

if numero_candidato < 1 or numero_candidato > len(candidatos_e):
	print("El número del candidato no es valido")
else:
	e = candidatos_e[numero_candidato - 1]
	d = inverso_modular(e, phi_n)

	print("Clave pública:", (e, n))
	print("Clave privada:", (d, n))
