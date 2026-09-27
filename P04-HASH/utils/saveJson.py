import json
import re
from pathlib import Path


def guardar_diccionario(datos, nombre_archivo):
    ruta = Path(nombre_archivo)
    temporal = ruta.with_suffix('.tmp')
    try:
        with temporal.open('w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
            archivo.write('\n')
        temporal.replace(ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def cargar_diccionario(nombre_archivo):
    ruta = Path(nombre_archivo)
    if not ruta.exists():
        return {}
    try:
        with ruta.open(encoding='utf-8') as archivo:
            datos = json.load(archivo)
    except json.JSONDecodeError as error:
        raise ValueError('El archivo de usuarios contiene JSON inválido.') from error
    if not isinstance(datos, dict) or any(
        not isinstance(nombre, str) or not nombre.strip()
        or not isinstance(valor, str) or not re.fullmatch(r'[0-9a-f]{64}', valor)
        for nombre, valor in datos.items()
    ):
        raise ValueError('El archivo de usuarios no tiene el formato esperado.')
    return datos
