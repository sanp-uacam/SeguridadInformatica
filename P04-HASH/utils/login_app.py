import tkinter as tk
from tkinter import messagebox
import hashlib

from utils import saveJson

ARCHIVO_DB = 'users-db.json'

# Colores de la interfaz
FONDO = '#f0f0f0'
TEXTO = '#333333'
VERDE = '#4CAF50'
AZUL = '#4C65AF'
ROJO = '#f44336'


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("420x520")
        self.root.configure(bg=FONDO)

        # Los usuarios se cargan del JSON (usuario: contraseña_hasheada)
        self.users = saveJson.cargar_diccionario(ARCHIVO_DB)

        self.create_widgets()

    def hash_password(self, password):
        """Hashea la contraseña usando SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def tiene_secuencia(self, password):
        """Busca secuencias de 3 seguidas como abc, cba, 123 o 321"""
        texto = password.lower()
        for i in range(len(texto) - 2):
            a = ord(texto[i])
            b = ord(texto[i + 1])
            c = ord(texto[i + 2])
            if b - a == 1 and c - b == 1:
                return True
            if a - b == 1 and b - c == 1:
                return True
        return False

    def validar_password(self, password, username):
        """Revisa las reglas y regresa la lista de las que no se cumplen"""
        especiales = "!@#$%^&*()-_=+[]{}|;:,.<>/?~`'\"\\"
        errores = []

        if len(password) < 8:
            errores.append("Debe tener mínimo 8 caracteres")

        tiene_mayus = any(c.isupper() for c in password)
        tiene_minus = any(c.islower() for c in password)
        if not tiene_mayus or not tiene_minus:
            errores.append("Debe combinar mayúsculas y minúsculas")

        if not any(c in especiales for c in password):
            errores.append("Debe incluir al menos un carácter especial")

        if self.tiene_secuencia(password):
            errores.append("No debe tener secuencias seguidas como 'abc' o '123'")

        if username and username.lower() in password.lower():
            errores.append("No debe incluir el nombre de usuario")

        return errores

    def crear_entrada(self, parent, oculta=False):
        """Campo de texto con colores fijos para que se vea igual en modo claro y oscuro"""
        entrada = tk.Entry(
            parent,
            font=('Arial', 12),
            width=20,
            bg='white',
            fg='black',
            insertbackground='black',  # el cursor
            relief='solid',
            borderwidth=1,
            highlightthickness=0
        )
        if oculta:
            entrada.config(show='*')
        return entrada

    def crear_boton(self, parent, texto, color, comando, ancho=14, tam=12):
        """En mac los botones ignoran el color de fondo, por eso se arma con un Label"""
        boton = tk.Label(
            parent,
            text=texto,
            font=('Arial', tam, 'bold'),
            bg=color,
            fg='white',
            width=ancho,
            pady=8,
            cursor='hand2'
        )
        boton.bind('<Button-1>', lambda event: comando())
        return boton

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=FONDO, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Título
        title_label = tk.Label(
            main_frame,
            text="Inicio de Sesión",
            font=('Arial', 18, 'bold'),
            bg=FONDO,
            fg=TEXTO
        )
        title_label.pack(pady=(0, 25))

        # Frame para campos de entrada
        input_frame = tk.Frame(main_frame, bg=FONDO)
        input_frame.pack(pady=10)

        # Usuario
        user_label = tk.Label(
            input_frame,
            text="Usuario:",
            font=('Arial', 12),
            bg=FONDO,
            fg=TEXTO,
            anchor='w',
            width=11
        )
        user_label.grid(row=0, column=0, padx=5, pady=10, sticky='w')

        self.user_entry = self.crear_entrada(input_frame)
        self.user_entry.grid(row=0, column=1, padx=5, pady=10)
        self.user_entry.focus()  # Focus al iniciar

        # Contraseña
        pass_label = tk.Label(
            input_frame,
            text="Contraseña:",
            font=('Arial', 12),
            bg=FONDO,
            fg=TEXTO,
            anchor='w',
            width=11
        )
        pass_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')

        self.pass_entry = self.crear_entrada(input_frame, oculta=True)
        self.pass_entry.grid(row=1, column=1, padx=5, pady=10)

        # Bind Enter key para login
        self.pass_entry.bind('<Return>', lambda event: self.login())

        # Botones
        button_frame = tk.Frame(main_frame, bg=FONDO)
        button_frame.pack(pady=15)

        login_btn = self.crear_boton(button_frame, "Iniciar Sesión", VERDE, self.login)
        login_btn.pack(pady=4)

        sigin_btn = self.crear_boton(button_frame, "Registrarse", AZUL, self.signin)
        sigin_btn.pack(pady=4)

        clear_btn = self.crear_boton(button_frame, "Limpiar", ROJO, self.clear_fields, ancho=11, tam=10)
        clear_btn.pack(pady=4)

        # Información de las reglas de la contraseña
        info_frame = tk.Frame(main_frame, bg=FONDO)
        info_frame.pack(pady=15)

        reglas = (
            "La contraseña debe tener:\n"
            "8 caracteres, mayúsculas y minúsculas,\n"
            "un carácter especial, sin secuencias\n"
            "y sin el nombre de usuario"
        )
        info_label = tk.Label(
            info_frame,
            text=reglas,
            font=('Arial', 10),
            bg=FONDO,
            fg='#666666',
            justify='center'
        )
        info_label.pack()

    def signin(self):
        """Registra un usuario nuevo validando la contraseña y guardando el hash"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        if username in self.users:
            messagebox.showerror("Error", "Ese usuario ya está registrado")
            return

        # Alertas de la contraseña
        errores = self.validar_password(password, username)
        if errores:
            mensaje = "La contraseña no es segura:\n\n"
            for error in errores:
                mensaje += "- " + error + "\n"
            messagebox.showwarning("Contraseña insegura", mensaje)
            return

        # Se guarda el hash, nunca la contraseña original
        self.users[username] = self.hash_password(password)
        saveJson.guardar_diccionario(self.users, ARCHIVO_DB)

        messagebox.showinfo("Éxito", f"Usuario {username} registrado correctamente")
        self.clear_fields()

    def login(self):
        """Verifica las credenciales del usuario"""
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
            fg=TEXTO
        )
        welcome_label.pack(pady=50)

        # Botón de salir
        logout_btn = tk.Label(
            dashboard,
            text="Cerrar Sesión",
            font=('Arial', 12, 'bold'),
            bg='#ff9800',
            fg='white',
            width=14,
            pady=8,
            cursor='hand2'
        )
        logout_btn.bind('<Button-1>', lambda event: dashboard.destroy())
        logout_btn.pack(pady=20)

        dashboard.mainloop()


def main():
    # Crear ventana principal
    root = tk.Tk()

    # Centrar ventana en la pantalla
    window_width = 420
    window_height = 520
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
