import json

def obtener_mensaje(filename="mensaje_oculto.json"):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("mensaje", "")

def save(data, filename="mensaje_oculto.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)