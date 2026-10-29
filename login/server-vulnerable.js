// Nombre conservado por compatibilidad; el login está parametrizado.
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('node:path');
async function createApp() {
  const db = new sqlite3.Database(':memory:');
  const run = (sql, params = []) => new Promise((resolve, reject) => db.run(sql, params, e => e ? reject(e) : resolve()));
  try {
    await run('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)');
    await run('INSERT INTO users (username, password) VALUES (?, ?)', ['admin', 'admin']);
    await run('INSERT INTO users (username, password) VALUES (?, ?)', ['juan', '1234']);
  } catch (error) { db.close(); throw error; }
  const app = express();
  app.use(express.json({ limit: '8kb' }));
  app.get(['/', '/index.html'], (_req, res) => res.sendFile(path.join(__dirname, 'index.html')));
  app.post(['/login-vulnerable', '/login-seguro'], (req, res) => {
    const { username, password } = req.body || {};
    if (typeof username !== 'string' || typeof password !== 'string') {
      return res.status(400).json({ ok: false, message: 'Usuario y contraseña deben ser texto' });
    }
    if (!username.trim() || !password.trim() || username.length > 100 || password.length > 100) {
      return res.status(400).json({ ok: false, message: 'Los campos deben contener de 1 a 100 caracteres' });
    }
    // Se comparan los valores exactos; no se recorta la contraseña.
    const query = 'SELECT username FROM users WHERE username = ? AND password = ?';
    db.get(query, [username, password], (error, row) => {
      if (error) return res.status(500).json({ ok: false, message: 'Error interno del servidor' });
      if (row) return res.json({ ok: true, user: row.username });
      return res.status(401).json({ ok: false, message: 'Credenciales inválidas' });
    });
  });
  app.use((error, _req, res, _next) => {
    const status = error.type === 'entity.too.large' ? 413 : error.type === 'entity.parse.failed' ? 400 : 500;
    res.status(status).json({ ok: false, message: status === 500 ? 'Error interno del servidor' : 'Petición JSON inválida o demasiado grande' });
  });
  return { app, db };
}
if (require.main === module) {
  createApp().then(({ app }) => {
    app.listen(Number(process.env.PORT || 3000), '127.0.0.1', () => console.log('LOGIN SEGURO: http://127.0.0.1:' + (process.env.PORT || 3000)));
  }).catch(() => { console.error('No se pudo iniciar la base de datos'); process.exitCode = 1; });
}
module.exports = { createApp };
