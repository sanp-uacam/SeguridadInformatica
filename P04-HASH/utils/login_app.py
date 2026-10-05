#Miranda Amaro Hernandez
import tkinter as tk
from tkinter import messagebox
import hashlib

from . import saveJson


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.configure(bg='#f0f0f0')

        # Archivo donde se guardan los usuarios y sus hashes
        self.archivo_usuarios = "users-db.json"

        # Cargar usuarios existentes
        self.users = saveJson.cargar_diccionario(
            self.archivo_usuarios
        )

        self.create_widgets()

    def hash_password(self, password):
        """Hashea la contraseña usando SHA-256"""
        return hashlib.sha256(
            password.encode('utf-8')
        ).hexdigest()

    def tiene_secuencia(self, password):
        """
        Busca secuencias simples como:
        abc, bcd, 123, 234
        y también al revés:
        cba, 321, etc.
        """

        password = password.lower()

        letras = "abcdefghijklmnopqrstuvwxyz"
        numeros = "0123456789"

        # Secuencias de letras
        for i in range(len(letras) - 2):
            secuencia = letras[i:i + 3]

            if secuencia in password:
                return True

            if secuencia[::-1] in password:
                return True

        # Secuencias de números
        for i in range(len(numeros) - 2):
            secuencia = numeros[i:i + 3]

            if secuencia in password:
                return True

            if secuencia[::-1] in password:
                return True

        return False

    def validar_password(self, username, password):
        """Valida las reglas solicitadas para la contraseña"""
        #EXTRA DE ASIGNACION
        #Poner requisitos para la contraseña (requisitos del pizarron)

        # Mínimo 8 caracteres
        if len(password) < 8:
            return False, \
                "La contraseña debe tener mínimo 8 caracteres."

        # Mayúscula
        if not any(
            caracter.isupper()
            for caracter in password
        ):
            return False, \
                "La contraseña debe contener una mayúscula."

        # Minúscula
        if not any(
            caracter.islower()
            for caracter in password
        ):
            return False, \
                "La contraseña debe contener una minúscula."

        # Carácter especial
        if not any(
            not caracter.isalnum()
            for caracter in password
        ):
            return False, \
                "La contraseña debe contener un carácter especial."

        # No debe incluir el nombre del usuario
        if username.lower() in password.lower():
            return False, \
                "La contraseña no debe contener el nombre de usuario."

        # No debe tener secuencias
        if self.tiene_secuencia(password):
            return False, \
                "La contraseña no debe contener secuencias como abc o 123."

        return True, "Contraseña válida"

    def create_widgets(self):

        # Frame principal
        main_frame = tk.Frame(
            self.root,
            bg='#f0f0f0',
            padx=20,
            pady=20
        )

        main_frame.pack(
            expand=True,
            fill='both'
        )

        # Título
        title_label = tk.Label(
            main_frame,
            text="Inicio de Sesión",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )

        title_label.pack(
            pady=(0, 30)
        )

        # Frame de entradas
        input_frame = tk.Frame(
            main_frame,
            bg='#f0f0f0'
        )

        input_frame.pack(
            pady=10
        )

        # Usuario
        user_label = tk.Label(
            input_frame,
            text="Usuario:",
            font=('Arial', 12),
            bg='#f0f0f0',
            anchor='w',
            width=15
        )

        user_label.grid(
            row=0,
            column=0,
            padx=5,
            pady=10,
            sticky='w'
        )

        self.user_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            width=20
        )

        self.user_entry.grid(
            row=0,
            column=1,
            padx=5,
            pady=10
        )

        self.user_entry.focus()

        # Contraseña
        pass_label = tk.Label(
            input_frame,
            text="Contraseña:",
            font=('Arial', 12),
            bg='#f0f0f0',
            anchor='w',
            width=15
        )

        pass_label.grid(
            row=1,
            column=0,
            padx=5,
            pady=10,
            sticky='w'
        )

        self.pass_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            width=20,
            show='*'
        )

        self.pass_entry.grid(
            row=1,
            column=1,
            padx=5,
            pady=10
        )

        # Enter para iniciar sesión
        self.pass_entry.bind(
            '<Return>',
            lambda event: self.login()
        )

        # Frame de botones
        button_frame = tk.Frame(
            main_frame,
            bg='#f0f0f0'
        )

        button_frame.pack(
            pady=20
        )

        # Botón Login
        login_btn = tk.Button(
            button_frame,
            text="Iniciar Sesión",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            width=15,
            command=self.login
        )

        login_btn.pack(
            pady=5
        )

        # Botón Registrarse
        signin_btn = tk.Button(
            button_frame,
            text="Registrarse",
            font=('Arial', 12, 'bold'),
            bg='#4C65AF',
            fg='white',
            width=15,
            command=self.signin
        )

        signin_btn.pack(
            pady=5
        )

        # Botón Limpiar
        clear_btn = tk.Button(
            button_frame,
            text="Limpiar",
            font=('Arial', 10),
            bg='#f44336',
            fg='white',
            width=12,
            command=self.clear_fields
        )

        clear_btn.pack(
            pady=5
        )

    def signin(self):
        """Registra un usuario nuevo"""

        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        # Verificar campos vacíos
        if not username or not password:
            messagebox.showerror(
                "Error",
                "Por favor, complete todos los campos"
            )
            return

        # Revisar si el usuario ya existe
        if username in self.users:
            messagebox.showerror(
                "Error",
                "El usuario ya está registrado"
            )
            return

        # Validar contraseña
        password_valida, mensaje = \
            self.validar_password(
                username,
                password
            )

        if not password_valida:
            messagebox.showerror(
                "Contraseña no válida",
                mensaje
            )
            return

        # Crear HASH de la contraseña
        hashed_password = \
            self.hash_password(password)

        # Guardar:
        # usuario -> hash
        self.users[username] = \
            hashed_password

        # Guardar en JSON
        guardado = \
            saveJson.guardar_diccionario(
                self.users,
                self.archivo_usuarios
            )

        if guardado:

            messagebox.showinfo(
                "Registro exitoso",
                f"Usuario {username} registrado correctamente"
            )

            self.clear_fields()

        else:

            # Si hubo error al guardar
            # eliminamos el usuario de memoria
            del self.users[username]

            messagebox.showerror(
                "Error",
                "No se pudo guardar el usuario"
            )

    def login(self):
        """Verifica las credenciales del usuario"""

        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror(
                "Error",
                "Por favor, complete todos los campos"
            )
            return

        # Verificar si existe el usuario
        if username in self.users:

            # Convertir contraseña ingresada a SHA-256
            hashed_password = \
                self.hash_password(password)

            # Comparar HASH introducido
            # contra HASH guardado
            if self.users[username] == hashed_password:

                messagebox.showinfo(
                    "Éxito",
                    f"¡Bienvenido, {username}!"
                )

                self.open_dashboard(
                    username
                )

            else:

                messagebox.showerror(
                    "Error",
                    "Contraseña incorrecta"
                )

        else:

            messagebox.showerror(
                "Error",
                "Usuario no encontrado"
            )

    def clear_fields(self):
        """Limpia los campos"""

        self.user_entry.delete(
            0,
            tk.END
        )

        self.pass_entry.delete(
            0,
            tk.END
        )

        self.user_entry.focus()

    def open_dashboard(self, username):
        """Abre ventana después del login"""

        # Cerrar login
        self.root.destroy()

        # Crear dashboard
        dashboard = tk.Tk()

        dashboard.title(
            "Dashboard Principal"
        )

        dashboard.geometry(
            "600x400"
        )

        dashboard.configure(
            bg='#ffffff'
        )

        welcome_label = tk.Label(
            dashboard,
            text=f"Bienvenido al Sistema, {username}!",
            font=('Arial', 16, 'bold'),
            bg='#ffffff',
            fg='#333333'
        )

        welcome_label.pack(
            pady=50
        )

        logout_btn = tk.Button(
            dashboard,
            text="Cerrar Sesión",
            font=('Arial', 12),
            bg='#ff9800',
            fg='white',
            command=dashboard.quit
        )

        logout_btn.pack(
            pady=20
        )

        dashboard.mainloop()


def main():

    # Crear ventana principal
    root = tk.Tk()

    # Tamaño de la ventana
    # 450 permite mostrar todos los botones
    window_width = 400
    window_height = 450

    # Obtener tamaño de pantalla
    screen_width = \
        root.winfo_screenwidth()

    screen_height = \
        root.winfo_screenheight()

    # Calcular centro
    x = (
        screen_width -
        window_width
    ) // 2

    y = (
        screen_height -
        window_height
    ) // 2

    # Posicionar ventana
    root.geometry(
        f'{window_width}x{window_height}+{x}+{y}'
    )

    # Crear aplicación
    app = LoginApp(root)

    # Ejecutar
    root.mainloop()


if __name__ == "__main__":
    main()