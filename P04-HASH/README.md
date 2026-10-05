# Práctica 4 – Algoritmo HASH

**Seguridad Informática** · Facultad de Ingeniería, UACAM
**Alumno:** Kerin Del Jesús González Maas · Grado 7, Grupo "A"
**Maestro:** Sergio A. Noh Puch

---

## Descripción

Aplicación de escritorio hecha con Python y Tkinter para registrar usuarios e iniciar sesión. La contraseña **nunca se guarda**: al registrarse se calcula su hash SHA-256 y solo ese hash se almacena en `users-db.json`. Al iniciar sesión se vuelve a calcular el hash de la contraseña escrita y se compara con el guardado.

## Ejecución

Requiere Python 3.10 o superior. No usa librerías externas: `hashlib`, `hmac`, `json` y `tkinter` vienen incluidas con Python.

```bash
python main.py
```

## Estructura

```
P04-HASH/
├── main.py              ← punto de entrada, abre la ventana
├── users-db.json        ← usuarios y sus hashes
└── utils/
    ├── __init__.py
    ├── login_app.py     ← interfaz gráfica (registro, login y panel)
    ├── saveJson.py      ← lectura/escritura del JSON y autenticación
    └── seguridad.py     ← cálculo del hash y reglas de contraseña
```

## Funcionamiento

**Registro**

1. El usuario escribe su nombre, su contraseña y la confirmación.
2. Mientras escribe, la ventana marca con ✓ cada regla que ya se cumple.
3. Si se cumplen todas las reglas y la confirmación coincide, se calcula `SHA-256(contraseña)`.
4. Se guarda el par `usuario: hash` en `users-db.json`.

**Inicio de sesión**

1. Se calcula el hash SHA-256 de la contraseña escrita.
2. Se compara con el hash guardado para ese usuario.
3. Si coinciden, se abre el panel, que muestra los dos hashes para comprobar que son iguales.

En ningún momento se descifra nada: un hash no se puede revertir, solo se puede volver a calcular y comparar.

## Reglas de contraseña

| Regla | Ejemplo que se rechaza |
|---|---|
| Mínimo 8 caracteres | `Ab#1x` |
| Al menos una mayúscula y una minúscula | `clave#99x` |
| Al menos un carácter especial | `ClaveSegura9` |
| Sin secuencias de 3 letras o números (ascendentes o descendentes) | `Xabc#9Tq`, `Tq#987Lz` |
| No incluye el nombre de usuario | usuario `pedro`, clave `Pedro#9Tq` |
| Sin espacios | `Tq#9 mLz` |

El nombre de usuario debe tener de 3 a 20 caracteres, solo letras sin acento, números o guion bajo. No se permiten nombres repetidos, aunque cambien mayúsculas y minúsculas.

## Ejemplo de `users-db.json`

```json
{
    "Prueba": "2d6095b66989cc372bb6eb96cd94ea7c6172a2d33e224493fb816d69c2a07e38"
}
```

Cada hash SHA-256 mide 64 caracteres hexadecimales (256 bits), sin importar la longitud de la contraseña.

## Medidas de seguridad implementadas

- **La contraseña nunca se escribe en disco**, solo su hash.
- **Comparación en tiempo constante** con `hmac.compare_digest`. Una comparación normal con `==` se detiene en el primer carácter distinto, y midiendo ese tiempo un atacante podría ir adivinando el hash.
- **No se revela si un usuario existe.** Si el usuario no está registrado, igual se hace la comparación contra un hash falso, y el mensaje de error es el mismo en ambos casos: "Usuario o contraseña incorrectos".
- **Guardado seguro del JSON.** Primero se escribe en un archivo temporal y después se reemplaza el original, para que no quede corrupto si el programa se cierra a la mitad.
- **Validación del JSON al cargarlo.** Si el archivo está dañado o tiene hashes inválidos, se muestra un aviso en lugar de sobrescribirlo.

## Limitaciones

- **No se usa sal.** Dos usuarios con la misma contraseña tienen el mismo hash, y contraseñas comunes pueden encontrarse en tablas precalculadas (*rainbow tables*). Se resolvería agregando una sal aleatoria distinta para cada usuario.
- **SHA-256 es muy rápido.** Eso lo hace bueno para verificar archivos, pero no para contraseñas, porque permite probar millones por segundo en un ataque de fuerza bruta. En un sistema real se usaría un algoritmo lento diseñado para contraseñas, como PBKDF2, bcrypt o Argon2.
- **El archivo JSON no está protegido.** Cualquiera con acceso a la carpeta puede leerlo o modificarlo.
