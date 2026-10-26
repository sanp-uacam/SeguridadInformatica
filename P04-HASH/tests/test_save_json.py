import json

from utils import saveJson


class TestNormalizar:
    def test_dict_simple(self):
        assert saveJson.normalizar_usuarios({"Ana": "h1"}) == {"ana": "h1"}

    def test_casefold_y_strip(self):
        assert saveJson.normalizar_usuarios({"  STRASSE ": "h"}) == {"strasse": "h"}
        assert saveJson.normalizar_usuarios({"Straße": "h"}) == {"strasse": "h"}

    def test_lista_un_par_por_objeto(self):
        datos = [{"ana": "h1"}, {"luis": "h2"}]
        assert saveJson.normalizar_usuarios(datos) == {"ana": "h1", "luis": "h2"}

    def test_formato_estructurado_antiguo(self):
        datos = [
            {"username": "Ana", "password_hash": "h1"},
            {"usuario": "Luis", "password": "h2"},
            {"usuario": "Eva", "contraseña": "h3"},
        ]
        assert saveJson.normalizar_usuarios(datos) == {"ana": "h1", "luis": "h2", "eva": "h3"}

    def test_duplicados_primero_gana(self):
        datos = [{"ana": "primero"}, {"ANA": "segundo"}]
        assert saveJson.normalizar_usuarios(datos) == {"ana": "primero"}

    def test_descarta_invalidos(self):
        datos = {"": "h", "  ": "h", "ok": "h", "sinhash": "", "num": 5, "nulo": None}
        assert saveJson.normalizar_usuarios(datos) == {"ok": "h"}

    def test_lista_con_elementos_no_dict(self):
        assert saveJson.normalizar_usuarios([1, "x", None, {"a": "h"}]) == {"a": "h"}

    def test_tipos_no_soportados(self):
        for valor in (None, 42, "texto"):
            assert saveJson.normalizar_usuarios(valor) == {}

    def test_vacio(self):
        assert saveJson.normalizar_usuarios({}) == {}
        assert saveJson.normalizar_usuarios([]) == {}


class TestGuardarCargar:
    def test_roundtrip(self, tmp_path):
        ruta = tmp_path / "db.json"
        assert saveJson.guardar_usuarios({"Ana": "h1", "Luis": "h2"}, str(ruta)) is True
        assert saveJson.cargar_usuarios(str(ruta)) == {"ana": "h1", "luis": "h2"}

    def test_guarda_objeto_unico_normalizado(self, tmp_path):
        ruta = tmp_path / "db.json"
        saveJson.guardar_usuarios({"ANA": "h"}, str(ruta))
        assert json.loads(ruta.read_text(encoding="utf-8")) == {"ana": "h"}

    def test_guardar_ruta_invalida_devuelve_false(self, tmp_path):
        ruta = tmp_path / "no_existe" / "db.json"
        assert saveJson.guardar_usuarios({"a": "h"}, str(ruta)) is False

    def test_cargar_archivo_inexistente(self, tmp_path):
        assert saveJson.cargar_usuarios(str(tmp_path / "nada.json")) == {}

    def test_cargar_json_corrupto(self, tmp_path):
        ruta = tmp_path / "db.json"
        ruta.write_text("{ no es json", encoding="utf-8")
        assert saveJson.cargar_usuarios(str(ruta)) == {}

    def test_cargar_archivo_vacio(self, tmp_path):
        ruta = tmp_path / "db.json"
        ruta.write_text("", encoding="utf-8")
        assert saveJson.cargar_usuarios(str(ruta)) == {}

    def test_cargar_formato_lista_antiguo(self, tmp_path):
        ruta = tmp_path / "db.json"
        ruta.write_text(json.dumps([{"username": "Ana", "password_hash": "h"}]), encoding="utf-8")
        assert saveJson.cargar_usuarios(str(ruta)) == {"ana": "h"}

    def test_caracteres_unicode(self, tmp_path):
        ruta = tmp_path / "db.json"
        saveJson.guardar_usuarios({"ñandú": "h"}, str(ruta))
        assert "ñandú" in ruta.read_text(encoding="utf-8")
        assert saveJson.cargar_usuarios(str(ruta)) == {"ñandú": "h"}

    def test_alias_compatibilidad(self):
        assert saveJson.guardar_diccionario is saveJson.guardar_usuarios
        assert saveJson.cargar_diccionario is saveJson.cargar_usuarios
