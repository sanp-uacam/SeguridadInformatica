"""Funciones para leer y guardar el diccionario usuario: hash."""
import json
import os
from pathlib import Path
import re
import tempfile

ARCHIVO = Path(__file__).resolve().parents[1] / "users-db.json"


def leer_usuarios(ruta=ARCHIVO):
    ruta = Path(ruta)
    if not ruta.exists():
        return {}
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError("No se pudo leer el JSON. Revisa el archivo antes de continuar.") from error
    if not isinstance(datos, dict):
        raise ValueError("El JSON debe contener un diccionario de usuarios y hashes.")
    nombres = set()
    for usuario, huella in datos.items():
        if (not re.fullmatch(r"[a-zA-Z0-9_]{3,20}", usuario)
                or not isinstance(huella, str)
                or not re.fullmatch(r"[0-9a-f]{64}", huella)
                or usuario.casefold() in nombres):
            raise ValueError("El JSON tiene un usuario o un hash inválido, o usuarios repetidos.")
        nombres.add(usuario.casefold())
    print(f"Usuarios leídos desde: {ruta}")
    return datos


def escribir_usuarios(datos, ruta=ARCHIVO):
    ruta = Path(ruta)
    temporal = None
    try:
        # Se termina de escribir antes de reemplazar el archivo anterior.
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=ruta.parent,
                                         suffix=".tmp", delete=False) as archivo:
            temporal = Path(archivo.name)
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
            archivo.write("\n")
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, ruta)
    except OSError as error:
        raise ValueError("No se pudo guardar el registro. Revisa los permisos de la carpeta.") from error
    finally:
        if temporal is not None and temporal.exists():
            temporal.unlink()
    print(f"Registro guardado correctamente en: {ruta}")
