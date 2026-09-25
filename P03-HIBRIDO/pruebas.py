"""
=============================================================================
 Seguridad Informatica - Practica 3
 PRUEBAS AUTOMATICAS del algoritmo hibrido RSA + AES

 Cubre el entregable 3: "Pruebas que demuestren el correcto funcionamiento".

 Ejecutar con:   python pruebas.py
=============================================================================
"""

import base64
import secrets
import traceback

from algoritmo_hibrido import (
    TAM_CLAVE_AES, TAM_BLOQUE_AES,
    generar_par_rsa, get_Msj_And_Key, decifrar_mensaje,
    Cifrado_AES_enviar_mensaje, aplicar_padding, quitar_padding,
    PaqueteCifrado,
)

# Se genera un solo par de claves para todas las pruebas (RSA es lento).
PUBLICA, PRIVADA = generar_par_rsa()

_resultados = []


def prueba(nombre):
    """Decorador que ejecuta una prueba y registra si paso o fallo."""
    def envoltura(funcion):
        try:
            funcion()
            _resultados.append((nombre, True, ""))
            print(f"  [OK]    {nombre}")
        except AssertionError as err:
            _resultados.append((nombre, False, str(err)))
            print(f"  [FALLA] {nombre}  -> {err}")
        except Exception as err:
            _resultados.append((nombre, False, repr(err)))
            print(f"  [ERROR] {nombre}  -> {err.__class__.__name__}: {err}")
            traceback.print_exc()
        return funcion
    return envoltura


def ciclo(mensaje: str) -> str:
    """Cifra y descifra un mensaje; devuelve el texto recuperado."""
    paq = get_Msj_And_Key(PUBLICA, mensaje)
    return decifrar_mensaje(
        paq.mensajeCifrado_AES, paq.iv_cifrado_RSA,
        paq.clave_AES_cifrada_RSA, PRIVADA,
    )


# ===========================================================================
print("\n--- GRUPO 1: FUNCIONAMIENTO BASICO ---")
# ===========================================================================

@prueba("Mensaje corto se recupera identico")
def _():
    m = "Hola"
    assert ciclo(m) == m


@prueba("Mensaje con acentos, enies y simbolos")
def _():
    m = "Camión, ñandú, ¿qué tal? 100% #seguro @UACAM"
    assert ciclo(m) == m


@prueba("Mensaje largo (10 000 caracteres)")
def _():
    m = "A" * 10_000
    assert ciclo(m) == m


@prueba("Mensaje de exactamente 16 bytes (un bloque justo)")
def _():
    m = "1234567890123456"
    assert len(m.encode()) == 16
    assert ciclo(m) == m


@prueba("Mensaje vacio")
def _():
    assert ciclo("") == ""


@prueba("Mensaje con saltos de linea y tabulaciones")
def _():
    m = "Linea 1\nLinea 2\tcon tabulacion\r\nFin"
    assert ciclo(m) == m


# ===========================================================================
print("\n--- GRUPO 2: PADDING PKCS#7 ---")
# ===========================================================================

@prueba("El padding siempre deja multiplo de 16 bytes")
def _():
    for n in range(0, 40):
        relleno = aplicar_padding(b"x" * n)
        assert len(relleno) % TAM_BLOQUE_AES == 0, f"falla con n={n}"


@prueba("Padding y quitar padding son inversos")
def _():
    for n in range(0, 40):
        datos = secrets.token_bytes(n)
        assert quitar_padding(aplicar_padding(datos)) == datos


@prueba("Un mensaje multiplo de 16 recibe un bloque completo de relleno")
def _():
    relleno = aplicar_padding(b"x" * 16)
    assert len(relleno) == 32
    assert relleno[-1] == 16


@prueba("Padding corrupto es rechazado")
def _():
    malo = b"x" * 15 + bytes([99])   # 99 no es un relleno valido
    try:
        quitar_padding(malo)
    except ValueError:
        return
    assert False, "deberia haber lanzado ValueError"


# ===========================================================================
print("\n--- GRUPO 3: ALEATORIEDAD Y NO DETERMINISMO ---")
# ===========================================================================

@prueba("Cifrar dos veces el mismo mensaje da criptogramas distintos")
def _():
    m = "Mensaje repetido"
    p1 = get_Msj_And_Key(PUBLICA, m)
    p2 = get_Msj_And_Key(PUBLICA, m)
    assert p1.mensajeCifrado_AES != p2.mensajeCifrado_AES, "el AES es determinista"
    assert p1.clave_AES_cifrada_RSA != p2.clave_AES_cifrada_RSA, "el RSA es determinista"
    assert p1.iv_cifrado_RSA != p2.iv_cifrado_RSA


@prueba("Ambos criptogramas distintos descifran al mismo texto")
def _():
    m = "Mensaje repetido"
    p1 = get_Msj_And_Key(PUBLICA, m)
    p2 = get_Msj_And_Key(PUBLICA, m)
    r1 = decifrar_mensaje(p1.mensajeCifrado_AES, p1.iv_cifrado_RSA,
                          p1.clave_AES_cifrada_RSA, PRIVADA)
    r2 = decifrar_mensaje(p2.mensajeCifrado_AES, p2.iv_cifrado_RSA,
                          p2.clave_AES_cifrada_RSA, PRIVADA)
    assert r1 == r2 == m


@prueba("Bloques repetidos no producen cifrado repetido (CBC no es ECB)")
def _():
    clave = secrets.token_bytes(TAM_CLAVE_AES)
    iv = secrets.token_bytes(TAM_BLOQUE_AES)
    # Dos bloques identicos de 16 bytes seguidos
    cifrado = Cifrado_AES_enviar_mensaje("A" * 32, iv, clave)
    b1, b2 = cifrado[:16], cifrado[16:32]
    assert b1 != b2, "bloques identicos dieron cifrado identico: parece modo ECB"


# ===========================================================================
print("\n--- GRUPO 4: SEGURIDAD (deben FALLAR) ---")
# ===========================================================================

@prueba("Otra clave privada RSA no puede descifrar")
def _():
    _, otra_privada = generar_par_rsa()
    paq = get_Msj_And_Key(PUBLICA, "Informacion confidencial")
    try:
        decifrar_mensaje(paq.mensajeCifrado_AES, paq.iv_cifrado_RSA,
                         paq.clave_AES_cifrada_RSA, otra_privada)
    except Exception:
        return
    assert False, "una clave privada ajena logro descifrar el mensaje"


@prueba("Alterar el criptograma AES rompe el descifrado")
def _():
    paq = get_Msj_And_Key(PUBLICA, "Transferir 1000 pesos a la cuenta 123")
    crudo = bytearray(base64.b64decode(paq.mensajeCifrado_AES))
    crudo[-1] ^= 0x01                       # se voltea un solo bit
    alterado = base64.b64encode(bytes(crudo)).decode()
    try:
        salida = decifrar_mensaje(alterado, paq.iv_cifrado_RSA,
                                  paq.clave_AES_cifrada_RSA, PRIVADA)
    except Exception:
        return                              # lo esperado: error de padding
    assert salida != "Transferir 1000 pesos a la cuenta 123", \
        "el mensaje alterado se descifro sin cambios"


@prueba("Alterar el IV cifrado con RSA rompe el descifrado")
def _():
    paq = get_Msj_And_Key(PUBLICA, "Mensaje de prueba de integridad")
    crudo = bytearray(base64.b64decode(paq.iv_cifrado_RSA))
    crudo[0] ^= 0xFF
    alterado = base64.b64encode(bytes(crudo)).decode()
    try:
        decifrar_mensaje(paq.mensajeCifrado_AES, alterado,
                         paq.clave_AES_cifrada_RSA, PRIVADA)
    except Exception:
        return
    assert False, "el IV alterado no produjo ningun error"


@prueba("Truncar el criptograma es detectado")
def _():
    paq = get_Msj_And_Key(PUBLICA, "Mensaje suficientemente largo para cortar")
    crudo = base64.b64decode(paq.mensajeCifrado_AES)[:-5]   # se quitan 5 bytes
    cortado = base64.b64encode(crudo).decode()
    try:
        decifrar_mensaje(cortado, paq.iv_cifrado_RSA,
                         paq.clave_AES_cifrada_RSA, PRIVADA)
    except ValueError:
        return
    assert False, "no se detecto el criptograma truncado"


# ===========================================================================
print("\n--- GRUPO 5: VALIDACION DE PARAMETROS ---")
# ===========================================================================

@prueba("Un IV de 32 bytes es rechazado (lo que pedia el enunciado)")
def _():
    clave = secrets.token_bytes(TAM_CLAVE_AES)
    iv_malo = secrets.token_bytes(32)
    try:
        Cifrado_AES_enviar_mensaje("Hola", iv_malo, clave)
    except ValueError:
        return
    assert False, "se acepto un IV de 32 bytes en modo CBC"


@prueba("Una clave AES de 16 bytes es rechazada (se exige AES-256)")
def _():
    try:
        Cifrado_AES_enviar_mensaje("Hola", secrets.token_bytes(16),
                                   secrets.token_bytes(16))
    except ValueError:
        return
    assert False, "se acepto una clave de 16 bytes"


# ===========================================================================
print("\n--- GRUPO 6: SERIALIZACION DEL PAQUETE ---")
# ===========================================================================

@prueba("El paquete sobrevive a un viaje de ida y vuelta por JSON")
def _():
    m = "Mensaje que viaja como JSON"
    paq = get_Msj_And_Key(PUBLICA, m)
    copia = PaqueteCifrado.desde_json(paq.a_json())
    assert decifrar_mensaje(copia.mensajeCifrado_AES, copia.iv_cifrado_RSA,
                            copia.clave_AES_cifrada_RSA, PRIVADA) == m


@prueba("Los tamanos cifrados con RSA-2048 son de 256 bytes")
def _():
    paq = get_Msj_And_Key(PUBLICA, "Hola")
    tam = paq.tamanos()
    assert tam["iv_cifrado_RSA"] == 256, tam
    assert tam["clave_AES_cifrada_RSA"] == 256, tam


# ===========================================================================
#  RESUMEN
# ===========================================================================
if __name__ == "__main__":
    total = len(_resultados)
    exitosas = sum(1 for _, ok, _ in _resultados if ok)

    print("\n" + "=" * 68)
    print(f" RESUMEN: {exitosas} de {total} pruebas superadas")
    print("=" * 68)

    fallidas = [(n, d) for n, ok, d in _resultados if not ok]
    if fallidas:
        print("\n Pruebas fallidas:")
        for nombre, detalle in fallidas:
            print(f"  - {nombre}: {detalle}")
    else:
        print(" Todas las pruebas se superaron correctamente.")
