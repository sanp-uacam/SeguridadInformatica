# Seguridad Informática
## Practica 2 – Algoritmo Hibrido RSA_AES

## Especificaciones Técnicas

### 1. Algoritmo Híbrido

El sistema debe implementar tres funciones principales:

#### a) get_Msj_And_Key(RSA_Publica)

- **Entrada:** Clave pública RSA del receptor
- **Proceso:**
  1. Generar una clave AES simétrica aleatoria (32 bytes)
  2. Generar un Vector de Inicialización (IV) aleatorio de 32 bytes
  3. Cifrar el mensaje con AES en modo CBC usando la clave generada y el IV
  4. Cifrar la clave AES con RSA usando la clave pública del receptor
  5. Cifrar el IV con RSA (o empaquetarlo junto con la clave cifrada)
- **Salida:**
  - `iv_cifrado_RSA`: IV cifrado con RSA
  - `mensajeCifrado_AES`: Mensaje cifrado con AES

#### b) decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)

- **Entrada:**
  - Mensaje cifrado con AES
  - IV cifrado con RSA
  - Clave privada RSA del receptor
- **Proceso:**
  1. Descifrar el IV con RSA usando la clave privada
  2. Descifrar la clave AES con RSA usando la clave privada (este paso ya debería estar incluido en los datos recibidos)
  3. Descifrar el mensaje con AES usando la clave recuperada y el IV
- **Salida:** Mensaje original en texto plano

#### c) Cifrado_AES_enviar_mensaje("Mensaje", iv)

- Función auxiliar que cifra un mensaje con AES usando un IV proporcionado
- Debe implementar el cifrado AES en modo CBC

---