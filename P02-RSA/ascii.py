d = 4457
n = 5561

c = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]

for i, valor_c in enumerate(c, start=1):
	m = pow(valor_c, d, n)
	print(f"c({i}) = {valor_c}  -->  m({i}) = {m}  -->  ASCII = {chr(m)}")

