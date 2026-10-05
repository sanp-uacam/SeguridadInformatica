n = 3703
p = 0
q = 0

for i in range(2, n):
    if n % i == 0:
        p = i
        q = n // i
        break;
print(f"Divisores encontrados: p = {p}, q = {q}")