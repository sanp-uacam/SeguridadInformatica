import json
import os


def normalizar_usuarios(datos):
    """Devuelve los usuarios como {"usuario": "hash"}."""
    pares = []

    if isinstance(datos, list):
        for usuario in datos:
            if not isinstance(usuario, dict):
                continue

            # Compatibilidad con el formato estructurado anterior.
            if "username" in usuario or "usuario" in usuario:
                username = usuario.get("username", usuario.get("usuario", ""))
                password_hash = usuario.get(
                    "password_hash",
                    usuario.get("password", usuario.get("contraseña", ""))
                )
                pares.append((username, password_hash))
            else:
                # Formato actual: un único par usuario: contraseña por objeto.
                pares.extend(usuario.items())
    elif isinstance(datos, dict):
        # Compatibilidad con la base anterior: {"usuario": "hash", ...}.
        pares.extend(datos.items())

    usuarios = {}
    for username, password_hash in pares:
        normalized_username = str(username).strip().casefold()
        if (
            normalized_username
            and isinstance(password_hash, str)
            and password_hash
        ):
            # El primer registro gana si el formato anterior tenía duplicados.
            usuarios.setdefault(normalized_username, password_hash)

    return usuarios


def guardar_usuarios(datos, nombre_archivo):
    """Guarda todos los usuarios dentro de un único objeto JSON."""
    try:
        usuarios = normalizar_usuarios(datos)
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(usuarios, archivo, ensure_ascii=False, indent=4)
        print(f"Datos guardados exitosamente en {nombre_archivo}")
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False


def cargar_usuarios(nombre_archivo):
    """Carga usuarios y garantiza que el resultado siempre sea un diccionario."""
    try:
        if not os.path.exists(nombre_archivo):
            print("El archivo no existe")
            return {}
            
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
        print(f"Datos cargados exitosamente desde {nombre_archivo}")
        return normalizar_usuarios(datos)
    except Exception as e:
        print(f"Error al cargar: {e}")
        return {}


# Alias para no romper otros módulos que todavía usan los nombres anteriores.
guardar_diccionario = guardar_usuarios
cargar_diccionario = cargar_usuarios

# Uso de las funciones
# mi_diccionario = {"clave": "valor", "numero": 42, "lista": [1, 2, 3]}
# guardar_diccionario(mi_diccionario, "users-db.json")
# datos_cargados = cargar_diccionario("users-db.json")
# print(datos_cargados)
