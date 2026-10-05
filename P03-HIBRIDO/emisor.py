import json
from hibrido import get_Msj_And_Key

print("EMISOR")
# Leer la clave pública 
print("Obteniendo la clave pública del receptor...")
try:
    with open("clave_publica.json", "r") as archivo:
        # Convertir a tupla (e, n) para el JSON
        RSA_Publica = tuple(json.load(archivo)) 

    # Enviar el mensaje oculto
    texto_original = input("Escribe el mensaje secreto que deseas enviar: ")

    # Ejecutar algoritmo híbrido (Genera la clave AES, cifra y empaqueta)
    iv_cifrado, clave_aes_cifrada, msj_cifrado_aes = get_Msj_And_Key(RSA_Publica, texto_original)

    # Enviar los datos para guardarlos en JSON
    datos_red = {
        "iv": iv_cifrado,
        "clave_aes": clave_aes_cifrada,
        "mensaje_hex": msj_cifrado_aes.hex() # Convertir bytes a texto para que JSON lo soporte
    }

    with open("mensaje_oculto.json", "w") as archivo:
        json.dump(datos_red, archivo, indent=4)

    print("¡El paquete ha sido enviado exitosamente (guardado en 'mensaje_oculto.json')!")

except FileNotFoundError:
    print("Error: No encontré la clave pública. El receptor debe iniciar primero.")