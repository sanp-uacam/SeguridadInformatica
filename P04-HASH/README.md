# Práctica 04: HASH

Esta práctica es una aplicación sencilla de registro e inicio de sesión. Su objetivo es mostrar que una contraseña no se guarda directamente: se guarda su hash SHA-256.

## Qué hace

La ventana permite registrar usuarios, validar reglas básicas de contraseña e iniciar sesión. Al guardar un usuario, `login_app.py` calcula el hash y `saveJson.py` lo almacena en `users-db.json`. Durante el acceso se calcula nuevamente el hash y se compara con `hmac.compare_digest`.

## Cómo ejecutarla

Desde esta carpeta:

```powershell
python main.py
```

Se abrirá la ventana de la práctica. Se necesita Python con Tkinter.

## Evidencias

La carpeta `evidencias` contiene seis capturas de la ventana de la aplicación:

- `Bienvenida.png`: pantalla inicial.
- `Registro.png`: formulario para crear un usuario.
- `Registro_exitoso.png`: confirmación del registro.
- `Iniciar_sesion.png`: formulario de acceso.
- `Inicio_Exito.png`: acceso correcto al sistema.
- `Datos.png`: información almacenada de la práctica.

El archivo `users-db.json` contiene datos locales de la práctica. SHA-256 sin sal se conserva porque forma parte del trabajo original; para un sistema real conviene usar Argon2id o scrypt.
