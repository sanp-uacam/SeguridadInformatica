# Mauricio A. Sonda Cahuich

import tkinter as tk
from tkinter import messagebox
import hashlib
import os
import re  # usado para validar la contraseña

from . import secureAES as AES
from . import saveJson

USERS_DB_FILE = 'users_db.json'
KEY_FILE = 'secret.key'


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')

        # clave AES persistente: se crea una sola vez y se reutiliza siempre
        self.key = AES.get_or_create_key(KEY_FILE)

        # carga usuarios desde JSON
        self.users = saveJson.cargar_diccionario(USERS_DB_FILE)
        if not self.users:
            self._registrar_usuario('admin', 'admin123', guardar=True)

        self.create_widgets()

    # seguridad 

    def hash_password(self, password, salt):
        # Hashea contraseña+salt usando SHA-256
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

    # --- Validación de política de contraseñas (nuevo) ---

    def _tiene_secuencia(self, password, longitud=3):
        # Detecta secuencias alfanuméricas consecutivas (ej: "abc", "123", "cba")
        p = password.lower()
        for i in range(len(p) - longitud + 1):
            sub = p[i:i + longitud]
            asc = all(ord(sub[j + 1]) - ord(sub[j]) == 1 for j in range(len(sub) - 1))
            desc = all(ord(sub[j + 1]) - ord(sub[j]) == -1 for j in range(len(sub) - 1))
            if asc or desc:
                return True
        return False

    def validar_password(self, password, username):
        # Devuelve una lista de errores según las reglas de seguridad requeridas
        errores = []
        if len(password) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
            errores.append("La contraseña debe incluir mayúsculas y minúsculas")
        if not re.search(r'[^A-Za-z0-9]', password):
            errores.append("La contraseña debe incluir al menos un carácter especial")
        if self._tiene_secuencia(password):
            errores.append("La contraseña no puede contener secuencias alfanuméricas (ej: abc, 123)")
        if username and username.lower() in password.lower():
            errores.append("La contraseña no puede contener el nombre de usuario")
        return errores

    def _registrar_usuario(self, username, password, guardar=True):
        # Genera salt, hashea, cifra con AES y guarda un usuario nuevo
        salt = os.urandom(16).hex()
        hashed = self.hash_password(password, salt)
        iv, hash_enc = AES.encode(self.key, hashed)
        self.users[username] = {'salt': salt, 'iv': iv, 'hash': hash_enc}
        if guardar:
            saveJson.guardar_diccionario(self.users, USERS_DB_FILE)

    def _verificar_password(self, username, password):
        # Recalcula el hash con el salt guardado y lo compara con el hash descifrado
        registro = self.users.get(username)
        if not registro:
            return False
        try:
            hash_guardado = AES.decode(self.key, registro['iv'], registro['hash'])
        except Exception:
            return False
        return self.hash_password(password, registro['salt']) == hash_guardado

    # UI

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=10, pady=10)
        main_frame.pack(expand=True, fill='both')

        # Título
        title_label = tk.Label(
            main_frame,
            text="Inicio de Sesión",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(0, 30))

        # campos de entrada
        input_frame = tk.Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(pady=10)

        # Usuario
        user_label = tk.Label(
            input_frame,
            text="Usuario:",
            font=('Arial', 12),
            bg='#f0f0f0',
            anchor='w',
            width=15
        )
        user_label.grid(row=0, column=0, padx=5, pady=10, sticky='w')

        self.user_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            width=20
        )
        self.user_entry.grid(row=0, column=1, padx=5, pady=10)
        self.user_entry.focus()

        # Contraseña
        pass_label = tk.Label(
            input_frame,
            text="Contraseña:",
            font=('Arial', 12),
            bg='#f0f0f0',
            anchor='w',
            width=15
        )
        pass_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')

        self.pass_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            width=20,
            show='*'
        )
        self.pass_entry.grid(row=1, column=1, padx=5, pady=10)

        self.pass_entry.bind('<Return>', lambda event: self.login())

        # Botones
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)

        login_btn = tk.Button(
            button_frame,
            text="Iniciar Sesión",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            width=12,
            command=self.login
        )

        sigin_btn = tk.Button(
            button_frame,
            text="Registrarse",
            font=('Arial', 12, 'bold'),
            bg="#4C65AF",
            fg='white',
            width=12,
            command=self.signin
        )

        login_btn.pack(pady=5)
        sigin_btn.pack(pady=1)

        clear_btn = tk.Button(
            button_frame,
            text="Limpiar",
            font=('Arial', 10),
            bg='#f44336',
            fg='white',
            width=10,
            command=self.clear_fields
        )
        clear_btn.pack(pady=5)

        info_frame = tk.Frame(main_frame, bg='#f0f0f0')
        info_frame.pack(pady=20)

    def signin(self):
        # abre un modal para registrar un nuevo usuario.
        reg_win = tk.Toplevel(self.root)
        reg_win.title("Registrar usuario")
        reg_win.geometry("320x260")
        reg_win.configure(bg='#f0f0f0')
        reg_win.grab_set()

        tk.Label(
            reg_win, text="Nuevo usuario", font=('Arial', 14, 'bold'), bg='#f0f0f0'
        ).pack(pady=(15, 10))

        form = tk.Frame(reg_win, bg='#f0f0f0')
        form.pack(pady=5)

        tk.Label(form, text="Usuario:", bg='#f0f0f0', width=12, anchor='w').grid(
            row=0, column=0, padx=5, pady=8)
        user_entry = tk.Entry(form, width=20)
        user_entry.grid(row=0, column=1, padx=5, pady=8)

        tk.Label(form, text="Contraseña:", bg='#f0f0f0', width=12, anchor='w').grid(
            row=1, column=0, padx=5, pady=8)
        pass_entry = tk.Entry(form, width=20, show='*')
        pass_entry.grid(row=1, column=1, padx=5, pady=8)

        tk.Label(form, text="Confirmar:", bg='#f0f0f0', width=12, anchor='w').grid(
            row=2, column=0, padx=5, pady=8)
        confirm_entry = tk.Entry(form, width=20, show='*')
        confirm_entry.grid(row=2, column=1, padx=5, pady=8)

        def confirmar_registro():
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            confirm = confirm_entry.get().strip()

            if not username or not password:
                messagebox.showerror("Error", "Complete todos los campos", parent=reg_win)
                return
            if username in self.users:
                messagebox.showerror("Error", "El usuario ya existe", parent=reg_win)
                return
            if password != confirm:
                messagebox.showerror("Error", "Las contraseñas no coinciden", parent=reg_win)
                return

            # Validación de política de contraseñas (nuevo)
            errores = self.validar_password(password, username)
            if errores:
                messagebox.showerror("Error", "\n".join(errores), parent=reg_win)
                return

            self._registrar_usuario(username, password, guardar=True)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente", parent=reg_win)
            reg_win.destroy()

        tk.Button(
            reg_win, text="Registrar", font=('Arial', 11, 'bold'),
            bg='#4C65AF', fg='white', command=confirmar_registro
        ).pack(pady=15)

    def login(self):
        # revisa las credenciales del usuario
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        if username not in self.users:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        if self._verificar_password(username, password):
            messagebox.showinfo("Éxito", f"¡Bienvenido, {username}!")
            self.open_dashboard(username)
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    def clear_fields(self):
        # limpia los campos de entrada
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()

    def open_dashboard(self, username):
        # abre la ventana principal después del login
        self.root.destroy()

        dashboard = tk.Tk()
        dashboard.title("Dashboard Principal")
        dashboard.geometry("800x1000")
        dashboard.configure(bg='#ffffff')

        welcome_label = tk.Label(
            dashboard,
            text=f"Bienvenido al Sistema, {username}!",
            font=('Arial', 16, 'bold'),
            bg='#ffffff',
            fg='#333333'
        )
        welcome_label.pack(pady=50)

        logout_btn = tk.Button(
            dashboard,
            text="Cerrar Sesión",
            font=('Arial', 12),
            bg='#ff9800',
            fg='white',
            command=dashboard.quit
        )
        logout_btn.pack(pady=20)

        dashboard.mainloop()


def main():
    root = tk.Tk()

    window_width = 1080
    window_height = 1000
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
