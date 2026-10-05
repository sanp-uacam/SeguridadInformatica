# ==========================================
# DATOS DE ENTRADA
# ==========================================
d = 4457
n = 5561
mensaje_cifrado = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]

print("=== PASO 5: DESCIFRADO DEL MENSAJE ===")
print(f"Clave privada (d): {d}")
print(f"Módulo (n): {n}\n")

mensaje_descifrado = []

print("Operaciones (M = C^d mod n):")
for C in mensaje_cifrado:
    
    M = pow(C, d, n)
    mensaje_descifrado.append(M)
    print(f"Cifrado: {C:4d} -> Descifrado: {C}^{d} mod {n} = {M}")

print(f"\nMensaje numérico final descifrado:\n{mensaje_descifrado}")