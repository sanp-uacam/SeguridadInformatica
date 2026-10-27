// ==========================================================================
//  server-seguro.js  —  VERSIÓN SEGURA (corrección de la vulnerabilidad)
//
//  Instalación:
//    npm install express sqlite3
//    node server-seguro.js
//
//  Corrección principal: CONSULTA PARAMETRIZADA (prepared statement).
//  Los datos del usuario se pasan como parámetros (?) separados del texto
//  SQL, por lo que el motor nunca los interpreta como código.
//
//  Escucha en el puerto 3001 para poder correr la versión vulnerable (3000)
//  y la segura (3001) al mismo tiempo y comparar el "antes y después".
//  Usa el mismo index.html (endpoint /login-vulnerable) para la demo.
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

  // ✅ SEGURO: consulta parametrizada. El SQL es fijo; la entrada del
  // usuario viaja aparte, en el arreglo de parámetros, y SIEMPRE se trata
  // como dato (valor literal), nunca como código SQL ejecutable.
  const query =
    "SELECT username FROM users WHERE username = ? AND password = ?";

  db.get(query, [username, password], (err, row) => {
    if (err) {
      // No se filtra el detalle del error SQL al cliente.
      console.error("Error en DB:", err.message);
      return res
        .status(500)
        .json({ ok: false, message: "Error interno del servidor" });
    }

    if (row) {
      return res.json({ ok: true, user: row.username });
    }
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3001, () =>
  console.log("SEGURO escuchando en http://localhost:3001"),
);
