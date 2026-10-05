import tkinter as tk
from tkinter import messagebox
import hashlib
import json
import os


# ==========================================================
# COLORES DE LA INTERFAZ
# ==========================================================

COLOR_BG = "#EAF2F8"
COLOR_CARD = "#D6EAF8"
COLOR_TEXT = "#1F3A5F"
COLOR_ENTRY_BG = "#FFFFFF"
COLOR_ENTRY_TEXT = "#17202A"

COLOR_PRIMARY = "#2E86C1"
COLOR_SECONDARY = "#5DADE2"
COLOR_DANGER = "#E74C3C"


# ==========================================================
# ARCHIVO DONDE SE GUARDAN LOS USUARIOS
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

USERS_FILE = os.path.join(
    BASE_DIR,
    "users_db.json"
)


# ==========================================================
# CLASE PRINCIPAL
# ==========================================================

class LoginApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Sistema de Login")

        self.root.geometry("700x550")

        self.root.resizable(False, False)

        self.root.configure(
            bg=COLOR_BG
        )

        self.users = self.cargar_usuarios()

        self.crear_interfaz()


    # ======================================================
    # HASH SHA-256
    # ======================================================

    def hash_password(self, password):

        return hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()


    # ======================================================
    # CARGAR USUARIOS
    # ======================================================

    def cargar_usuarios(self):

        if os.path.exists(USERS_FILE):

            try:

                with open(
                    USERS_FILE,
                    "r",
                    encoding="utf-8"
                ) as archivo:

                    return json.load(archivo)

            except Exception:

                pass


        usuarios = {
            "admin": self.hash_password("admin123")
        }

        self.guardar_usuarios(
            usuarios
        )

        return usuarios


    # ======================================================
    # GUARDAR USUARIOS
    # ======================================================

    def guardar_usuarios(
        self,
        usuarios=None
    ):

        if usuarios is None:

            usuarios = self.users

        with open(
            USERS_FILE,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                usuarios,
                archivo,
                indent=4
            )


    # ======================================================
    # CREAR INTERFAZ
    # ======================================================

    def crear_interfaz(self):

        # --------------------------------------------------
        # TÍTULO
        # --------------------------------------------------

        titulo = tk.Label(
            self.root,
            text="Inicio de Sesión",
            font=("Arial", 30, "bold"),
            bg=COLOR_BG,
            fg=COLOR_TEXT
        )

        titulo.pack(
            pady=(40, 25)
        )


        # --------------------------------------------------
        # FRAME PRINCIPAL
        # --------------------------------------------------

        frame = tk.Frame(
            self.root,
            bg=COLOR_CARD,
            padx=40,
            pady=35
        )

        frame.pack(
            padx=60,
            pady=10
        )


        # --------------------------------------------------
        # USUARIO
        # --------------------------------------------------

        label_usuario = tk.Label(
            frame,
            text="Usuario:",
            font=("Arial", 16, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_TEXT
        )

        label_usuario.grid(
            row=0,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )


        self.entry_usuario = tk.Entry(
            frame,
            font=("Arial", 16),
            width=25,
            bg=COLOR_ENTRY_BG,
            fg=COLOR_ENTRY_TEXT,
            insertbackground=COLOR_TEXT,
            relief="flat",
            highlightthickness=2,
            highlightbackground="#A9CCE3",
            highlightcolor=COLOR_PRIMARY
        )

        self.entry_usuario.grid(
            row=0,
            column=1,
            padx=15,
            pady=15,
            ipady=8
        )


        # --------------------------------------------------
        # CONTRASEÑA
        # --------------------------------------------------

        label_password = tk.Label(
            frame,
            text="Contraseña:",
            font=("Arial", 16, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_TEXT
        )

        label_password.grid(
            row=1,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )


        self.entry_password = tk.Entry(
            frame,
            font=("Arial", 16),
            width=25,
            show="*",
            bg=COLOR_ENTRY_BG,
            fg=COLOR_ENTRY_TEXT,
            insertbackground=COLOR_TEXT,
            relief="flat",
            highlightthickness=2,
            highlightbackground="#A9CCE3",
            highlightcolor=COLOR_PRIMARY
        )

        self.entry_password.grid(
            row=1,
            column=1,
            padx=15,
            pady=15,
            ipady=8
        )


        # --------------------------------------------------
        # FRAME DE BOTONES
        # --------------------------------------------------

        frame_botones = tk.Frame(
            self.root,
            bg=COLOR_BG
        )

        frame_botones.pack(
            pady=25
        )


        # --------------------------------------------------
        # BOTÓN INICIAR SESIÓN
        # --------------------------------------------------

        boton_login = tk.Button(
            frame_botones,
            text="Iniciar Sesión",
            command=self.iniciar_sesion,
            font=("Arial", 14, "bold"),

            bg=COLOR_PRIMARY,
            fg="#1F2937",

            activebackground="#21618C",
            activeforeground="#FFFFFF",

            width=15,
            height=2,

            relief="raised",
            bd=2,
            cursor="hand2"
        )

        boton_login.grid(
            row=0,
            column=0,
            padx=8
        )


        # --------------------------------------------------
        # BOTÓN REGISTRARSE
        # --------------------------------------------------

        boton_registro = tk.Button(
            frame_botones,
            text="Registrarse",
            command=self.registrar_usuario,
            font=("Arial", 14, "bold"),

            bg=COLOR_SECONDARY,
            fg="#1F2937",

            activebackground="#3498DB",
            activeforeground="#FFFFFF",

            width=15,
            height=2,

            relief="raised",
            bd=2,
            cursor="hand2"
        )

        boton_registro.grid(
            row=0,
            column=1,
            padx=8
        )


        # --------------------------------------------------
        # BOTÓN LIMPIAR
        # --------------------------------------------------

        boton_limpiar = tk.Button(
            frame_botones,
            text="Limpiar",
            command=self.limpiar_campos,
            font=("Arial", 14, "bold"),

            bg=COLOR_DANGER,
            fg="#1F2937",

            activebackground="#C0392B",
            activeforeground="#FFFFFF",

            width=15,
            height=2,

            relief="raised",
            bd=2,
            cursor="hand2"
        )

        boton_limpiar.grid(
            row=0,
            column=2,
            padx=8
        )


        # Permitir iniciar sesión presionando ENTER
        self.root.bind(
            "<Return>",
            lambda event: self.iniciar_sesion()
        )


        # Cursor inicial
        self.entry_usuario.focus()


    # ======================================================
    # INICIAR SESIÓN
    # ======================================================

    def iniciar_sesion(self):

        usuario = self.entry_usuario.get().strip()

        password = self.entry_password.get()


        if not usuario or not password:

            messagebox.showwarning(
                "Campos vacíos",
                "Ingresa usuario y contraseña."
            )

            return


        password_hash = self.hash_password(
            password
        )


        if (
            usuario in self.users
            and
            self.users[usuario] == password_hash
        ):

            messagebox.showinfo(
                "Inicio de sesión",
                f"¡Bienvenido {usuario}!"
            )

            self.limpiar_campos()

        else:

            messagebox.showerror(
                "Error",
                "Usuario o contraseña incorrectos."
            )


    # ======================================================
    # REGISTRAR USUARIO
    # ======================================================

    def registrar_usuario(self):

        usuario = self.entry_usuario.get().strip()

        password = self.entry_password.get()


        if not usuario or not password:

            messagebox.showwarning(
                "Campos vacíos",
                "Escribe un usuario y una contraseña."
            )

            return


        if usuario in self.users:

            messagebox.showwarning(
                "Usuario existente",
                "Ese usuario ya está registrado."
            )

            return


        if len(password) < 4:

            messagebox.showwarning(
                "Contraseña",
                "La contraseña debe tener al menos 4 caracteres."
            )

            return


        password_hash = self.hash_password(
            password
        )


        self.users[usuario] = password_hash


        self.guardar_usuarios()


        messagebox.showinfo(
            "Registro exitoso",
            f"Usuario '{usuario}' registrado correctamente.\n\n"
            "La contraseña fue almacenada utilizando SHA-256."
        )


        self.limpiar_campos()


    # ======================================================
    # LIMPIAR CAMPOS
    # ======================================================

    def limpiar_campos(self):

        self.entry_usuario.delete(
            0,
            tk.END
        )

        self.entry_password.delete(
            0,
            tk.END
        )

        self.entry_usuario.focus()


# ==========================================================
# FUNCIÓN MAIN
# ==========================================================

def main():

    root = tk.Tk()

    app = LoginApp(root)

    root.mainloop()


# ==========================================================
# EJECUTAR
# ==========================================================

if __name__ == "__main__":

    main()