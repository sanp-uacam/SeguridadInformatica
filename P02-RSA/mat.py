e = 19
yn = 5412

for d in range(1, 6001):
    if (e * d) % yn == 1:
        print("El valor de d es:", d)
        break
