import json
import tkinter as tk

import pytest

from utils import saveJson


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


class Form:
    """Maneja la ventana de registro por sus widgets."""

    def __init__(self, app):
        self.app = app
        app.root.deiconify()
        app.root.update()
        before = set(app.root.winfo_children())
        app.signin()
        self.win = next(w for w in app.root.winfo_children() if w not in before)
        self.win.update()
        entries = [w for w in walk(self.win) if isinstance(w, tk.Entry)]
        self.user, self.pwd, self.confirm = entries
        self.buttons = {w.cget("text"): w for w in walk(self.win) if isinstance(w, tk.Button)}
        self.labels = [w for w in walk(self.win) if isinstance(w, tk.Label)]

    def fill(self, user, pwd, confirm=None):
        for entry, text in ((self.user, user), (self.pwd, pwd), (self.confirm, pwd if confirm is None else confirm)):
            entry.delete(0, tk.END)
            entry.insert(0, text)

    def submit(self):
        self.buttons["Crear cuenta"].invoke()

    def checklist(self):
        return {k: lbl.cget("text")[0] for k, lbl in self.app.password_rules.items()}

    def status(self):
        return next(l.cget("text") for l in self.labels if l.cget("fg") == "#b00020" and l.cget("font") == "Arial 10" and l not in self.app.password_rules.values())


@pytest.fixture
def form(app):
    return Form(app)


GOOD = "Zq!k9Tm#"


class TestChecklist:
    def test_inicial_todo_rojo(self, form):
        assert set(form.checklist().values()) == {"✗"} or form.checklist()["no_sequence"] == "✓"
        assert form.checklist()["length"] == "✗"

    def test_se_actualiza_al_teclear(self, form):
        form.user.insert(0, "ana")
        form.pwd.insert(0, GOOD)
        form.pwd.focus_force()
        form.win.update()
        form.pwd.event_generate("<KeyRelease>")
        form.win.update()
        assert set(form.checklist().values()) == {"✓"}

    def test_aviso_no_coinciden(self, form):
        form.pwd.insert(0, GOOD)
        form.confirm.insert(0, "otra")
        form.confirm.focus_force()
        form.win.update()
        form.confirm.event_generate("<KeyRelease>")
        form.win.update()
        assert any(l.cget("text") == "Las contraseñas no coinciden" for l in form.labels)


class TestCrearUsuario:
    def test_campos_vacios(self, form, messages):
        form.submit()
        assert messages == [("error", "Error", "Por favor, complete todos los campos")]

    def test_falta_confirmacion(self, form, messages):
        form.user.insert(0, "ana")
        form.pwd.insert(0, GOOD)
        form.submit()
        assert messages[-1][2] == "Por favor, complete todos los campos"

    def test_usuario_ya_existe(self, form, app, messages):
        app.users["ana"] = "h"
        form.fill("ANA", GOOD)
        form.submit()
        assert messages[-1][2] == "El usuario ya existe"
        assert app.users["ana"] == "h"

    def test_password_debil(self, form, app, messages):
        form.fill("ana", "abc")
        form.submit()
        assert messages[-1][2] == "La contraseña no cumple todos los requisitos"
        assert "ana" not in app.users

    @pytest.mark.parametrize("pwd", ["Zq!k9T#", "zq!k9tm#", "Zqak9Tmx", "Zq!abcTm"])
    def test_cada_regla_bloquea(self, form, app, messages, pwd):
        form.fill("ana", pwd)
        form.submit()
        assert messages[-1][2] == "La contraseña no cumple todos los requisitos"
        assert app.users == {}

    def test_password_igual_a_usuario(self, form, app, messages):
        form.fill("Zq!k9Tm#", "Zq!k9Tm#")
        form.submit()
        assert messages[-1][2] == "La contraseña no cumple todos los requisitos"

    def test_confirmacion_distinta(self, form, app, messages):
        form.fill("ana", GOOD, "Zq!k9Tm$")
        form.submit()
        assert messages[-1][2] == "Las contraseñas no coinciden"
        assert app.users == {}

    def test_registro_correcto(self, form, app, messages):
        form.fill("  Ana ", GOOD)
        form.submit()
        assert messages[-1] == ("info", "Éxito", "Usuario registrado correctamente")
        assert app.users == {"ana": app.hash_password(GOOD)}
        assert not form.win.winfo_exists()

    def test_guarda_hash_no_texto_plano(self, form, app, messages):
        form.fill("ana", GOOD)
        form.submit()
        contenido = open(app.users_file, encoding="utf-8").read()
        assert GOOD not in contenido
        assert json.loads(contenido) == {"ana": app.hash_password(GOOD)}

    def test_rellena_login_tras_registro(self, form, app, messages):
        form.fill("Ana", GOOD)
        form.submit()
        assert app.user_entry.get() == "ana"
        assert app.pass_entry.get() == ""

    def test_registrado_puede_loguear(self, form, app, messages, monkeypatch):
        form.fill("ana", GOOD)
        form.submit()
        llamadas = []
        monkeypatch.setattr(app, "open_dashboard", llamadas.append)
        app.pass_entry.insert(0, GOOD)
        app.login()
        assert llamadas == ["ana"]

    def test_persistencia_entre_sesiones(self, form, app, messages):
        form.fill("ana", GOOD)
        form.submit()
        assert saveJson.cargar_usuarios(app.users_file) == {"ana": app.hash_password(GOOD)}

    def test_fallo_al_guardar_revierte(self, form, app, messages, monkeypatch):
        monkeypatch.setattr(saveJson, "guardar_usuarios", lambda *a, **k: False)
        form.fill("ana", GOOD)
        form.submit()
        assert messages[-1][2] == "No se pudo guardar el usuario"
        assert "ana" not in app.users
        assert form.win.winfo_exists()

    def test_enter_en_confirmar_crea(self, form, app, messages):
        form.fill("ana", GOOD)
        form.confirm.focus_force()
        form.win.update()
        form.confirm.event_generate("<Return>")
        form.win.update()
        assert "ana" in app.users

    def test_cancelar_cierra_sin_guardar(self, form, app, messages):
        form.fill("ana", GOOD)
        form.buttons["Cancelar"].invoke()
        assert not form.win.winfo_exists()
        assert app.users == {}
        assert messages == []

    def test_dos_registros_distintos(self, app, messages):
        for nombre in ("ana", "luis"):
            f = Form(app)
            f.fill(nombre, GOOD if nombre == "ana" else "Pw#9xKm!")
            f.submit()
        assert set(app.users) == {"ana", "luis"}
