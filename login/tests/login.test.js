const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { once } = require('node:events');
const { createApp } = require('../server-vulnerable');
const payloads = require('./payloads.cjs');
let server, db, base;
before(async () => {
 const instance=await createApp();db=instance.db;
 server=instance.app.listen(0,'127.0.0.1');await once(server,'listening');
 base=`http://127.0.0.1:${server.address().port}`;
});
after(async()=>{await new Promise(resolve=>server.close(resolve));await new Promise(resolve=>db.close(resolve));});
async function post(body,route='/login-vulnerable') {
 const response=await fetch(base+route,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 return {status:response.status,body:await response.json()};
}
for(const [username,password] of [['admin','admin'],['juan','1234']]) {
 test(`Control válido ${username}`,async()=>assert.deepEqual(await post({username,password}),{status:200,body:{ok:true,user:username}}));
}
test('Contraseña incorrecta',async()=>assert.deepEqual(await post({username:'admin',password:'x'}),{status:401,body:{ok:false,message:'Credenciales inválidas'}}));
for(const item of payloads) {
 test(`${item.id} bloqueado ${item.name}`,async()=>assert.deepEqual(await post({username:item.username,password:item.password}),{status:401,body:{ok:false,message:'Credenciales inválidas'}}));
}
const invalid=[{},null,{username:'admin'},{password:'admin'},{username:'',password:'admin'},{username:'   ',password:'admin'},{username:'admin',password:''},{username:12,password:'admin'},{username:[],password:'admin'},{username:'admin',password:{}},{username:'a'.repeat(101),password:'x'},{username:'admin',password:'x'.repeat(101)}];
invalid.forEach((body,index)=>test(`Validación de entrada ${index+1}`,async()=>{
 const result=await post(body);assert.equal(result.status,400);assert.equal(result.body.ok,false);
 assert.equal(JSON.stringify(result.body).includes('SQLITE'),false);
}));
test('JSON mal formado responde sin detalles internos',async()=>{
 const res=await fetch(base+'/login-vulnerable',{method:'POST',headers:{'Content-Type':'application/json'},body:'{incorrecto'});
 assert.equal(res.status,400);assert.deepEqual(await res.json(),{ok:false,message:'Petición JSON inválida.'});
});
test('Ruta segura equivalente',async()=>assert.deepEqual(await post({username:'admin',password:'admin'},'/login-secure'),{status:200,body:{ok:true,user:'admin'}}));
test('El servidor no publica su código fuente',async()=>assert.equal((await fetch(base+'/server-vulnerable.js')).status,404));
