# Practica 2 - Algoritmo RSA
# Alumno: Angel Antonio Perez Reyes
# Seguridad Informatica
# Imparte: Sergio Noh Puch

p = 67
q = 83

n = p * q
phi = (p - 1) * (q - 1)

print("PASO 1 y 2: CALCULO DE n Y phi(n)")
print("p =", p)
print("q =", q)
print("n = p * q =", p, "*", q, "=", n)
print("phi(n) = (p-1) * (q-1) =", p - 1, "*", q - 1, "=", phi)


def mcd(a, b):
    while b != 0:
        residuo = a % b
        a = b
        b = residuo
    return a


print()
print("PASO 3: BUSQUEDA DE e")
print("Condiciones: 1 < e < phi(n) y mcd(e, phi(n)) = 1")
print()

contador = 0
numero = 2
e = 0

while contador < 4:
    divisor = mcd(numero, phi)

    if divisor == 1:
        contador = contador + 1
        e = numero
        print("e =", numero, " mcd =", divisor, " --> CANDIDATO", contador)
    else:
        print("e =", numero, " mcd =", divisor, " --> no sirve")

    numero = numero + 1

print()
print("El cuarto candidato es e =", e)


print()
print("PASO 4: BUSQUEDA DE d (algoritmo extendido de Euclides)")
print("Se busca d tal que", e, "* d mod", phi, "= 1")


def euclides_extendido(a, b):
    # devuelve (mcd, x, y) tal que a*x + b*y = mcd
    if b == 0:
        return a, 1, 0
    g, x1, y1 = euclides_extendido(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y


g, x, y = euclides_extendido(e, phi)
d = x % phi

print("mcd(e, phi) =", g)
print("Coeficiente x (antes de ajustar) =", x)
print("d = x mod phi =", d)
print("Comprobacion:", e, "*", d, "=", e * d)
print(e * d, "mod", phi, "=", (e * d) % phi)

print()
print("CLAVE PUBLICA  = (", e, ",", n, ")")
print("CLAVE PRIVADA  = (", d, ",", n, ")")


print()
print("PASO 5: DESCIFRADO DEL MENSAJE")
print("Formula: M = C^d mod n")
print()

cifrado = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]

mensaje = ""

for c in cifrado:
    m = pow(c, d, n)
    letra = chr(m)
    mensaje = mensaje + letra
    print("C =", c, " -> M =", m, " -> letra =", letra)

print()
print("MENSAJE DESCIFRADO:", mensaje)
