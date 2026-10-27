// LABORATORIO EDUCATIVO - VERSION SEGURA
// Sin dependencias externas: modulo http nativo + node:sqlite (Node >=22).
// Misma ruta POST /login-vulnerable y puerto 3000, para que index.html funcione sin cambios.
// Correcciones: consultas parametrizadas, validacion de entrada, manejo seguro de errores
// (sin filtrar SQL/trazas/mensajes internos) y contrasenas con hash salado (scrypt, KDF integrado).
// Ejecutar:  node server-seguro.js   ->  http://localhost:3000

const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { DatabaseSync } = require("node:sqlite");

// --- Hashing de contrasenas con scrypt (KDF memory-hard integrado) ---
// Formato almacenado: scrypt$<salt_hex>$<hash_hex>
function hashPassword(plain) {
  const salt = crypto.randomBytes(16);
  const derived = crypto.scryptSync(plain, salt, 32);
  return `scrypt$${salt.toString("hex")}$${derived.toString("hex")}`;
}
function verifyPassword(plain, stored) {
  try {
    const [scheme, saltHex, hashHex] = String(stored).split("$");
    if (scheme !== "scrypt" || !saltHex || !hashHex) return false;
    const salt = Buffer.from(saltHex, "hex");
    const expected = Buffer.from(hashHex, "hex");
    const derived = crypto.scryptSync(plain, salt, expected.length);
    return expected.length === derived.length && crypto.timingSafeEqual(expected, derived);
  } catch { return false; }
}

const db = new DatabaseSync(":memory:");
db.exec("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)");
const seed = db.prepare("INSERT INTO users (username, password) VALUES (?, ?)");
seed.run("admin", hashPassword("admin"));   // credenciales demo, ahora como hash salado
seed.run("juan", hashPassword("1234"));

function send(res, code, obj) {
  res.writeHead(code, { "Content-Type": "application/json" });
  res.end(JSON.stringify(obj));
}

const server = http.createServer((req, res) => {
  if (req.method === "GET" && (req.url === "/" || req.url === "/index.html")) {
    return fs.readFile(path.join(__dirname, "index.html"), (e, data) => {
      if (e) { res.writeHead(404); return res.end("not found"); }
      res.writeHead(200, { "Content-Type": "text/html" }); res.end(data);
    });
  }

  if (req.method === "POST" && req.url === "/login-vulnerable") {
    let raw = "";
    let tooBig = false;
    req.on("data", (c) => { raw += c; if (raw.length > 10000) { tooBig = true; req.destroy(); } });
    req.on("end", () => {
      if (tooBig) return send(res, 413, { ok: false, message: "Petición demasiado grande" });

      // 1) Parseo controlado de JSON
      let body;
      try { body = JSON.parse(raw || "null"); }
      catch { return send(res, 400, { ok: false, message: "JSON inválido" }); }

      // 2) Validacion de presencia y tipo
      const username = body && body.username;
      const password = body && body.password;
      if (typeof username !== "string" || typeof password !== "string" ||
          username.length === 0 || password.length === 0 ||
          username.length > 64 || password.length > 128) {
        return send(res, 400, { ok: false, message: "Usuario y contraseña son obligatorios" });
      }

      // 3) Autenticacion con consulta PARAMETRIZADA (la entrada nunca se concatena al SQL)
      try {
        const row = db.prepare("SELECT id, username, password FROM users WHERE username = ?").get(username);
        if (row && verifyPassword(password, row.password)) {
          return send(res, 200, { ok: true, user: row.username });
        }
        // Mismo resultado para usuario inexistente o contrasena incorrecta
        return send(res, 401, { ok: false, message: "Credenciales inválidas" });
      } catch (err) {
        console.error("[seguro] error interno:", err.message);  // no se filtra al cliente
        return send(res, 500, { ok: false, message: "Error interno del servidor" });
      }
    });
    return;
  }

  res.writeHead(404); res.end("not found");
});

server.listen(3000, () => console.log("http://localhost:3000"));
