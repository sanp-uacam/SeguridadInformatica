# 67406 Login SQLi

Alumno: Moran Escalante Bryan Arturo

La consulta del login utiliza parámetros de SQLite para separar la sentencia de los valores recibidos.

## Ejecución

```sh
npm ci
npm test
npm start
```

Abrir http://localhost:3000. Cuentas de demostración: admin/admin y juan/1234.

La ruta histórica POST /login-vulnerable y POST /login-secure ejecutan la misma consulta parametrizada.

## Pruebas

La suite contiene 32 casos: tres controles de autenticación, 14 payloads SQLi, 12 validaciones de entrada y tres comprobaciones de JSON, rutas y publicación de archivos. Usa una base en memoria y un puerto local automático. Se verificó con Node.js 24.22.1.
