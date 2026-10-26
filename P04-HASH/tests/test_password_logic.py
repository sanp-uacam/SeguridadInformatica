import hashlib

import pytest

from utils.login_app import LoginApp


@pytest.fixture
def logic():
    """Instancia sin Tk: solo métodos puros."""
    obj = LoginApp.__new__(LoginApp)
    obj.users = {}
    return obj


class TestHash:
    def test_sha256_conocido(self, logic):
        assert logic.hash_password("abc") == hashlib.sha256(b"abc").hexdigest()

    def test_determinista_y_hex64(self, logic):
        h = logic.hash_password("Clave!x9")
        assert h == logic.hash_password("Clave!x9")
        assert len(h) == 64
        int(h, 16)

    def test_distintas_claves_distinto_hash(self, logic):
        assert logic.hash_password("a") != logic.hash_password("A")

    def test_unicode_y_vacio(self, logic):
        assert logic.hash_password("") == hashlib.sha256(b"").hexdigest()
        assert logic.hash_password("ñ🔐") == hashlib.sha256("ñ🔐".encode()).hexdigest()


class TestSecuencias:
    @pytest.mark.parametrize("pwd", ["abc", "xyzabc", "123", "321", "cba", "Pabcq", "a987b", "ABC", "9abcd0"])
    def test_detecta(self, logic, pwd):
        assert logic.has_alpha_numeric_sequence(pwd) is True

    @pytest.mark.parametrize("pwd", ["", "ab", "12", "acb", "135", "aaa", "111", "ab1", "a1b2c3", "ab!c", "zab"])
    def test_no_detecta(self, logic, pwd):
        assert logic.has_alpha_numeric_sequence(pwd) is False

    def test_no_cruza_alfa_y_digito(self, logic):
        # 'b','c','d' alfabéticos consecutivos pero separados por símbolo
        assert logic.has_alpha_numeric_sequence("b!c!d") is False

    def test_secuencia_en_medio(self, logic):
        assert logic.has_alpha_numeric_sequence("Z#456#Z") is True


class TestValidatePassword:
    VALIDA = "Zq!k9Tm#"

    def test_valida_cumple_todo(self, logic):
        assert all(logic.validate_password("ana", self.VALIDA).values())

    def test_claves_del_resultado(self, logic):
        assert set(logic.validate_password("a", "b")) == {
            "length", "uppercase", "no_sequence", "special", "not_username",
        }

    def test_longitud(self, logic):
        assert logic.validate_password("u", "Zq!k9T#")["length"] is False  # 7
        assert logic.validate_password("u", "Zq!k9Tm#")["length"] is True  # 8

    def test_mayuscula(self, logic):
        assert logic.validate_password("u", "zq!k9tm#")["uppercase"] is False
        assert logic.validate_password("u", "Zq!k9tm#")["uppercase"] is True

    def test_especial(self, logic):
        assert logic.validate_password("u", "Zqak9Tmx")["special"] is False
        assert logic.validate_password("u", "Zqak9Tm_")["special"] is True

    def test_especial_unicode_cuenta(self, logic):
        assert logic.validate_password("u", "Zqak9Tmñ")["special"] is True

    def test_secuencia(self, logic):
        assert logic.validate_password("u", "Zq!abcTm")["no_sequence"] is False

    def test_no_igual_usuario(self, logic):
        assert logic.validate_password("Admin!Zz", "admin!zz")["not_username"] is False
        assert logic.validate_password("  admin!zz ", "ADMIN!ZZ")["not_username"] is False
        assert logic.validate_password("otro", "admin!zz")["not_username"] is True

    def test_password_vacia_no_pasa_not_username(self, logic):
        checks = logic.validate_password("", "")
        assert checks["not_username"] is False
        assert not all(checks.values())

    def test_password_solo_espacios(self, logic):
        assert logic.validate_password("u", "        ")["not_username"] is False


class TestFindUser:
    def test_encuentra_normalizado(self, logic):
        logic.users = {"ana": "hash"}
        assert logic.find_user("  ANA ") == "hash"

    def test_no_existe(self, logic):
        assert logic.find_user("nadie") is None
