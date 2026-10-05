# Demostracion y pruebas del algoritmo hibrido AES + RSA

import rsa_simple
from hibrido import get_Msj_And_Key, decifrar_mensaje, Cifrado_AES_enviar_mensaje


print("=" * 60)
print("1. GENERACION DE LLAVES RSA (practica 2)")
print("=" * 60)

RSA_Publica, RSA_Privada = rsa_simple.generar_llaves(p=67, q=83)

print("Clave publica  (e, n) =", RSA_Publica)
print("Clave privada  (d, n) =", RSA_Privada)


print()
print("=" * 60)
print("2. EMISOR: cifrado hibrido")
print("=" * 60)

mensaje_original = "Mensaje secreto de Angel Perez"

iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(RSA_Publica, mensaje_original)

print("Mensaje original     :", mensaje_original)
print("Mensaje cifrado AES  :", mensajeCifrado_AES)
print("IV cifrado con RSA   :", iv_cifrado_RSA["iv"])
print("Llave cifrada con RSA:", iv_cifrado_RSA["key"][:8], "...")


print()
print("=" * 60)
print("3. RECEPTOR: descifrado")
print("=" * 60)

recuperado = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)

print("Mensaje recuperado   :", recuperado)
print("Coincide?            :", recuperado == mensaje_original)


print()
print("=" * 60)
print("4. PRUEBAS")
print("=" * 60)

# Prueba A: varios mensajes de distinta longitud
casos = ["A", "Hola mundo", "x" * 100, "Acentos: n a e i o u"]
for texto in casos:
    paquete, cif = get_Msj_And_Key(RSA_Publica, texto)
    salida = decifrar_mensaje(cif, paquete, RSA_Privada)
    estado = "OK" if salida == texto else "FALLO"
    print(f"[{estado}] longitud {len(texto):>3} -> {texto[:30]}")

# Prueba B: el mismo mensaje cifrado dos veces da resultados distintos
_, c1 = get_Msj_And_Key(RSA_Publica, "repetido")
_, c2 = get_Msj_And_Key(RSA_Publica, "repetido")
print()
print("[OK] Dos cifrados del mismo texto son distintos:", c1 != c2)

# Prueba C: la llave privada equivocada no descifra
paquete, cif = get_Msj_And_Key(RSA_Publica, "no me vas a leer")
llave_mala = rsa_simple.generar_llaves(p=61, q=71)[1]
try:
    decifrar_mensaje(cif, paquete, llave_mala)
    print("[FALLO] descifro con la llave equivocada")
except Exception as err:
    print("[OK] Con llave privada equivocada falla:", type(err).__name__)

# Prueba D: funcion auxiliar con IV proporcionado
from Crypto.Random import get_random_bytes
iv_manual = get_random_bytes(16)
llave, cifrado_manual = Cifrado_AES_enviar_mensaje("Mensaje", iv_manual)
print("[OK] Cifrado_AES_enviar_mensaje devuelve:", cifrado_manual)
