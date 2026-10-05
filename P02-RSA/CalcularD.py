# Paso 4 - Clave privada d
phi = 5412
e = 17

# Algoritmo extendido de Euclides
def inverso_modular(a, m):
    m0 = m
    y = 0
    x = 1
    
    while a > 1:
        q = a // m
        t = m
        m = a % m
        a = t
        t = y
        y = x - q * y
        x = t
        
    if x < 0:
        x = x + m0
    return x

d = inverso_modular(e, phi)

print("e:", e)
print("phi:", phi)
print("d:", d)