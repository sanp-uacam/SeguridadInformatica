import pytest

from cifrado_hibrido import (
    ErrorCifrado,
    Cifrado_AES_enviar_mensaje,
    decifrar_mensaje,
    generar_claves_rsa,
    get_Msj_And_Key,
)


@pytest.fixture(scope="module")
def claves():
    return generar_claves_rsa(2048)


@pytest.mark.parametrize(
    "mensaje",
    ["", "hola", "Mensaje con acentos: informacion y cancion", "Cifrado seguro 🔐"],
)
def test_cifrar_y_descifrar_recupera_el_original(claves, mensaje):
    sobre, cifrado = get_Msj_And_Key(claves.publica_pem, mensaje)
    assert decifrar_mensaje(cifrado, sobre, claves.privada_pem) == mensaje


def test_mismo_mensaje_produce_resultados_distintos(claves):
    primero = get_Msj_And_Key(claves.publica_pem, "repetido")
    segundo = get_Msj_And_Key(claves.publica_pem, "repetido")
    assert primero != segundo


def test_detecta_modificacion_del_mensaje(claves):
    sobre, cifrado = get_Msj_And_Key(claves.publica_pem, "no modificar")
    alterado = cifrado[:-1] + bytes([cifrado[-1] ^ 1])
    with pytest.raises(ErrorCifrado, match="autenticidad"):
        decifrar_mensaje(alterado, sobre, claves.privada_pem)


def test_rechaza_clave_privada_de_otro_receptor(claves):
    otras_claves = generar_claves_rsa(2048)
    sobre, cifrado = get_Msj_And_Key(claves.publica_pem, "secreto")
    with pytest.raises(ErrorCifrado, match="sobre RSA"):
        decifrar_mensaje(cifrado, sobre, otras_claves.privada_pem)


def test_rechaza_sobre_truncado(claves):
    sobre, cifrado = get_Msj_And_Key(claves.publica_pem, "secreto")
    with pytest.raises(ErrorCifrado):
        decifrar_mensaje(cifrado, sobre[:-10], claves.privada_pem)


def test_valida_longitudes_de_aes():
    with pytest.raises(ValueError, match="clave AES"):
        Cifrado_AES_enviar_mensaje("hola", b"0" * 16, b"x" * 16)
    with pytest.raises(ValueError, match="IV"):
        Cifrado_AES_enviar_mensaje("hola", b"0" * 32, b"x" * 32)

