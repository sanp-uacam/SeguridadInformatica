import json
import os

def guardar_diccionario(datos, nombre_archivo):
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
        print(f"Datos guardados exitosamente en {nombre_archivo}")
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False

def cargar_diccionario(nombre_archivo):
    try:
        if not os.path.exists(nombre_archivo):
            print("El archivo no existe")
            return {}
            
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
        print(f"Datos cargados exitosamente desde {nombre_archivo}")
        return datos
    except Exception as e:
        print(f"Error al cargar: {e}")
        return {}

# Uso de las funciones
# mi_diccionario = {"clave": "valor", "numero": 42, "lista": [1, 2, 3]}
# guardar_diccionario(mi_diccionario, "users-db.json")
# datos_cargados = cargar_diccionario("users-db.json")
# print(datos_cargados)