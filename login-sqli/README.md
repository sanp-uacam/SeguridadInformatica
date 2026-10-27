# Login SQLi — Demo y corrección

Práctica de Seguridad Informática: detección de inyección SQL en un login y su corrección
por parametrización.

- `index.html` — formulario del login (envía a `/login-vulnerable`).
- `server-vulnerable.js` — versión **vulnerable** (puerto 3000).
- `server-seguro.js` — versión **corregida / parametrizada** (puerto 3001).
- `REPORTE.md` — reporte: payloads, por qué funcionan, corrección y conclusiones.

## Requisitos

- Node.js (incluye npm). Descargar de https://nodejs.org (versión LTS).

## Instalación

```bash
npm install
```

(equivale a `npm install express sqlite3`)

## Ejecutar

Versión vulnerable:

```bash
npm run vulnerable
```

Luego abrir http://localhost:3000

Versión segura (en otra terminal, al mismo tiempo):

```bash
npm run seguro
```

Luego abrir http://localhost:3001

## Cómo probar la inyección

En el formulario, en el campo **Usuario**, escribir uno de los payloads del reporte, por ejemplo:

- `admin' --`  (contraseña: cualquier cosa) → entra como admin
- `' OR '1'='1`  (en usuario y contraseña) → entra como admin

Contra `server-vulnerable.js` (3000) **funcionan**; contra `server-seguro.js` (3001)
responden `401 Credenciales inválidas`.
