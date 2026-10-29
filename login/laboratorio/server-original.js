
// npm init -v
// npm install express sqlite3
// node server-vulnerable.js

const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const app = express();
app.use(express.json());
app.get("/", (req, res) => res.sendFile(path.join(__dirname, "..", "index.html")));

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


  const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;

  console.log("Query ejecutada:", query); 

  db.get(query, (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (row) return res.json({ ok: true, user: row.username });
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3001, "127.0.0.1", () => console.log("LABORATORIO VULNERABLE: http://127.0.0.1:3001"));
