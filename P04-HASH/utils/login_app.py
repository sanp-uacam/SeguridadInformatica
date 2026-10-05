import tkinter as tk
from tkinter import messagebox
import hashlib
import os

from utils import saveJson
from utils import passwordPolicy

# Archivo donde se persisten los usuarios (al lado de main.py)
RUTA_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "users-db.json"
)


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("420x480")
        self.root.configure(bg='#f0f0f0')

        # Base de datos de usuarios  ->  { usuario: hash_sha256 }
        self.users = saveJson.cargar_diccionario(RUTA_DB)
        if not isinstance(self.users, dict):
            self.users = {}

        self.create_widgets()

    # ------------------------------------------------------------------
    # HASH
    # ------------------------------------------------------------------
    def hash_password(self, password):
        """Hashea la contrasena usando SHA-256 y regresa el digest en hexadecimal."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    # ------------------------------------------------------------------
    # INTERFAZ
    # ------------------------------------------------------------------
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        title_label = tk.Label(
            main_frame,
            text="Inicio de Sesión",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(0, 20))

        input_frame = tk.Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(pady=10)

        # Usuario
        user_label = tk.Label(
            input_frame,
            text="Usuario:",
            font=('Arial', 12),
            bg='#f0f0f0',
            anchor='w',
            width=12
        )
        user_label.grid(row=0, column=0, padx=5, pady=10, sticky='w')

        self.user_entry = tk.Entry(input_frame, font=('Arial', 12), width=20)
        self.user_entry.grid(row=0, column=1, padx=5, pady=10)
        self.user_entry.focus()

        # Contraseña
        pass_label = tk.Label(
            input_frame,
            text="Contraseña:",
            font=('Arial', 12),
            bg='#f0f0f0',
            anchor='w',
            width=12
        )
        pass_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')

        self.pass_entry = tk.Entry(input_frame, font=('Arial', 12), width=20, show='*')
        self.pass_entry.grid(row=1, column=1, padx=5, pady=10)
        self.pass_entry.bind('<Return>', lambda event: self.login())
        self.pass_entry.bind('<KeyRelease>', self.actualizar_fuerza)

        # Indicador de fuerza de la contraseña
        self.strength_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        )
        self.strength_label.pack()

        # Botones
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=15)

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

        # Requisitos de la contraseña (siempre visibles)
        info_frame = tk.Frame(main_frame, bg='#f0f0f0')
        info_frame.pack(pady=10, fill='x')

        tk.Label(
            info_frame,
            text="La contraseña debe cumplir:",
            font=('Arial', 9, 'bold'),
            bg='#f0f0f0',
            fg='#555555'
        ).pack(anchor='w')

        requisitos = [
            "• Mínimo 8 caracteres",
            "• Mayúsculas y minúsculas",
            "• Sin secuencias (abc, 123)",
            "• Al menos un carácter especial",
            "• No incluir el nombre de usuario",
        ]
        for r in requisitos:
            tk.Label(
                info_frame,
                text=r,
                font=('Arial', 9),
                bg='#f0f0f0',
                fg='#666666'
            ).pack(anchor='w')

    def actualizar_fuerza(self, event=None):
        password = self.pass_entry.get()
        if not password:
            self.strength_label.config(text="")
            return
        texto, color = passwordPolicy.fuerza(password)
        self.strength_label.config(text=f"Seguridad: {texto}", fg=color)

    # ------------------------------------------------------------------
    # REGISTRO
    # ------------------------------------------------------------------
    def signin(self):
        """Registra un usuario nuevo: valida la contraseña, la hashea y la guarda."""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        if username in self.users:
            messagebox.showerror("Error", f"El usuario '{username}' ya está registrado")
            return

        # ALERTAS: reglas de la contraseña
        alertas = passwordPolicy.validar(password, username)
        if alertas:
            messagebox.showwarning(
                "Contraseña insegura",
                "La contraseña no cumple con:\n\n" + "\n".join(f"- {a}" for a in alertas)
            )
            return

        # Se guarda el usuario y el HASH, nunca la contraseña en texto plano
        self.users[username] = self.hash_password(password)
        saveJson.guardar_diccionario(self.users, RUTA_DB)

        messagebox.showinfo(
            "Registro exitoso",
            f"Usuario '{username}' registrado correctamente.\nYa puede iniciar sesión."
        )
        self.clear_fields()

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------
    def login(self):
        """Verifica las credenciales del usuario comparando hashes."""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

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
        self.strength_label.config(text="")
        self.user_entry.focus()

    def open_dashboard(self, username):
        """Abre la ventana principal después del login exitoso"""
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

        # Se muestra el hash almacenado 
        hash_label = tk.Label(
            dashboard,
            text=f"Hash SHA-256 almacenado:\n{self.users.get(username, '')}",
            font=('Courier', 9),
            bg='#ffffff',
            fg='#777777',
            wraplength=550
        )
        hash_label.pack(pady=10)

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

    window_width = 420
    window_height = 480
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
