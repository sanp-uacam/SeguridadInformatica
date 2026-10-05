import tkinter as tk
from tkinter import messagebox, ttk

from .auth import registrar_usuario, verificar_login


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Práctica HASH · Acceso')
        self.root.geometry('460x360')
        self.root.minsize(460, 360)
        self.registro = None
        self.panel = ttk.Frame(root, padding=28)
        self.panel.pack(fill='both', expand=True)
        self.create_widgets()

    def campo(self, contenedor, etiqueta, oculto=False):
        ttk.Label(contenedor, text=etiqueta).pack(anchor='w', pady=(10, 4))
        entrada = ttk.Entry(contenedor, show='*' if oculto else '')
        entrada.pack(fill='x')
        return entrada

    def create_widgets(self):
        ttk.Label(self.panel, text='Accede a tu cuenta',
                  font=('Arial', 19, 'bold')).pack(anchor='w')
        self.user_entry = self.campo(self.panel, 'Usuario')
        self.pass_entry = self.campo(self.panel, 'Contraseña', oculto=True)
        self.pass_entry.bind('<Return>', lambda event: self.login())
        botones = ttk.Frame(self.panel)
        botones.pack(fill='x', pady=22)
        ttk.Button(botones, text='Entrar', command=self.login).pack(side='left')
        ttk.Button(botones, text='Registrarse', command=self.signin).pack(side='left', padx=8)
        ttk.Button(botones, text='Limpiar', command=self.clear_fields).pack(side='right')
        self.user_entry.focus_set()

    def signin(self):
        if self.registro is not None and self.registro.winfo_exists():
            self.registro.lift()
            return
        ventana = tk.Toplevel(self.root)
        self.registro = ventana
        ventana.title('Crear una cuenta')
        ventana.geometry('480x510')
        ventana.transient(self.root)
        ventana.grab_set()
        formulario = ttk.Frame(ventana, padding=24)
        formulario.pack(fill='both', expand=True)
        ttk.Label(formulario, text='Registro de usuario',
                  font=('Arial', 18, 'bold')).pack(anchor='w')
        nombre = self.campo(formulario, 'Nombre de usuario')
        clave = self.campo(formulario, 'Contraseña', oculto=True)
        confirmacion = self.campo(formulario, 'Confirmar contraseña', oculto=True)
        ttk.Label(formulario, text=(
            'Mínimo 8 caracteres, mayúsculas, minúsculas y un carácter especial.\n'
            'No incluyas tu usuario ni secuencias como 123, 321, abc o cba.'
        ), wraplength=420).pack(anchor='w', pady=18)

        def guardar():
            try:
                registrar_usuario(nombre.get(), clave.get(), confirmacion.get())
            except ValueError as error:
                messagebox.showerror('Revisa el registro', str(error), parent=ventana)
                return
            except OSError:
                messagebox.showerror('Archivo de usuarios',
                                     'No se pudo leer o guardar el archivo de usuarios.', parent=ventana)
                return
            self.clear_fields()
            self.user_entry.insert(0, nombre.get().strip())
            ventana.destroy()
            self.pass_entry.focus_set()
            messagebox.showinfo('Cuenta creada', 'Ya puedes iniciar sesión.', parent=self.root)

        ttk.Button(formulario, text='Crear cuenta', command=guardar).pack(fill='x')
        ttk.Button(formulario, text='Cancelar', command=ventana.destroy).pack(pady=8)
        confirmacion.bind('<Return>', lambda event: guardar())
        nombre.focus_set()

    def login(self):
        try:
            nombre = verificar_login(self.user_entry.get(), self.pass_entry.get())
        except ValueError as error:
            messagebox.showerror('No se pudo entrar', str(error), parent=self.root)
            return
        except OSError:
            messagebox.showerror('Archivo de usuarios',
                                 'No se pudo leer el archivo de usuarios.', parent=self.root)
            return
        self.pass_entry.delete(0, tk.END)
        self.open_dashboard(nombre)

    def clear_fields(self):
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus_set()

    def open_dashboard(self, nombre):
        self.panel.pack_forget()
        bienvenida = ttk.Frame(self.root, padding=28)
        bienvenida.pack(fill='both', expand=True)
        ttk.Label(bienvenida, text=f'¡Bienvenido, {nombre}!', wraplength=390,
                  font=('Arial', 18, 'bold')).pack(pady=30)
        ttk.Label(bienvenida, text='Has iniciado sesión correctamente.').pack()

        def cerrar_sesion():
            bienvenida.destroy()
            self.panel.pack(fill='both', expand=True)
            self.clear_fields()

        ttk.Button(bienvenida, text='Cerrar sesión', command=cerrar_sesion).pack(pady=25)


def main():
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
