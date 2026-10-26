# LoginHash

Aplicación de escritorio desarrollada con Python y Tkinter que permite registrar usuarios, validar contraseñas e iniciar sesión mediante credenciales almacenadas localmente.

## Características

- Registro e inicio de sesión de usuarios.
- Validación visual de los requisitos de contraseña.
- Contraseñas almacenadas como hashes SHA-256.
- Búsqueda directa de usuarios mediante un objeto JSON.
- Prevención de nombres de usuario duplicados.
- Notificaciones modales que permanecen delante de la ventana activa.

## Requisitos

- Python 3.10 o posterior.
- Git.
- Tkinter.

Las dependencias de Python adicionales están declaradas en `requirements.txt`.

## Instalación en Windows

1. Instala [Python](https://www.python.org/downloads/windows/) y activa la opción **Add Python to PATH** durante la instalación. La distribución oficial de Python incluye Tkinter.
2. Abre PowerShell y clona el repositorio:

   ```powershell
   git clone https://github.com/CastilloDevX/LoginHash.git
   cd LoginHash
   ```

3. Crea y activa un entorno virtual:

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación, habilítala para la sesión actual y vuelve a intentarlo:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```

4. Instala las dependencias:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. Ejecuta la aplicación:

   ```powershell
   python main.py
   ```

## Instalación en Linux

1. Instala Python, el soporte para entornos virtuales, Tkinter y Git. En Ubuntu o Debian:

   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-tk git
   ```

   En Fedora:

   ```bash
   sudo dnf install python3 python3-tkinter git
   ```

2. Clona el repositorio:

   ```bash
   git clone https://github.com/CastilloDevX/LoginHash.git
   cd LoginHash
   ```

3. Crea y activa un entorno virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Instala las dependencias:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. Ejecuta la aplicación:

   ```bash
   python main.py
   ```

## Base de datos local

`users-db.json` se crea localmente al registrar el primer usuario y está excluido de Git para evitar publicar credenciales. Su estructura es un objeto que relaciona cada usuario con el hash de su contraseña:

```json
{
    "usuario": "hash_sha256"
}
```

Para reiniciar todos los usuarios, cierra la aplicación y elimina `users-db.json`. Se generará nuevamente con el próximo registro.

## Uso

1. Ejecuta `main.py`.
2. Selecciona **Registrarse** para crear una cuenta.
3. Completa los requisitos de contraseña mostrados en pantalla.
4. Inicia sesión con el usuario y la contraseña registrados.

> [!NOTE]
> Este proyecto es educativo. Para un sistema de producción se recomienda almacenar las contraseñas con un algoritmo especializado como Argon2, bcrypt o scrypt, junto con una sal única por usuario.
