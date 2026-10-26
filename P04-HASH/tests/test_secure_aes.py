import base64

import pytest

pytest.importorskip("Crypto", reason="pycryptodome no instalado")

from utils import secureAES


@pytest.fixture
def key():
    return secureAES.getKey(16)


def test_getkey_tamano_y_aleatoriedad():
    for size in (16, 24, 32):
        assert len(secureAES.getKey(size)) == size
    assert secureAES.getKey(16) != secureAES.getKey(16)


@pytest.mark.parametrize("texto", ["", "a", "hola mundo", "x" * 16, "x" * 100, "ñandú 🔐 contraseña"])
def test_roundtrip(key, texto):
    iv, cifrado = secureAES.encode(key, texto)
    assert secureAES.decode(key, iv, cifrado) == texto


def test_salida_es_base64_y_iv_16_bytes(key):
    iv, cifrado = secureAES.encode(key, "hola")
    assert len(base64.b64decode(iv)) == 16
    assert len(base64.b64decode(cifrado)) % 16 == 0


def test_iv_distinto_cada_vez(key):
    a = secureAES.encode(key, "mismo")
    b = secureAES.encode(key, "mismo")
    assert a[0] != b[0]
    assert a[1] != b[1]


def test_clave_incorrecta_falla(key):
    iv, cifrado = secureAES.encode(key, "secreto")
    otra = secureAES.getKey(16)
    try:
        resultado = secureAES.decode(otra, iv, cifrado)
    except (ValueError, UnicodeDecodeError):
        return
    assert resultado != "secreto"


def test_clave_invalida_en_encode():
    with pytest.raises(ValueError):
        secureAES.encode(b"corta", "x")
