# Práctica 3 — Algoritmo Híbrido RSA + AES

**Seguridad Informática** · Facultad de Ingeniería, UACAM
Alumno: Kerin Del Jesús González Maas · Grado 7, Grupo "A"

---

## Instalación y ejecución

```bash
pip install -r requirements.txt

python algoritmo_hibrido.py    # demostración interactiva
python pruebas.py              # suite de 21 pruebas automáticas
```

Requiere Python 3.8 o superior.

---

## Archivos

| Archivo | Contenido |
|---|---|
| `algoritmo_hibrido.py` | Implementación de las tres funciones del enunciado |
| `pruebas.py` | 21 pruebas automáticas en 6 grupos |
| `requirements.txt` | Dependencia: `cryptography` |

Al ejecutar se generan `clave_publica.pem`, `clave_privada.pem` y `paquete_cifrado.json`.

---

## Por qué un cifrado híbrido

RSA no puede cifrar mensajes más grandes que su módulo y es lento. AES es rápido y maneja cualquier tamaño, pero requiere que ambas partes compartan una clave secreta, y transmitirla por un canal inseguro es justamente el problema. El esquema híbrido resuelve ambos:

- El **mensaje** se cifra con **AES** (rápido, sin límite de tamaño).
- La **clave AES** se cifra con **RSA** (resuelve el intercambio de clave).

Es el mismo principio que usan TLS/HTTPS, PGP y la mensajería cifrada.

---

## Flujo del proceso

```
EMISOR                                          RECEPTOR
──────────────────────────────────────────────────────────────────────
mensaje en texto plano
       │
       ├─► clave AES aleatoria (32 bytes)
       ├─► IV aleatorio (16 bytes)
       │
       ├─► AES-256-CBC + PKCS#7 ──► mensajeCifrado_AES ──────┐
       ├─► RSA-OAEP(clave AES) ──► clave_AES_cifrada_RSA ────┤
       └─► RSA-OAEP(IV) ─────────► iv_cifrado_RSA ───────────┤
                                                             │
                          ══ canal inseguro ══════════════►  │
                                                             ▼
                                        RSA⁻¹(iv_cifrado_RSA) ──► IV
                                        RSA⁻¹(clave_cifrada) ──► clave AES
                                                             │
                                        AES-CBC⁻¹ + quitar padding
                                                             │
                                                             ▼
                                                 mensaje en texto plano
```

---

## Justificación de las decisiones de diseño

| Decisión | Valor | Por qué |
|---|---|---|
| Tamaño de clave AES | 32 bytes (AES-256) | Lo pide el enunciado. Margen de seguridad amplio, incluso frente a ataques cuánticos (Grover reduce 256 a ~128 bits efectivos). |
| Modo de operación | CBC | Lo pide el enunciado. Encadena cada bloque con el anterior vía XOR, por lo que bloques de texto plano idénticos producen cifrados distintos, a diferencia de ECB. |
| Tamaño del IV | 16 bytes | AES opera en bloques de 128 bits; en CBC el IV **debe** medir exactamente un bloque. Ver nota sobre el enunciado abajo. |
| Padding | PKCS#7 | Estándar y reversible sin ambigüedad. Implementado a mano para mostrar el mecanismo. |
| Tamaño de clave RSA | 2048 bits | Mínimo recomendado por NIST hasta 2030. Con OAEP-SHA256 permite cifrar hasta 190 bytes, suficiente para la clave (32) y el IV (16). |
| Exponente público RSA | 65537 | Estándar (F4). Primo, y su forma binaria hace la exponenciación rápida. Exponentes pequeños como 3 son vulnerables a ataques de raíz cúbica. |
| Relleno RSA | OAEP con SHA-256 | Añade aleatoriedad, por lo que cifrar dos veces el mismo dato da resultados distintos. RSA "en crudo" es determinista y filtra información. |
| Generador aleatorio | `secrets` | Usa el CSPRNG del sistema operativo. `random` es predecible y no sirve para material criptográfico. |
| Codificación de salida | Base64 | Permite transmitir los bytes cifrados como texto (JSON, correo) sin corromperlos. |

---

## Notas sobre el enunciado

**1. IV de 32 bytes → se implementa con 16.**
El PDF pide un IV aleatorio de 32 bytes, pero AES tiene bloques de 128 bits y el modo CBC exige un IV de exactamente 16 bytes. Con 32 la librería rechaza la operación. Existe una prueba automática (`Un IV de 32 bytes es rechazado`) que documenta este comportamiento.

**2. La clave AES cifrada falta en la salida.**
El enunciado lista como salida de `get_Msj_And_Key` únicamente `iv_cifrado_RSA` y `mensajeCifrado_AES`, pero el proceso sí indica cifrar la clave AES, y sin ella el receptor no puede descifrar nada. El paquete incluye también `clave_AES_cifrada_RSA`.

---

## Pruebas

`pruebas.py` ejecuta 21 pruebas agrupadas en seis bloques:

1. **Funcionamiento básico** — mensajes cortos, largos (10 000 caracteres), vacíos, con acentos y ñ, con saltos de línea, y de exactamente un bloque.
2. **Padding PKCS#7** — que siempre deje múltiplo de 16, que sea reversible, y que rechace relleno corrupto.
3. **Aleatoriedad** — que cifrar dos veces lo mismo dé criptogramas distintos, y que bloques repetidos no produzcan cifrado repetido (verifica que no se degradó a ECB).
4. **Seguridad** — que una clave privada ajena no descifre, y que alterar o truncar el criptograma rompa el proceso.
5. **Validación de parámetros** — que se rechacen IV y claves de tamaño incorrecto.
6. **Serialización** — que el paquete sobreviva a JSON y que los bloques RSA midan 256 bytes.

---

## Análisis de seguridad

### Fortalezas

- **Confidencialidad.** AES-256 no tiene ataques prácticos conocidos mejores que la fuerza bruta. RSA-2048 tampoco ha sido factorizado.
- **Clave de sesión efímera.** Cada ejecución genera una clave AES nueva, así que comprometer un mensaje no compromete los anteriores ni los posteriores.
- **No determinismo.** OAEP en RSA e IV aleatorio en CBC garantizan que el mismo mensaje nunca produzca el mismo criptograma. Un observador no puede detectar mensajes repetidos.
- **Aleatoriedad criptográfica.** El uso de `secrets` evita que las claves sean predecibles.

### Debilidades del esquema

- **No hay autenticación ni integridad.** Esta es la limitación más importante. CBC solo aporta confidencialidad: un atacante puede modificar el criptograma y, aunque el descifrado suele fallar por padding, el esquema no garantiza detectar la manipulación. La solución sería añadir un HMAC-SHA256 sobre el criptograma (Encrypt-then-MAC) o usar AES-GCM en lugar de CBC.
- **Vulnerable a padding oracle.** Si el sistema revelara al atacante la diferencia entre "padding inválido" y otros errores, sería posible descifrar el mensaje completo sin conocer la clave. Por eso conviene no exponer mensajes de error detallados en producción.
- **Sin autenticación del emisor.** Cualquiera con la clave pública del receptor puede enviar un mensaje haciéndose pasar por otro. Se resolvería firmando digitalmente con la clave privada del emisor.
- **Sin protección contra repetición.** Un atacante puede reenviar un paquete capturado y el receptor lo aceptará como válido. Se mitiga con marcas de tiempo o números de secuencia.
- **La clave privada se guarda sin cifrar.** `clave_privada.pem` se escribe con `NoEncryption()` por simplicidad didáctica. En un sistema real debería protegerse con contraseña o almacenarse en un módulo de hardware.
- **Horizonte cuántico.** RSA-2048 sería roto por el algoritmo de Shor en una computadora cuántica suficientemente grande. AES-256 resistiría mucho mejor. La migración apunta a algoritmos post-cuánticos como ML-KEM (Kyber).
