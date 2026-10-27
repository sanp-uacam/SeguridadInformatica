# Inyección SQL en un login

**Autor:** Daniel A. Esquivel Gómez · **Fecha:** 2026-10-26

## 1. Payloads que funcionan

Estos dos payloads entran como `admin` sin conocer la contraseña:

| Payload en `username` | Resultado |
|---|---|
| `admin' OR '1'='1` | HTTP 200, entra como admin |
| `' OR 1=1 -- ` | HTTP 200, entra como admin |

## 2. Por qué funcionan

El servidor pega lo que escribes directamente dentro de la consulta SQL:

```sql
SELECT * FROM users WHERE username = '<tu entrada>' AND password = '<tu entrada>'
```

- **`OR '1'='1'`** añade una condición siempre verdadera, así la consulta devuelve una fila aunque la contraseña sea incorrecta.
- **`--`** es un comentario en SQL: borra el resto de la consulta, incluida la comprobación de contraseña.

La causa es la misma: **la entrada se trata como código SQL y no como un dato.**

## 3. Corrección: consulta parametrizada

Antes (vulnerable):

```js
const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
```

Después (segura):

```js
const row = db.prepare("SELECT id, username, password FROM users WHERE username = ?").get(username);
```

El `?` deja un hueco para el valor. La entrada llega como **dato puro**, así que `admin' OR '1'='1` se busca literalmente como nombre de usuario y no existe.

Además, la versión segura: valida los campos, no muestra errores internos y guarda las contraseñas con hash (scrypt).

## 4. Resultados

| Prueba | Vulnerable | Segura |
|---|---|---|
| Login normal (admin/admin) | 200 | 200 |
| Payload `OR '1'='1` | 200 (entra) | 401 (bloqueado) |
| Payload `--` | 200 (entra) | 401 (bloqueado) |

## 5. Conclusiones

- Concatenar la entrada del usuario en SQL permite alterar la consulta y saltarse el login.
- Usar consultas parametrizadas (`?`) elimina el problema de raíz.
- Nunca mostrar errores internos al usuario ni guardar contraseñas en texto plano.
