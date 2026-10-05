import math

# Datos de entrada 
p = 67
q = 83
mensaje_cifrado = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]

# Paso 1: Calcular n
n = p * q

# Paso 2: Calcular phi(n)
phi_n = (p - 1) * (q - 1)

# Paso 3: Elegir e (clave pública)
candidatos_e = []
# Iteramos para encontrar los candidatos que cumplen la condición mcd(e, phi_n) == 1
for e_potencial in range(2, phi_n):
    if math.gcd(e_potencial, phi_n) == 1:
        candidatos_e.append(e_potencial)
        # Nos detenemos al encontrar el cuarto candidato
        if len(candidatos_e) == 4:
            break

e = candidatos_e[3] # Se selecciona el cuarto elemento de la lista

# Paso 4: Calcular d (clave privada)
# pow(base, exponente, modulo) con exponente -1 calcula el inverso multiplicativo modular
d = pow(e, -1, phi_n)

# Paso 5: Descifrar el mensaje
# Aplicamos la fórmula m = c^d mod n para cada bloque cifrado
mensaje_descifrado = [pow(c, d, n) for c in mensaje_cifrado]

# Paso 6: 
# Convertir los números descifrados a texto usando código ASCII
texto_descifrado = ''.join([chr(numero) for numero in mensaje_descifrado])

# Salida de resultados 
print(f"Paso 1: n = {n}")
print(f"Paso 2: phi(n) = {phi_n}")
print(f"Paso 3: Primeros 4 candidatos para 'e': {candidatos_e}")
print(f"        Valor de 'e' elegido = {e}")
print(f"        Clave Publica ({e}, {n})")
print(f"Paso 4: Clave privada 'd' = {d}")
print(f"        Clave Privada ({d}, {n})")
print(f"Paso 5: Mensaje descifrado: {mensaje_descifrado}")
print(f"Paso 6: Texto descifrado: {texto_descifrado}")
