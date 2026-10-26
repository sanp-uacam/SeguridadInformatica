# Práctica 2 - Algoritmo Híbrido RSA + AES

## Lenguaje
Python 3.

## Librería
`cryptography`

Instalación:

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python algoritmo_hibrido.py
```

El programa:
1. Genera un par RSA de 2048 bits.
2. Genera una clave AES aleatoria de 32 bytes (AES-256).
3. Genera un IV de 16 bytes para AES-CBC.
4. Cifra el mensaje con AES-256-CBC + PKCS7.
5. Cifra con RSA-OAEP la clave AES y el IV.
6. Descifra ambos con la clave privada RSA.
7. Descifra el mensaje con AES.
8. Comprueba automáticamente que el mensaje final es igual al original.

## Nota importante sobre el enunciado

El PDF indica un IV aleatorio de 32 bytes, pero AES tiene bloques de 16 bytes y AES-CBC requiere un IV de exactamente 16 bytes. Por eso, para una implementación AES-CBC válida, este código utiliza un IV de 16 bytes.

Además, el texto del enunciado indica que `decifrar_mensaje` debe recuperar la clave AES, pero en la lista de salida de `get_Msj_And_Key` no aparece explícitamente la clave AES cifrada. Para que el algoritmo sea funcional, el código devuelve también `clave_AES_cifrada_RSA`.

Estas dos decisiones deben explicarse al profesor como correcciones técnicas necesarias para que el algoritmo descrito pueda ejecutarse correctamente.

## Flujo

EMISOR:
Mensaje
 -> genera clave AES-256
 -> genera IV de 16 bytes
 -> AES-CBC cifra mensaje
 -> RSA-OAEP cifra clave AES
 -> RSA-OAEP cifra IV
 -> envía paquete

RECEPTOR:
paquete
 -> RSA descifra clave AES
 -> RSA descifra IV
 -> AES-CBC descifra mensaje
 -> mensaje original

## Pruebas recomendadas

- Mensaje corto.
- Mensaje con espacios, acentos y símbolos.
- Mensaje largo.
- Comprobar que cada ejecución genera nuevos datos cifrados.
- Intentar descifrar con una clave RSA privada diferente: debe fallar.
- Modificar el ciphertext: el descifrado debe fallar o producir un error de padding.

## Entregables cubiertos

- Código fuente.
- Explicación del funcionamiento.
- Justificación de tamaños y modos.
- Diagrama de flujo (puede elaborarse con el flujo incluido en este README).
- Pruebas automáticas.
- Análisis básico de seguridad.
