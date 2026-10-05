import tkinter as tk
from tkinter import messagebox
import hashlib
import re
from utils.saveJson import guardar_diccionario, cargar_diccionario

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')
        
        self.db_filename = "users_db.json"
        
        # Cargamos los datos. Si el archivo no existe, saveJson devuelve {}, 
        # así que lo convertimos a una lista [] para soportar múltiples usuarios.
        datos = cargar_diccionario(self.db_filename)
        self.users = datos if isinstance(datos, list) else []
        
        self.create_widgets()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def validate_password(self, username, password):
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."
        if not (re.search(r"[a-z]", password) and re.search(r"[A-Z]", password)):
            return False, "La contraseña debe contener mayúsculas y minúsculas."
        if not re.search(r"[\W_]", password):
            return False, "La contraseña debe contener al menos un carácter especial."
        if username.lower() in password.lower():
            return False, "La contraseña no debe incluir el nombre de usuario."
            
        return True, "Contraseña válida"

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        title_label = tk.Label(
            main_frame, text="Inicio de Sesión", font=('Arial', 18, 'bold'),
            bg='#f0f0f0', fg='#333333'
        )
        title_label.pack(pady=(0, 30))
        
        input_frame = tk.Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(pady=10)
        
        user_label = tk.Label(
            input_frame, text="Usuario:", font=('Arial', 12),
            bg='#f0f0f0', anchor='w', width=15
        )
        user_label.grid(row=0, column=0, padx=5, pady=10, sticky='w')
        
        self.user_entry = tk.Entry(input_frame, font=('Arial', 12), width=20)
        self.user_entry.grid(row=0, column=1, padx=5, pady=10)
        self.user_entry.focus()  
        
        pass_label = tk.Label(
            input_frame, text="Contraseña:", font=('Arial', 12),
            bg='#f0f0f0', anchor='w', width=15
        )
        pass_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')
        
        self.pass_entry = tk.Entry(
            input_frame, font=('Arial', 12), width=20, show='*'
        )
        self.pass_entry.grid(row=1, column=1, padx=5, pady=10)
        
        self.pass_entry.bind('<Return>', lambda event: self.login())
        
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        login_btn = tk.Button(
            button_frame, text="Iniciar Sesión", font=('Arial', 12, 'bold'),
            bg='#4CAF50', fg='white', width=12, command=self.login
        )
        
        sigin_btn = tk.Button(
            button_frame, text="Registrarse", font=('Arial', 12, 'bold'),
            bg="#4C65AF", fg='white', width=12, command=self.signin
        )
        
        login_btn.pack(pady=5)
        sigin_btn.pack(pady=1)
        
        clear_btn = tk.Button(
            button_frame, text="Limpiar", font=('Arial', 10),
            bg='#f44336', fg='white', width=10, command=self.clear_fields
        )
        clear_btn.pack(pady=5)
        
    def signin(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return
            
        # Buscar si el usuario ya existe en la lista de diccionarios
        if any(usuario.get("User") == username for usuario in self.users):
            messagebox.showerror("Error", "Este usuario ya se encuentra registrado.")
            return
            
        es_valida, mensaje = self.validate_password(username, password)
        if not es_valida:
            messagebox.showerror("Error en Contraseña", mensaje)
            return
            
        hashed_password = self.hash_password(password)
        
        # Agregamos el nuevo usuario con la estructura exacta del pizarrón
        self.users.append({
            "User": username,
            "Pass": hashed_password
        })
        
        guardar_diccionario(self.users, self.db_filename)
        
        messagebox.showinfo("Éxito", f"Usuario {username} registrado correctamente.")
        self.clear_fields()
    
    def login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return
        
        datos = cargar_diccionario(self.db_filename)
        self.users = datos if isinstance(datos, list) else []
        
        # Buscar el diccionario que corresponde a este usuario
        usuario_encontrado = next((u for u in self.users if u.get("User") == username), None)
        
        if usuario_encontrado:
            hashed_password = self.hash_password(password)
            if usuario_encontrado.get("Pass") == hashed_password:
                messagebox.showinfo("Éxito", f"¡Bienvenido, {username}!")
                self.open_dashboard(username)
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")
    
    def clear_fields(self):
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()
    
    def open_dashboard(self, username):
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
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()