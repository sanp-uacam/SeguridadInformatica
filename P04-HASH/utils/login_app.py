import tkinter as tk
from tkinter import messagebox
import hashlib
import re

from utils import saveJson

DB_FILE = "users-db.json"


def hashear(password):
    """Hashea la contraseña usando SHA-256 (login/logvear en el diagrama)."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def contiene_secuencia(password, longitud=3):
    """Detecta secuencias ascendentes o descendentes de caracteres,
    ej. '1234', 'abcd', 'dcba' (lo que en el pizarrón se llama
    'secuencia alta/numerica')."""
    for i in range(len(password) - longitud + 1):
        fragmento = password[i:i + longitud]
        ascendente = all(
            ord(fragmento[j + 1]) - ord(fragmento[j]) == 1
            for j in range(len(fragmento) - 1)
        )
        descendente = all(
            ord(fragmento[j]) - ord(fragmento[j + 1]) == 1
            for j in range(len(fragmento) - 1)
        )
        if ascendente or descendente:
            return True
    return False


def validar_contrasena(password, username):
    """Devuelve la lista de reglas (del pizarrón) que la contraseña
    NO cumple. Lista vacía = contraseña válida."""
    errores = []
    if len(password) < 8:
        errores.append("Debe tener al menos 8 caracteres")
    if not any(c.isupper() for c in password):
        errores.append("Debe incluir mayúsculas")
    if not any(c.islower() for c in password):
        errores.append("Debe incluir minúsculas")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\];/\\~`]', password):
        errores.append("Debe incluir un carácter especial")
    if contiene_secuencia(password):
        errores.append("No debe tener secuencias (ej. 1234, abcd)")
    if username and username.lower() in password.lower():
        errores.append("No debe incluir el nombre de usuario")
    return errores


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')

        # Base de datos de usuarios: {"usuario": "hash_sha256"}
        # Se carga desde users-db.json (persistente entre ejecuciones)
        self.users = saveJson.cargar_diccionario(DB_FILE)
        if not self.users:
            # Usuario demo por defecto la primera vez que se ejecuta
            self.users = {"admin": hashear("Admin#2024")}
            saveJson.guardar_diccionario(self.users, DB_FILE)

        self.create_widgets()

    def hash_password(self, password):
        """Hashea la contraseña usando SHA-256."""
        return hashear(password)

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
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

        # Frame para campos de entrada
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
        self.user_entry.focus()  # Focus al iniciar

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
            show='*'  # Oculta la contraseña
        )
        self.pass_entry.grid(row=1, column=1, padx=5, pady=10)

        # Bind Enter key para login
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

    # ------------------------------------------------------------------
    # Registro (rama roja "Registro / guardar" del diagrama)
    # ------------------------------------------------------------------
    def signin(self):
        """Abre la ventana de registro de un nuevo usuario."""
        ventana = tk.Toplevel(self.root)
        ventana.title("Registro de Usuario")
        ventana.geometry("420x430")
        ventana.configure(bg='#f0f0f0')
        ventana.grab_set()  # Modal

        frame = tk.Frame(ventana, bg='#f0f0f0', padx=20, pady=20)
        frame.pack(expand=True, fill='both')

        tk.Label(frame, text="Crear cuenta", font=('Arial', 16, 'bold'),
                  bg='#f0f0f0').pack(pady=(0, 15))

        tk.Label(frame, text="Usuario:", font=('Arial', 11), bg='#f0f0f0',
                  anchor='w').pack(fill='x')
        user_entry = tk.Entry(frame, font=('Arial', 11))
        user_entry.pack(fill='x', pady=(0, 10))

        tk.Label(frame, text="Contraseña:", font=('Arial', 11), bg='#f0f0f0',
                  anchor='w').pack(fill='x')
        pass_entry = tk.Entry(frame, font=('Arial', 11), show='*')
        pass_entry.pack(fill='x', pady=(0, 10))

        tk.Label(frame, text="Confirmar contraseña:", font=('Arial', 11),
                  bg='#f0f0f0', anchor='w').pack(fill='x')
        confirm_entry = tk.Entry(frame, font=('Arial', 11), show='*')
        confirm_entry.pack(fill='x', pady=(0, 10))

        # Checklist de reglas (equivalente al bloque "Alerts" del pizarrón)
        reglas_txt = (
            "Requisitos de la contraseña:\n"
            "• Al menos 8 caracteres\n"
            "• Mayúsculas y minúsculas\n"
            "• Sin secuencias (ej. 1234, abcd)\n"
            "• Al menos un carácter especial\n"
            "• No debe incluir el nombre de usuario"
        )
        reglas_label = tk.Label(
            frame, text=reglas_txt, font=('Arial', 9), bg='#f0f0f0',
            fg='#555555', justify='left', anchor='w'
        )
        reglas_label.pack(fill='x', pady=(0, 15))

        def registrar():
            username = user_entry.get().strip()
            password = pass_entry.get()
            confirm = confirm_entry.get()

            if not username or not password or not confirm:
                messagebox.showerror("Error", "Complete todos los campos",
                                      parent=ventana)
                return

            if username in self.users:
                messagebox.showerror("Error", "Ese usuario ya existe",
                                      parent=ventana)
                return

            if password != confirm:
                messagebox.showerror("Error", "Las contraseñas no coinciden",
                                      parent=ventana)
                return

            errores = validar_contrasena(password, username)
            if errores:
                messagebox.showerror(
                    "Contraseña inválida",
                    "La contraseña no cumple:\n- " + "\n- ".join(errores),
                    parent=ventana
                )
                return

            # Registro / guardar -> {user: usuario, pass: Hash}
            self.users[username] = self.hash_password(password)
            saveJson.guardar_diccionario(self.users, DB_FILE)

            messagebox.showinfo("Éxito", "Usuario registrado correctamente",
                                 parent=ventana)
            ventana.destroy()

        tk.Button(
            frame, text="Registrar", font=('Arial', 12, 'bold'),
            bg='#4C65AF', fg='white', command=registrar
        ).pack(pady=10)

    # ------------------------------------------------------------------
    # Login (rama azul "loguear -> SHA-256 -> Hash -> =?" del diagrama)
    # ------------------------------------------------------------------
    def login(self):
        """Verifica las credenciales del usuario."""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        # Verificar usuario y contraseña
        if username in self.users:
            hashed_password = self.hash_password(password)
            if self.users[username] == hashed_password:
                messagebox.showinfo("Éxito", f"¡Bienvenido, {username}!")
                self.open_dashboard(username)
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    def clear_fields(self):
        """Limpia los campos de entrada"""
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()

    def open_dashboard(self, username):
        """Abre la ventana principal después del login exitoso"""
        # Cerrar ventana de login
        self.root.destroy()

        # Crear nueva ventana
        dashboard = tk.Tk()
        dashboard.title("Dashboard Principal")
        dashboard.geometry("600x400")
        dashboard.configure(bg='#ffffff')

        # Bienvenida
        welcome_label = tk.Label(
            dashboard,
            text=f"Bienvenido al Sistema, {username}!",
            font=('Arial', 16, 'bold'),
            bg='#ffffff',
            fg='#333333'
        )
        welcome_label.pack(pady=50)

        # Botón de salir
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
    # Crear ventana principal
    root = tk.Tk()

    # Centrar ventana en la pantalla
    window_width = 400
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    # Iniciar aplicación
    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
