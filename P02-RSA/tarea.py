import math

# ==========================================
# DATOS DE ENTRADA 
# ==========================================
phi_n = 5412 

print("=== PASO 3: CÁLCULO DE CLAVE PÚBLICA (e) ===")
print(f"Buscando candidatos para 'e' con phi(n) = {phi_n}...\n")

candidatos_encontrados = 0
limite_candidatos = 5 

for e in range(2, phi_n):
    if math.gcd(e, phi_n) == 1:
        candidatos_encontrados += 1
        print(f"Candidato {candidatos_encontrados}: e = {e}")
        
        if candidatos_encontrados == limite_candidatos:
            break

