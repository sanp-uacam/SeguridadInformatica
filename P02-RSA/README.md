# Práctica 2: Algoritmo RSA

Esta práctica contiene archivos de utilidad para trabajar con el algoritmo RSA
y descifrar una serie de números, cuyo significado es **Hola Mundo**.

## Archivos

- `ascii.py`: utilidades relacionadas con la conversión ASCII.
- `complete.py`: resolución completa del proceso de descifrado.
- `d.py`: cálculo del exponente privado RSA.
- `e.py`: cálculo del exponente público RSA.
- `mat.py`: operaciones matemáticas auxiliares.
- `mcd.py`: cálculo del máximo común divisor.
- `mensaje.py`: tratamiento del mensaje que se desea descifrar.
- `n_φn.py`: cálculo de `n` y de la función phi de Euler.

## Objetivo

El objetivo es utilizar las herramientas matemáticas y de conversión incluidas
en esta carpeta para descifrar un mensaje RSA y obtener la palabra.
La palabra descifrada representa el mensaje **Hola Mundo**.

## Funcionamiento

Los archivos de esta práctica apoyan las operaciones necesarias para el
descifrado RSA: conversión de valores, cálculo de `n`, `phi(n)`, `e` y `d`, y
operaciones matemáticas auxiliares. Al completar el proceso se recupera la
palabra oculta (**Hola Mundo**).
