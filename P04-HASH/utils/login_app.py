"""Login con registro, reglas visibles y almacenamiento SHA-256."""
import hashlib
import json
import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

DATABASE_PATH = Path(__file__).with_name("users_db.json")


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def has_consecutive_numbers(password):
    """Detecta dígitos adyacentes consecutivos, ascendentes o descendentes."""
    for digits in re.findall(r"\d+", password):
        if any(
            int(digits[index + 1]) - int(digits[index]) == step
            for index in range(len(digits) - 1)
            for step in (1, -1)
        ):
            return True
    return False


def password_rules(username, password):
    user = username.strip().casefold()
    return [
        ("Al menos 8 caracteres", len(password) >= 8),
        ("Incluye una letra mayúscula", bool(re.search(r"[A-Z]", password))),
        ("Incluye una letra minúscula", bool(re.search(r"[a-z]", password))),
        ("Incluye un número", bool(re.search(r"\d", password))),
        ("No usar números consecutivos (ej. 123)", not has_consecutive_numbers(password)),
        ("Incluye un carácter especial", bool(re.search(r"[^A-Za-z0-9]", password))),
        ("No contiene el nombre de usuario", bool(user) and user not in password.casefold()),
    ]


class LoginApp:
    def __init__(self, root):
        self.root = root
        root.title("Sistema de Login")
        root.configure(bg="#f4f6f8")
        self.configure_styles()
        self.users = self.load_users()
        self.create_widgets()

    def configure_styles(self):
        """Usa el tema clam: respeta los colores también en macOS."""
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Login.TButton", background="#257a44", foreground="white", padding=(12, 8), font=("Arial", 11, "bold"))
        style.map("Login.TButton", background=[("active", "#1b5b32")])
        style.configure("Register.TButton", background="#315ea8", foreground="white", padding=(12, 8), font=("Arial", 11, "bold"))
        style.map("Register.TButton", background=[("active", "#24477f")])
        style.configure("Clear.TButton", background="#e3e7eb", foreground="#17212b", padding=(12, 7), font=("Arial", 10))
        style.map("Clear.TButton", background=[("active", "#cfd6dd")])

    def load_users(self):
        if not DATABASE_PATH.exists():
            return {}
        try:
            with DATABASE_PATH.open(encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def save_users(self):
        with DATABASE_PATH.open("w", encoding="utf-8") as file:
            json.dump(self.users, file, ensure_ascii=False, indent=2)

    def create_widgets(self):
        frame = tk.Frame(self.root, bg="#f4f6f8", padx=28, pady=25)
        frame.pack(expand=True, fill="both")
        tk.Label(frame, text="Inicio de sesión", font=("Arial", 19, "bold"), bg="#f4f6f8", fg="#17212b").pack(pady=(0, 20))
        form = tk.Frame(frame, bg="#f4f6f8")
        form.pack()
        tk.Label(form, text="Usuario:", bg="#f4f6f8", fg="#17212b").grid(row=0, column=0, padx=(0, 10), pady=7, sticky="w")
        self.login_username = tk.StringVar()
        self.login_password = tk.StringVar()
        self.user_entry = tk.Entry(form, width=25, font=("Arial", 11), textvariable=self.login_username)
        self.user_entry.grid(row=0, column=1, pady=7)
        tk.Label(form, text="Contraseña:", bg="#f4f6f8", fg="#17212b").grid(row=1, column=0, padx=(0, 10), pady=7, sticky="w")
        self.pass_entry = tk.Entry(form, width=25, font=("Arial", 11), show="●", textvariable=self.login_password)
        self.pass_entry.grid(row=1, column=1, pady=7)
        self.pass_entry.bind("<Return>", lambda _: self.login())
        checks = tk.Frame(frame, bg="#f4f6f8")
        checks.pack(fill="x", padx=30, pady=(10, 4))
        self.login_rule_labels = self.create_rule_labels(checks)
        self.login_username.trace_add("write", self.update_login_rules)
        self.login_password.trace_add("write", self.update_login_rules)
        self.update_login_rules()
        buttons = tk.Frame(frame, bg="#f4f6f8")
        buttons.pack(pady=16)
        ttk.Button(buttons, text="Iniciar sesión", command=self.login, style="Login.TButton").grid(row=0, column=0, padx=4)
        ttk.Button(buttons, text="Registrarse", command=self.open_register, style="Register.TButton").grid(row=0, column=1, padx=4)
        ttk.Button(frame, text="Limpiar", command=self.clear_fields, style="Clear.TButton").pack()
        self.user_entry.focus()

    @staticmethod
    def create_rule_labels(parent):
        labels = []
        for _ in password_rules("", ""):
            label = tk.Label(parent, anchor="w", bg="#f4f6f8", font=("Arial", 10))
            label.pack(fill="x")
            labels.append(label)
        return labels

    @staticmethod
    def paint_rules(labels, username, password):
        for label, (text, passed) in zip(labels, password_rules(username, password)):
            label.config(text=("✓ Cumple: " if passed else "✗ Falta: ") + text,
                         fg="#16743a" if passed else "#b42318")

    def update_login_rules(self, *_):
        self.paint_rules(self.login_rule_labels, self.login_username.get(), self.login_password.get())

    def open_register(self):
        window = tk.Toplevel(self.root)
        window.title("Registro de usuario")
        window.configure(bg="#f4f6f8")
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()
        frame = tk.Frame(window, bg="#f4f6f8", padx=30, pady=25)
        frame.pack()
        tk.Label(frame, text="Crear cuenta", font=("Arial", 17, "bold"), bg="#f4f6f8", fg="#17212b").pack(pady=(0, 16))
        tk.Label(frame, text="Usuario", bg="#f4f6f8", fg="#17212b", anchor="w").pack(fill="x")
        register_username = tk.StringVar()
        register_password = tk.StringVar()
        username = tk.Entry(frame, width=32, font=("Arial", 11), textvariable=register_username)
        username.pack(pady=(3, 12))
        tk.Label(frame, text="Contraseña", bg="#f4f6f8", fg="#17212b", anchor="w").pack(fill="x")
        password = tk.Entry(frame, width=32, font=("Arial", 11), show="●", textvariable=register_password)
        password.pack(pady=(3, 10))
        checks = tk.Frame(frame, bg="#f4f6f8")
        checks.pack(fill="x", pady=(0, 14))
        labels = self.create_rule_labels(checks)

        def update_rules(*_):
            self.paint_rules(labels, register_username.get(), register_password.get())

        def register():
            user, secret = username.get().strip(), password.get()
            if not user:
                messagebox.showerror("Registro", "Escribe un nombre de usuario.", parent=window)
            elif user.casefold() in {existing.casefold() for existing in self.users}:
                messagebox.showerror("Registro", "Ese usuario ya está registrado.", parent=window)
            elif not all(ok for _, ok in password_rules(user, secret)):
                messagebox.showerror("Registro", "La contraseña aún no cumple todos los requisitos.", parent=window)
            else:
                self.users[user] = hash_password(secret)
                self.save_users()
                messagebox.showinfo("Registro", "Usuario registrado correctamente.", parent=window)
                window.destroy()
                self.user_entry.delete(0, tk.END)
                self.user_entry.insert(0, user)
                self.pass_entry.focus()

        register_username.trace_add("write", update_rules)
        register_password.trace_add("write", update_rules)
        password.bind("<Return>", lambda _: register())
        ttk.Button(frame, text="Guardar registro", command=register, style="Register.TButton").pack()
        username.focus()
        update_rules()

    def login(self):
        username, password = self.user_entry.get().strip(), self.pass_entry.get()
        if not username or not password:
            messagebox.showerror("Inicio de sesión", "Completa usuario y contraseña.")
            return
        stored = next((user for user in self.users if user.casefold() == username.casefold()), None)
        if stored is None:
            messagebox.showerror("Inicio de sesión", "Usuario no encontrado. Regístralo primero.")
        elif self.users[stored] != hash_password(password):
            messagebox.showerror("Inicio de sesión", "Contraseña incorrecta.")
        else:
            messagebox.showinfo("Inicio de sesión", f"¡Bienvenido, {stored}!")

    def clear_fields(self):
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()


def main():
    root = tk.Tk()
    root.geometry("470x470")
    root.resizable(False, False)
    LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
