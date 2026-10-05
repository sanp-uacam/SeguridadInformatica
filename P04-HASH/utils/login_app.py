import tkinter as tk
from tkinter import messagebox
import hashlib
import hmac
import os
import re

from utils import saveJson

# Ruta del JSON siempre junto al proyecto (carpeta padre de /utils),
# sin importar desde dónde se ejecute main.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "users-db.json")


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.configure(bg='#f0f0f0')

        self.db_file = DB_FILE
        self.users = saveJson.cargar_diccionario(self.db_file) or {}

        self.create_widgets()

    # ------------------------------------------------------------------
    # HASH
    # ------------------------------------------------------------------
    def hash_password(self, password):
        """Devuelve el hash SHA-256 de la contraseña (64 caracteres hex).

        Es una función de una sola via: del hash no se puede volver
        a la contraseña original.
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    # ------------------------------------------------------------------
    # VALIDACION DE LA CONTRASENA (reglas del pizarron)
    # ------------------------------------------------------------------
    def _tiene_secuencia(self, password, longitud=3):
        """Detecta secuencias consecutivas ascendentes o descendentes.

        Ejemplos que detecta: 123, 321, abc, cba, XYZ.
        """
        p = password.lower()
        for i in range(len(p) - longitud + 1):
            bloque = p[i:i + longitud]
            if not (bloque.isdigit() or bloque.isalpha()):
                continue
            diferencias = [ord(bloque[j + 1]) - ord(bloque[j])
                           for j in range(longitud - 1)]
            if all(d == 1 for d in diferencias) or all(d == -1 for d in diferencias):
                return True
        return False

    def validar_contrasena(self, username, password):
        """Aplica las 5 reglas. Devuelve (bool, mensaje)."""

        # 1. Longitud minima de 8 caracteres
        if len(password) < 8:
            return False, "La contrasena debe tener al menos 8 caracteres."

        # 2. Mayusculas y minusculas
        if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
            return False, "La contrasena debe contener mayusculas y minusculas."

        # 3. Al menos un caracter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-\[\]\\/+=~`;\']', password):
            return False, "La contrasena debe contener al menos un caracter especial."

        # 4. No debe incluir el nombre de usuario
        if username and username.lower() in password.lower():
            return False, "La contrasena no debe incluir el nombre de usuario."

        # 5. Sin secuencias alfabeticas ni numericas
        if self._tiene_secuencia(password):
            return False, ("La contrasena no debe contener secuencias "
                           "alfabeticas o numericas (ej. abc, 123, 321).")

        return True, "Contrasena valida"

    # ------------------------------------------------------------------
    # REGISTRO
    # ------------------------------------------------------------------
    def signin(self):
        """Registra un nuevo usuario guardando unicamente el hash."""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        if username in self.users:
            messagebox.showerror("Error", "El usuario ya existe.")
            return

        es_valida, mensaje = self.validar_contrasena(username, password)
        if not es_valida:
            messagebox.showerror("Alerta de Contrasena", mensaje)
            return

        # Se guarda el HASH, nunca la contrasena en texto plano
        self.users[username] = self.hash_password(password)
        saveJson.guardar_diccionario(self.users, self.db_file)

        messagebox.showinfo("Exito",
                            f"Usuario '{username}' registrado correctamente.")
        self.clear_fields()

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------
    def login(self):
        """Compara el hash de lo escrito contra el hash almacenado."""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        if username not in self.users:
            messagebox.showerror("Error", "Usuario o contrasena incorrectos")
            return

        hash_ingresado = self.hash_password(password)
        hash_guardado = self.users[username]

        # compare_digest compara en tiempo constante (evita timing attacks)
        if hmac.compare_digest(hash_ingresado, hash_guardado):
            messagebox.showinfo("Exito", f"Bienvenido, {username}!")
            self.open_dashboard(username)
        else:
            messagebox.showerror("Error", "Usuario o contrasena incorrectos")

    # ------------------------------------------------------------------
    # INTERFAZ
    # ------------------------------------------------------------------
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        title_label = tk.Label(
            main_frame,
            text="Inicio de Sesion",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(0, 20))

        input_frame = tk.Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(pady=5)

        user_label = tk.Label(input_frame, text="Usuario:", font=('Arial', 12),
                              bg='#f0f0f0', anchor='w', width=12)
        user_label.grid(row=0, column=0, padx=5, pady=8, sticky='w')

        self.user_entry = tk.Entry(input_frame, font=('Arial', 12), width=20)
        self.user_entry.grid(row=0, column=1, padx=5, pady=8)
        self.user_entry.focus()

        pass_label = tk.Label(input_frame, text="Contrasena:", font=('Arial', 12),
                              bg='#f0f0f0', anchor='w', width=12)
        pass_label.grid(row=1, column=0, padx=5, pady=8, sticky='w')

        self.pass_entry = tk.Entry(input_frame, font=('Arial', 12),
                                   width=20, show='*')
        self.pass_entry.grid(row=1, column=1, padx=5, pady=8)
        self.pass_entry.bind('<Return>', lambda event: self.login())

        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=15)

        login_btn = tk.Button(button_frame, text="Iniciar Sesion",
                              font=('Arial', 12, 'bold'), bg='#4CAF50',
                              fg='white', width=12, command=self.login)
        login_btn.pack(pady=4)

        signin_btn = tk.Button(button_frame, text="Registrarse",
                               font=('Arial', 12, 'bold'), bg="#4C65AF",
                               fg='white', width=12, command=self.signin)
        signin_btn.pack(pady=4)

        clear_btn = tk.Button(button_frame, text="Limpiar", font=('Arial', 10),
                              bg='#f44336', fg='white', width=10,
                              command=self.clear_fields)
        clear_btn.pack(pady=4)

        # Recordatorio de las reglas para el usuario
        reglas = ("Requisitos: 8+ caracteres, mayusculas y minusculas,\n"
                  "un caracter especial, sin secuencias (abc / 123)\n"
                  "y sin incluir el nombre de usuario.")
        info_label = tk.Label(main_frame, text=reglas, font=('Arial', 8),
                              bg='#f0f0f0', fg='#666666', justify='center')
        info_label.pack(pady=(10, 0))

    def clear_fields(self):
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()

    def open_dashboard(self, username):
        """Abre la ventana principal despues del login exitoso."""
        self.root.destroy()

        dashboard = tk.Tk()
        dashboard.title("Dashboard Principal")
        dashboard.geometry("600x400")
        dashboard.configure(bg='#ffffff')

        welcome_label = tk.Label(
            dashboard,
            text=f"Bienvenido al Sistema, {username}!",
            font=('Arial', 16, 'bold'),
            bg='#ffffff',
            fg='#333333'
        )
        welcome_label.pack(pady=50)

        logout_btn = tk.Button(dashboard, text="Cerrar Sesion",
                               font=('Arial', 12), bg='#ff9800', fg='white',
                               command=dashboard.destroy)
        logout_btn.pack(pady=20)

        dashboard.mainloop()


def main():
    root = tk.Tk()

    window_width = 420
    window_height = 440
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    app = LoginApp(root)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    root.mainloop()


if __name__ == "__main__":
    main()