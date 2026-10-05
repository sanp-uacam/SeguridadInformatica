"""Persistencia local de usuarios en formato JSON."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def guardar_diccionario(datos: dict[str, str], nombre_archivo: str | Path) -> bool:
    """Guarda de forma atomica para evitar archivos parcialmente escritos."""

    destino = Path(nombre_archivo)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal: str | None = None
    try:
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=destino.parent, delete=False
        ) as archivo:
            temporal = archivo.name
            json.dump(datos, archivo, ensure_ascii=False, indent=4, sort_keys=True)
            archivo.write("\n")
        os.replace(temporal, destino)
        return True
    except (OSError, TypeError):
        if temporal and os.path.exists(temporal):
            os.unlink(temporal)
        return False


def cargar_diccionario(nombre_archivo: str | Path) -> dict[str, str]:
    """Carga la base de datos; devuelve un diccionario vacio si no existe."""

    origen = Path(nombre_archivo)
    if not origen.exists():
        return {}
    try:
        with origen.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        if not isinstance(datos, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in datos.items()
        ):
            raise ValueError("La base de usuarios no tiene el formato esperado")
        return datos
    except (OSError, json.JSONDecodeError, ValueError):
        return {}
