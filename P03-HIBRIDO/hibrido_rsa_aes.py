# -*- coding: utf-8 -*-
"""
======================================================================
 Practica 3 - Algoritmo Hibrido RSA + AES
 Seguridad Informatica | Facultad de Ingenieria - UACAM
 Alumno: Kevin del Jesus Gonzalez Maas
 Docente: Sergio A Noh Puch          Grado: 7   Grupo: "A"
----------------------------------------------------------------------
 De que trata:
   El mensaje lo cifro con AES-256 en modo CBC, y esa clave AES junto con
   el IV los protejo con RSA. Asi aprovecho lo bueno de los dos: la
   velocidad del simetrico y la comodidad del asimetrico para repartir la
   clave sin tener que ponernos de acuerdo antes.

 Requisito:
   pip install pycryptodome
======================================================================
"""

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# ----------------------------------------------------------------------
# DATOS DE LA PRACTICA
# ----------------------------------------------------------------------

BITS_RSA = 2048          # tamanio de la clave RSA
TAM_CLAVE_AES = 32       # los 32 bytes que pide el profesor = AES-256
TAM_IV = 32              # se pide el IV de 32 bytes
TAM_BLOQUE = 16          # esto no lo elijo yo: AES siempre parte en bloques de 16

MENSAJE = ("Hola profe, este mensaje viaja cifrado con AES-256 en modo CBC "
           "y la clave simetrica viaja protegida con RSA. "
           "-- Kevin del Jesus Gonzalez Maas, 7 'A'.")

# Aqui guardo la clave AES del envio activo, porque la funcion c) del
# profesor se llama nada mas con el mensaje y el IV, sin la clave.
CLAVE_AES_ACTUAL = None


def a_hex(datos, limite=None):
    """Paso los bytes a hexadecimal, si no no hay forma de mostrarlos."""
    texto = datos.hex().upper()
    return texto[:limite] + "..." if limite and len(texto) > limite else texto


# ======================================================================
# LAS TRES FUNCIONES QUE PIDE EL PROFESOR
# ======================================================================

def Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes=None):
    """
    Funcion c) del profesor: Cifrado_AES_enviar_mensaje("Mensaje", iv)

    Cifra con AES en modo CBC usando el IV que se le pasa. Como solo se le
    mandan dos cosas, si no me dan la clave uso la del envio activo. Del IV
    de 32 bytes tomo los primeros 16, porque el bloque de AES mide 16.
    """
    if clave_aes is None:
        clave_aes = CLAVE_AES_ACTUAL
    if clave_aes is None:
        raise ValueError("No hay clave AES activa. Hay que correr primero get_Msj_And_Key().")
    if isinstance(mensaje, str):
        mensaje = mensaje.encode("utf-8")
    cifrador = AES.new(clave_aes, AES.MODE_CBC, iv[:TAM_BLOQUE])
    return cifrador.encrypt(pad(mensaje, TAM_BLOQUE))


def get_Msj_And_Key(RSA_Publica, mensaje=MENSAJE, verboso=True):
    """
    Funcion a) del profesor:
        iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(RSA_Publica)

    Es la parte del que manda: entra la clave publica del receptor y salen
    las dos cosas que viajan por el canal.
    """
    global CLAVE_AES_ACTUAL

    # --- Paso 1 del profesor: clave AES aleatoria de 32 bytes. Uso
    #     get_random_bytes y no random, porque random se puede predecir.
    clave_aes = get_random_bytes(TAM_CLAVE_AES)
    CLAVE_AES_ACTUAL = clave_aes

    # --- Paso 2 del profesor: IV aleatorio de 32 bytes. Genero los 32 que
    #     se piden aunque AES solo ocupe 16; los otros 16 viajan igual
    #     dentro del paquete cifrado, asi que no se pierde nada.
    iv = get_random_bytes(TAM_IV)

    # --- Paso 3 del profesor: cifrar el mensaje con AES-CBC. Se lo
    #     encargo a la funcion c).
    mensajeCifrado_AES = Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes)

    # --- Pasos 4 y 5 del profesor: cifrar con RSA la clave AES y el IV.
    #     La especificacion deja empaquetar el IV junto con la clave, y asi
    #     lo hice: pego los dos y cifro los 64 bytes de un solo golpe.
    paquete = iv + clave_aes                      # 32 + 32 = 64 bytes
    cifrador_rsa = PKCS1_OAEP.new(RSA_Publica)
    iv_cifrado_RSA = cifrador_rsa.encrypt(paquete)

    if verboso:
        print("  Clave AES generada (32 bytes) : %s" % a_hex(clave_aes))
        print("  IV generado       (32 bytes) : %s" % a_hex(iv))
        print("  IV efectivo para CBC (16 B)  : %s" % a_hex(iv[:TAM_BLOQUE]))
        print("  Paquete IV+clave cifrado RSA : %d bytes" % len(iv_cifrado_RSA))
        print("  Mensaje cifrado con AES      : %d bytes (%d bloques de 16)"
              % (len(mensajeCifrado_AES), len(mensajeCifrado_AES) // TAM_BLOQUE))

    return iv_cifrado_RSA, mensajeCifrado_AES


def decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada, verboso=True):
    """
    Funcion b) del profesor:
        decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)

    Es la parte del que recibe: entra lo que viajo por el canal mas su
    clave privada, y sale el mensaje original.
    """
    # --- Pasos 1 y 2 del profesor: descifrar el IV y la clave AES con RSA.
    #     El paso 2 ya deberia venir en los datos
    #     recibidos, y asi quedo: con una sola operacion saco las dos.
    descifrador_rsa = PKCS1_OAEP.new(RSA_Privada)
    paquete = descifrador_rsa.decrypt(iv_cifrado_RSA)

    iv = paquete[:TAM_IV]           # primeros 32 bytes: el IV
    clave_aes = paquete[TAM_IV:]    # ultimos 32 bytes: la clave AES

    if verboso:
        print("  Paquete recuperado con RSA   : %d bytes" % len(paquete))
        print("  IV recuperado                : %s" % a_hex(iv))
        print("  Clave AES recuperada         : %s" % a_hex(clave_aes))

    # --- Paso 3 del profesor: descifrar el mensaje con AES.
    descifrador = AES.new(clave_aes, AES.MODE_CBC, iv[:TAM_BLOQUE])
    texto_plano = unpad(descifrador.decrypt(mensajeCifrado_AES), TAM_BLOQUE)
    return texto_plano.decode("utf-8")


# ======================================================================
# PRUEBAS (entregable 3: demostrar el correcto funcionamiento)
# ======================================================================

def pruebas(RSA_Publica, RSA_Privada):
    """Cuatro pruebas para comprobar que el sistema hace lo que debe."""
    resultados = []

    # Prueba 1: mensajes de varios tamanios, incluyendo el vacio, uno que
    # mide justo 16 (ahi el relleno agrega un bloque entero) y uno largo.
    casos = ["", "A", "1234567890123456", "X" * 1000]
    ok1 = True
    print("  Prueba 1 - Distintas longitudes de mensaje (relleno PKCS#7)")
    for caso in casos:
        iv_p, msg_p = get_Msj_And_Key(RSA_Publica, caso, verboso=False)
        igual = decifrar_mensaje(msg_p, iv_p, RSA_Privada, verboso=False) == caso
        ok1 = ok1 and igual
        print("     %4d caracteres -> %4d bytes cifrados -> %s"
              % (len(caso), len(msg_p), "CORRECTO" if igual else "FALLO"))
    resultados.append(("1. Cifrado y descifrado con distintas longitudes", ok1))
    print("     Resultado: %s\n" % ("CORRECTO" if ok1 else "FALLO"))

    # Prueba 2: mando el mismo texto dos veces. Tienen que salir
    # criptogramas distintos, porque cada envio usa clave e IV nuevos.
    iv1, msg1 = get_Msj_And_Key(RSA_Publica, verboso=False)
    iv2, msg2 = get_Msj_And_Key(RSA_Publica, verboso=False)
    d1 = decifrar_mensaje(msg1, iv1, RSA_Privada, verboso=False)
    d2 = decifrar_mensaje(msg2, iv2, RSA_Privada, verboso=False)
    ok2 = (msg1 != msg2 and d1 == MENSAJE and d2 == MENSAJE)
    resultados.append(("2. Dos envios iguales dan criptogramas distintos", ok2))
    print("  Prueba 2 - Mismo mensaje enviado dos veces")
    print("     Envio 1 (inicio) : %s" % a_hex(msg1, 32))
    print("     Envio 2 (inicio) : %s" % a_hex(msg2, 32))
    print("     Son diferentes pero ambos descifran bien: %s" % ("SI" if ok2 else "NO"))
    print("     Resultado: %s\n" % ("CORRECTO" if ok2 else "FALLO"))

    # Prueba 3: hago como si alguien interceptara el mensaje y le cambiara
    # un solo byte. Ya no se debe poder leer igual.
    alterado = bytearray(msg1)
    alterado[5] ^= 0x01
    print("  Prueba 3 - Se altera un byte del mensaje cifrado")
    try:
        salida = decifrar_mensaje(bytes(alterado), iv1, RSA_Privada, verboso=False)
        ok3 = (salida != MENSAJE)
        print("     El texto recuperado quedo danado: %s" % ("SI" if ok3 else "NO"))
    except Exception as error:
        ok3 = True
        print("     El descifrado fallo, como se esperaba (%s)" % type(error).__name__)
    resultados.append(("3. Un criptograma alterado no devuelve el mensaje", ok3))
    print("     Resultado: %s\n" % ("CORRECTO" if ok3 else "FALLO"))

    # Prueba 4: con otra clave privada no se debe poder leer nada. Esto
    # demuestra que la seguridad esta en la clave, no en esconder el codigo.
    otra_privada = RSA.generate(BITS_RSA)
    print("  Prueba 4 - Intento de descifrar con una clave privada ajena")
    try:
        salida = decifrar_mensaje(msg1, iv1, otra_privada, verboso=False)
        ok4 = (salida != MENSAJE)
        print("     Salio basura en lugar del mensaje: %s" % ("SI" if ok4 else "NO"))
    except Exception as error:
        ok4 = True
        print("     El descifrado fallo, como se esperaba (%s)" % type(error).__name__)
    resultados.append(("4. Una clave privada equivocada no descifra", ok4))
    print("     Resultado: %s\n" % ("CORRECTO" if ok4 else "FALLO"))

    print("-" * 70)
    print("  RESUMEN DE PRUEBAS")
    for nombre, ok in resultados:
        print("     [%s] %s" % ("OK" if ok else "  ", nombre))
    total = sum(1 for _, ok in resultados if ok)
    print("\n  Pruebas superadas: %d de %d" % (total, len(resultados)))
    print("-" * 70)
    return total == len(resultados)


# ======================================================================
# PROGRAMA PRINCIPAL
# ======================================================================

def main():
    print("=" * 70)
    print(" PRACTICA 3 - ALGORITMO HIBRIDO RSA + AES")
    print(" Seguridad Informatica | Facultad de Ingenieria - UACAM")
    print(" Alumno: Kevin del Jesus Gonzalez Maas")
    print("=" * 70)

    print("\nDATOS DEL ENVIO")
    print("  Mensaje original  : \"%s\"" % MENSAJE)
    print("  Longitud          : %d caracteres" % len(MENSAJE))
    print("  Cifrado simetrico : AES-256 en modo CBC con relleno PKCS#7")
    print("  Cifrado asimetrico: RSA de %d bits con relleno OAEP" % BITS_RSA)

    # --- Paso 1: las claves del que va a recibir el mensaje
    print("\nPASO 1: Generar el par de claves RSA del receptor")
    llave = RSA.generate(BITS_RSA)
    RSA_Privada = llave
    RSA_Publica = llave.publickey()
    # Los numeros los corto al imprimir porque completos son de 600 digitos
    print("  n (%d bits) : %s..." % (llave.n.bit_length(), str(llave.n)[:60]))
    print("  e = %d" % llave.e)
    print("  d = %s..." % str(llave.d)[:60])
    print("  Clave publica  KU = (e, n)")
    print("  Clave privada  KR = (d, n)")

    # --- Paso 2: el emisor prepara el envio
    print("\nPASO 2: El emisor prepara el envio")
    print("  iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(RSA_Publica)")
    iv_cifrado_RSA, mensajeCifrado_AES = get_Msj_And_Key(RSA_Publica)

    print("\n  Lo que viaja por el canal:")
    print("  a) iv_cifrado_RSA (IV + clave AES protegidos con RSA):")
    print("     %s..." % a_hex(iv_cifrado_RSA, 64))
    print("  b) mensajeCifrado_AES (en hexadecimal):")
    hexadecimal = a_hex(mensajeCifrado_AES)
    for i in range(0, len(hexadecimal), 64):
        print("     %s" % hexadecimal[i:i + 64])

    # --- Paso 3: el receptor abre el envio
    print("\nPASO 3: El receptor descifra el envio")
    print("  decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)")
    recuperado = decifrar_mensaje(mensajeCifrado_AES, iv_cifrado_RSA, RSA_Privada)
    print("\n  MENSAJE DESCIFRADO:")
    print("  \"%s\"" % recuperado)

    # --- Paso 4: pruebo la funcion auxiliar por separado
    print("\nPASO 4: Prueba de la funcion auxiliar")
    print("  Cifrado_AES_enviar_mensaje(\"Mensaje\", iv)")
    iv_demo = get_random_bytes(TAM_IV)
    cifrado_demo = Cifrado_AES_enviar_mensaje("Mensaje", iv_demo)
    print("  Texto de entrada : \"Mensaje\" (7 bytes)")
    print("  IV utilizado     : %s" % a_hex(iv_demo))
    print("  Resultado        : %s (%d bytes)" % (a_hex(cifrado_demo), len(cifrado_demo)))

    print("\nCOMPROBACION FINAL")
    print("  Mensaje original   : \"%s\"" % MENSAJE)
    print("  Mensaje recuperado : \"%s\"" % recuperado)
    print("  Coinciden: %s" % ("SI" if recuperado == MENSAJE else "NO"))

    print("\n" + "=" * 70)
    print(" PRUEBAS DE FUNCIONAMIENTO")
    print("=" * 70 + "\n")
    todo_bien = pruebas(RSA_Publica, RSA_Privada)

    print("=" * 70)
    print(" RESULTADO GENERAL: %s"
          % ("TODO CORRECTO" if todo_bien and recuperado == MENSAJE else "HAY FALLOS"))
    print("=" * 70)


if __name__ == "__main__":
    main()
