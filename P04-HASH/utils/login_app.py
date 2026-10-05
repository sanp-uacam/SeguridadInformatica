import tkinter as tk
from tkinter import messagebox
import hashlib
import hmac
from pathlib import Path

from utils import saveJson
from utils.admin_view import AdminView
from utils.password_window import PasswordWindow
from utils.user_view import UserView


USERS_FILE = Path(__file__).resolve().parent.parent / "users-db.json"

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("500x430")
        self.background_color = '#242424'
        self.text_color = '#f2f2f2'
        self.input_color = '#333333'
        self.root.configure(bg=self.background_color)
        
        # Base de datos local: usuario -> contraseña hasheada.
        self.users = saveJson.cargar_diccionario(str(USERS_FILE))
        
        self.create_widgets()
    
    def hash_password(self, password):
        """Hashea la contraseña usando SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def validate_password(self, username, password):
        """Devuelve los requisitos que todavía no cumple la contraseña."""
        errors = []
        if len(password) < 8:
            errors.append("tener al menos 8 caracteres")
        if not any(character.isupper() for character in password):
            errors.append("incluir una mayúscula")
        if not any(character.islower() for character in password):
            errors.append("incluir una minúscula")
        if not any(character.isdigit() for character in password):
            errors.append("incluir un número")
        if not any(not character.isalnum() for character in password):
            errors.append("incluir un carácter especial")
        if username.lower() in password.lower():
            errors.append("no contener el nombre de usuario")
        return errors
    
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.background_color, padx=45, pady=20)
        main_frame.pack(expand=True, fill='both')

        title_label = tk.Label(
            main_frame,
            text="Inicio de Sesión",
            font=('Arial', 22, 'bold'),
            bg=self.background_color,
            fg=self.text_color
        )
        title_label.pack(pady=(0, 22))

        input_frame = tk.Frame(main_frame, bg=self.background_color)
        input_frame.pack(pady=5)

        user_label = tk.Label(
            input_frame,
            text="Usuario:",
            font=('Arial', 12),
            bg=self.background_color,
            fg=self.text_color,
            anchor='w',
            width=12
        )
        user_label.grid(row=0, column=0, padx=(0, 15), pady=12, sticky='w')

        self.user_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            width=25,
            bg=self.input_color,
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=0,
            highlightthickness=1,
            highlightbackground='#555555',
            highlightcolor='#aaaaaa'
        )
        self.user_entry.grid(row=0, column=1, pady=12, ipady=7)

        pass_label = tk.Label(
            input_frame,
            text="Contraseña:",
            font=('Arial', 12),
            bg=self.background_color,
            fg=self.text_color,
            anchor='w',
            width=12
        )
        pass_label.grid(row=1, column=0, padx=(0, 15), pady=12, sticky='w')

        self.pass_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            width=25,
            show='*',
            bg=self.input_color,
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=0,
            highlightthickness=1,
            highlightbackground='#555555',
            highlightcolor='#aaaaaa'
        )
        self.pass_entry.grid(row=1, column=1, pady=12, ipady=7)
        self.pass_entry.bind('<Return>', lambda event: self.login())

        self.show_password = tk.BooleanVar(value=False)
        show_password_check = tk.Checkbutton(
            input_frame,
            text='Ver contraseña',
            variable=self.show_password,
            command=self.toggle_password_visibility,
            font=('Arial', 10),
            bg=self.background_color,
            fg=self.text_color,
            activebackground=self.background_color,
            activeforeground=self.text_color,
            selectcolor=self.background_color,
            anchor='w'
        )
        show_password_check.grid(row=2, column=1, pady=(0, 5), sticky='w')

        button_frame = tk.Frame(main_frame, bg=self.background_color)
        button_frame.pack(pady=(35, 0))

        login_btn = tk.Button(
            button_frame,
            text="Iniciar Sesión",
            font=('Arial', 12, 'bold'),
            bg='#363636',
            fg='#111111',
            activebackground='#4a4a4a',
            activeforeground='#111111',
            width=20,
            height=1,
            relief='flat',
            bd=0,
            highlightthickness=0,
            command=self.login
        )

        signin_btn = tk.Button(
            button_frame,
            text="Registrarse",
            font=('Arial', 12, 'bold'),
            bg='#363636',
            fg='#111111',
            activebackground='#4a4a4a',
            activeforeground='#111111',
            width=20,
            height=1,
            relief='flat',
            bd=0,
            highlightthickness=0,
            command=self.signin
        )

        login_btn.pack(pady=6, ipady=3)
        signin_btn.pack(pady=6, ipady=3)

        clear_btn = tk.Button(
            button_frame,
            text="Limpiar",
            font=('Arial', 12, 'bold'),
            bg='#363636',
            fg='#111111',
            activebackground='#4a4a4a',
            activeforeground='#111111',
            width=20,
            height=1,
            relief='flat',
            bd=0,
            highlightthickness=0,
            command=self.clear_fields
        )
        clear_btn.pack(pady=6, ipady=3)

        self.user_entry.focus_set()

    def toggle_password_visibility(self):
        self.pass_entry.configure(show='' if self.show_password.get() else '*')

        
    def signin(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        if username in self.users:
            messagebox.showerror("Error", "El usuario ya está registrado")
            return

        password_errors = self.validate_password(username, password)
        if password_errors:
            requirements = "\n".join(f"- {error}" for error in password_errors)
            messagebox.showerror(
                "Contraseña insegura",
                f"La contraseña debe:\n{requirements}",
            )
            return

        self.users[username] = self.hash_password(password)
        if saveJson.guardar_diccionario(self.users, str(USERS_FILE)):
            messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente")
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
            if hmac.compare_digest(self.users[username], hashed_password):
                messagebox.showinfo("Éxito", f"¡Bienvenido, {username}!")
                if username.lower() == 'admin':
                    self.open_admin_dashboard(username)
                else:
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
        self.root.destroy()
        UserView(
            username,
            self.users,
            self.hash_password,
            self.validate_password,
            str(USERS_FILE)
        ).run()

    def open_admin_dashboard(self, username):
        self.root.destroy()
        AdminView(
            username,
            self.users,
            self.hash_password,
            self.validate_password,
            str(USERS_FILE)
        ).run()

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
    root.deiconify()
    root.lift()
    root.focus_force()
    root.attributes('-topmost', True)
    root.after(500, lambda: root.attributes('-topmost', False))
    root.mainloop()

if __name__ == "__main__":
    main()