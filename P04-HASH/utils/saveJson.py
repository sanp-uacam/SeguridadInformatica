"""Persistencia en JSON y autenticación. La contraseña nunca se escribe al disco."""

import hmac
import json
import os
from pathlib import Path
import re
import tempfile

from .seguridad import generar_hash, reglas_contrasena, validar_usuario

RUTA_DATOS = Path(__file__).resolve().parent.parent / "users-db.json"


class ErrorDatos(Exception):
    """Un archivo ilegible no se trata como una base de datos vacía."""


class AlmacenUsuarios:
    def __init__(self, ruta=RUTA_DATOS):
        self.ruta = Path(ruta)

    def cargar(self):
        try:
            with self.ruta.open(encoding="utf-8") as archivo:
                usuarios = json.load(archivo)
        except FileNotFoundError:
            return {}
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ErrorDatos("No se pudo leer users-db.json. Revisa el archivo; no se sobrescribió.") from error
        if not isinstance(usuarios, dict):
            raise ErrorDatos("users-db.json debe contener un objeto con usuarios y hashes.")
        nombres = set()
        for nombre, valor in usuarios.items():
            if (not re.fullmatch(r"[A-Za-z0-9_]{3,20}", nombre)
                    or not isinstance(valor, str) or not re.fullmatch(r"[0-9a-f]{64}", valor)
                    or nombre.casefold() in nombres):
                raise ErrorDatos("users-db.json contiene un usuario o hash inválido, o nombres duplicados.")
            nombres.add(nombre.casefold())
        return usuarios

    def guardar(self, usuarios):
        # Se reemplaza el archivo únicamente cuando terminó de escribirse el JSON.
        temporal = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.ruta.parent,
                                             suffix=".tmp", delete=False) as archivo:
                temporal = Path(archivo.name)
                json.dump(usuarios, archivo, ensure_ascii=False, indent=4)
                archivo.write("\n")
                archivo.flush()
                os.fsync(archivo.fileno())
            os.replace(temporal, self.ruta)
        except OSError as error:
            raise ErrorDatos("No se pudo guardar users-db.json. Revisa los permisos de la carpeta.") from error
        finally:
            if temporal is not None and temporal.exists():
                temporal.unlink(missing_ok=True)

    def registrar(self, usuario, contrasena, confirmacion):
        usuario = usuario.strip()
        validar_usuario(usuario)
        errores = [regla for regla, cumple in reglas_contrasena(usuario, contrasena) if not cumple]
        if errores:
            raise ValueError("Revisa la contraseña: " + "; ".join(errores) + ".")
        if contrasena != confirmacion:
            raise ValueError("Las contraseñas no coinciden.")
        usuarios = self.cargar()
        if any(nombre.casefold() == usuario.casefold() for nombre in usuarios):
            raise ValueError("Ese nombre de usuario ya está registrado.")
        usuarios[usuario] = generar_hash(contrasena)
        self.guardar(usuarios)
        print(f"Registro guardado en: {self.ruta}")
        return usuario

    def autenticar(self, usuario, contrasena):
        usuarios = self.cargar()
        nombre = next((n for n in usuarios if n.casefold() == usuario.strip().casefold()), None)
        calculado = generar_hash(contrasena)
        guardado = usuarios[nombre] if nombre else "0" * 64
        # La comparación usa ambos hashes; no se descifra ni se recupera la clave.
        coincide = hmac.compare_digest(calculado, guardado)
        if nombre is None or not coincide:
            return None
        print("Acceso concedido: el hash calculado coincide con el almacenado.")
        return {"usuario": nombre, "hash_calculado": calculado, "hash_guardado": guardado}
