"""Práctica HASH · Kerin. Ejecutar con Python 3.10 o posterior."""

from datetime import datetime
import tkinter as tk

from .saveJson import AlmacenUsuarios, ErrorDatos
from .seguridad import reglas_contrasena

FONDO = "#eef3f6"
AZUL = "#122b3d"
TEXTO = "#193549"
GRIS = "#5c7080"
VERDE = "#087e78"
ROJO = "#b12b3c"


class Aplicacion:
    def __init__(self, root, almacen=None):
        self.root = root
        self.almacen = almacen or AlmacenUsuarios()
        self.sesion = None
        root.title("Kerin | Práctica HASH")
        root.geometry("980x730")
        root.minsize(930, 730)
        root.configure(bg=FONDO)
        root.option_add("*Font", ("Segoe UI", 10))
        self.menu = tk.Frame(root, bg=AZUL, width=250)
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)
        self.etiqueta(self.menu, "Hash", 26, "#ffffff", AZUL, True).pack(anchor="w", padx=28, pady=(38, 8))
        self.etiqueta(self.menu, "SEGURIDAD INFORMÁTICA", 9, "#83c9c6", AZUL, True).pack(anchor="w", padx=28)
        self.etiqueta(self.menu, "Una contraseña.\nUna huella\ndigital.", 19, "white", AZUL, True).pack(anchor="w", padx=28, pady=(48, 20))
        self.etiqueta(self.menu, "01   Registra tu usuario\n\n02   Guarda su hash\n\n03   Verifica tu acceso", 11, "#d0dfe7", AZUL).pack(anchor="w", padx=28)
        self.etiqueta(self.menu, "KERIN\nPráctica de autenticación\nPython · SHA-256 · JSON", 10, "#a9bfcd", AZUL).pack(side="bottom", anchor="w", padx=28, pady=32)
        self.contenido = tk.Frame(root, bg=FONDO)
        self.contenido.pack(side="right", fill="both", expand=True, padx=36, pady=16)
        self.mostrar_formulario()

    @staticmethod
    def etiqueta(parent, texto, tam=10, color=TEXTO, fondo="white", negrita=False):
        return tk.Label(parent, text=texto, bg=fondo, fg=color, justify="left", anchor="w",
                        font=("Segoe UI", tam, "bold" if negrita else "normal"))

    def limpiar_pantalla(self):
        self.root.unbind("<Return>")
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def boton(self, parent, texto, comando, primario=True):
        return tk.Button(parent, text=texto, command=comando, bg=VERDE if primario else "#e5eef2",
                         fg="white" if primario else TEXTO, activebackground="#c8e7e4",
                         activeforeground=TEXTO, relief="flat", bd=0, cursor="hand2",
                         font=("Segoe UI", 11, "bold"), padx=18, pady=7)

    def campo(self, parent, titulo, variable, oculto=False):
        self.etiqueta(parent, titulo, 10, negrita=True).pack(anchor="w", pady=(6, 3))
        entrada = tk.Entry(parent, textvariable=variable, show="•" if oculto else "",
                           font=("Segoe UI", 12), bg="#f5f8fa", fg=TEXTO, relief="flat",
                           highlightthickness=1, highlightbackground="#c9d7e0", highlightcolor=VERDE)
        entrada.pack(fill="x", ipady=5)
        return entrada

    def mostrar_formulario(self, registro=False, usuario="", mensaje=""):
        self.limpiar_pantalla()
        self.sesion = None
        self.registro = registro
        self.etiqueta(self.contenido, "REGISTRO" if registro else "ACCESO AL SISTEMA", 10, VERDE, FONDO, True).pack(anchor="w")
        self.etiqueta(self.contenido, "Crea tu cuenta" if registro else "Tu acceso comienza aquí", 25, TEXTO, FONDO, True).pack(anchor="w", pady=(8, 6))
        self.etiqueta(self.contenido, "Completa las reglas para guardar tu registro." if registro else "Ingresa tus datos para comprobar tu identidad.", 11, GRIS, FONDO).pack(anchor="w", pady=(0, 18))
        tarjeta = tk.Frame(self.contenido, bg="white", padx=26, pady=14)
        tarjeta.pack(fill="x")
        self.usuario = tk.StringVar(value=usuario)
        self.clave = tk.StringVar()
        self.confirmacion = tk.StringVar()
        self.entrada_usuario = self.campo(tarjeta, "Usuario", self.usuario)
        self.entrada_clave = self.campo(tarjeta, "Contraseña", self.clave, True)
        self.entradas_secretas = [self.entrada_clave]
        if registro:
            self.entradas_secretas.append(self.campo(tarjeta, "Confirma tu contraseña", self.confirmacion, True))
        self.ver_clave = tk.BooleanVar(value=False)
        tk.Checkbutton(tarjeta, text="Mostrar contraseña", variable=self.ver_clave, command=self.alternar_clave,
                       bg="white", fg=GRIS, activebackground="white", bd=0).pack(anchor="w", pady=(6, 2))
        if registro:
            self.indicadores = []
            for texto, _ in reglas_contrasena("", ""):
                indicador = self.etiqueta(tarjeta, "○  " + texto, 9, GRIS)
                indicador.pack(anchor="w")
                self.indicadores.append(indicador)
            self.usuario.trace_add("write", self.actualizar_reglas)
            self.clave.trace_add("write", self.actualizar_reglas)
            self.actualizar_reglas()
        self.estado = self.etiqueta(tarjeta, mensaje, 10, VERDE)
        self.estado.configure(wraplength=540)
        self.estado.pack(anchor="w", fill="x", pady=(6, 5))
        self.boton(tarjeta, "Guardar registro" if registro else "Iniciar sesión", self.enviar).pack(fill="x")
        self.boton(tarjeta, "Volver al acceso" if registro else "Crear una cuenta",
                   lambda: self.mostrar_formulario(not registro), False).pack(fill="x", pady=(8, 0))
        self.etiqueta(self.contenido, "El archivo JSON almacena el hash, nunca la contraseña.", 10, GRIS, FONDO).pack(anchor="w", pady=(15, 0))
        self.root.bind("<Return>", lambda evento: self.enviar())
        self.entrada_usuario.focus_set()

    def actualizar_reglas(self, *_):
        for etiqueta, (texto, cumple) in zip(self.indicadores, reglas_contrasena(self.usuario.get(), self.clave.get())):
            etiqueta.configure(text=("✓  " if cumple else "○  ") + texto, fg=VERDE if cumple else GRIS)

    def alternar_clave(self):
        for entrada in self.entradas_secretas:
            entrada.configure(show="" if self.ver_clave.get() else "•")

    def enviar(self):
        usuario, clave = self.usuario.get().strip(), self.clave.get()
        if not usuario or not clave:
            self.estado.configure(text="Completa el usuario y la contraseña.", fg=ROJO)
            return
        try:
            if self.registro:
                if not all(cumple for _, cumple in reglas_contrasena(usuario, clave)):
                    self.estado.configure(text="La contraseña aún no cumple todas las reglas indicadas.", fg=ROJO)
                    return
                nombre = self.almacen.registrar(usuario, clave, self.confirmacion.get())
                self.clave.set("")
                self.confirmacion.set("")
                self.mostrar_formulario(usuario=nombre, mensaje="Cuenta creada. Ya puedes iniciar sesión.")
            else:
                resultado = self.almacen.autenticar(usuario, clave)
                self.clave.set("")
                if resultado is None:
                    self.estado.configure(text="Usuario o contraseña incorrectos. Intenta de nuevo.", fg=ROJO)
                    self.entrada_clave.focus_set()
                else:
                    self.sesion = resultado
                    self.mostrar_panel()
        except (ValueError, ErrorDatos) as error:
            self.estado.configure(text=str(error), fg=ROJO)

    def mostrar_panel(self):
        self.limpiar_pantalla()
        self.etiqueta(self.contenido, "IDENTIDAD VERIFICADA", 10, VERDE, FONDO, True).pack(anchor="w")
        self.etiqueta(self.contenido, f"Hola, {self.sesion['usuario']}.", 30, TEXTO, FONDO, True).pack(anchor="w", pady=(10, 5))
        self.etiqueta(self.contenido, "Tu sesión está activa.", 13, GRIS, FONDO).pack(anchor="w", pady=(0, 18))
        tarjeta = tk.Frame(self.contenido, bg="white", padx=26, pady=18)
        tarjeta.pack(fill="x")
        self.etiqueta(tarjeta, "✓  Acceso autorizado", 18, VERDE, negrita=True).pack(anchor="w")
        self.etiqueta(tarjeta, "Último acceso: " + datetime.now().strftime("%d/%m/%Y · %H:%M:%S"), 10, GRIS).pack(anchor="w", pady=(10, 24))
        self.etiqueta(tarjeta, "¿Qué se comprobó?", 13, negrita=True).pack(anchor="w")
        self.etiqueta(tarjeta, "Se calculó SHA-256 de la contraseña ingresada y se comparó\ncon el hash guardado para este usuario en users-db.json.", 10, GRIS).pack(anchor="w", pady=(10, 18))
        for titulo, clave in (("HASH GUARDADO EN JSON", "hash_guardado"), ("HASH CALCULADO AL INGRESAR", "hash_calculado")):
            self.etiqueta(tarjeta, titulo, 9, GRIS, negrita=True).pack(anchor="w", pady=(8, 5))
            valor = self.sesion[clave]
            tk.Label(tarjeta, text=valor[:32] + "\n" + valor[32:], font=("Consolas", 12),
                     justify="left", anchor="w", bg="#edf6f5", fg=VERDE, padx=12, pady=9).pack(fill="x")
        self.etiqueta(tarjeta, "RESULTADO: LOS DOS HASHES COINCIDEN", 10, VERDE, negrita=True).pack(anchor="w", pady=(18, 0))
        self.boton(self.contenido, "Cerrar sesión", self.mostrar_formulario).pack(anchor="w", pady=(16, 12))


def main():
    root = tk.Tk()
    Aplicacion(root)
    root.mainloop()


if __name__ == "__main__":
    main()
