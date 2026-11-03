# ==========================================
# Práctica 2: Algoritmo RSA
# Autor: Fernando Adriano Sabido Quijano
# Ingeniería en Tecnología de Software
# ==========================================
import math

def main():
    print("=== PRÁCTICA 2 - ALGORITMO RSA ===")
    
    # Definición de los números primos iniciales
    p = 67
    q = 83

    # Paso 1: Cálculo del módulo n
    n = p * q
    print(f"[*] Modulo n calculado: {n}")

    # Paso 2: Cálculo de la función de Euler phi(n)
    phi = (p - 1) * (q - 1)
    print(f"[*] Valor de phi(n) calculado: {phi}")

    # Paso 3: Selección de la clave pública (e)
    # Buscamos coprimos de phi(n)
    candidatos_e = []
    for i in range(2, phi):
        if math.gcd(i, phi) == 1:
            candidatos_e.append(i)
            # Detenemos la búsqueda al obtener 5 candidatos
            if len(candidatos_e) == 5:
                break

    # Seleccionamos el cuarto candidato según las instrucciones
    e = candidatos_e[3] 
    print(f"[*] Candidatos para e: {candidatos_e}")
    print(f"[*] Clave publica elegida (e): {e}")

    # Paso 4: Cálculo de la clave privada (d)
    # Inverso multiplicativo modular
    d = pow(e, -1, phi)
    print(f"[*] Clave privada calculada (d): {d}")

    # Paso 5: Proceso de descifrado
    # Arreglo de cifrogramas proporcionados
    cifrogramas = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]

    mensaje_descifrado = ""
    print("\n[*] Iniciando descifrado del mensaje...")

    for c in cifrogramas:
        # Aplicando M = C^d mod n
        m = pow(c, d, n)
        caracter = chr(m)
        mensaje_descifrado += caracter
        print(f"    Cifrado: {c} -> ASCII: {m} -> Caracter: '{caracter}'")

    print(f"\n[+] MENSAJE FINAL DESCIFRADO: {mensaje_descifrado}")

if __name__ == '__main__':
    main()
