// ==========================================================================
//  server-vulnerable.js  —  VERSIÓN VULNERABLE (NO USAR EN PRODUCCIÓN)
//  Demo educativa de inyección SQL para Seguridad Informática.
//
//  Instalación:
//    npm init -y
//    npm install express sqlite3
//    node server-vulnerable.js
//
//  La query se construye concatenando la entrada del usuario directamente
//  dentro del string SQL (template literal), por lo que es vulnerable a SQLi.
// ==========================================================================

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
  const { username, password } = req.body;

  // ❌ VULNERABLE: la entrada del usuario se interpola directamente en el SQL.
  const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;

  console.log("Query ejecutada:", query);

  db.get(query, (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (row) return res.json({ ok: true, user: row.username });
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3000, () =>
  console.log("VULNERABLE escuchando en http://localhost:3000"),
);
