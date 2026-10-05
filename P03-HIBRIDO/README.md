# Práctica 2: Algoritmo Híbrido (RSA - AES)

Este sistema implementa un sistema criptográfico híbrido cliente-servidor simulado. Utiliza **AES-256 (Modo CBC)** para el cifrado masivo de datos y **RSA (con generación dinámica de primos)** para el intercambio seguro de la llave simétrica y el Vector de Inicialización (IV).

## Requisitos Previos
El sistema requiere la instalación de la librería criptográfica oficial:
```
pip install pycryptodome
```

## Ejecución

Para simular correctamente el envío de datos a través de la red, es necesario ejecutar los scripts en dos terminales separadas.

**Paso 1: Iniciar el Receptor**
1. Abre una terminal y navega a la carpeta del proyecto:
   ```
   cd P3_Hibrido
   ```

2. Ejecuta el receptor para generar las claves RSA y exportar la clave pública en formato JSON:
   ```
   python3 receptor.py
   ```

*(El programa se pausará esperando el mensaje).*

**Paso 2: Iniciar el Emisor**
1. Abre una segunda terminal y navega a la misma carpeta:
   ```
   cd P3_Hibrido
   ```

2. Ejecuta el emisor:
   ```
   python3 emisor.py
   ```

3. Escribe el mensaje secreto en la consola cuando el sistema lo solicite. Al dar ENTER, el sistema empaquetará los datos en \`mensaje_oculto.json\`.

**Paso 3: Descifrar el Mensaje**
1. Regresa a la primera terminal (la del Receptor).
2. Presiona **ENTER**. El sistema leerá el archivo JSON, descifrará las llaves con RSA y recuperará el texto plano con AES.

## 📁 Estructura del Proyecto
* `hibrido.py`: Script central con la lógica matemática y algoritmos de cifrado.
* `receptor.py`: Script que genera claves RSA y descifra el mensaje final.
* `emisor.py`: Script que genera claves AES, cifra el texto y empaqueta los datos.
* `clave_publica.json`: Archivo de intercambio generado por el receptor con la clave pública RSA (e, n).
* `mensaje_oculto.json`: Paquete de red generado con la prueba de mensaje ("i wanna be Yoursm"), conteniendo el IV y la clave AES cifrados con RSA junto al criptograma en hexadecimal.