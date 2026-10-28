const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('node:path');

const LOGIN_QUERY = 'SELECT username FROM users WHERE username = ? AND password = ?';

async function createApp() {
  const db = new sqlite3.Database(':memory:');
  await new Promise((resolve, reject) => {
    db.serialize(() => {
      db.run('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)');
      db.run('INSERT INTO users (username, password) VALUES (?, ?)', ['admin', 'admin']);
      db.run('INSERT INTO users (username, password) VALUES (?, ?)', ['juan', '1234'], error => error ? reject(error) : resolve());
    });
  });
  const app = express();
  app.use(express.json({ limit: '8kb' }));
  app.get('/', (_req, res) => res.sendFile(path.join(__dirname, 'index.html')));
  app.post(['/login-vulnerable', '/login-secure'], (req, res) => {
    const { username, password } = req.body || {};
    if (typeof username !== 'string' || typeof password !== 'string' ||
        !username.trim() || !password.trim() || username.length > 100 || password.length > 100) {
      return res.status(400).json({ ok: false, message: 'Completa usuario y contraseña con datos válidos.' });
    }
    // Los valores se enlazan como datos y no forman parte del texto SQL.
    db.get(LOGIN_QUERY, [username, password], (error, row) => {
      if (error) return res.status(500).json({ ok: false, message: 'Error interno del servidor.' });
      if (row) return res.json({ ok: true, user: row.username });
      return res.status(401).json({ ok: false, message: 'Credenciales inválidas' });
    });
  });
  app.use((error, _req, res, _next) => {
    if (error.type === 'entity.parse.failed' || error.type === 'entity.too.large') {
      return res.status(400).json({ ok: false, message: 'Petición JSON inválida.' });
    }
    return res.status(500).json({ ok: false, message: 'Error interno del servidor.' });
  });
  return { app, db };
}

if (require.main === module) {
  createApp().then(({ app }) => {
    const port = Number(process.env.PORT || 3000);
    app.listen(port, '127.0.0.1', () => console.log(`Login parametrizado disponible en http://localhost:${port}`));
  }).catch(() => { console.error('No se pudo iniciar la aplicación.'); process.exitCode = 1; });
}
module.exports = { createApp, LOGIN_QUERY };
