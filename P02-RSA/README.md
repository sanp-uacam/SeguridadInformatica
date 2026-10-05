# Practica RSA

La practica calcula `n = p*q` y `phi(n) = (p-1)*(q-1)` para `p=67`, `q=83`. Recorre los enteros desde 2 para seleccionar el cuarto `e` coprimo con `phi(n)`, obtiene `d` con el algoritmo extendido de Euclides y descifra cada bloque `C` con `M = C^d mod n`.

Ejecutar con Python 3:

```powershell
python rsa_practica.py
```

Resultados esperados: `n=5561`, `phi(n)=5412`, candidatos validos `[5, 7, 13, 17]`, `e=17`, `d=4457` y mensaje `HOLA MUNDO`.

Los parametros son pequenos por ser un ejercicio manual; no son seguros para proteger informacion real.
