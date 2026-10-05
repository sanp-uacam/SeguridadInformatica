d = 4457
n = 5561

mensaje_cifrado = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]

mensaje_descifrado = ""

print("Cifrado -> ASCII -> Caracter")
for c in mensaje_cifrado:
    m = pow(c, d) % n
    letra = chr(m)
    mensaje_descifrado += letra
    print(f"{c:7d} -> {m:5d} -> '{letra}'")
print("Mensaje final descifrado:", mensaje_descifrado)