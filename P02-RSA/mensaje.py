
c = 2597
n = 5561
e = 17
d = 4457

m = pow(c, d) % n
c = pow(m, e) % n

print("C:", c)
print("M:", m)
