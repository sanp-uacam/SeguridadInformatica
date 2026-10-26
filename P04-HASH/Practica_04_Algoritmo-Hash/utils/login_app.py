import tkinter as tk
from tkinter import messagebox, simpledialog
import hashlib
import os
from utils import saveJson

DB_FILE = "users-db.json"

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')
        
        # Cargar base de datos JSON o crearla con un usuario por defecto
        self.users = saveJson.cargar_diccionario(DB_FILE)
        if not self.users:
            # Crear usuario admin por defecto (contraseña: admin123)
            self.users = {
                'admin': self.hash_password('admin123')
            }
            saveJson.guardar_diccionario(self.users, DB_FILE)
        
        self.create_widgets()
    
    def hash_password(self, password):
        """Hashea la contraseña usando SHA-256 de forma real"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
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
        title_label.pack(pady=(0, 20))
        
        # Frame para campos de entrada
        input_frame = tk.Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(pady=5)
        
        # Usuario
        user_label = tk.Label(
            input_frame, 
            text="Usuario:", 
            font=('Arial', 12),
            bg='#f0f0f0',
            anchor='w',
            width=12
        )
        user_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.user_entry = tk.Entry(
            input_frame, 
            font=('Arial', 12),
            width=20
        )
        self.user_entry.grid(row=0, column=1, padx=5, pady=5)
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
        pass_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.pass_entry = tk.Entry(
            input_frame, 
            font=('Arial', 12),
            width=20,
            show='*'
        )
        self.pass_entry.grid(row=1, column=1, padx=5, pady=5)
        self.pass_entry.bind('<Return>', lambda event: self.login())
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=15)
        
        login_btn = tk.Button(
            button_frame,
            text="Iniciar Sesión",
            font=('Arial', 11, 'bold'),
            bg='#4CAF50',
            fg='white',
            width=14,
            command=self.login
        )
        
        sigin_btn = tk.Button(
            button_frame,
            text="Registrarse",
            font=('Arial', 11, 'bold'),
            bg="#4C65AF",
            fg='white',
            width=14,
            command=self.signin
        )
        
        clear_btn = tk.Button(
            button_frame,
            text="Limpiar",
            font=('Arial', 10),
            bg='#f44336',
            fg='white',
            width=10,
            command=self.clear_fields
        )
        
        login_btn.pack(pady=3)
        sigin_btn.pack(pady=3)
        clear_btn.pack(pady=3)
        
    def signin(self):
        """Registro de nuevos usuarios persistido en JSON"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Advertencia", "Escribe usuario y contraseña en las casillas para registrarte.")
            return

        if username in self.users:
            messagebox.showerror("Error", f"El usuario '{username}' ya existe.")
            return

        # Hashear la contraseña y guardar en diccionario
        hashed_pass = self.hash_password(password)
        self.users[username] = hashed_pass
        
        # Persistir en JSON
        if saveJson.guardar_diccionario(self.users, DB_FILE):
            messagebox.showinfo("Éxito", f"Usuario '{username}' registrado correctamente.")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "No se pudo guardar el usuario en la base de datos.")

    def login(self):
        """Verifica las credenciales del usuario"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return
        
        # Recargar base de datos para asegurar sincronización
        self.users = saveJson.cargar_diccionario(DB_FILE)
        
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
    window_width = 400
    window_height = 420
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()