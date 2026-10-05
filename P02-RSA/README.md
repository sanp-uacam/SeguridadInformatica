# Práctica 02: RSA

Esta práctica muestra cómo funciona RSA con números pequeños. El programa calcula las claves, prueba candidatos para elegir el exponente público y descifra el mensaje entregado.

## Qué hace

Usa `p = 67` y `q = 83`. Calcula `n`, `phi(n)`, encuentra el cuarto candidato válido `e = 17` y obtiene `d = 4457` con Euclides extendido. Al final descifra los bloques y recupera **HOLA MUNDO**. También vuelve a cifrar el resultado para comprobar que coincide.

## Cómo se obtiene cada resultado

1. Se multiplican los primos: `n = 67 × 83 = 5561`.
2. Se calcula `phi(n) = (67 - 1) × (83 - 1) = 5412`.
3. Se prueban valores desde 2 y se calcula su mcd con 5412. Los primeros intentos son `2 (mcd 2)`, `3 (mcd 3)`, `4 (mcd 4)`, `5 (mcd 1)`, `6 (mcd 6)`, `7 (mcd 1)`, `8 (mcd 4)`, `9 (mcd 3)`, `10 (mcd 2)`, `11 (mcd 1)`, `12 (mcd 12)`, `13 (mcd 1)`, `14 (mcd 2)`, `15 (mcd 3)`, `16 (mcd 4)` y `17 (mcd 1)`. Los cuatro válidos son `5, 7, 13, 17`; por eso `e = 17`.
4. Euclides extendido divide sucesivamente `5412 ÷ 17 = 318`, con residuo `6`, y `17 ÷ 6 = 2`, con residuo `5`, `6 ÷ 5 = 1`, con residuo `1`. Al regresar las sustituciones se obtiene `1 = 17 × (-955) + 5412 × 3`. El coeficiente de 17 es `-955`; se ajusta al módulo: `d = -955 mod 5412 = 4457`. Así, `17 × 4457 mod 5412 = 1`.
5. Cada bloque se calcula por separado con `m = c^4457 mod 5561`. Por ejemplo, `1058` produce `72`, que corresponde a `H`; `2597` produce `79`, que corresponde a `O`; `4955` produce `76`, que corresponde a `L`. La lista completa es `72, 79, 76, 65, 32, 77, 85, 78, 68, 79`, y sus valores ASCII forman `HOLA MUNDO`.
6. Para comprobar el resultado se aplica `c = m^17 mod 5561` a cada valor obtenido. Los primeros son `72^17 mod 5561 = 1058`, `79^17 mod 5561 = 2597` y `76^17 mod 5561 = 4955`. Los diez resultados coinciden con los bloques del enunciado, por lo que el descifrado es consistente.

## Cómo ejecutarla

Desde esta carpeta:

```powershell
python main.py
```

No necesita instalar paquetes adicionales.

## Evidencia

La evidencia está en `evidencias/terminal_resultado.png`. Es una captura real de PowerShell con los cálculos, el mensaje descifrado y el recifrado correcto.

Es un ejercicio académico. Sus claves pequeñas no sirven para proteger información real.
