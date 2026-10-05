"""Interfaz grafica Tkinter para registro e inicio de sesion."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from .auth import authenticate_user, register_user, validate_password
from .saveJson import cargar_diccionario, guardar_diccionario


DATABASE_PATH = Path(__file__).resolve().parent.parent / "users-db.json"
BACKGROUND = "#F3F6FA"
NAVY = "#17365D"
BLUE = "#2F75B5"


class LoginApp:
    def __init__(self, root: tk.Tk, database_path: Path = DATABASE_PATH):
        self.root = root
        self.database_path = database_path
        self.users = cargar_diccionario(self.database_path)
        self.root.title("Practica 04 - Login con SHA-256")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)
        self.create_widgets()

    def create_widgets(self) -> None:
        panel = tk.Frame(self.root, bg="white", padx=34, pady=30, relief="solid", bd=1)
        panel.pack(padx=28, pady=28, fill="both", expand=True)

        tk.Label(
            panel,
            text="Inicio de sesion",
            font=("Arial", 21, "bold"),
            bg="white",
            fg=NAVY,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 6))
        tk.Label(
            panel,
            text="Credenciales protegidas con SHA-256",
            font=("Arial", 10),
            bg="white",
            fg="#5B6573",
        ).grid(row=1, column=0, columnspan=2, pady=(0, 22))

        tk.Label(panel, text="Usuario", font=("Arial", 11), bg="white").grid(
            row=2, column=0, sticky="w", pady=7
        )
        self.user_entry = tk.Entry(panel, font=("Arial", 12), width=25)
        self.user_entry.grid(row=2, column=1, padx=(16, 0), pady=7)

        tk.Label(panel, text="Contrasena", font=("Arial", 11), bg="white").grid(
            row=3, column=0, sticky="w", pady=7
        )
        self.pass_entry = tk.Entry(panel, font=("Arial", 12), width=25, show="*")
        self.pass_entry.grid(row=3, column=1, padx=(16, 0), pady=7)
        self.pass_entry.bind("<Return>", lambda _event: self.login())

        buttons = tk.Frame(panel, bg="white")
        buttons.grid(row=4, column=0, columnspan=2, pady=(22, 0))
        tk.Button(
            buttons,
            text="Iniciar sesion",
            font=("Arial", 11, "bold"),
            bg=BLUE,
            fg="white",
            activebackground=NAVY,
            activeforeground="white",
            width=15,
            command=self.login,
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            buttons,
            text="Registrarse",
            font=("Arial", 11, "bold"),
            bg=NAVY,
            fg="white",
            activebackground=BLUE,
            activeforeground="white",
            width=15,
            command=self.signin,
        ).grid(row=0, column=1, padx=5)

        self.user_entry.focus_set()

    def signin(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Registro de usuario")
        window.configure(bg="white")
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()

        frame = tk.Frame(window, bg="white", padx=28, pady=24)
        frame.pack()
        tk.Label(
            frame,
            text="Crear cuenta",
            font=("Arial", 18, "bold"),
            fg=NAVY,
            bg="white",
        ).grid(row=0, column=0, columnspan=2, pady=(0, 16))

        tk.Label(frame, text="Usuario", bg="white").grid(row=1, column=0, sticky="w")
        username_entry = tk.Entry(frame, width=28, font=("Arial", 11))
        username_entry.grid(row=1, column=1, padx=(12, 0), pady=6)

        tk.Label(frame, text="Contrasena", bg="white").grid(row=2, column=0, sticky="w")
        password_entry = tk.Entry(frame, width=28, font=("Arial", 11), show="*")
        password_entry.grid(row=2, column=1, padx=(12, 0), pady=6)

        rules = tk.Label(
            frame,
            text=(
                "Minimo 8 caracteres; mayuscula, minuscula,\n"
                "numero y caracter especial. No use su usuario."
            ),
            justify="left",
            font=("Arial", 9),
            fg="#5B6573",
            bg="white",
        )
        rules.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 14))

        status = tk.Label(frame, text="", justify="left", fg="#B42318", bg="white")
        status.grid(row=4, column=0, columnspan=2, sticky="w")

        def update_rules(_event=None) -> None:
            result = validate_password(username_entry.get(), password_entry.get())
            status.configure(text="\n".join(result.errors[:3]))

        def save_user() -> None:
            success, detail = register_user(
                self.users, username_entry.get(), password_entry.get()
            )
            if not success:
                messagebox.showerror("Registro no valido", detail, parent=window)
                return
            if not guardar_diccionario(self.users, self.database_path):
                self.users.pop(username_entry.get().strip(), None)
                messagebox.showerror(
                    "Error", "No fue posible guardar el usuario.", parent=window
                )
                return
            messagebox.showinfo("Registro", detail, parent=window)
            self.user_entry.delete(0, tk.END)
            self.user_entry.insert(0, username_entry.get().strip())
            window.destroy()
            self.pass_entry.focus_set()

        password_entry.bind("<KeyRelease>", update_rules)
        password_entry.bind("<Return>", lambda _event: save_user())
        tk.Button(
            frame,
            text="Guardar registro",
            font=("Arial", 11, "bold"),
            bg=BLUE,
            fg="white",
            width=18,
            command=save_user,
        ).grid(row=5, column=0, columnspan=2, pady=(16, 0))
        username_entry.focus_set()

    def login(self) -> None:
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Complete usuario y contrasena.")
            return
        if authenticate_user(self.users, username, password):
            messagebox.showinfo("Acceso correcto", f"Bienvenido, {username}.")
            self.open_dashboard(username)
        else:
            messagebox.showerror("Acceso denegado", "Usuario o contrasena incorrectos.")

    def open_dashboard(self, username: str) -> None:
        dashboard = tk.Toplevel(self.root)
        dashboard.title("Sesion iniciada")
        dashboard.configure(bg="white")
        dashboard.geometry("430x220")
        dashboard.resizable(False, False)
        tk.Label(
            dashboard,
            text=f"Bienvenido, {username}",
            font=("Arial", 18, "bold"),
            bg="white",
            fg=NAVY,
        ).pack(pady=(55, 8))
        tk.Label(
            dashboard,
            text="El hash almacenado coincide con la contrasena capturada.",
            font=("Arial", 10),
            bg="white",
            fg="#5B6573",
        ).pack()
        tk.Button(dashboard, text="Cerrar sesion", command=dashboard.destroy).pack(pady=24)
        self.pass_entry.delete(0, tk.END)


def main() -> None:
    root = tk.Tk()
    width, height = 500, 360
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
