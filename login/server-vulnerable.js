
// npm init -v
// npm install express sqlite3
// node server-vulnerable.js

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
  const body = req.body;
  if (body === null || typeof body !== "object" || Array.isArray(body)) {
    return res.status(400).json({ ok: false, message: "Solicitud inválida" });
  }

  const { username, password } = body;
  if (typeof username !== "string" || typeof password !== "string") {
    return res.status(400).json({ ok: false, message: "Solicitud inválida" });
  }

  const query = "SELECT * FROM users WHERE username = ? AND password = ?";

  db.get(query, [username, password], (err, row) => {
    if (err) {
      console.error("Error al consultar las credenciales:", err);
      return res.status(500).json({ ok: false, message: "Error interno" });
    }
    if (row) return res.json({ ok: true, user: row.username });
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3000, () => console.log("http://localhost:3000"));
