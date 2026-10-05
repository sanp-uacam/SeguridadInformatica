import json
from hibrido import generar_claves_rsa, decifrar_mensaje

print("RECEPTOR")
# Generar claves publicas 
print("Generando claves RSA...")
RSA_Publica, RSA_Privada = generar_claves_rsa()

# Guardar clave
with open("clave_publica.json", "w") as archivo:
    json.dump(RSA_Publica, archivo)
print("Clave pública compartida en 'clave_publica.json'.\n")

input("Presionar ENTER cuando el emisor haya creado 'mensaje_oculto.json'...")

# Recibir los datos
try:
    with open("mensaje_oculto.json", "r") as archivo:
        datos_recibidos = json.load(archivo)
        
    iv_cifrado = datos_recibidos["iv"]
    clave_aes_cifrada = datos_recibidos["clave_aes"]
    # Los bytes no se pueden guardar en JSON, así que el emisor los mandó en hex. 
    # Regresar en bytes para AES
    msj_cifrado_aes = bytes.fromhex(datos_recibidos["mensaje_hex"]) 

    # 3. Descifrar el paquete con laprivada
    texto_recuperado = decifrar_mensaje(msj_cifrado_aes, clave_aes_cifrada, iv_cifrado, RSA_Privada)

    print(f"\nÉXITO. Mensaje original: {texto_recuperado}")

except FileNotFoundError:
    print("Error: El archivo 'mensaje_oculto.json' no existe. Ejecuta el emisor primero.")