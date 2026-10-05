import time
from utils import secureAES as AES
from utils import login_app
from utils import saveJson

def demostrar_criptografia():
    """Ejecuta una demostración en consola del flujo Emisor-Receptor (RSA+AES)"""
    print("="*55)
    print(" DEMOSTRACIÓN: SISTEMA DE ENCRIPTADO HÍBRIDO (RSA + AES)")
    print("="*55)
    
    # 1. El RECEPTOR genera sus llaves
    print("\n[Receptor] Generando par de llaves RSA (Pública y Privada)...")
    llave_privada, llave_publica = AES.generar_llaves_rsa()
    
    # Mensaje de prueba
    mensaje_original = "Este es un mensaje confidencial para el profesor."
    print(f"\n[Emisor] Mensaje original a enviar: '{mensaje_original}'")
    
    # 2. El EMISOR cifra el mensaje
    print("[Emisor] Cifrando mensaje con AES y protegiendo Llave/VI con RSA...")
    paquete_enviado = AES.emisor_cifrar(mensaje_original, llave_publica)
    
    # Lo que viajaría "por internet"
    print("\n" + "-"*20 + " RED " + "-"*20)
    print(f"Paquete RSA (Llave + VI): {paquete_enviado['datos_rsa'][:50]}... [Truncado]")
    print(f"Mensaje cifrado (AES): {paquete_enviado['mensaje_cifrado_aes']}")
    print("-" * 45 + "\n")
    
    # 3. El RECEPTOR descifra el paquete
    print("[Receptor] Paquete recibido. Descifrando RSA para obtener llaves AES...")
    mensaje_recibido = AES.receptor_descifrar(paquete_enviado, llave_privada)
    
    print(f"[Receptor] Mensaje descifrado con éxito: '{mensaje_recibido}'")
    print("="*55)
    print("\nAbriendo la interfaz gráfica del Sistema de Login...\n")

if __name__ == "__main__":
    # 1. Ejecutar primero la demostración en la terminal
    demostrar_criptografia()
    
    # Pausa breve para que el usuario pueda leer la terminal antes de que salga la ventana
    time.sleep(2)
    
    # 2. Iniciar la aplicación gráfica del login
    login_app.main()