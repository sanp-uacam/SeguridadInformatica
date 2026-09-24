import hashlib
import hmac
import os
import string
import tkinter as tk
from tkinter import messagebox

from utils import saveJson


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(BASE_DIR, "users-db.json")


def hash_password(password):
    """Genera el hash SHA-256 de una contraseña."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def has_simple_sequence(password, sequence_length=3):
    """Detecta secuencias simples como abc, cba, 123 o 321."""
    value = password.lower()
    bases = (string.ascii_lowercase, string.digits)

    for base in bases:
        for candidate_base in (base, base[::-1]):
            for i in range(len(candidate_base) - sequence_length + 1):
                sequence = candidate_base[i:i + sequence_length]
                if sequence in value:
                    return True
    return False


def validate_password(username, password):
    """Valida las reglas indicadas para la contraseña."""
    errors = []

    if len(password) < 8:
        errors.append("Debe tener al menos 8 caracteres.")
    if not any(char.isupper() for char in password):
        errors.append("Debe incluir al menos una mayúscula.")
    if not any(char.islower() for char in password):
        errors.append("Debe incluir al menos una minúscula.")
    if not any(not char.isalnum() and not char.isspace() for char in password):
        errors.append("Debe incluir al menos un carácter especial.")
    if username and username.lower() in password.lower():
        errors.append("No debe incluir el nombre de usuario.")
    if has_simple_sequence(password):
        errors.append("No debe contener secuencias simples como abc, cba, 123 o 321.")

    return errors


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Práctica HASH - Alfredo J Cruz Miss")
        self.root.configure(bg="#f0f0f0")

        # Los usuarios se cargan desde JSON. La contraseña nunca se guarda en texto plano.
        self.users = saveJson.cargar_diccionario(USERS_FILE)
        if not isinstance(self.users, dict):
            self.users = {}

        self.create_widgets()

    def hash_password(self, password):
        """Mantiene el método dentro de la clase para usarlo desde el login."""
        return hash_password(password)

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        title_label = tk.Label(
            main_frame,
            text="Inicio de Sesión",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        )
        title_label.pack(pady=(0, 6))

        tk.Label(
            main_frame,
            text="Práctica HASH  •  Alumno: Alfredo J Cruz Miss",
            font=("Arial", 10, "italic"),
            bg="#f0f0f0",
            fg="#666666",
        ).pack(pady=(0, 18))

        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.pack(pady=10)

        tk.Label(
            input_frame,
            text="Usuario:",
            font=("Arial", 12),
            bg="#f0f0f0",
            anchor="w",
            width=15,
        ).grid(row=0, column=0, padx=5, pady=10, sticky="w")

        self.user_entry = tk.Entry(input_frame, font=("Arial", 12), width=20)
        self.user_entry.grid(row=0, column=1, padx=5, pady=10)
        self.user_entry.focus()

        tk.Label(
            input_frame,
            text="Contraseña:",
            font=("Arial", 12),
            bg="#f0f0f0",
            anchor="w",
            width=15,
        ).grid(row=1, column=0, padx=5, pady=10, sticky="w")

        self.pass_entry = tk.Entry(input_frame, font=("Arial", 12), width=20, show="*")
        self.pass_entry.grid(row=1, column=1, padx=5, pady=10)
        self.pass_entry.bind("<Return>", lambda event: self.login())

        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Iniciar Sesión",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=14,
            command=self.login,
        ).pack(pady=5)

        tk.Button(
            button_frame,
            text="Registrarse",
            font=("Arial", 12, "bold"),
            bg="#4C65AF",
            fg="white",
            width=14,
            command=self.signin,
        ).pack(pady=5)

        tk.Button(
            button_frame,
            text="Limpiar",
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            width=10,
            command=self.clear_fields,
        ).pack(pady=5)

    def signin(self):
        """Abre una ventana para registrar un usuario nuevo."""
        register_window = tk.Toplevel(self.root)
        register_window.title("Registro de usuario - Alfredo J Cruz Miss")
        register_window.geometry("460x430")
        register_window.resizable(False, False)
        register_window.configure(bg="#f0f0f0")
        register_window.transient(self.root)
        register_window.grab_set()

        tk.Label(
            register_window,
            text="Registro",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
        ).pack(pady=(20, 4))

        tk.Label(
            register_window,
            text="Práctica HASH  •  Alfredo J Cruz Miss",
            font=("Arial", 9, "italic"),
            bg="#f0f0f0",
            fg="#666666",
        ).pack(pady=(0, 10))

        form = tk.Frame(register_window, bg="#f0f0f0")
        form.pack()

        tk.Label(form, text="Usuario:", font=("Arial", 11), bg="#f0f0f0").grid(
            row=0, column=0, padx=8, pady=8, sticky="w"
        )
        user_entry = tk.Entry(form, font=("Arial", 11), width=24)
        user_entry.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(form, text="Contraseña:", font=("Arial", 11), bg="#f0f0f0").grid(
            row=1, column=0, padx=8, pady=8, sticky="w"
        )
        pass_entry = tk.Entry(form, font=("Arial", 11), width=24, show="*")
        pass_entry.grid(row=1, column=1, padx=8, pady=8)

        tk.Label(form, text="Confirmar:", font=("Arial", 11), bg="#f0f0f0").grid(
            row=2, column=0, padx=8, pady=8, sticky="w"
        )
        confirm_entry = tk.Entry(form, font=("Arial", 11), width=24, show="*")
        confirm_entry.grid(row=2, column=1, padx=8, pady=8)

        rules = (
            "La contraseña debe cumplir:\n"
            "• Mínimo 8 caracteres\n"
            "• Mayúsculas y minúsculas\n"
            "• Al menos un carácter especial\n"
            "• Sin secuencias simples (abc, 123, etc.)\n"
            "• No incluir el nombre de usuario"
        )
        tk.Label(
            register_window,
            text=rules,
            justify="left",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#444444",
        ).pack(pady=12)

        def register_user():
            username = user_entry.get().strip()
            password = pass_entry.get()
            confirmation = confirm_entry.get()

            if not username or not password or not confirmation:
                messagebox.showerror("Error", "Complete todos los campos.", parent=register_window)
                return

            if username in self.users:
                messagebox.showerror("Error", "Ese usuario ya está registrado.", parent=register_window)
                return

            if password != confirmation:
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=register_window)
                return

            errors = validate_password(username, password)
            if errors:
                messagebox.showerror(
                    "Contraseña no válida",
                    "Corrija lo siguiente:\n\n" + "\n".join(f"• {error}" for error in errors),
                    parent=register_window,
                )
                return

            # Se guarda únicamente el hash SHA-256, nunca la contraseña original.
            self.users[username] = self.hash_password(password)

            if not saveJson.guardar_diccionario(self.users, USERS_FILE):
                self.users.pop(username, None)
                messagebox.showerror("Error", "No se pudo guardar el usuario.", parent=register_window)
                return

            messagebox.showinfo(
                "Registro exitoso",
                "Usuario registrado correctamente.\nLa contraseña fue almacenada como hash SHA-256.",
                parent=register_window,
            )
            self.user_entry.delete(0, tk.END)
            self.user_entry.insert(0, username)
            self.pass_entry.delete(0, tk.END)
            register_window.destroy()
            self.pass_entry.focus()

        tk.Button(
            register_window,
            text="Guardar usuario",
            font=("Arial", 11, "bold"),
            bg="#4C65AF",
            fg="white",
            width=16,
            command=register_user,
        ).pack(pady=8)

        user_entry.focus()

    def login(self):
        """Hashea la contraseña ingresada y compara ese hash con el guardado."""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        stored_hash = self.users.get(username)
        if stored_hash is None:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        entered_hash = self.hash_password(password)

        # El login es válido solamente si ambos hashes coinciden.
        if hmac.compare_digest(stored_hash, entered_hash):
            messagebox.showinfo("Éxito", f"¡Bienvenido, {username}!")
            self.open_dashboard(username)
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    def clear_fields(self):
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()

    def open_dashboard(self, username):
        self.root.withdraw()

        dashboard = tk.Toplevel(self.root)
        dashboard.title("Dashboard Principal - Alfredo J Cruz Miss")
        dashboard.geometry("600x400")
        dashboard.configure(bg="#ffffff")

        tk.Label(
            dashboard,
            text=f"Bienvenido al Sistema, {username}!",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#333333",
        ).pack(pady=(45, 10))

        tk.Label(
            dashboard,
            text="Práctica HASH\nAlumno: Alfredo J Cruz Miss",
            font=("Arial", 11),
            bg="#ffffff",
            fg="#666666",
            justify="center",
        ).pack(pady=10)

        def logout():
            dashboard.destroy()
            self.clear_fields()
            self.root.deiconify()

        tk.Button(
            dashboard,
            text="Cerrar Sesión",
            font=("Arial", 12),
            bg="#ff9800",
            fg="white",
            command=logout,
        ).pack(pady=20)



def main():
    root = tk.Tk()

    window_width = 400
    window_height = 450
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.resizable(False, False)

    LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
