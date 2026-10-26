// npm install express sqlite3
// node server-seguro.js

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

  // CORREGIDO: El texto del usuario ya NO se mete
  // dentro del SQL, sino que viaja aparte como parametro.
  // Asi SQLite lo trata como dato y nunca como código, lo que elimina
  // la inyeccion SQL.
  const query = "SELECT * FROM users WHERE username = ? AND password = ?";

  db.get(query, [username, password], (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (row) return res.json({ ok: true, user: row.username });
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3000, () => console.log("http://localhost:3000"));
