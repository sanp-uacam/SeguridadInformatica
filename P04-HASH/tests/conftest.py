import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def messages(monkeypatch):
    # Captura messagebox.showinfo/showerror sin abrir diálogos
    from tkinter import messagebox

    log = []
    monkeypatch.setattr(
        messagebox, "showinfo", lambda title, msg, **kw: log.append(("info", title, msg))
    )
    monkeypatch.setattr(
        messagebox, "showerror", lambda title, msg, **kw: log.append(("error", title, msg))
    )
    return log


@pytest.fixture
def root():
    import tkinter as tk

    try:
        r = tk.Tk()
    except tk.TclError:
        pytest.skip("sin display disponible para Tk")
    r.withdraw()
    yield r
    try:
        r.destroy()
    except tk.TclError:
        pass


@pytest.fixture
def app(root, tmp_path, monkeypatch, messages):
    # LoginApp real con base de datos temporal (nunca toca users-db.json)
    from utils import login_app, saveJson

    db = tmp_path / "users-db.json"
    with monkeypatch.context() as m:
        m.setattr(saveJson, "cargar_usuarios", lambda path: {})
        instance = login_app.LoginApp(root)
    instance.users_file = str(db)
    instance.users = {}
    return instance
