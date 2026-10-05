# Práctica 04 — Algoritmo Hash

Sistema de **login y registro de usuarios** en Python (Tkinter) que aplica
el flujo diseñado en clase:

```
Registro  ->  validar reglas de la contraseña  ->  SHA-256  ->  guardar {user, pass: Hash} en JSON
Login     ->  SHA-256(password ingresado)  ->  comparar (=?) contra el hash guardado
```

## Reglas de la contraseña (registro)

- Mínimo 8 caracteres
- Mayúsculas y minúsculas
- Sin secuencias (ej. `1234`, `abcd`)
- Al menos un carácter especial
- No debe incluir el nombre de usuario

Si alguna regla falla, el registro se rechaza y se muestra qué faltó.

## Estructura del proyecto

```
Practica_HASH/
├── main.py                 # Punto de entrada
├── users-db.json           # Base de datos de usuarios (se crea al ejecutar)
└── utils/
    ├── __init__.py
    ├── login_app.py         # UI de login/registro + validación + hash SHA-256
    ├── saveJson.py           # Guardar/cargar diccionarios en JSON
    └── secureAES.py          # Cifrado AES (utilidad incluida para una
                               # futura extensión con cifrado híbrido RSA+AES)
```

## Cómo ejecutar

```bash
python main.py
```

Al primer arranque se crea un usuario demo (`admin` / `Admin#2024`) y el
archivo `users-db.json`. Desde la ventana principal se puede:

- **Iniciar Sesión**: hashea la contraseña ingresada y la compara contra la
  guardada.
- **Registrarse**: abre un formulario, valida la contraseña contra las
  reglas de arriba y, si es válida, guarda `{usuario: hash}` en
  `users-db.json`.

## Notas técnicas

- El hash se calcula con `hashlib.sha256`.
- La persistencia usa `json.dump` / `json.load` (módulo `saveJson.py`).
- `secureAES.py` (AES-CBC con `pycrypto`/`pycryptodome`) queda incluido
  en el proyecto para una posible extensión donde el mensaje se cifre con
  AES y la llave viaje cifrada con RSA (esquema híbrido), pero no forma
  parte del flujo de login de esta práctica.
