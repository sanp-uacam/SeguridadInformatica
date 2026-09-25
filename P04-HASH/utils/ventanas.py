"""Interfaz de escritorio con pestañas. Usa solamente Tkinter y ttk."""
from datetime import datetime
import tkinter as tk
from tkinter import ttk

from . import cuentas
from .archivo_json import ARCHIVO

ALUMNO = "Kevin Del Jesus Gonzalez Maas"
FONDO = "#f5f3f8"
TINTA = "#302840"
MORADO = "#6950a1"
GRIS = "#716a7c"
VERDE = "#28735c"
ROJO = "#aa3548"


class VentanaAcceso:
    def __init__(self, ventana, ruta=ARCHIVO):
        self.ventana = ventana
        self.ruta = ruta
        self.sesion = None
        ventana.title("Práctica HASH | " + ALUMNO)
        ventana.geometry("960x680")
        ventana.minsize(940, 660)
        ventana.configure(bg=FONDO)
        estilo = ttk.Style(ventana)
        estilo.theme_use("clam")
        estilo.configure("TNotebook", background=FONDO, borderwidth=0)
        estilo.configure("TNotebook.Tab", padding=(26, 10), font=("Segoe UI", 11), background="#e7e1ef", foreground=GRIS)
        estilo.map("TNotebook.Tab", background=[("selected", "white")], foreground=[("selected", MORADO)])
        cabecera = tk.Frame(ventana, bg=MORADO, padx=28, pady=18)
        cabecera.pack(fill="x")
        self.texto(cabecera, "CONTROL DE ACCESO", 20, "white", MORADO, True).pack(anchor="w")
        self.texto(cabecera, "Seguridad Informática  /  Práctica de funciones hash", 10, "#eee9f8", MORADO).pack(anchor="w", pady=(4, 0))
        pie = tk.Frame(ventana, bg=FONDO, padx=28, pady=13)
        pie.pack(side="bottom", fill="x")
        self.texto(pie, ALUMNO, 10, GRIS, FONDO).pack(side="left")
        self.texto(pie, "Python + Tkinter", 9, GRIS, FONDO).pack(side="right")
        self.cuerpo = tk.Frame(ventana, bg=FONDO)
        self.cuerpo.pack(fill="both", expand=True, padx=28, pady=20)
        self.mostrar_acceso()

    @staticmethod
    def texto(padre, contenido, tam=10, color=TINTA, fondo="white", negrita=False):
        return tk.Label(padre, text=contenido, font=("Segoe UI", tam, "bold" if negrita else "normal"),
                        fg=color, bg=fondo, anchor="w", justify="left")

    @staticmethod
    def boton(padre, titulo, accion, secundario=False):
        return tk.Button(padre, text=titulo, command=accion, bg="#ede7f5" if secundario else MORADO,
                         fg=MORADO if secundario else "white", activebackground="#d6c9ea",
                         activeforeground=TINTA, font=("Segoe UI", 11, "bold"), relief="flat",
                         borderwidth=0, padx=20, pady=10, cursor="hand2")

    def entrada(self, padre, titulo, variable, secreta=False):
        self.texto(padre, titulo, negrita=True).pack(anchor="w", pady=(9, 4))
        campo = tk.Entry(padre, textvariable=variable, show="*" if secreta else "", font=("Segoe UI", 11),
                         fg=TINTA, bg="#faf9fc", relief="flat", highlightthickness=1,
                         highlightbackground="#d9d2e4", highlightcolor=MORADO)
        campo.pack(fill="x", ipady=7)
        return campo

    def vaciar_cuerpo(self):
        self.ventana.unbind("<Return>")
        for elemento in self.cuerpo.winfo_children():
            elemento.destroy()

    def mostrar_acceso(self, usuario="", aviso=""):
        self.vaciar_cuerpo()
        self.sesion = None
        self.pestanas = ttk.Notebook(self.cuerpo)
        self.pestanas.pack(fill="both", expand=True)
        acceso = tk.Frame(self.pestanas, bg="white", padx=24, pady=18)
        registro = tk.Frame(self.pestanas, bg="white", padx=24, pady=18)
        self.pestanas.add(acceso, text="Iniciar sesión")
        self.pestanas.add(registro, text="Registrar usuario")
        self.acceso_usuario = tk.StringVar(value=usuario)
        self.acceso_clave = tk.StringVar()
        formulario = tk.Frame(acceso, bg="white")
        formulario.pack(side="left", fill="both", expand=True, padx=(0, 32))
        self.texto(formulario, "Bienvenido", 23, negrita=True).pack(anchor="w", pady=(0, 4))
        self.texto(formulario, "Ingresa con una cuenta registrada.", color=GRIS).pack(anchor="w")
        self.campo_usuario = self.entrada(formulario, "Usuario", self.acceso_usuario)
        self.campo_clave = self.entrada(formulario, "Contraseña", self.acceso_clave, True)
        visible = tk.BooleanVar()
        tk.Checkbutton(formulario, text="Ver contraseña", variable=visible, bg="white", fg=GRIS,
                       activebackground="white", command=lambda: self.campo_clave.configure(show="" if visible.get() else "*")).pack(anchor="w", pady=7)
        self.aviso_acceso = self.texto(formulario, aviso, color=VERDE)
        self.aviso_acceso.configure(wraplength=400)
        self.aviso_acceso.pack(fill="x", pady=(0, 10))
        botones = tk.Frame(formulario, bg="white")
        botones.pack(fill="x")
        self.boton(botones, "Entrar", self.entrar).pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.boton(botones, "Limpiar", self.limpiar, True).pack(side="left")
        resumen = tk.Frame(acceso, bg="#f0ebf7", padx=20, pady=20, width=320)
        resumen.pack(side="right", fill="y")
        resumen.pack_propagate(False)
        self.texto(resumen, "¿Cómo se verifica?", 15, MORADO, "#f0ebf7", True).pack(anchor="w")
        for titulo, detalle in (("01  Usuario", "Se busca tu registro en el JSON."),
                                ("02  Contraseña", "Se calcula su huella SHA-256."),
                                ("03  Comparación", "Si los hashes coinciden, entras.")):
            self.texto(resumen, titulo, 11, TINTA, "#f0ebf7", True).pack(anchor="w", pady=(22, 5))
            self.texto(resumen, detalle, 10, GRIS, "#f0ebf7").pack(anchor="w")
        self.preparar_registro(registro)
        self.pestanas.bind("<<NotebookTabChanged>>", self.cambiar_pestana)
        self.ventana.bind("<Return>", self.enviar_actual)
        self.campo_usuario.focus_set()

    def preparar_registro(self, panel):
        self.registro_usuario = tk.StringVar()
        self.registro_clave = tk.StringVar()
        self.repeticion = tk.StringVar()
        campos = tk.Frame(panel, bg="white")
        campos.pack(side="left", fill="both", expand=True, padx=(0, 28))
        self.texto(campos, "Nueva cuenta", 21, negrita=True).pack(anchor="w")
        self.texto(campos, "Elige tu usuario y confirma la contraseña.", color=GRIS).pack(anchor="w", pady=(3, 0))
        self.entrada(campos, "Usuario", self.registro_usuario)
        self.entrada(campos, "Contraseña", self.registro_clave, True)
        self.entrada(campos, "Repetir contraseña", self.repeticion, True)
        self.aviso_registro = self.texto(campos, "", color=ROJO)
        self.aviso_registro.configure(wraplength=400)
        self.aviso_registro.pack(fill="x", pady=(9, 8))
        self.boton(campos, "Guardar cuenta", self.guardar).pack(fill="x")
        reglas = tk.Frame(panel, bg="#f8f5ed", padx=18, pady=18, width=330)
        reglas.pack(side="right", fill="y")
        reglas.pack_propagate(False)
        self.texto(reglas, "Requisitos de la clave", 14, TINTA, "#f8f5ed", True).pack(anchor="w", pady=(0, 12))
        self.lista_reglas = []
        for regla in cuentas.REGLAS:
            etiqueta = self.texto(reglas, "• " + regla, 10, GRIS, "#f8f5ed")
            etiqueta.configure(wraplength=285)
            etiqueta.pack(fill="x", pady=6)
            self.lista_reglas.append(etiqueta)
        self.registro_usuario.trace_add("write", self.marcar_reglas)
        self.registro_clave.trace_add("write", self.marcar_reglas)

    def marcar_reglas(self, *_):
        estados = cuentas.revisar_clave(self.registro_usuario.get(), self.registro_clave.get())
        for etiqueta, regla, cumple in zip(self.lista_reglas, cuentas.REGLAS, estados):
            etiqueta.configure(text=("✓ " if cumple else "• ") + regla, fg=VERDE if cumple else GRIS)

    def cambiar_pestana(self, _=None):
        self.acceso_clave.set("")
        self.registro_clave.set("")
        self.repeticion.set("")

    def enviar_actual(self, _=None):
        if self.pestanas.index(self.pestanas.select()) == 0:
            self.entrar()
        else:
            self.guardar()

    def limpiar(self):
        self.acceso_usuario.set("")
        self.acceso_clave.set("")
        self.aviso_acceso.configure(text="")
        self.campo_usuario.focus_set()

    def entrar(self):
        try:
            sesion = cuentas.comprobar(self.acceso_usuario.get(), self.acceso_clave.get(), self.ruta)
        except ValueError as error:
            self.aviso_acceso.configure(text=str(error), fg=ROJO)
            return
        self.acceso_clave.set("")
        if sesion is None:
            self.aviso_acceso.configure(text="Usuario o contraseña incorrectos.", fg=ROJO)
            return
        self.sesion = sesion
        self.mostrar_sesion()

    def guardar(self):
        try:
            nombre = cuentas.registrar(self.registro_usuario.get(), self.registro_clave.get(),
                                       self.repeticion.get(), self.ruta)
        except ValueError as error:
            self.aviso_registro.configure(text=str(error))
            return
        self.registro_clave.set("")
        self.repeticion.set("")
        self.mostrar_acceso(nombre, "Cuenta guardada. Ya puedes entrar.")

    def mostrar_sesion(self):
        self.vaciar_cuerpo()
        nombre, guardado, calculado = self.sesion
        tarjeta = tk.Frame(self.cuerpo, bg="white", padx=28, pady=24)
        tarjeta.pack(fill="both", expand=True)
        self.texto(tarjeta, "SESIÓN INICIADA", 10, VERDE, negrita=True).pack(anchor="w")
        self.texto(tarjeta, f"Bienvenido, {nombre}", 26, negrita=True).pack(anchor="w", pady=(10, 8))
        self.texto(tarjeta, "Identidad comprobada mediante SHA-256.", 12, GRIS).pack(anchor="w")
        self.texto(tarjeta, "Acceso: " + datetime.now().strftime("%d/%m/%Y  %H:%M:%S"), color=GRIS).pack(anchor="w", pady=(10, 20))
        self.texto(tarjeta, "Comprobación del acceso", 13, negrita=True).pack(anchor="w", pady=(0, 8))
        for etiqueta, dato in (("Usuario encontrado", nombre), ("Archivo consultado", "users-db.json"),
                               ("Resultado", "El hash ingresado coincide con el guardado")):
            fila = tk.Frame(tarjeta, bg="#f6f3fa", padx=12, pady=8)
            fila.pack(fill="x", pady=2)
            self.texto(fila, etiqueta, 10, GRIS, "#f6f3fa").pack(side="left")
            self.texto(fila, dato, 10, TINTA, "#f6f3fa", True).pack(side="right")
        acciones = tk.Frame(tarjeta, bg="white")
        acciones.pack(fill="x", pady=(22, 0))
        self.boton(acciones, "Cerrar sesión", self.mostrar_acceso).pack(side="left")
        self.boton(acciones, "Consultar hashes", self.ver_hashes, True).pack(side="right")

    def ver_hashes(self):
        detalle = tk.Toplevel(self.ventana)
        detalle.title("Comparación SHA-256")
        detalle.geometry("720x320")
        detalle.configure(bg="white")
        detalle.transient(self.ventana)
        detalle.grab_set()
        for titulo, huella in (("Hash almacenado en JSON", self.sesion[1]), ("Hash calculado al ingresar", self.sesion[2])):
            self.texto(detalle, titulo, 11, MORADO, negrita=True).pack(anchor="w", padx=24, pady=(20, 8))
            campo = tk.Entry(detalle, font=("Consolas", 10), relief="flat", readonlybackground="#f2eef8", fg=TINTA)
            campo.insert(0, huella)
            campo.configure(state="readonly")
            campo.pack(fill="x", padx=24, ipady=9)
        self.texto(detalle, "Los dos valores coinciden. La contraseña no se guarda en el archivo.", color=VERDE).pack(anchor="w", padx=24, pady=18)
        self.boton(detalle, "Volver", detalle.destroy, True).pack(anchor="e", padx=24)
        return detalle


def abrir_programa():
    ventana = tk.Tk()
    VentanaAcceso(ventana)
    ventana.mainloop()
