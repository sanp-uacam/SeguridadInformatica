import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding


def Cifrado_AES_enviar_mensaje(mensaje_bytes, clave_aes, iv):
    # Implementa cifrado AES en modo CBC
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(mensaje_bytes) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(clave_aes), modes.CBC(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(padded_data) + encryptor.finalize()


def get_Msj_And_Key(mensaje, RSA_Publica):
    clave_aes = os.urandom(32) 
    iv = os.urandom(16) 
    
    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje.encode('utf-8'), clave_aes, iv)
    
    
    clave_aes_cifrada = RSA_Publica.encrypt(
        clave_aes,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    
    
    iv_cifrado_RSA = RSA_Publica.encrypt(
        iv,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    
    return mensajeCifrado_AES, iv_cifrado_RSA, clave_aes_cifrada


def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, clave_aes_cifrada, RSA_Privada):
    
    iv = RSA_Privada.decrypt(
        iv_cifrado_RSA,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    
  
    clave_aes = RSA_Privada.decrypt(
        clave_aes_cifrada,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    
   
    cipher = Cipher(algorithms.AES(clave_aes), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(mensajeCifrado_AES) + decryptor.finalize()
    
    unpadder = sym_padding.PKCS7(128).unpadder()
    mensaje_bytes = unpadder.update(padded_data) + unpadder.finalize()
    
    return mensaje_bytes.decode('utf-8')


if __name__ == "__main__":
   
    clave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    clave_publica = clave_privada.public_key()
    
    mensaje_original = "Este es un mensaje secreto para la práctica de Seguridad Informática."
    print(f"Mensaje Original: {mensaje_original}\n")
    
    # Cifrado
    msj_cifrado, iv_cifrado, clave_cifrada = get_Msj_And_Key(mensaje_original, clave_publica)
    print(f"Mensaje Cifrado (AES): {msj_cifrado.hex()[:50]}...")
    print(f"IV Cifrado (RSA): {iv_cifrado.hex()[:50]}...")
    
    # Descifrado
    msj_recuperado = decifrar_mensaje(msj_cifrado, iv_cifrado, clave_cifrada, clave_privada)
    print(f"\nMensaje Recuperado: {msj_recuperado}")
    
    assert mensaje_original == msj_recuperado
    print("\n✓ Prueba superada: El mensaje se descifró correctamente.")