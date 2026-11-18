const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const path = require('node:path');
const { test } = require('node:test');

const baseUrl = 'http://127.0.0.1:3000';
const fixture = { username: 'admin', password: 'admin' };
const unauthorized = { ok: false, message: 'Credenciales inválidas' };
const invalid = { ok: false, message: 'Datos inválidos' };
const incompleteCases = [
  ['Usuario omitido', { password: fixture.password }],
  ['Contraseña omitida', { username: fixture.username }],
  ['Ambos campos omitidos', {}],
  ['Usuario vacío', { ...fixture, username: '' }],
  ['Contraseña vacía', { ...fixture, password: '' }],
  ['Usuario con espacios solamente', { ...fixture, username: '   ' }],
  ['Contraseña con espacios solamente', { ...fixture, password: '   ' }],
  ['Usuario nulo', { ...fixture, username: null }],
  ['Contraseña nula', { ...fixture, password: null }],
];

for (const [file, incompleteStatus, incompleteResponse] of [
  ['server-vulnerable.js', 401, unauthorized],
  ['server-corregido.js', 400, invalid],
]) {
  test(file, { timeout: 30000 }, async (t) => {
    const child = spawn(process.execPath, [path.join(__dirname, '..', file)], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    const closed = once(child, 'close');
    t.after(async () => {
      child.kill();
      await closed;
    });

    let stderr = '';
    child.stderr.setEncoding('utf8');
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.stdout.resume();
    await Promise.race([
      once(child.stdout, 'data', { signal: AbortSignal.timeout(5000) }),
      closed.then(([code]) => {
        throw new Error(`El servidor terminó al iniciar (${code}). ${stderr}`);
      }),
    ]);

    await t.test('GET / entrega el formulario con ambos campos obligatorios', async () => {
      const response = await fetch(baseUrl, { signal: AbortSignal.timeout(3000) });
      assert.equal(response.status, 200);
      assert.match(response.headers.get('content-type'), /^text\/html\b/);
      const html = await response.text();
      assert.match(html, /<form\b[^>]*id="loginForm"/);
      assert.match(html, /<input\b[^>]*id="username"[^>]*\brequired\b/);
      assert.match(html, /<input\b[^>]*id="password"[^>]*\brequired\b/);
    });

    const loginCases = [
      ['Credenciales válidas', fixture, 200, { ok: true, user: fixture.username }],
      ['Contraseña incorrecta', { ...fixture, password: 'incorrecta' }, 401, unauthorized],
      ['Usuario inexistente', { ...fixture, username: 'usuario-inexistente' }, 401, unauthorized],
      ...incompleteCases.map(([name, body]) => [name, body, incompleteStatus, incompleteResponse]),
    ];

    for (const [name, body, status, expected] of loginCases) {
      await t.test(name, async () => {
        const response = await fetch(`${baseUrl}/login-vulnerable`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
          signal: AbortSignal.timeout(3000),
        });
        assert.equal(response.status, status);
        assert.match(response.headers.get('content-type'), /^application\/json\b/);
        assert.deepEqual(await response.json(), expected);
      });
    }
  });
}
