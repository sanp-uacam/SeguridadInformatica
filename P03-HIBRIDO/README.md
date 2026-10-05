# Práctica - Cifrado Híbrido RSA + AES-256

Implementación de un esquema de **cifrado híbrido**: el mensaje se cifra con
AES-256 (rápido, cualquier longitud) y la clave AES + el IV se protegen con
RSA-2048 (permite compartir la clave simétrica sin un canal secreto previo).

## Requisitos

- Python 3.10+
- Librería [`cryptography`](https://cryptography.io/)

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python algoritmo_hibrido.py
```

Al ejecutarlo se muestra:
1. Una demostración de cifrado/descifrado de un mensaje de ejemplo.
2. Una batería de pruebas automáticas (ver más abajo).

## Cómo funciona (paso a paso)

**Emisor:**
1. Genera una clave AES-256 (32 bytes) nueva para ese mensaje ("clave de sesión").
2. Genera un IV aleatorio de 16 bytes.
3. Cifra el mensaje con AES-256 en modo CBC + relleno PKCS7.
4. Cifra la clave de sesión con la clave **pública** RSA del receptor (RSA-OAEP).
5. Cifra el IV de la misma forma con RSA-OAEP.
6. Envía: `mensaje_cifrado`, `clave_sesion_cifrada`, `iv_cifrado`.

**Receptor:**
1. Descifra la clave de sesión con su clave **privada** RSA.
2. Descifra el IV con su clave privada RSA.
3. Usa clave de sesión + IV para descifrar el mensaje con AES-256-CBC.
4. Obtiene el mensaje original.

```
EMISOR                                           RECEPTOR
mensaje
  │
  ├─ genera clave AES-256 (sesión)
  ├─ genera IV (16 bytes)
  ├─ AES-256-CBC cifra mensaje ───────┐
  ├─ RSA-OAEP cifra clave de sesión   │
  ├─ RSA-OAEP cifra IV                │
  └─ envía paquete ───────────────────┼──────────►  recibe paquete
                                       │              ├─ RSA descifra clave de sesión (clave privada)
                                       │              ├─ RSA descifra IV (clave privada)
                                       └──────────────┤─ AES-256-CBC descifra mensaje
                                                       └─ mensaje original
```

## Justificación de tamaños y modos

| Parámetro          | Valor            | Justificación                                                                 |
|---------------------|------------------|--------------------------------------------------------------------------------|
| Clave RSA           | 2048 bits        | Mínimo recomendado actualmente para RSA en producción; buen balance seguridad/rendimiento. |
| Clave AES           | 32 bytes (256 bits) | AES-256 ofrece el mayor margen de seguridad de la familia AES; el costo extra frente a AES-128 es mínimo. |
| IV (AES-CBC)        | 16 bytes (128 bits) | En modo CBC el IV **debe** medir exactamente el tamaño de bloque de AES (128 bits = 16 bytes), sin importar el tamaño de la clave. Un IV de 32 bytes no es válido para AES-CBC. |
| Relleno simétrico   | PKCS7            | Relleno estándar y bien soportado para cifradores por bloques como AES. |
| Relleno asimétrico  | OAEP + SHA-256   | Esquema recomendado actualmente para cifrado con RSA; evita las debilidades del relleno PKCS#1 v1.5. |
| Clave AES / IV por mensaje | Se generan nuevos en cada envío | Evita reutilizar la misma clave/IV en distintos mensajes, lo cual comprometería la confidencialidad en modo CBC. |

## Pruebas automáticas incluidas

El script ejecuta automáticamente:

- Cifrado/descifrado de un mensaje corto.
- Cifrado/descifrado de un mensaje con espacios, acentos y símbolos.
- Cifrado/descifrado de un mensaje largo.
- Verificación de que dos cifrados del mismo mensaje son distintos entre sí
  (porque la clave AES y el IV cambian en cada ejecución).
- Intento de descifrar con una clave privada RSA distinta a la correcta:
  debe fallar.
- Alteración de un byte del texto cifrado: el descifrado debe fallar o
  producir un resultado corrupto (no el mensaje original).

## Análisis básico de seguridad

- **Confidencialidad del mensaje:** depende de AES-256, considerado seguro
  frente a ataques por fuerza bruta con la tecnología actual.
- **Confidencialidad de la clave de sesión:** depende de RSA-2048 con OAEP;
  solo quien tenga la clave privada correspondiente puede recuperar la clave
  AES y el IV.
- **Integridad:** este esquema **no** incluye verificación de integridad
  (no hay HMAC ni cifrado autenticado). Si el atacante modifica el
  `mensaje_cifrado`, el descifrado AES-CBC puede fallar (error de relleno) o,
  en el peor caso, producir un mensaje distinto sin avisar. Para producción
  se recomendaría usar un modo autenticado como AES-GCM o añadir un HMAC
  sobre el texto cifrado.
- **Reutilización de claves:** al generar una clave AES y un IV nuevos por
  cada mensaje se evitan los problemas típicos de reutilizar IV en CBC
  (fuga de patrones entre mensajes).
- **Gestión de la clave privada:** en este ejercicio la clave privada vive
  en memoria durante la ejecución; en un sistema real debería almacenarse
  cifrada y protegida (por ejemplo, con una passphrase o un HSM).
