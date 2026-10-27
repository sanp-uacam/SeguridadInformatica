/**
 * Login — versión SEGURA
 * -----------------------------------------------------------------------------
 * Corrige la inyección SQL de `server-vulnerable.js`.
 *
 * La causa de la vulnerabilidad era construir la consulta CONCATENANDO la
 * entrada del usuario dentro del texto SQL. Aquí ya no concateno: uso
 * CONSULTAS PREPARADAS (parametrizadas). La plantilla del SQL viaja con
 * marcadores `?` y los valores se mandan por separado, de modo que lo que
 * escribe el usuario se trata SIEMPRE como dato, nunca como código SQL.
 *
 * Ejecutar:
 *   npm install
 *   node server-seguro.js        ->  http://localhost:3001
 *
 * Práctica: 2do Parcial · Login SQL injection · Seguridad Informática · UACAM
 */

const express = require("express");
const sqlite3 = require("sqlite3").verbose();

const app = express();
app.use(express.json());
app.use(express.static(__dirname)); // sirve index.html / index-seguro.html

// ---------------------------------------------------------------------------
// Base de datos de prueba (en memoria), idéntica a la del servidor vulnerable.
// ---------------------------------------------------------------------------
const db = new sqlite3.Database(":memory:");
db.serialize(() => {
  db.run(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)",
  );
  db.run("INSERT INTO users (username, password) VALUES ('admin', 'admin')");
  db.run("INSERT INTO users (username, password) VALUES ('juan', '1234')");
});

// ---------------------------------------------------------------------------
// Endpoint de login seguro
// ---------------------------------------------------------------------------
app.post("/login-seguro", (req, res) => {
  const { username, password } = req.body;

  // Validación mínima: exijo que ambos campos existan y sean texto.
  if (typeof username !== "string" || typeof password !== "string") {
    return res.status(400).json({ ok: false, message: "Petición inválida" });
  }
  const u = username.trim();
  const p = password.trim();
  if (u.length === 0 || u.length > 64 || p.length === 0 || p.length > 64) {
    return res.status(400).json({ ok: false, message: "Usuario o contraseña con longitud inválida" });
  }

  // CORRECCIÓN: la plantilla SQL es FIJA y usa marcadores (?). El motor
  // compila primero la consulta y después inserta los valores como datos,
  // así una comilla ' o un -- en la entrada ya no cambian la consulta.
  const query = "SELECT * FROM users WHERE username = ? AND password = ?";

  console.log("Query preparada:", query);
  console.log("Parametros     :", [u, p]);

  db.get(query, [u, p], (err, row) => {
    if (err) {
      console.error("Error interno:", err.message);
      return res.status(500).json({ ok: false, message: "Error interno del servidor" });
    }
    if (row) return res.json({ ok: true, user: row.username });
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3001, () => console.log("http://localhost:3001"));
