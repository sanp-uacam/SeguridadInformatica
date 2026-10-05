# Practica 04 - Algoritmo Hash

Aplicacion de escritorio en Python/Tkinter que registra usuarios, valida
contrasenas, almacena un hash SHA-256 en JSON y verifica el hash durante el
inicio de sesion.

## Ejecutar

```bash
python3 main.py
```

No requiere paquetes externos: utiliza solamente la biblioteca estandar de
Python.

## Probar

```bash
python3 -m unittest discover -s tests -v
```

## Reglas de contrasena

- Minimo 8 caracteres.
- Al menos una mayuscula y una minuscula.
- Al menos un numero.
- Al menos un caracter especial.
- No puede contener el nombre de usuario, sin distinguir mayusculas.

El archivo `users-db.json` almacena pares `usuario: hash`, nunca la contrasena
en texto plano.
