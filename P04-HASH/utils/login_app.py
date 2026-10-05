"""Interfaz de registro e inicio de sesion para la practica SHA-256."""
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from utils.password_rules import validate_password
from utils.users_db import UserRepository

DATA_FILE = Path(__file__).resolve().parents[1] / "usuarios.json"

class LoginApp:
    def __init__(self, root):
        self.root, self.repository = root, UserRepository(DATA_FILE)
        root.title("Practica HASH - Inicio de sesion"); root.geometry("460x360"); root.resizable(False, False); root.configure(bg="#F0F4F8")
        self._create()
    def _create(self):
        frame = tk.Frame(self.root, bg="#F0F4F8", padx=28, pady=24); frame.pack(expand=True, fill="both")
        tk.Label(frame, text="Inicio de sesion", font=("Arial", 19, "bold"), bg="#F0F4F8", fg="#17365D").pack(pady=(0, 22))
        fields = tk.Frame(frame, bg="#F0F4F8"); fields.pack()
        tk.Label(fields, text="Usuario:", bg="#F0F4F8").grid(row=0, column=0, padx=6, pady=9, sticky="w")
        self.user = tk.Entry(fields, width=28, font=("Arial", 11)); self.user.grid(row=0, column=1, padx=6, pady=9)
        tk.Label(fields, text="Contrasena:", bg="#F0F4F8").grid(row=1, column=0, padx=6, pady=9, sticky="w")
        self.password = tk.Entry(fields, width=28, font=("Arial", 11), show="*"); self.password.grid(row=1, column=1, padx=6, pady=9); self.password.bind("<Return>", lambda _: self.login())
        buttons = tk.Frame(frame, bg="#F0F4F8"); buttons.pack(pady=18)
        tk.Button(buttons, text="Iniciar sesion", width=15, bg="#2E8B57", fg="white", command=self.login).grid(row=0, column=0, padx=5)
        tk.Button(buttons, text="Registrarse", width=15, bg="#2E75B6", fg="white", command=self.register_window).grid(row=0, column=1, padx=5)
        tk.Label(frame, text="Se guarda solamente el hash SHA-256 de la contrasena.", font=("Arial", 9), bg="#F0F4F8", fg="#52606D").pack(pady=15); self.user.focus()
    def login(self):
        username, password = self.user.get().strip(), self.password.get()
        if not username or not password: messagebox.showerror("Datos incompletos", "Escribe usuario y contrasena."); return
        if self.repository.authenticate(username, password): messagebox.showinfo("Acceso concedido", f"Bienvenido, {username}.")
        else: messagebox.showerror("Acceso denegado", "Usuario o contrasena incorrectos.")
        self.password.delete(0, tk.END)
    def register_window(self):
        w = tk.Toplevel(self.root); w.title("Registrar usuario"); w.geometry("480x410"); w.resizable(False, False); w.configure(bg="#F0F4F8")
        f = tk.Frame(w, bg="#F0F4F8", padx=24, pady=20); f.pack(expand=True, fill="both")
        tk.Label(f, text="Registro", font=("Arial", 17, "bold"), bg="#F0F4F8", fg="#17365D").pack(pady=(0, 14))
        tk.Label(f, text="Usuario", bg="#F0F4F8").pack(anchor="w"); u = tk.Entry(f, width=34, font=("Arial", 11)); u.pack(pady=(2, 10))
        tk.Label(f, text="Contrasena", bg="#F0F4F8").pack(anchor="w"); p = tk.Entry(f, width=34, font=("Arial", 11), show="*"); p.pack(pady=(2, 10))
        tk.Label(f, text="8+ caracteres, mayuscula, minuscula, numero y especial.\nSin secuencias abc/123 ni el nombre de usuario.", justify="left", bg="#F0F4F8", fg="#52606D", font=("Arial", 9)).pack(anchor="w", pady=(0, 13))
        def save():
            username, password = u.get().strip(), p.get()
            if not username or not password: messagebox.showerror("Datos incompletos", "Escribe usuario y contrasena.", parent=w); return
            errors = validate_password(username, password)
            if errors: messagebox.showerror("Contrasena no valida", "\n".join("- " + e for e in errors), parent=w); return
            if not self.repository.register(username, password): messagebox.showerror("Usuario existente", "El usuario ya esta registrado.", parent=w); return
            messagebox.showinfo("Registro exitoso", "Usuario guardado con hash SHA-256.", parent=w); w.destroy()
        tk.Button(f, text="Guardar registro", width=18, bg="#2E75B6", fg="white", command=save).pack(); u.focus()

def main():
    root = tk.Tk(); LoginApp(root); root.mainloop()
