# 72966_CERVANTES - Login SQL injection

David Cervantes Malfavon

El login se corrigió mediante consultas parametrizadas de SQLite. Se compararon 16 entradas contra la consulta original: 12 consiguieron acceso indebido, tres provocaron errores SQL y una fue rechazada como control. La versión corregida rechazó las 16; los accesos normales siguen funcionando.

## Instalación y ejecución

Requiere Node.js y npm. Se verificó con Node.js 24.11.0 y npm 11.6.1.

Desde esta carpeta:

```bash
npm ci
npm test
npm run compare
npm start
```

La versión corregida abre en http://127.0.0.1:3000. Conserva el archivo `server-vulnerable.js` y la ruta `/login-vulnerable` por compatibilidad; su consulta usa `?` y valores separados. `/login-seguro` ejecuta la misma lógica.

Para comparar en el navegador, en otra terminal:

```bash
npm run lab:vulnerable
```

La copia original de laboratorio abre en http://127.0.0.1:3001. Esa copia mantiene intencionalmente la consulta vulnerable para reproducir los resultados; no es el servidor predeterminado. Ambos escuchan solo en la interfaz local. `npm run compare` inicia y cierra sus propios servidores y necesita libre el puerto 3001: cierra primero la demostración manual si está abierta.

Cuentas de demostración: `admin` / `admin` y `juan` / `1234`. El formulario muestra la contraseña en texto para registrar el payload y distinguir las pruebas.

## Corrección

```js
const query = 'SELECT username FROM users WHERE username = ? AND password = ?';
db.get(query, [username, password], (error, row) => { /* respuesta */ });
```

Se validan tipo, campos vacíos y longitud máxima de 100 caracteres. Las contraseñas se comparan sin recortar sus espacios. Se controlan JSON mal formado, cuerpos de más de 8 KB y errores internos. La carpeta completa ya no se publica por HTTP; el servidor entrega únicamente el formulario en sus rutas previstas.

## Archivos y evidencias

- [Reporte PDF](Reporte_72966_CERVANTES.pdf): resultados, explicación, código, conclusiones y diez capturas organizadas en cinco comparaciones.
- [Reporte en Markdown](REPORTE_72966_CERVANTES.md).
- [Índice de las 17 capturas](evidencias/INDICE.md).
- [Resultados HTTP completos](evidencias/resultados-comparacion.json).
- [Registro de 45 pruebas aprobadas](evidencias/pruebas-automatizadas.txt).
- [Registro de comparación](evidencias/comparacion-http.txt).
- `tests/payloads.cjs`: entradas exactas, incluidos espacios finales.
- `tests/login.test.cjs`: controles de autenticación, inyección, validación y publicación de archivos.
- `tests/compare.cjs`: comparación reproducible por HTTP, con comprobaciones de los resultados originales y corregidos.
- `laboratorio/server-original.js`: consulta original del commit `c3d7fa16fdd6447ed29866f636e86fc8dd025721`, con cambios de puerto, escucha local y entrega del formulario.

## Alcance

Las pruebas se ejecutaron sobre SQLite en memoria y cuentas de demostración locales. No existe gestión de sesiones ni almacenamiento seguro de contraseñas en este ejercicio. La corrección documentada corresponde a SQL injection y las validaciones descritas.
