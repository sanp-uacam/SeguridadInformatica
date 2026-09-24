# Práctica 03: cifrado híbrido RSA-AES

Esta práctica combina dos algoritmos: AES cifra el mensaje y RSA protege la clave AES. Así se aprovecha la rapidez de AES y la distribución segura de claves de RSA.

## Qué hace

El programa genera una clave AES-256 y un IV nuevo para cada mensaje. Cifra el texto con AES-CBC, empaqueta la clave y el IV, y cifra ese paquete con RSA-OAEP de 2048 bits. El receptor abre el paquete con su clave privada, recupera la clave AES y obtiene el mensaje original.

El programa usa un IV de 16 bytes porque es el tamaño que exige AES-CBC; la clave AES sí tiene 32 bytes, como pide la práctica.

## Cómo se obtiene cada resultado

1. Se genera un par RSA de 2048 bits. La clave pública queda disponible para cifrar; la clave privada permanece en memoria y se reserva para descifrar.
2. Se crean al azar 32 bytes para `clave_AES` y 16 bytes para `iv`. La clave aporta AES-256; el IV inicia CBC con un valor nuevo para cada mensaje.
3. El mensaje se convierte a bytes UTF-8. `pad` agrega bytes hasta completar bloques de 16; `AES.new(clave_AES, AES.MODE_CBC, iv)` cifra esos bloques y produce `mensajeCifrado_AES`.
4. Se forma `clave_AES || iv`, que mide `32 + 16 = 48` bytes. `PKCS1_OAEP` cifra ese paquete con la clave pública RSA y produce `iv_cifrado_RSA` de 256 bytes para RSA de 2048 bits.
5. El receptor aplica OAEP con la clave privada y recupera los 48 bytes. Los primeros 32 son la clave AES y los últimos 16 son el IV. Con ambos crea el descifrador CBC y recupera los bytes rellenados del mensaje.
6. `unpad` elimina el relleno PKCS#7 y `decode('utf-8')` convierte los bytes a texto. El programa compara el texto recuperado con el texto enviado; si son iguales, imprime `Verificacion: CORRECTA`.

## Cómo ejecutarla

Instala PyCryptodome una sola vez:

```powershell
python -m pip install pycryptodome
```

Después ejecuta:

```powershell
python main.py --mensaje "Hola mundo"
```

Si omites `--mensaje`, el programa lo solicita por consola.

## Evidencia

La carpeta `evidencias` contiene `terminal_resultado.png`. Es una captura real de PowerShell con el mensaje original, el mensaje recuperado y `Verificacion: CORRECTA`.

El informe también explica el flujo y las limitaciones de seguridad. CBC cifra, pero no autentica; un sistema real debe añadir autenticación, por ejemplo AES-GCM o un MAC independiente.
