# Practica 03 - Algoritmo hibrido RSA + AES

Implementacion educativa en Python de RSA-OAEP con SHA-256 y AES-256-CBC.
El mensaje se autentica con HMAC-SHA-256 antes del descifrado.

## Instalacion y ejecucion

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py "Mensaje de prueba"
pytest -q
```

## Archivos

- `cifrado_hibrido.py`: implementacion solicitada.
- `main.py`: demostracion desde la terminal.
- `tests/`: pruebas automatizadas.

## Nota tecnica

Aunque la consigna menciona un IV de 32 bytes, AES-CBC siempre utiliza bloques
de 128 bits; por ello el IV correcto mide 16 bytes. La clave AES si mide 32
bytes (AES-256). El parametro `clave_AES` tambien se hizo explicito en la
funcion auxiliar, pues no es posible cifrar un mensaje solamente con un IV.
