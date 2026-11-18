// Version SEGURA del login.
// Correccion de la inyeccion SQL mediante consultas PARAMETRIZADAS.
//
// npm install express sqlite3
// node server-secure.js

const express = require("express");
const sqlite3 = require("sqlite3").verbose();

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

  // CORRECCION: la consulta ya NO concatena la entrada del usuario.
  // Se usan marcadores de posicion (?) y los valores se pasan por separado.
  // El motor de la base de datos trata username y password SIEMPRE como
  // datos, nunca como parte del codigo SQL, por lo que una comilla o un
  // "OR 1=1" dejan de alterar la consulta.
  const query = "SELECT * FROM users WHERE username = ? AND password = ?";

  db.get(query, [username, password], (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (row) return res.json({ ok: true, user: row.username });
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3000, () => console.log("http://localhost:3000"));
