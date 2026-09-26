# Practica Hash

Aplicacion de escritorio con registro e inicio de sesion. La contrasena debe tener al menos 8 caracteres, mayuscula, minuscula, numero y simbolo; no puede incluir el usuario ni secuencias ascendentes o descendentes de tres letras o numeros. El registro guarda en `usuarios.json` el nombre de usuario y el resumen SHA-256, nunca la contrasena original.

## Ejecucion

Requiere Python 3 con Tkinter:

```powershell
python main.py
```

El archivo `usuarios.json` se crea junto a `main.py` al registrar la primera cuenta. No se debe subir ese archivo con cuentas reales.

La consigna didactica solicita SHA-256 directo. En sistemas reales, SHA-256 sin sal y rapido no es adecuado para almacenar contrasenas; se recomienda Argon2id, scrypt o PBKDF2 con sal unica.
