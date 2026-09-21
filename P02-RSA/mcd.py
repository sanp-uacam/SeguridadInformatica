numero = int(input("Número: "))
divisor = 2
factores = []

while divisor * divisor <= numero:
	while numero % divisor == 0:
		factores.append(divisor)
		numero //= divisor
	divisor += 1

if numero > 1:
	factores.append(numero)

print(", ".join(str(factor) for factor in factores))
