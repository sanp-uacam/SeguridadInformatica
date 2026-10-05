import tkinter as tk
from tkinter import messagebox
import hashlib
#Hash y validación de contraseña
from utils import password_policy
#Guardar/cargar usuarios en JSON
from utils import saveJson

USERS_DB_FILE = "users-db.json"  # Archivo de usuarios registrados

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')
        
        # Base de datos simulada (usuario: contraseña_hasheada)
        self.users = {
            'admin': 'pass-hash'
        }

        # Cargar usuarios ya registrados en ejecuciones anteriores
        usuarios_guardados = saveJson.cargar_diccionario(USERS_DB_FILE)
        if usuarios_guardados:
            self.users.update(usuarios_guardados)

        self.create_widgets()
    
    def hash_password(self, password):
        """Hashea la contraseña usando SHA-256"""
        return password_policy.hash_password(password)  
    
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
        
        # Botones lado a lado
        login_btn.pack(side='left', padx=5)
        sigin_btn.pack(side='left', padx=5)
        
        # Información de usuarios demo
        info_frame = tk.Frame(main_frame, bg='#f0f0f0')
        info_frame.pack(pady=20)
        

        
    def signin(self):
        self.open_register_window()  

    def open_register_window(self):
        """Ventana de registro de usuario"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Registro de usuario")
        ventana.geometry("380x430")
        ventana.configure(bg='#f0f0f0')
        ventana.grab_set() 

        tk.Label(
            ventana, text="Crear cuenta", font=('Arial', 16, 'bold'),
            bg='#f0f0f0', fg='#333333'
        ).pack(pady=(15, 10))

        form = tk.Frame(ventana, bg='#f0f0f0')
        form.pack(pady=5)

        tk.Label(form, text="Usuario:", font=('Arial', 11), bg='#f0f0f0',
                 width=14, anchor='w').grid(row=0, column=0, padx=5, pady=8, sticky='w')
        user_entry = tk.Entry(form, font=('Arial', 11), width=20)
        user_entry.grid(row=0, column=1, padx=5, pady=8)

        tk.Label(form, text="Contraseña:", font=('Arial', 11), bg='#f0f0f0',
                 width=14, anchor='w').grid(row=1, column=0, padx=5, pady=8, sticky='w')
        pass_entry = tk.Entry(form, font=('Arial', 11), width=20, show='*')
        pass_entry.grid(row=1, column=1, padx=5, pady=8)

        tk.Label(form, text="Confirmar:", font=('Arial', 11), bg='#f0f0f0',
                 width=14, anchor='w').grid(row=2, column=0, padx=5, pady=8, sticky='w')
        pass_confirm_entry = tk.Entry(form, font=('Arial', 11), width=20, show='*')
        pass_confirm_entry.grid(row=2, column=1, padx=5, pady=8)

        # Recordatorio de los requisitos
        requisitos_texto = (
            "La contraseña debe tener:\n"
            "• Mínimo 8 caracteres\n"
            "• Mayúsculas y minúsculas\n"
            "• Sin secuencia numérica (ej. 123)\n"
            "• Un carácter especial (ej. !@#$)\n"
            "• No debe incluir el nombre de usuario"
        )
        tk.Label(
            ventana, text=requisitos_texto, font=('Arial', 9), justify='left',
            bg='#f0f0f0', fg='#555555'
        ).pack(pady=(10, 10))

        def registrar():
            username = user_entry.get().strip()
            password = pass_entry.get()
            confirm = pass_confirm_entry.get()

            if not username or not password:
                messagebox.showerror("Error", "Complete usuario y contraseña.", parent=ventana)
                return

            if username in self.users:
                messagebox.showerror("Error", "Ese usuario ya existe.", parent=ventana)
                return

            if password != confirm:
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=ventana)
                return

            # Validar los requisitos
            errores = password_policy.validar_password(password, username)
            if errores:
                mensaje = "La contraseña no cumple con:\n\n- " + "\n- ".join(errores)
                messagebox.showwarning("Contraseña inválida", mensaje, parent=ventana)
                return

            # Se guarda el hash, no la contraseña
            hashed = self.hash_password(password)
            self.users[username] = hashed
            saveJson.guardar_diccionario(self.users, USERS_DB_FILE)

            messagebox.showinfo("Éxito", f"Usuario '{username}' registrado correctamente.", parent=ventana)
            ventana.destroy()

        tk.Button(
            ventana, text="Registrar", font=('Arial', 12, 'bold'),
            bg="#4C65AF", fg='white', width=14, command=registrar
        ).pack(pady=10)
    
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