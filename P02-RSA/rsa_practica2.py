# =============================================================
#  Seguridad Informatica - Practica 2: Algoritmo RSA
#  Universidad Autonoma de Campeche - Facultad de Ingenieria
#
#  Alumno: Kerin Del Jesus Gonzalez Maas
#  Grado: 7   Grupo: "A"
#  Maestro: Sergio A. Noh Puch
# =============================================================

from math import gcd

# -------------------------------------------------------------
# DATOS DE ENTRADA
# -------------------------------------------------------------
p = 67
q = 83

print("=" * 55)
print(" PRACTICA 2 - ALGORITMO RSA")
print("=" * 55)
print(f"Datos de entrada:  p = {p}   q = {q}\n")

# -------------------------------------------------------------
# PASO 1: Calcular n = p * q
#   n es el modulo, se usa en el cifrado y en el descifrado.
# -------------------------------------------------------------
n = p * q
print("PASO 1 - Calcular n")
print(f"  n = p * q = {p} * {q} = {n}\n")

# -------------------------------------------------------------
# PASO 2: Calcular phi(n) = (p-1) * (q-1)
#   Funcion de Euler. Cuenta cuantos numeros menores que n
#   son primos relativos con n.
# -------------------------------------------------------------
phi = (p - 1) * (q - 1)
print("PASO 2 - Calcular phi(n)")
print(f"  phi(n) = (p-1)*(q-1) = {p-1} * {q-1} = {phi}\n")

# -------------------------------------------------------------
# PASO 3: Elegir e (clave publica)
#   Condiciones:  1 < e < phi(n)   y   mcd(e, phi(n)) = 1
#   La practica pide el CUARTO candidato valido.
#   Se recorre e desde 2 y se anota cada intento para justificar
#   por que los primeros tres se descartan o se aceptan.
# -------------------------------------------------------------
print("PASO 3 - Elegir e (cuarto candidato valido)")
print("  e   | mcd(e, phi) | resultado")
print("  ----+-------------+------------------")

candidatos = []
e_probado = 2
while len(candidatos) < 4:
    g = gcd(e_probado, phi)
    if g == 1:
        candidatos.append(e_probado)
        estado = f"VALIDO  (candidato #{len(candidatos)})"
    else:
        estado = "descartado"
    print(f"  {e_probado:<3} | {g:^11} | {estado}")
    e_probado += 1

e = candidatos[3]          # el cuarto candidato de la lista
print(f"\n  Candidatos validos encontrados: {candidatos}")
print(f"  --> Se toma el CUARTO:  e = {e}")
print(f"  Clave publica = (e, n) = ({e}, {n})\n")


# -------------------------------------------------------------
# PASO 4: Calcular d (clave privada)
#   d es el inverso multiplicativo de e modulo phi(n):
#        e * d = 1 (mod phi(n))
#   Se resuelve con el ALGORITMO EXTENDIDO DE EUCLIDES, que
#   ademas del mcd devuelve los coeficientes x, y tales que:
#        e*x + phi*y = mcd(e, phi)
#   Si el mcd es 1, entonces x es el inverso buscado.
# -------------------------------------------------------------
def euclides_extendido(a, b):
    """Devuelve (mcd, x, y) tal que a*x + b*y = mcd(a, b)."""
    if b == 0:
        return (a, 1, 0)
    mcd, x1, y1 = euclides_extendido(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return (mcd, x, y)


print("PASO 4 - Calcular d con el algoritmo extendido de Euclides")

# Se muestran las divisiones sucesivas (Euclides "normal")
a, b = phi, e
print("  Divisiones sucesivas:")
while b != 0:
    print(f"    {a} = {a // b} * {b} + {a % b}")
    a, b = b, a % b

mcd, x, y = euclides_extendido(e, phi)
d = x % phi                # se normaliza para que quede positivo

print(f"\n  Coeficientes de Bezout: {e}*({x}) + {phi}*({y}) = {mcd}")
print(f"  Como el coeficiente de e es negativo, se suma phi(n):")
print(f"    d = {x} + {phi} = {d}")
print(f"\n  Comprobacion:  e * d = {e} * {d} = {e*d}")
print(f"                 {e*d} mod {phi} = {(e*d) % phi}  (debe ser 1)")
print(f"  Clave privada = (d, n) = ({d}, {n})\n")


# -------------------------------------------------------------
# PASO 5: Descifrar el mensaje
#   Formula:  m = c^d mod n
#   pow(c, d, n) hace la exponenciacion modular de forma
#   eficiente (no calcula el numero gigante completo).
#   Cada numero descifrado es un codigo ASCII.
# -------------------------------------------------------------
mensaje_cifrado = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]

print("PASO 5 - Descifrar el mensaje")
print("  Formula: m = c^d mod n\n")
print("   Bloque |    c   |  m = c^d mod n | Caracter ASCII")
print("  --------+--------+----------------+---------------")

texto = ""
for i, c in enumerate(mensaje_cifrado, start=1):
    m = pow(c, d, n)          # exponenciacion modular
    caracter = chr(m)         # se convierte el numero a caracter ASCII
    texto += caracter
    visible = "(espacio)" if caracter == " " else caracter
    print(f"   {i:^6} | {c:^6} | {m:^14} | {visible}")

print("\n" + "=" * 55)
print(f"  MENSAJE DESCIFRADO:  {texto}")
print("=" * 55)


# -------------------------------------------------------------
# VERIFICACION EXTRA (opcional):
#   Se vuelve a cifrar el texto obtenido con la clave publica
#   y se compara con el criptograma original. Si coinciden,
#   las claves e y d son correctas.
# -------------------------------------------------------------
recifrado = [pow(ord(ch), e, n) for ch in texto]
print("\nVerificacion - se vuelve a cifrar con la clave publica:")
print(f"  Original:  {mensaje_cifrado}")
print(f"  Recifrado: {recifrado}")
print(f"  Coinciden: {recifrado == mensaje_cifrado}")
