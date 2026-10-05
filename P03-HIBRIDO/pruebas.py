# Pruebas del algoritmo hibrido AES + RSA
# Ejecutar con: python pruebas.py

import rsa_simple
from hibrido import get_Msj_And_Key, decifrar_mensaje, Cifrado_AES_enviar_mensaje
from Crypto.Random import get_random_bytes

RSA_Publica, RSA_Privada = rsa_simple.generar_llaves(p=67, q=83)

resultados = []


def prueba(nombre, condicion, detalle=""):
    estado = "PASA" if condicion else "FALLA"
    resultados.append(condicion)
    print(f"[{estado}] {nombre}" + (f"  -> {detalle}" if detalle else ""))


print("=" * 62)
print("PRUEBAS DEL ALGORITMO HIBRIDO")
print("=" * 62)
print(f"Clave publica  (e, n) = {RSA_Publica}")
print(f"Clave privada  (d, n) = {RSA_Privada}")
print()

# ---- Prueba 1: ciclo completo ----
mensaje = "Mensaje secreto de Angel Perez"
paquete, cifrado = get_Msj_And_Key(RSA_Publica, mensaje)
recuperado = decifrar_mensaje(cifrado, paquete, RSA_Privada)
prueba("Ciclo completo cifrado/descifrado", recuperado == mensaje, recuperado)

# ---- Prueba 2: longitudes variables ----
print()
casos = {
    "1 caracter": "A",
    "menor a un bloque": "Hola",
    "exacto 16 bytes": "1234567890123456",
    "mayor a un bloque": "x" * 100,
    "con acentos UTF-8": "Contrasena: nino, accion, Mexico",
}
for nombre, texto in casos.items():
    pq, cf = get_Msj_And_Key(RSA_Publica, texto)
    out = decifrar_mensaje(cf, pq, RSA_Privada)
    prueba(f"Longitud: {nombre} ({len(texto)} chars)", out == texto)

# ---- Prueba 3: no determinismo ----
print()
_, c1 = get_Msj_And_Key(RSA_Publica, "mensaje repetido")
_, c2 = get_Msj_And_Key(RSA_Publica, "mensaje repetido")
prueba("El mismo texto produce cifrados distintos (IV aleatorio)", c1 != c2)

# ---- Prueba 4: tamanos correctos ----
print()
paquete, _ = get_Msj_And_Key(RSA_Publica, "test")
iv_rec = rsa_simple.descifrar_bytes(paquete["iv"], RSA_Privada)
key_rec = rsa_simple.descifrar_bytes(paquete["key"], RSA_Privada)
prueba("IV mide 16 bytes (tamano de bloque AES)", len(iv_rec) == 16, f"{len(iv_rec)} bytes")
prueba("Llave AES mide 32 bytes (AES-256)", len(key_rec) == 32, f"{len(key_rec)} bytes")

# ---- Prueba 5: llave privada incorrecta ----
print()
pq, cf = get_Msj_And_Key(RSA_Publica, "no me vas a leer")
_, llave_mala = rsa_simple.generar_llaves(p=61, q=71)
try:
    salida = decifrar_mensaje(cf, pq, llave_mala)
    prueba("Llave privada incorrecta no descifra", False, f"descifro: {salida}")
except Exception as err:
    prueba("Llave privada incorrecta no descifra", True, type(err).__name__)

# ---- Prueba 6: mensaje alterado ----
print()
pq, cf = get_Msj_And_Key(RSA_Publica, "mensaje integro")
alterado = ("B" if cf[0] != "B" else "C") + cf[1:]
try:
    salida = decifrar_mensaje(alterado, pq, RSA_Privada)
    prueba("Mensaje alterado no devuelve el original", salida != "mensaje integro")
except Exception as err:
    prueba("Mensaje alterado no devuelve el original", True, type(err).__name__)

# ---- Prueba 7: funcion auxiliar ----
print()
iv_manual = get_random_bytes(16)
llave, cif = Cifrado_AES_enviar_mensaje("Mensaje", iv_manual)
prueba("Cifrado_AES_enviar_mensaje con IV externo", isinstance(cif, str) and len(cif) > 0, cif)
prueba("Genera llave de 32 bytes si no se proporciona", len(llave) == 32)

# ---- Resumen ----
print()
print("=" * 62)
total = len(resultados)
exitosas = sum(resultados)
print(f"RESULTADO: {exitosas}/{total} pruebas superadas")
print("=" * 62)
