from Crypto.PublicKey import RSA

print("--- GENERADOR DE CLAVES RSA ---")
print("Generando claves RSA de 2048 bits...")

clave_privada = RSA.generate(2048)
clave_publica = clave_privada.publickey()

with open("privada.pem", "wb") as f:
    f.write(clave_privada.export_key())

with open("publica.pem", "wb") as f:
    f.write(clave_publica.export_key())

print("¡Exito! Claves generadas y guardadas como 'privada.pem' y 'publica.pem'.")
