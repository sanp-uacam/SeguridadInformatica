import tkinter as tk

import pytest

from utils import saveJson


def set_entry(entry, text):
    entry.delete(0, tk.END)
    entry.insert(0, text)


@pytest.fixture
def dashboards(app, monkeypatch):
    """Evita abrir dashboard real: registra las llamadas."""
    calls = []
    monkeypatch.setattr(app, "open_dashboard", lambda u: calls.append(u))
    return calls


class TestLogin:
    def test_campos_vacios(self, app, messages, dashboards):
        app.login()
        assert messages == [("error", "Error", "Por favor, complete todos los campos")]
        assert dashboards == []

    def test_falta_password(self, app, messages, dashboards):
        set_entry(app.user_entry, "ana")
        app.login()
        assert messages[-1][2] == "Por favor, complete todos los campos"

    def test_solo_espacios_en_usuario(self, app, messages, dashboards):
        set_entry(app.user_entry, "   ")
        set_entry(app.pass_entry, "x")
        app.login()
        assert messages[-1][2] == "Por favor, complete todos los campos"

    def test_usuario_inexistente(self, app, messages, dashboards):
        set_entry(app.user_entry, "nadie")
        set_entry(app.pass_entry, "x")
        app.login()
        assert messages == [("error", "Error", "Usuario no encontrado")]
        assert dashboards == []

    def test_password_incorrecta(self, app, messages, dashboards):
        app.users["ana"] = app.hash_password("Zq!k9Tm#")
        set_entry(app.user_entry, "ana")
        set_entry(app.pass_entry, "mala")
        app.login()
        assert messages == [("error", "Error", "Contraseña incorrecta")]
        assert dashboards == []

    def test_login_correcto(self, app, messages, dashboards):
        app.users["ana"] = app.hash_password("Zq!k9Tm#")
        set_entry(app.user_entry, "ana")
        set_entry(app.pass_entry, "Zq!k9Tm#")
        app.login()
        assert messages == [("info", "Éxito", "¡Bienvenido, ana!")]
        assert dashboards == ["ana"]

    def test_usuario_insensible_a_mayusculas_y_espacios(self, app, messages, dashboards):
        app.users["ana"] = app.hash_password("Zq!k9Tm#")
        set_entry(app.user_entry, "  ANA ")
        set_entry(app.pass_entry, "Zq!k9Tm#")
        app.login()
        assert dashboards == ["ana"]

    def test_password_sensible_a_mayusculas(self, app, messages, dashboards):
        app.users["ana"] = app.hash_password("Zq!k9Tm#")
        set_entry(app.user_entry, "ana")
        set_entry(app.pass_entry, "zq!k9tm#")
        app.login()
        assert messages[-1][2] == "Contraseña incorrecta"

    def test_password_no_se_recorta(self, app, messages, dashboards):
        app.users["ana"] = app.hash_password("Zq!k9Tm#")
        set_entry(app.user_entry, "ana")
        set_entry(app.pass_entry, "Zq!k9Tm# ")
        app.login()
        assert messages[-1][2] == "Contraseña incorrecta"

    def test_enter_en_password_lanza_login(self, app, messages, dashboards):
        app.root.deiconify()
        app.root.update()
        set_entry(app.user_entry, "nadie")
        set_entry(app.pass_entry, "x")
        app.pass_entry.focus_force()
        app.root.update()
        app.pass_entry.event_generate("<Return>")
        app.root.update()
        assert messages and messages[-1][2] == "Usuario no encontrado"


class TestClear:
    def test_limpia_campos(self, app):
        set_entry(app.user_entry, "ana")
        set_entry(app.pass_entry, "x")
        app.clear_fields()
        assert app.user_entry.get() == ""
        assert app.pass_entry.get() == ""

    def test_password_enmascarada(self, app):
        assert app.pass_entry.cget("show") == "*"


class TestInit:
    def test_ruta_db_en_raiz_proyecto(self, root, monkeypatch, messages):
        from utils import login_app

        monkeypatch.setattr(saveJson, "cargar_usuarios", lambda p: {"ana": "h"})
        inst = login_app.LoginApp(root)
        assert inst.users_file.endswith("users-db.json")
        assert "utils" not in inst.users_file.split("/")[-2:-1]
        assert inst.users == {"ana": "h"}

    def test_titulo(self, app):
        assert app.root.title() == "Sistema de Login"


class TestShowMessage:
    def test_info_y_error_se_distinguen(self, app, messages):
        app.show_message("info", "T", "m")
        app.show_message("error", "T", "m")
        assert [m[0] for m in messages] == ["info", "error"]

    def test_topmost_se_restaura(self, app, messages):
        app.show_message("info", "T", "m")
        assert not app.root.attributes("-topmost")

    def test_topmost_se_restaura_si_dialogo_falla(self, app, monkeypatch):
        from tkinter import messagebox

        def boom(*a, **k):
            raise RuntimeError("fallo")

        monkeypatch.setattr(messagebox, "showinfo", boom)
        with pytest.raises(RuntimeError):
            app.show_message("info", "T", "m")
        assert not app.root.attributes("-topmost")


class TestDashboard:
    def _dashboard(self, app):
        return [w for w in app.root.winfo_children() if isinstance(w, tk.Toplevel)]

    def test_abre_y_oculta_login(self, app):
        app.open_dashboard("ana")
        assert app.root.state() == "withdrawn"
        dash = self._dashboard(app)[-1]
        labels = [w.cget("text") for w in dash.winfo_children() if isinstance(w, tk.Label)]
        assert "Bienvenido al Sistema, ana!" in labels

    def test_logout_restaura_login_y_limpia(self, app):
        set_entry(app.user_entry, "ana")
        set_entry(app.pass_entry, "x")
        app.open_dashboard("ana")
        dash = self._dashboard(app)[-1]
        btn = next(w for w in dash.winfo_children() if isinstance(w, tk.Button))
        btn.invoke()
        assert app.root.state() == "normal"
        assert app.user_entry.get() == ""
        assert app.pass_entry.get() == ""
        assert not dash.winfo_exists()
