const crypto = require("crypto");
const express = require("express");
const sqlite3 = require("sqlite3").verbose();

const app = express();
app.use(express.json({ limit: "1kb" }));
app.use(express.static(__dirname));

const db = new sqlite3.Database(":memory:");

db.serialize(() => {
  db.run(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, password_salt TEXT NOT NULL)",
  );
  const insertUser = db.prepare(
    "INSERT INTO users (username, password_hash, password_salt) VALUES (?, ?, ?)",
  );
  insertUser.run("admin", ...hashPassword("admin"));
  insertUser.run("juan", ...hashPassword("1234"));
  insertUser.finalize();
});

function hashPassword(password, salt = crypto.randomBytes(16)) {
  const passwordHash = crypto.scryptSync(password, salt, 64);
  return [passwordHash.toString("hex"), salt.toString("hex")];
}

function isValidCredentials(body) {
  return (
    body &&
    typeof body === "object" &&
    !Array.isArray(body) &&
    typeof body.username === "string" &&
    typeof body.password === "string" &&
    body.username.length >= 1 &&
    body.username.length <= 64 &&
    body.password.length >= 1 &&
    body.password.length <= 128
  );
}

function loginHandler(req, res) {
  if (!isValidCredentials(req.body)) {
    return res.status(400).json({ ok: false, message: "Datos de login inválidos" });
  }

  const { username, password } = req.body;

  db.get(
    "SELECT username, password_hash, password_salt FROM users WHERE username = ?",
    [username],
    (err, row) => {
      if (err) {
        console.error("Error al consultar el usuario:", err);
        return res.status(500).json({ ok: false, message: "Error interno" });
      }

      let passwordMatches = false;
      if (row) {
        try {
          const [candidateHash] = hashPassword(
            password,
            Buffer.from(row.password_salt, "hex"),
          );
          const storedHash = Buffer.from(row.password_hash, "hex");
          const candidateHashBuffer = Buffer.from(candidateHash, "hex");
          passwordMatches =
            storedHash.length === candidateHashBuffer.length &&
            crypto.timingSafeEqual(storedHash, candidateHashBuffer);
        } catch (hashError) {
          console.error("Error al verificar la contraseña:", hashError);
          return res.status(500).json({ ok: false, message: "Error interno" });
        }
      }

      if (passwordMatches) {
        return res.json({ ok: true, user: row.username });
      }
      return res.status(401).json({ ok: false, message: "Credenciales inválidas" });
    },
  );
}

app.post(["/login", "/login-vulnerable"], loginHandler);

app.use((err, req, res, next) => {
  if (err.type === "entity.parse.failed" || err.type === "entity.too.large") {
    return res.status(400).json({ ok: false, message: "Solicitud inválida" });
  }
  return next(err);
});

app.listen(3000, () => {
  console.log("http://localhost:3000");
});
