const { spawn } = require('node:child_process');
const { once } = require('node:events');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createApp } = require('../server-vulnerable');
const payloads = require('./payloads.cjs');
(async () => {
  const original=spawn(process.execPath,[path.join(__dirname,'../laboratorio/server-original.js')],{stdio:['ignore','pipe','pipe']});
  let server, db;
  try {
    await Promise.race([once(original.stdout,'data'), once(original,'exit').then(([code])=>{throw new Error('El laboratorio no inició: '+code);})]);
    const built=await createApp(); db=built.db;
    server=built.app.listen(0,'127.0.0.1'); await once(server,'listening');
    const secure=`http://127.0.0.1:${server.address().port}`;
    const rows=[];
    for(const p of payloads){
      const row={...p};
      for(const [key,url] of [['before','http://127.0.0.1:3001'],['after',secure]]){
        const r=await fetch(url+'/login-vulnerable',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:p.username,password:p.password})});
        row[key]={status:r.status,body:await r.json()};
      }
      assert.equal(row.before.status,p.baseline,p.id+' original');
      if (p.baseline === 200) {
        const user = {P02:'juan',P09:'hacker',P10:'1234'}[p.id] || 'admin';
        assert.deepEqual(row.before.body,{ok:true,user},p.id+' resultado original');
      } else if (p.baseline === 500) {
        assert.match(row.before.body.error,/SQLITE_ERROR/);
      } else assert.equal(row.before.body.ok,false);
      assert.equal(row.after.status,401,p.id+' corregido');
      assert.equal(row.after.body.ok,false);
      rows.push(row);
      console.log(`${p.id} ${p.technique}: ${row.before.status} -> ${row.after.status}`);
    }
    fs.writeFileSync(path.join(__dirname,'../evidencias/resultados-comparacion.json'),JSON.stringify({sourceCommit:'c3d7fa16fdd6447ed29866f636e86fc8dd025721',method:'HTTP local; SQLite en memoria; original adaptado en puerto y entrega del formulario',rows},null,2));
  } finally {
    original.kill();
    if(server) await new Promise(r=>server.close(r));
    if(db) await new Promise(r=>db.close(r));
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
