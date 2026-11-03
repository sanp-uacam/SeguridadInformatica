import tkinter as tk
from tkinter import messagebox
import hashlib
import re
import saveJson


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')

        # Archivo donde se guardará la base de datos de usuarios
        self.db_file = "users-db.json"

        # Cargar usuarios desde el archivo JSON al iniciar
        self.users = saveJson.cargar_diccionario(self.db_file)
        if not self.users:
            self.users = {}

        self.create_widgets()

    def hash_password(self, password):
        # Hashea la contraseña usando el algoritmo SHA-256
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def validar_contrasena(self, username, password):
        # 1. 8 caracteres
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."

        # 2. Mayúsculas y minúsculas
        if not (re.search(r'[A-Z]', password) and re.search(r'[a-z]', password)):
            return False, "Debe incluir letras mayúsculas y minúsculas."

        # 3. Carácter especial (cualquier carácter que no sea alfanumérico)
        if not re.search(r'[^a-zA-Z0-9]', password):
            return False, "Debe incluir al menos un carácter especial."

        # 4. No incluya el nombre de usuario
        if username.lower() in password.lower():
            return False, "La contraseña no debe contener el nombre de usuario."

        # 5. Sin secuencias altas/numéricas (patrones obvios)
        secuencias_prohibidas = [
            "123", "234", "345", "456", "567", "678", "789", "890", "012",
            "abc", "bcd", "cde", "def", "efg", "fgh", "ghi", "hij", "ijk",
            "jkl", "klm", "lmn", "mno", "nop", "opq", "pqr", "qrs", "rst",
            "stu", "tuv", "uvw", "vwx", "wxy", "xyz"
        ]
        password_lower = password.lower()
        if any(sec in password_lower for sec in secuencias_prohibidas):
            return False, "Evita usar secuencias alfanuméricas comunes (ej. 123, abc)."

        return True, "Contraseña válida"

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Título
        title_label = tk.Label(
            main_frame, text="Inicio de Sesión", font=('Arial', 18, 'bold'),
            bg='#f0f0f0', fg='#333333'
        )
        title_label.pack(pady=(0, 30))

        # Frame para campos de entrada
        input_frame = tk.Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(pady=10)

        # Usuario
        user_label = tk.Label(
            input_frame, text="Usuario:", font=('Arial', 12),
            bg='#f0f0f0', anchor='w', width=15
        )
        user_label.grid(row=0, column=0, padx=5, pady=10, sticky='w')

        self.user_entry = tk.Entry(input_frame, font=('Arial', 12), width=20)
        self.user_entry.grid(row=0, column=1, padx=5, pady=10)
        self.user_entry.focus()

        # Contraseña
        pass_label = tk.Label(
            input_frame, text="Contraseña:", font=('Arial', 12),
            bg='#f0f0f0', anchor='w', width=15
        )
        pass_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')

        self.pass_entry = tk.Entry(
            input_frame, font=('Arial', 12), width=20, show='*'
        )
        self.pass_entry.grid(row=1, column=1, padx=5, pady=10)

        # Bind Enter key para login
        self.pass_entry.bind('<Return>', lambda event: self.login())

        # Botones
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

        # Recargar datos para evitar sobreescrituras si hay cambios externos
        self.users = saveJson.cargar_diccionario(self.db_file)

        if username in self.users:
            messagebox.showerror("Error", "Este usuario ya se encuentra registrado.")
            return

        # Validar la contraseña contra las políticas
        es_valida, mensaje = self.validar_contrasena(username, password)
        if not es_valida:
            messagebox.showwarning("Alerta de Seguridad", mensaje)
            return

        # Generar hash y guardar
        hashed_password = self.hash_password(password)
        self.users[username] = hashed_password

        if saveJson.guardar_diccionario(self.users, self.db_file):
            messagebox.showinfo("Éxito", f"Usuario '{username}' registrado correctamente.")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "Hubo un problema al guardar los datos.")

    def login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        # Cargar los datos más recientes
        self.users = saveJson.cargar_diccionario(self.db_file)

        # Verificación del usuario y contraseña
        if username in self.users:
            # Hash ingresado =? Hash guardado
            hashed_password = self.hash_password(password)
            if self.users[username] == hashed_password:
                messagebox.showinfo("Éxito", f"¡Bienvenido de nuevo, {username}!")
                self.open_dashboard(username)
            else:
                messagebox.showerror("Error", "La contraseña es incorrecta.")
        else:
            messagebox.showerror("Error", "No se encontró el usuario.")

    def clear_fields(self):
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()

    def open_dashboard(self, username):
        self.root.destroy()

        dashboard = tk.Tk()
        dashboard.title("Panel de Control")
        dashboard.geometry("600x400")
        dashboard.configure(bg='#ffffff')

        welcome_label = tk.Label(
            dashboard, text=f"Sesión iniciada como: {username}",
            font=('Arial', 16, 'bold'), bg='#ffffff', fg='#333333'
        )
        welcome_label.pack(pady=50)

        logout_btn = tk.Button(
            dashboard, text="Cerrar Sesión", font=('Arial', 12),
            bg='#e67e22', fg='white', command=dashboard.quit
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
