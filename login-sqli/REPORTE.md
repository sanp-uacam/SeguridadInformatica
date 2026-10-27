# Reporte — 2do Parcial: Login e Inyección SQL

**Alumno:** Kevin Javier Ruiz Tillit
**Usuario / matrícula:** 64134_ruiz
**Materia:** Seguridad Informática
**Práctica:** Detección de vulnerabilidades de inyección SQL en un login y corrección mediante parametrización.

---

## 1. Contexto y objetivo

Se analiza un login de demostración (Node.js + Express + SQLite en memoria) que autentica
usuarios contra una tabla `users`. El objetivo es:

1. Detectar la(s) vulnerabilidad(es) de **inyección SQL (SQLi)**.
2. Demostrar con **payloads que funcionan** y explicar **por qué** funcionan.
3. **Corregir** la vulnerabilidad mediante **parametrización** de la consulta (prepared statements).
4. Conclusiones.

**Datos de prueba (seed de la base):**

| id | username | password |
|----|----------|----------|
| 1  | admin    | admin    |
| 2  | juan     | 1234     |

---

## 2. La vulnerabilidad

El endpoint `POST /login-vulnerable` construye la consulta SQL **concatenando directamente**
la entrada del usuario dentro del texto SQL mediante un *template literal*:

```js
const { username, password } = req.body;

// ❌ VULNERABLE
const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;

db.get(query, (err, row) => { ... });
```

**Problema:** no hay separación entre **código** (la instrucción SQL) y **datos** (lo que
teclea el usuario). Todo lo que el usuario escriba se vuelve parte de la consulta. Si la
entrada contiene caracteres especiales de SQL —comilla simple `'`, guiones de comentario
`--`, operadores lógicos `OR`, `UNION`— el atacante puede **cerrar la cadena y reescribir la
lógica de la consulta**.

Debilidades adicionales observadas:

- **Contraseñas en texto plano** en la base de datos (sin hash).
- **Fuga de errores SQL** al cliente: `res.status(500).json({ error: err.message })` revela
  mensajes internos del motor, útiles para un atacante.
- Se seleccionan **todas las columnas** (`SELECT *`), incluida `password`.

---

## 3. Payloads que funcionan (y por qué)

> Para cada payload se muestra la **consulta final** que se arma en el servidor y el efecto.
> Todos se prueban en el formulario del login (campos Usuario / Contraseña) o enviando el
> JSON directamente al endpoint `/login-vulnerable`.

### Payload 1 — Bypass con comentario `--` (entrar como admin sin contraseña)

| Campo | Valor |
|-------|-------|
| Usuario | `admin' --` |
| Contraseña | *(cualquier cosa, p. ej. `x`)* |

Consulta resultante:

```sql
SELECT * FROM users WHERE username = 'admin' --' AND password = 'x'
```

**Por qué funciona:** la comilla cierra el literal del `username` justo después de `admin`;
el `--` inicia un **comentario de línea en SQL**, por lo que todo lo que sigue (incluido
`AND password = '...'`) **se ignora**. La consulta queda efectivamente como
`WHERE username = 'admin'` → devuelve la fila de admin → **inicia sesión como admin sin saber
la contraseña**. Respuesta: `{ "ok": true, "user": "admin" }`.

> Nota: también sirve para suplantar a cualquier usuario conocido, p. ej. `juan' --`.

### Payload 2 — Tautología `OR '1'='1'` (condición siempre verdadera)

| Campo | Valor |
|-------|-------|
| Usuario | `' OR '1'='1` |
| Contraseña | `' OR '1'='1` |

Consulta resultante:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '' OR '1'='1'
```

**Por qué funciona:** `'1'='1'` es **siempre verdadero**, así que el `WHERE` se cumple para
las filas de la tabla. Como el servidor usa `db.get(...)`, devuelve **la primera fila**
(`admin`) → **inicia sesión como admin**. Es la inyección "clásica" de bypass de login.

### Payload 3 — `OR 1=1` + comentario (variante robusta)

| Campo | Valor |
|-------|-------|
| Usuario | `' OR 1=1 --` |
| Contraseña | *(vacío o cualquier cosa)* |

Consulta resultante:

```sql
SELECT * FROM users WHERE username = '' OR 1=1 --' AND password = ''
```

**Por qué funciona:** `OR 1=1` vuelve la condición siempre verdadera y `--` comenta el resto,
eliminando la verificación de contraseña. Devuelve la primera fila (`admin`). Es más robusto
porque no depende de las comillas del campo password.

### Payload 4 — Forjar datos con `UNION SELECT` (avanzado: confirmar control total)

| Campo | Valor |
|-------|-------|
| Usuario | `zzz' UNION SELECT 1,'hacker','x' -- ` |
| Contraseña | *(cualquier cosa)* |

Consulta resultante:

```sql
SELECT * FROM users WHERE username = 'zzz' UNION SELECT 1,'hacker','x' --' AND password = '...'
```

**Por qué funciona:** `username = 'zzz'` no existe, así que la parte izquierda del `UNION` no
devuelve nada; la derecha inyecta una **fila falsa** con 3 columnas (porque la tabla tiene 3:
id, username, password). `db.get` devuelve esa fila forjada → respuesta
`{ "ok": true, "user": "hacker" }`. Esto demuestra que no solo se puede saltar el login, sino
**inyectar/leer datos arbitrarios** (base de las técnicas UNION-based para exfiltrar
información de otras tablas).

---

## 4. Corrección: parametrización de la consulta (prepared statement)

La solución correcta es **separar el código SQL de los datos** usando **parámetros `?`**
(prepared statement). El texto SQL queda fijo y la entrada del usuario viaja aparte, en el
arreglo de parámetros; el driver la trata **siempre como valor literal**, nunca como SQL
ejecutable:

```js
app.post("/login-vulnerable", (req, res) => {
  const { username, password } = req.body;

  // ✅ SEGURO: consulta parametrizada
  const query =
    "SELECT username FROM users WHERE username = ? AND password = ?";

  db.get(query, [username, password], (err, row) => {
    if (err) {
      console.error("Error en DB:", err.message);      // no se filtra al cliente
      return res.status(500).json({ ok: false, message: "Error interno del servidor" });
    }
    if (row) return res.json({ ok: true, user: row.username });
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});
```

**Qué cambió y por qué corrige la vulnerabilidad:**

| Antes (vulnerable) | Después (seguro) | Efecto |
|--------------------|------------------|--------|
| `` `... username = '${username}' ...` `` (interpolación) | `... username = ? AND password = ?` + `[username, password]` | La entrada ya **no** puede alterar la estructura de la consulta. |
| `SELECT *` | `SELECT username` | No se exponen columnas sensibles (password). |
| `res.json({ error: err.message })` | mensaje genérico + `console.error` | No se filtran detalles internos del motor al cliente. |

Con esto, si se envía `admin' --` o `' OR '1'='1`, el motor busca **literalmente** un usuario
cuyo nombre sea esa cadena completa (que no existe) → la inyección **falla** y responde
`401 Credenciales inválidas`.

**Mejoras recomendadas adicionales (buenas prácticas):**

- **Hashear** contraseñas (p. ej. `bcrypt`) en lugar de guardarlas en texto plano.
- **Validar/normalizar** la entrada (longitud, formato) como capa extra.
- **Mínimo privilegio** para el usuario de base de datos.
- No exponer mensajes de error detallados al usuario final.

---

## 5. Evidencias (capturas)

Todas las pruebas se ejecutaron en vivo, levantando ambos servidores en localhost
(vulnerable en el puerto 3000 y seguro en el puerto 3001) con la base de datos en memoria
(`admin`/`admin`, `juan`/`1234`). Capturas en la carpeta `/capturas`:

1. **`01-vulnerable-payload1-admin-bypass.jpg`** — Login vulnerable (puerto 3000) con el
   payload `admin' --` → respuesta `{ "ok": true, "user": "admin" }`. Bypass exitoso sin
   conocer la contraseña.
2. **`02-vulnerable-payload2-or-1equal1.png`** — Payload `' OR '1'='1` en usuario y
   contraseña → `{ "ok": true, "user": "admin" }`. Tautología clásica.
3. **`03-vulnerable-payload4-union-select.png`** — Payload
   `zzz' UNION SELECT 1,'hacker','x' --` → `{ "ok": true, "user": "hacker" }`. Se **forjó**
   una fila inexistente: la respuesta nunca debería mostrar un usuario "hacker".
4. **`04-seguro-payload-bloqueado.png`** — El **mismo** payload `admin' --` contra el login
   **seguro** (puerto 3001, consulta parametrizada) → `{ "ok": false, "message":
   "Credenciales inválidas" }` (HTTP 401). La inyección queda neutralizada.
5. **`05-seguro-login-legitimo-funciona.png`** — Login legítimo `admin`/`admin` contra el
   servidor seguro → `{ "ok": true, "user": "admin" }`. Confirma que la corrección **no
   rompe** el funcionamiento normal del login.
6. **`06-log-consola-queries-inyectadas.txt`** — Log de consola del servidor vulnerable
   (`console.log("Query ejecutada:", query)`) mostrando, en texto, cada consulta SQL ya
   modificada por la inyección antes de ejecutarse contra la base de datos.

---

## 6. Conclusiones

- La causa raíz de la inyección SQL es **mezclar código y datos**: construir el SQL
  concatenando directamente la entrada del usuario. Un simple `'` o `--` permite reescribir la
  lógica de la consulta y **saltarse la autenticación** o incluso **forjar/leer datos**.
- La corrección efectiva y estándar es la **parametrización (prepared statements)**: el SQL es
  fijo y los datos viajan como parámetros, por lo que la entrada nunca se ejecuta como código.
  Con el mismo payload que antes vulneraba el login, ahora se obtiene `401`.
- La seguridad se refuerza con medidas complementarias: **hash** de contraseñas, **no filtrar
  errores internos**, seleccionar solo las columnas necesarias, validación de entrada y
  mínimo privilegio en la base de datos. La defensa en profundidad reduce el impacto aunque
  una capa falle.
