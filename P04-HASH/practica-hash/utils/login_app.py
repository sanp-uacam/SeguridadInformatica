import tkinter as tk
from tkinter import messagebox
import hashlib
import os

try:
    from utils import saveJson
except ModuleNotFoundError:
    import saveJson

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # raíz del proyecto
DB_FILE = os.path.join(BASE_DIR, "users-db.json")
print("Base de datos en:", DB_FILE)


class PasswordValidator:
    """Reglas de contraseña según el diagrama."""

    REGLAS = [
        ("min_len",       "Mínimo 8 caracteres"),
        ("mayus_minus",   "Mayúsculas y minúsculas"),
        ("sin_secuencia", "Sin secuencias (abc, 123, 321...)"),
        ("especial",      "Al menos 1 carácter especial"),
        ("sin_usuario",   "No incluye el nombre de usuario"),
    ]

    @staticmethod
    def tiene_secuencia(password, longitud=3):
        """Detecta secuencias alfabéticas o numéricas ascendentes/descendentes."""
        p = password.lower()
        for i in range(len(p) - longitud + 1):
            trozo = p[i:i + longitud]
            if not (trozo.isalpha() or trozo.isdigit()):
                continue
            codigos = [ord(c) for c in trozo]
            difs = {codigos[j + 1] - codigos[j] for j in range(longitud - 1)}
            if difs == {1} or difs == {-1}:
                return True
        return False

    @classmethod
    def validar(cls, password, usuario=""):
        return {
            "min_len": len(password) >= 8,
            "mayus_minus": any(c.isupper() for c in password)
                           and any(c.islower() for c in password),
            "sin_secuencia": not cls.tiene_secuencia(password),
            "especial": any(not c.isalnum() and not c.isspace() for c in password),
            "sin_usuario": bool(password)
                           and (not usuario or usuario.lower() not in password.lower()),
        }

    @classmethod
    def es_valida(cls, password, usuario=""):
        return all(cls.validar(password, usuario).values())


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.configure(bg='#f0f0f0')

        # Base de datos: {usuario: hash_sha256}
        self.users = saveJson.cargar_diccionario(DB_FILE)

        self.create_widgets()

    # ---------- Hash ----------
    def hash_password(self, password):
        """Hashea la contraseña usando SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    # ---------- UI ----------
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        tk.Label(main_frame, text="Inicio de Sesión",
                 font=('Arial', 18, 'bold'), bg='#f0f0f0',
                 fg='#333333').pack(pady=(0, 20))

        input_frame = tk.Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Usuario:", font=('Arial', 12),
                 bg='#f0f0f0', anchor='w', width=12
                 ).grid(row=0, column=0, padx=5, pady=8, sticky='w')
        self.user_entry = tk.Entry(input_frame, font=('Arial', 12), width=22)
        self.user_entry.grid(row=0, column=1, padx=5, pady=8)
        self.user_entry.focus()

        tk.Label(input_frame, text="Contraseña:", font=('Arial', 12),
                 bg='#f0f0f0', anchor='w', width=12
                 ).grid(row=1, column=0, padx=5, pady=8, sticky='w')
        self.pass_entry = tk.Entry(input_frame, font=('Arial', 12),
                                   width=22, show='*')
        self.pass_entry.grid(row=1, column=1, padx=5, pady=8)

        # Validación en tiempo real (también al cambiar el usuario, por la regla 5)
        self.user_entry.bind('<KeyRelease>', self.actualizar_alertas)
        self.pass_entry.bind('<KeyRelease>', self.actualizar_alertas)
        self.pass_entry.bind('<Return>', lambda e: self.login())

        # ---- Alertas ----
        alert_frame = tk.LabelFrame(main_frame, text="Requisitos de la contraseña",
                                    font=('Arial', 10, 'bold'), bg='#f0f0f0',
                                    fg='#555555', padx=10, pady=5)
        alert_frame.pack(pady=10, fill='x')

        self.alert_labels = {}
        for clave, texto in PasswordValidator.REGLAS:
            lbl = tk.Label(alert_frame, text=f"✗  {texto}", font=('Arial', 10),
                           bg='#f0f0f0', fg='#f44336', anchor='w')
            lbl.pack(fill='x')
            self.alert_labels[clave] = lbl

        # ---- Botones ----
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Iniciar Sesión", font=('Arial', 12, 'bold'),
                  bg='#4CAF50', fg='white', width=14,
                  command=self.login).pack(pady=4)

        self.signin_btn = tk.Button(button_frame, text="Registrarse",
                                    font=('Arial', 12, 'bold'), bg="#4C65AF",
                                    fg='white', width=14, state='disabled',
                                    command=self.signin)
        self.signin_btn.pack(pady=4)

        tk.Button(button_frame, text="Limpiar", font=('Arial', 10),
                  bg='#f44336', fg='white', width=10,
                  command=self.clear_fields).pack(pady=4)

    # ---------- Alertas en tiempo real ----------
    def actualizar_alertas(self, event=None):
        password = self.pass_entry.get()
        usuario = self.user_entry.get().strip()
        resultado = PasswordValidator.validar(password, usuario)

        for clave, texto in PasswordValidator.REGLAS:
            ok = resultado[clave]
            self.alert_labels[clave].config(
                text=f"{'✓' if ok else '✗'}  {texto}",
                fg='#4CAF50' if ok else '#f44336'
            )

        todo_ok = all(resultado.values()) and usuario
        self.signin_btn.config(state='normal' if todo_ok else 'disabled')

    # ---------- Registro ----------
    def signin(self):
        """Registra un usuario nuevo guardando usuario: hash"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return
        if not PasswordValidator.es_valida(password, username):
            messagebox.showerror("Error", "La contraseña no cumple los requisitos")
            return
        if username in self.users:
            messagebox.showerror("Error", "El usuario ya existe")
            return

        self.users[username] = self.hash_password(password)
        if saveJson.guardar_diccionario(self.users, DB_FILE):
            messagebox.showinfo("Registro", f"Usuario '{username}' registrado")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "No se pudo guardar el usuario")

    # ---------- Login ----------
    def login(self):
        """Verifica las credenciales del usuario comparando hashes"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        if username not in self.users:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        if self.users[username] == self.hash_password(password):
            messagebox.showinfo("Éxito", f"¡Bienvenido, {username}!")
            self.open_dashboard(username)
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    def clear_fields(self):
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()
        self.actualizar_alertas()

    def open_dashboard(self, username):
        self.root.destroy()

        dashboard = tk.Tk()
        dashboard.title("Dashboard Principal")
        dashboard.geometry("600x400")
        dashboard.configure(bg='#ffffff')

        tk.Label(dashboard, text=f"Bienvenido al Sistema, {username}!",
                 font=('Arial', 16, 'bold'), bg='#ffffff',
                 fg='#333333').pack(pady=50)

        tk.Button(dashboard, text="Cerrar Sesión", font=('Arial', 12),
                  bg='#ff9800', fg='white', command=dashboard.quit).pack(pady=20)

        dashboard.mainloop()


def main():
    root = tk.Tk()

    window_width, window_height = 440, 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()