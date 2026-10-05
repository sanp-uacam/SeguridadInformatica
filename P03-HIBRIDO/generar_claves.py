# ====== generar_claves.py ======
from Crypto.PublicKey import RSA

clave_privada = RSA.generate(2048)
clave_publica = clave_privada.publickey()

with open("privada.pem", "wb") as f:
    f.write(clave_privada.export_key())

with open("publica.pem", "wb") as f:
    f.write(clave_publica.export_key())

print("Claves generadas: privada.pem  y publica.pem ")