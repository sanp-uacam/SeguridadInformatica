# Práctica 2 – Algoritmo RSA

**Seguridad Informática** · Facultad de Ingeniería, UACAM
**Alumno:** Kerin Del Jesús González Maas · Grado 7, Grupo "A"
**Maestro:** Sergio A. Noh Puch

---

## Descripción

Script en Python que genera un par de claves RSA a partir de los primos dados y descifra el mensaje de la práctica. Muestra en la terminal cada paso del proceso, incluida la tabla de candidatos de `e` y el desarrollo del algoritmo extendido de Euclides.

## Ejecución

Requiere Python 3. No usa librerías externas (solo `math`).

```bash
python rsa_practica2.py
```

## Datos de entrada

| Parámetro | Valor |
|---|---|
| p | 67 |
| q | 83 |
| Mensaje cifrado | `1058 2597 4955 4201 3162 4343 2754 2497 336 2597` |

## Pasos que realiza

1. **Calcula n** = p · q
2. **Calcula φ(n)** = (p − 1)(q − 1)
3. **Elige e**: recorre los valores desde 2, muestra cada candidato con su mcd y toma el **cuarto** que cumple `mcd(e, φ(n)) = 1`
4. **Calcula d** con el **algoritmo extendido de Euclides** (función `euclides_extendido`), mostrando las divisiones sucesivas y comprobando que `e · d mod φ(n) = 1`
5. **Descifra el mensaje** bloque por bloque con `m = c^d mod n` y convierte cada número a su carácter ASCII
6. **Verifica** el resultado volviendo a cifrar el texto con la clave pública y comparándolo con el criptograma original

## Resultados

| Valor | Resultado |
|---|---|
| n | 5561 |
| φ(n) | 5412 |
| Candidatos válidos de e | 5, 7, 13, **17** |
| e (clave pública) | **17** |
| d (clave privada) | **4457** |
| Comprobación | 17 · 4457 = 75769 ≡ 1 (mod 5412) |
| Clave pública | (17, 5561) |
| Clave privada | (4457, 5561) |

### Descifrado

| c | 1058 | 2597 | 4955 | 4201 | 3162 | 4343 | 2754 | 2497 | 336 | 2597 |
|---|---|---|---|---|---|---|---|---|---|---|
| m | 72 | 79 | 76 | 65 | 32 | 77 | 85 | 78 | 68 | 79 |
| ASCII | H | O | L | A | ␣ | M | U | N | D | O |

**Mensaje descifrado: `HOLA MUNDO`**

Al volver a cifrar el mensaje con la clave pública (17, 5561) se obtiene exactamente el criptograma original, lo que confirma que el par de claves es correcto.

## Nota

Para la exponenciación modular se usa `pow(c, d, n)` en lugar de `(c ** d) % n`. La segunda forma calcula primero la potencia completa (un número de miles de dígitos) y después reduce el módulo; `pow` con tres argumentos reduce en cada paso y es mucho más eficiente.
