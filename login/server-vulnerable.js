
// npm init -v
// npm install express sqlite3
// node server-vulnerable.js
//
// NOTA (corrección aplicada): este archivo contenía una inyección SQL por
// concatenación de strings en /login-vulnerable. Se corrigió sustituyendo
// la query por una consulta parametrizada (prepared statement) y se
// agregó validación de entrada. El nombre del archivo y de la ruta se
// conservan tal cual por pedido explícito, pese a que ya no son
// vulnerables. Ver login/docs/INFORME-SQLI.md para el detalle completo
// (antes/después, pruebas de explotación y de verificación).

const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const app = express();
app.use(express.json());
app.use(express.static(__dirname));

const db = new sqlite3.Database(":memory:");


db.serialize(() => {
  db.run(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)",
  );
  db.run("INSERT INTO users (username, password) VALUES ('admin', 'admin')");
  db.run("INSERT INTO users (username, password) VALUES ('juan', '1234')");
});


app.post("/login-vulnerable", (req, res) => {
  const { username, password } = req.body ?? {};

  // --- Validación básica de entrada ---
  // Antes no existía: cualquier valor (incluido ausente/objeto/array)
  // llegaba directo a la query.
  if (typeof username !== "string" || typeof password !== "string") {
    return res.status(400).json({ ok: false, message: "Datos inválidos" });
  }
  if (username.trim() === "" || password.trim() === "") {
    return res
      .status(400)
      .json({ ok: false, message: "Usuario y contraseña son obligatorios" });
  }
  if (username.length > 100 || password.length > 100) {
    return res.status(400).json({ ok: false, message: "Datos inválidos" });
  }

  // --- Consulta parametrizada (prepared statement) ---
  // ANTES (vulnerable a SQLi):
  //   const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
  //   db.get(query, (err, row) => { ... });
  // AHORA: los "?" son placeholders; sqlite3 envía username/password como
  // datos, nunca como parte del texto SQL. Comillas, "--", "OR 1=1", etc.
  // ya no pueden alterar la lógica de la consulta.
  const query = "SELECT * FROM users WHERE username = ? AND password = ?";
  console.log(
    `Intento de login -> query fija: ${query} | username recibido (como dato, no como SQL): ${JSON.stringify(username)}`,
  );

  db.get(query, [username, password], (err, row) => {
    if (err) {
      // ANTES se devolvía err.message al cliente (fuga de información del
      // motor de BD). AHORA solo se loguea en el servidor.
      console.error("Error de base de datos:", err.message);
      return res.status(500).json({ ok: false, message: "Error interno" });
    }
    if (row) {
      console.log(`  -> resultado: ACEPTADO como "${row.username}"`);
      return res.json({ ok: true, user: row.username });
    }
    console.log("  -> resultado: RECHAZADO (credenciales inválidas)");
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3000, () => console.log("http://localhost:3000"));
