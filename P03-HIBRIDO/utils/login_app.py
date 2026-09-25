import tkinter as tk
from tkinter import messagebox
import hashlib
from utils import saveJson

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.configure(bg='#f0f0f0')

        # Base de datos (usuario: contraseña_hasheada) guardada en JSON
        self.archivo_db = "users-db.json"
        self.users = saveJson.cargar_diccionario(self.archivo_db)

        self.create_widgets()

    def hash_password(self, password):
        """Hashea la contraseña usando SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def tiene_secuencia(self, password):
        """Revisa si hay 3 caracteres seguidos en secuencia (abc, cba, 123, 321)"""
        texto = password.lower()
        for i in range(len(texto) - 2):
            a, b, c = texto[i], texto[i + 1], texto[i + 2]
            if (a + b + c).isdigit() or (a + b + c).isalpha():
                if ord(b) - ord(a) == 1 and ord(c) - ord(b) == 1:
                    return True
                if ord(a) - ord(b) == 1 and ord(b) - ord(c) == 1:
                    return True
        return False

    def validar_password(self, username, password):
        """Regresa la lista de alertas que no cumple la contraseña"""
        alertas = []
        if len(password) < 8:
            alertas.append("Debe tener al menos 8 caracteres")
        if not any(c.isupper() for c in password) or not any(c.islower() for c in password):
            alertas.append("Debe tener mayúsculas y minúsculas")
        if self.tiene_secuencia(password):
            alertas.append("No debe tener secuencias alfabéticas o numéricas (abc, 123)")
        if not any(not c.isalnum() and not c.isspace() for c in password):
            alertas.append("Debe tener al menos un carácter especial")
        if username.lower() in password.lower():
            alertas.append("No debe incluir el nombre de usuario")
        return alertas

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
            fg='#333333',
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
            fg='#333333',
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
            fg='#333333',
            width=12,
            command=self.login
        )

        sigin_btn = tk.Button(
            button_frame,
            text="Registrarse",
            font=('Arial', 12, 'bold'),
            bg="#4C65AF",
            fg='#333333',
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
            fg='#333333',
            width=10,
            command=self.clear_fields
        )
        clear_btn.pack(pady=5)

        # Información de usuarios demo
        info_frame = tk.Frame(main_frame, bg='#f0f0f0')
        info_frame.pack(pady=20)



    def signin(self):
        """Registra un usuario nuevo guardando el hash de su contraseña"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        if username in self.users:
            messagebox.showerror("Error", "El usuario ya existe")
            return

        # Alertas de la contraseña
        alertas = self.validar_password(username, password)
        if alertas:
            messagebox.showwarning("Contraseña no válida", "\n".join(alertas))
            return

        # Se guarda el hash, no la contraseña
        self.users[username] = self.hash_password(password)
        saveJson.guardar_diccionario(self.users, self.archivo_db)
        messagebox.showinfo("Registro", f"Usuario {username} registrado")
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
            fg='#333333'
        )
        welcome_label.pack(pady=50)

        # Botón de salir
        logout_btn = tk.Button(
            dashboard,
            text="Cerrar Sesión",
            font=('Arial', 12),
            bg='#ff9800',
            fg='#333333',
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
