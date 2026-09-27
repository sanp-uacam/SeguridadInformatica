import tkinter as tk
from tkinter import messagebox
import hashlib
import os

try:
    from utils import saveJson
except ImportError:
    import saveJson

# Archivo donde se persisten los usuarios registrados (usuario -> hash SHA-256)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_DB_PATH = os.path.join(BASE_DIR, "users_db.json")


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')

        # Carga usuarios existentes desde el JSON. Si no existe el archivo
        # (primera ejecucion), se crea un usuario admin por defecto con su
        # contrasena ya hasheada, y se guarda de inmediato.
        self.users = saveJson.cargar_diccionario(USERS_DB_PATH)
        if not self.users:
            self.users = {
                'admin': self.hash_password('admin123')
            }
            saveJson.guardar_diccionario(self.users, USERS_DB_PATH)

        self.create_widgets()

    def hash_password(self, password):
        """Hashea la contrasena usando SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Titulo
        title_label = tk.Label(
            main_frame,
            text="Inicio de Sesion",
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

        # Contrasena
        pass_label = tk.Label(
            input_frame,
            text="Contrasena:",
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
            show='*'  # Oculta la contrasena
        )
        self.pass_entry.grid(row=1, column=1, padx=5, pady=10)

        # Bind Enter key para login
        self.pass_entry.bind('<Return>', lambda event: self.login())

        # Botones
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)

        login_btn = tk.Button(
            button_frame,
            text="Iniciar Sesion",
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

        # Informacion de usuarios demo
        info_frame = tk.Frame(main_frame, bg='#f0f0f0')
        info_frame.pack(pady=20)

    def signin(self):
        """Registra un nuevo usuario: hashea su contrasena y lo persiste en JSON."""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        if username in self.users:
            messagebox.showerror("Error", "Ese usuario ya existe")
            return

        self.users[username] = self.hash_password(password)
        saveJson.guardar_diccionario(self.users, USERS_DB_PATH)

        messagebox.showinfo("Exito", f"Usuario '{username}' registrado correctamente")
        self.clear_fields()

    def login(self):
        """Verifica las credenciales del usuario"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        # Verificar usuario y contrasena
        if username in self.users:
            hashed_password = self.hash_password(password)
            if self.users[username] == hashed_password:
                messagebox.showinfo("Exito", f"Bienvenido, {username}!")
                self.open_dashboard(username)
            else:
                messagebox.showerror("Error", "Contrasena incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    def clear_fields(self):
        """Limpia los campos de entrada"""
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()

    def open_dashboard(self, username):
        """Abre la ventana principal despues del login exitoso"""
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

        # Boton de salir
        logout_btn = tk.Button(
            dashboard,
            text="Cerrar Sesion",
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

    # Iniciar aplicacion
    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
