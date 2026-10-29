const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { once } = require('node:events');
const { createApp } = require('../server-vulnerable');
const payloads = require('./payloads.cjs');
let server, db, base;
before(async () => {
  const built = await createApp(); db = built.db;
  server = built.app.listen(0, '127.0.0.1'); await once(server, 'listening');
  base = `http://127.0.0.1:${server.address().port}`;
});
after(async () => {
  if (server) await new Promise(r => server.close(r));
  if (db) await new Promise(r => db.close(r));
});
async function post(data, route = '/login-vulnerable') {
  const r = await fetch(base + route, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  return { status: r.status, body: await r.json() };
}
for (const [username, password] of [['admin', 'admin'], ['juan', '1234']]) {
  test(`Acepta credenciales válidas de ${username}`, async () => {
    assert.deepEqual(await post({ username, password }), { status: 200, body: { ok: true, user: username } });
  });
}
for (const data of [
  {username:'admin',password:'incorrecta'}, {username:'inexistente',password:'admin'},
  {username:'admin',password:' admin '}, {username:'Admin',password:'admin'},
]) test('Rechaza credenciales incorrectas: ' + JSON.stringify(data), async () => {
  assert.deepEqual(await post(data), {status:401,body:{ok:false,message:'Credenciales inválidas'}});
});
for (const p of payloads) test(`${p.id}: ${p.technique}`, async () => {
  assert.deepEqual(await post(p), {status:401,body:{ok:false,message:'Credenciales inválidas'}});
});
for (const data of [
  {}, {username:'admin'}, {password:'admin'}, {username:null,password:'admin'},
  {username:7,password:'admin'}, {username:{a:1},password:'admin'},
  {username:['admin'],password:'admin'}, {username:'admin',password:[]},
  {username:'',password:'admin'}, {username:'admin',password:''},
  {username:'   ',password:'admin'}, {username:'admin',password:'   '},
  {username:'a'.repeat(101),password:'admin'}, {username:'admin',password:'a'.repeat(101)}, null,
]) test('Valida entrada: ' + JSON.stringify(data), async () => {
  const r=await post(data); assert.equal(r.status,400); assert.equal(r.body.ok,false);
});
test('Longitud máxima válida se procesa', async () => {
  assert.equal((await post({username:'x'.repeat(100),password:'x'.repeat(100)})).status,401);
});
test('JSON mal formado no revela detalles internos', async () => {
  const r=await fetch(base+'/login-vulnerable',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"username":'});
  assert.equal(r.status,400); assert.deepEqual(await r.json(),{ok:false,message:'Petición JSON inválida o demasiado grande'});
});
test('Cuerpo demasiado grande se rechaza', async () => {
  assert.equal((await post({username:'x'.repeat(9000),password:'admin'})).status,413);
});
test('Cuerpo ausente se rechaza', async () => {
  assert.equal((await fetch(base+'/login-vulnerable',{method:'POST'})).status,400);
});
test('Alias seguro acepta acceso válido', async () => {
  assert.equal((await post({username:'admin',password:'admin'},'/login-seguro')).status,200);
});
test('Alias seguro rechaza inyección', async () => {
  assert.equal((await post(payloads[0],'/login-seguro')).status,401);
});
test('Formulario disponible y conectado', async () => {
  const r=await fetch(base+'/'); assert.equal(r.status,200); assert.match(await r.text(),/login-vulnerable/);
});
test('Código fuente no publicado por HTTP', async () => {
  assert.equal((await fetch(base+'/server-vulnerable.js')).status,404);
});
