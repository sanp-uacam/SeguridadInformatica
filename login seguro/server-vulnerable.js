
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

// Crear base de datos de prueba
db.serialize(() => {
  db.run(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
  );

  db.run(
    "INSERT INTO users (username, password) VALUES ('admin', 'admin')"
  );

  db.run(
    "INSERT INTO users (username, password) VALUES ('juan', '1234')"
  );
});

// LOGIN PROTEGIDO CONTRA SQL INJECTION
// Se conserva la ruta original para no modificar index.html

app.post("/login-vulnerable", (req, res) => {
  const { username, password } = req.body || {};

  // Validar los datos recibidos
  if (
    typeof username !== "string" ||
    typeof password !== "string" ||
    !username ||
    !password
  ) {
    return res.status(400).json({
      ok: false,
      message: "Usuario y contraseña requeridos"
    });
  }

  // Consulta SQL parametrizada
  const query =
    "SELECT id, username FROM users WHERE username = ? AND password = ?";

  // Los parámetros se envían separados de la consulta
  db.get(query, [username, password], (err, row) => {
    if (err) {
      console.error("Error de base de datos:", err.message);

      return res.status(500).json({
        ok: false,
        message: "Error interno del servidor"
      });
    }

    if (row) {
      return res.json({
        ok: true,
        user: row.username
      });
    }

    return res.status(401).json({
      ok: false,
      message: "Credenciales inválidas"
    });
  });
});

// Iniciar servidor
app.listen(3000, () => {
  console.log("Servidor protegido en http://localhost:3000");
});
