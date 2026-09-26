# Practica de cifrado hibrido RSA-AES

## Archivos

- `rsa_aes_hybrid.py`: funciones de cifrado y descifrado.
- `test_hybrid.py`: pruebas de ida y vuelta, Unicode, IV y manipulacion de ciphertext.
- `Reporte_Practica_2_RSA_AES.docx`: explicacion, diagrama de flujo, decisiones de diseno y analisis de seguridad.
- `requirements.txt`: dependencia de Python.

## Uso

Instalar la dependencia y ejecutar desde esta carpeta:

```powershell
python -m pip install -r requirements.txt
python demo.py
```

Funciones principales: `get_Msj_And_Key(RSA_Publica, mensaje)`, `decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)` y `Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)`.

## Aclaraciones del diseno

AES-CBC requiere un IV de 16 bytes, porque AES siempre usa bloques de 128 bits. La clave de AES-256 mide 32 bytes. Con RSA-2048 y OAEP-SHA-256 se cifra un solo paquete de 48 bytes `clave_AES || IV`; el nombre `iv_cifrado_RSA` se conserva por compatibilidad con la consigna. CBC no autentica por si solo: para produccion se recomienda AES-GCM o MAC independiente.
