// npm init -v
// npm install express sqlite3
// node server-vulnerable.js
//
// NOTA: este archivo tenia una inyeccion SQL en /login-vulnerable porque la
// consulta se construia concatenando la entrada del usuario. Se corrigio
// usando una consulta parametrizada (prepared statement) y validacion de
// entrada. Las evidencias de las pruebas (antes/despues) estan en
// login/evidencias/. El nombre del archivo se conserva.

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
  const { username, password } = req.body || {};

  // Validacion de entrada: solo aceptamos texto y campos no vacios.
  if (typeof username !== "string" || typeof password !== "string") {
    return res.status(400).json({ ok: false, message: "Datos inválidos" });
  }
  if (username.trim() === "" || password.trim() === "") {
    return res
      .status(400)
      .json({ ok: false, message: "Usuario y contraseña son obligatorios" });
  }

  // Correccion de la inyeccion SQL: consulta parametrizada.
  // Los "?" son marcadores de posicion; sqlite3 envia username y password
  // como DATOS, nunca como parte del texto SQL. Asi, comillas, "--" u
  // "OR 1=1" dejan de alterar la logica de la consulta.
  const query = "SELECT id, username FROM users WHERE username = ? AND password = ?";

  db.get(query, [username, password], (err, row) => {
    if (err) {
      // No devolvemos el error de la BD al cliente para no filtrar informacion.
      console.error("Error de base de datos:", err.message);
      return res.status(500).json({ ok: false, message: "Error interno" });
    }
    if (row) return res.json({ ok: true, user: row.username });
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3000, () => console.log("http://localhost:3000"));
