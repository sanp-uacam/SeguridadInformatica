const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const app = express();
app.use(express.json());
app.use(express.static(__dirname));

const db = new sqlite3.Database(":memory:");

db.serialize(() => {
  db.run(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
  );
  db.run("INSERT INTO users (username, password) VALUES (?, ?)", ["admin", "admin"]);
  db.run("INSERT INTO users (username, password) VALUES (?, ?)", ["juan", "1234"]);
});

app.post("/login-vulnerable", (req, res) => {
  const { username, password } = req.body;

  // 1. Validación básica de entrada (evita inyección de objetos JSON o valores vacíos)
  if (typeof username !== "string" || typeof password !== "string") {
    return res.status(400).json({ ok: false, message: "Formato de datos inválido" });
  }

  // 2. Consulta parametrizada (Prepared Statement) usando '?'
  const query = "SELECT * FROM users WHERE username = ? AND password = ?";

  console.log("Ejecutando query parametrizada con valores:", [username, password]);

  // Se pasan los parámetros en un arreglo como segundo argumento
  db.get(query, [username, password], (err, row) => {
    if (err) {
      // 3. No exponer detalles técnicos de la base de datos al cliente
      console.error("Error interno de BD:", err.message);
      return res.status(500).json({ ok: false, message: "Error interno del servidor" });
    }
    
    if (row) {
      return res.json({ ok: true, user: row.username });
    }
    
    res.status(401).json({ ok: false, message: "Credenciales inválidas" });
  });
});

app.listen(3000, () => console.log("Servidor seguro en http://localhost:3000"));