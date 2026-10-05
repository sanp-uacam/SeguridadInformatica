# Sistema de Login con SHA-256

Aplicacion de escritorio desarrollada en Python con Tkinter. El proyecto implementa un formulario de inicio de sesion y registro de usuarios, valida contrasenas seguras y almacena los usuarios junto con el hash SHA-256 de sus contrasenas en un archivo JSON.


## Funcionalidades

- Registro de nuevos usuarios.
- Validacion de contrasenas.
- Generacion de hashes mediante SHA-256.
- Inicio de sesion comparando hashes.
- Persistencia de usuarios en un archivo JSON.
- Visualizacion u ocultacion de la contrasena mediante la casilla `Ver contrasena`.
- Dashboard para usuarios normales.
- Cambio de contrasena despues de iniciar sesion.
- Panel de administracion para consultar usuarios y hashes.
- Eliminacion permanente de usuarios desde el panel de administracion.

## Responsabilidad de cada archivo

### `main.py`

Es el punto de entrada de la aplicacion. Importa el modulo del login y ejecuta `login_app.main()`.

La aplicacion debe iniciarse desde este archivo y desde la carpeta raiz del proyecto.

### `utils/login_app.py`

Contiene la clase `LoginApp`, que coordina el flujo inicial:

- Carga los usuarios desde `users-db.json`.
- Muestra el formulario de login y registro.
- Calcula el hash SHA-256.
- Valida las contrasenas.
- Comprueba las credenciales.
- Decide que vista abrir despues de un login correcto.

Si el usuario autenticado se llama `admin`, se abre el panel de administracion. Cualquier otro usuario accede a la vista normal.

## Cuenta de administrador

Las credenciales del administrador son:

Usuario:

```text
admin
```

Contrasena:

```text
Papure2@05
```

### `utils/user_view.py`

Contiene la vista del usuario normal. Esta vista muestra:

- Mensaje de bienvenida.
- Boton `Cambiar contrasena`.
- Boton `Cerrar sesion`.

El usuario puede cambiar su contrasena porque ya inicio sesion.

### `utils/admin_view.py`

Contiene el panel de administracion. El administrador puede:

- Consultar los nombres de usuario registrados.
- Consultar el hash SHA-256 asociado a cada usuario.
- Seleccionar y eliminar usuarios.
- Cerrar sesion.

El administrador no puede eliminarse a si mismo. La eliminacion se confirma antes de modificar el JSON.

El administrador no tiene un boton para cambiar contrasenas de otros usuarios. Esto mantiene separadas las funciones de administracion de usuarios y cambio de credenciales.

### `utils/password_window.py`

Contiene la ventana reutilizable para cambiar la contrasena de un usuario autenticado. Solicita:

1. Nueva contrasena.
2. Confirmacion de la nueva contrasena.

La nueva contrasena solo se guarda si las dos nuevas coinciden y cumple todos los requisitos de seguridad.

### `utils/saveJson.py`

Contiene las funciones para persistir los datos:

- `guardar_diccionario(datos, nombre_archivo)`: guarda un diccionario en JSON.
- `cargar_diccionario(nombre_archivo)`: carga el JSON o devuelve un diccionario vacio si el archivo todavia no existe.

### `utils/secureAES.py`

Contiene funciones relacionadas con AES. Actualmente no forma parte del flujo de login, que utiliza SHA-256 porque es el algoritmo solicitado para esta practica.

## Flujo de registro

1. El usuario escribe un nombre de usuario y una contrasena.
2. La aplicacion comprueba que ambos campos tengan contenido.
3. Se comprueba que el usuario no exista.
4. La contrasena se valida.
5. Se calcula el hash SHA-256 de la contrasena.
6. Se guarda el usuario y el hash en `users-db.json`.
7. La contrasena original se descarta y no se guarda.

Las reglas actuales de la contrasena son:

- Tener al menos 8 caracteres.
- Incluir una letra mayuscula.
- Incluir una letra minuscula.
- Incluir un numero.
- Incluir un caracter especial.
- No contener el nombre de usuario.

## Flujo de inicio de sesion

1. El usuario introduce su nombre y su contrasena.
2. La aplicacion carga el hash guardado para ese usuario.
3. Calcula el SHA-256 de la contrasena introducida.
4. Compara ambos hashes mediante `hmac.compare_digest`.
5. Si coinciden, se abre la vista correspondiente.
6. Si no coinciden, se muestra un mensaje de error.

El JSON tiene una estructura similar a esta:

```json
{
    "usuario": "hash_sha256_de_la_contrasena"
}
```

## Cambio de contrasena

La opcion `Cambiar contrasena` esta disponible en la vista del usuario normal despues de iniciar sesion.

No se trata de una recuperacion de contrasena. Para recuperar una contrasena sin conocer la actual normalmente se necesita un correo electronico, un codigo de verificacion, un token temporal u otro mecanismo de identidad.

El cambio de contrasena funciona de la siguiente manera:


1. Se solicita la nueva contrasena dos veces.
2. Se validan las reglas de seguridad.
3. Se calcula el nuevo hash.
4. Se actualiza el registro del usuario en `users-db.json`.

## Panel de administracion

El panel se abre cuando el usuario autenticado tiene el nombre `admin`.

Desde esta pantalla se pueden consultar los usuarios y los hashes almacenados. Tambien se puede seleccionar un usuario y eliminarlo definitivamente de `users-db.json`. Despues de eliminarlo, el nombre de usuario vuelve a estar disponible para un nuevo registro.

El panel no puede mostrar contrasenas en texto plano porque esas contrasenas nunca se guardan. Un hash SHA-256 no se puede revertir de forma directa para recuperar el texto original.

## Instalacion y ejecucion

### Requisito principal

Se necesita Python 3 con soporte para Tkinter.

### Ejecutar desde la terminal

Desde la carpeta del proyecto:

```bash
python3 main.py
```