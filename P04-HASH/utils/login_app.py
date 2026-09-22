import tkinter as tk
from tkinter import messagebox
import hashlib
import os
import re

from utils import saveJson

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("400x400")
        self.root.configure(bg='#f0f0f0')

        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.users_file = os.path.join(project_dir, "users-db.json")
        self.users = saveJson.cargar_usuarios(self.users_file)
        self.password_rules = {}
        
        self.create_widgets()
    
    def hash_password(self, password):
        """Hashea la contraseña usando SHA-256"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def find_user(self, username):
        """Obtiene directamente el hash asociado al nombre de usuario."""
        return self.users.get(username.strip().casefold())

    def show_message(self, message_type, title, message, parent=None):
        """Muestra una notificación modal siempre delante de su ventana."""
        owner = parent or self.root
        owner.lift()
        owner.focus_force()
        try:
            owner.attributes("-topmost", True)
        except tk.TclError:
            pass

        try:
            show = messagebox.showinfo if message_type == "info" else messagebox.showerror
            return show(title, message, parent=owner)
        finally:
            try:
                owner.attributes("-topmost", False)
            except tk.TclError:
                pass
    
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
        
        # Información de usuarios demo
        info_frame = tk.Frame(main_frame, bg='#f0f0f0')
        info_frame.pack(pady=20)
        

        
    def signin(self):
        """Abre el formulario de registro."""
        register_window = tk.Toplevel(self.root)
        register_window.title("Registro de Usuario")
        register_window.geometry("500x520")
        register_window.configure(bg="#f0f0f0")
        register_window.transient(self.root)
        register_window.grab_set()

        main_frame = tk.Frame(register_window, bg="#f0f0f0", padx=24, pady=20)
        main_frame.pack(expand=True, fill="both")

        title_label = tk.Label(
            main_frame,
            text="Registro",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=(0, 18))

        form_frame = tk.Frame(main_frame, bg="#f0f0f0")
        form_frame.pack(fill="x")

        tk.Label(
            form_frame,
            text="Usuario:",
            font=("Arial", 12),
            bg="#f0f0f0",
            width=16,
            anchor="w"
        ).grid(row=0, column=0, padx=5, pady=8, sticky="w")

        register_user_entry = tk.Entry(form_frame, font=("Arial", 12), width=26)
        register_user_entry.grid(row=0, column=1, padx=5, pady=8)
        register_user_entry.focus()

        tk.Label(
            form_frame,
            text="Contraseña:",
            font=("Arial", 12),
            bg="#f0f0f0",
            width=16,
            anchor="w"
        ).grid(row=1, column=0, padx=5, pady=8, sticky="w")

        register_pass_entry = tk.Entry(form_frame, font=("Arial", 12), width=26, show="*")
        register_pass_entry.grid(row=1, column=1, padx=5, pady=8)

        tk.Label(
            form_frame,
            text="Confirmar:",
            font=("Arial", 12),
            bg="#f0f0f0",
            width=16,
            anchor="w"
        ).grid(row=2, column=0, padx=5, pady=8, sticky="w")

        confirm_pass_entry = tk.Entry(form_frame, font=("Arial", 12), width=26, show="*")
        confirm_pass_entry.grid(row=2, column=1, padx=5, pady=8)

        checklist_frame = tk.LabelFrame(
            main_frame,
            text="Requisitos de contraseña",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#333333",
            padx=12,
            pady=10
        )
        checklist_frame.pack(fill="x", pady=18)

        rules = [
            ("length", "8 caracteres"),
            ("uppercase", "Al menos una mayúscula"),
            ("no_sequence", "Sin secuencia alfabética o numérica"),
            ("special", "Al menos un carácter especial"),
            ("not_username", "Que no sea el nombre de usuario")
        ]

        self.password_rules = {}
        for index, (key, text) in enumerate(rules):
            label = tk.Label(
                checklist_frame,
                text=f"✗ {text}",
                font=("Arial", 10),
                bg="#f0f0f0",
                fg="#b00020",
                anchor="w"
            )
            label.grid(row=index, column=0, sticky="w", pady=3)
            self.password_rules[key] = label

        status_label = tk.Label(main_frame, text="", font=("Arial", 10), bg="#f0f0f0", fg="#b00020")
        status_label.pack(pady=(0, 10))

        def refresh_checklist(event=None):
            username = register_user_entry.get().strip()
            password = register_pass_entry.get()
            checks = self.validate_password(username, password)

            for key, label in self.password_rules.items():
                passed = checks[key]
                symbol = "✓" if passed else "✗"
                color = "#2e7d32" if passed else "#b00020"
                text = dict(rules)[key]
                label.configure(text=f"{symbol} {text}", fg=color)

            if confirm_pass_entry.get() and password != confirm_pass_entry.get():
                status_label.configure(text="Las contraseñas no coinciden")
            else:
                status_label.configure(text="")

        def create_user():
            username = register_user_entry.get().strip().casefold()
            password = register_pass_entry.get()
            confirm_password = confirm_pass_entry.get()

            if not username or not password or not confirm_password:
                self.show_message(
                    "error", "Error", "Por favor, complete todos los campos", register_window
                )
                return

            if username in self.users:
                self.show_message("error", "Error", "El usuario ya existe", register_window)
                return

            checks = self.validate_password(username, password)
            refresh_checklist()

            if not all(checks.values()):
                self.show_message(
                    "error",
                    "Error",
                    "La contraseña no cumple todos los requisitos",
                    register_window
                )
                return

            if password != confirm_password:
                self.show_message("error", "Error", "Las contraseñas no coinciden", register_window)
                return

            self.users[username] = self.hash_password(password)
            if not saveJson.guardar_usuarios(self.users, self.users_file):
                self.users.pop(username, None)
                self.show_message("error", "Error", "No se pudo guardar el usuario", register_window)
                return

            self.show_message("info", "Éxito", "Usuario registrado correctamente", register_window)
            register_window.destroy()
            self.user_entry.delete(0, tk.END)
            self.pass_entry.delete(0, tk.END)
            self.user_entry.insert(0, username)
            self.pass_entry.focus()

        register_user_entry.bind("<KeyRelease>", refresh_checklist)
        register_pass_entry.bind("<KeyRelease>", refresh_checklist)
        confirm_pass_entry.bind("<KeyRelease>", refresh_checklist)
        confirm_pass_entry.bind("<Return>", lambda event: create_user())

        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Crear cuenta",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=14,
            command=create_user
        ).pack(side="left", padx=6)

        tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 12),
            bg="#757575",
            fg="white",
            width=10,
            command=register_window.destroy
        ).pack(side="left", padx=6)

        refresh_checklist()

    def validate_password(self, username, password):
        """Evalúa las reglas visibles del checklist de registro."""
        normalized_user = username.strip().lower()
        normalized_password = password.strip().lower()

        return {
            "length": len(password) >= 8,
            "uppercase": any(char.isupper() for char in password),
            "no_sequence": not self.has_alpha_numeric_sequence(password),
            "special": bool(re.search(r"[^A-Za-z0-9]", password)),
            "not_username": bool(normalized_password) and normalized_password != normalized_user
        }

    def has_alpha_numeric_sequence(self, password):
        """Detecta secuencias consecutivas de 3 o más caracteres: abc, cba, 123, 321."""
        value = password.lower()
        for index in range(len(value) - 2):
            chunk = value[index:index + 3]
            if chunk.isalpha() or chunk.isdigit():
                codes = [ord(char) for char in chunk]
                if codes[1] == codes[0] + 1 and codes[2] == codes[1] + 1:
                    return True
                if codes[1] == codes[0] - 1 and codes[2] == codes[1] - 1:
                    return True
        return False
    
    def login(self):
        """Verifica las credenciales del usuario"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        
        if not username or not password:
            self.show_message("error", "Error", "Por favor, complete todos los campos")
            return
        
        # Verificar usuario y contraseña
        stored_password_hash = self.find_user(username)
        if stored_password_hash:
            hashed_password = self.hash_password(password)
            if stored_password_hash == hashed_password:
                normalized_username = username.casefold()
                self.show_message("info", "Éxito", f"¡Bienvenido, {normalized_username}!")
                self.open_dashboard(normalized_username)
            else:
                self.show_message("error", "Error", "Contraseña incorrecta")
        else:
            self.show_message("error", "Error", "Usuario no encontrado")
    
    def clear_fields(self):
        """Limpia los campos de entrada"""
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()
    
    def open_dashboard(self, username):
        """Abre la ventana principal después del login exitoso"""
        self.root.withdraw()

        dashboard = tk.Toplevel(self.root)
        dashboard.title("Dashboard Principal")
        dashboard.geometry("600x400")
        dashboard.configure(bg='#ffffff')

        def logout():
            dashboard.destroy()
            self.clear_fields()
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

        dashboard.protocol("WM_DELETE_WINDOW", logout)
        
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
            command=logout
        )
        logout_btn.pack(pady=20)

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
