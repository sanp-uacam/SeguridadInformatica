"""Reglas y operaciones de las cuentas de esta práctica."""
import hashlib
from pathlib import Path

from .saveJson import cargar_diccionario, guardar_diccionario

DATABASE = Path(__file__).resolve().parent.parent / 'users-db.json'


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def validar_registro(nombre, clave, confirmacion):
    errores = []
    nombre = nombre.strip()
    if not nombre:
        errores.append('Escribe un nombre de usuario.')
    if clave != confirmacion:
        errores.append('Las contraseñas no coinciden.')
    if len(clave) < 8:
        errores.append('Usa al menos 8 caracteres.')
    if not any(c.isupper() for c in clave) or not any(c.islower() for c in clave):
        errores.append('Incluye mayúsculas y minúsculas.')
    if not any(not c.isalnum() and not c.isspace() for c in clave):
        errores.append('Incluye un carácter especial, como #, ! o @.')
    if nombre and nombre.casefold() in clave.casefold():
        errores.append('La contraseña no puede contener tu nombre de usuario.')
    # Wilbert novelo ruiz: revisar también las secuencias en sentido inverso.
    secuencias = ('0123456789', 'abcdefghijklmnopqrstuvwxyz')
    clave_minuscula = clave.casefold()
    if any(cadena[i:i + 3] in clave_minuscula
           for serie in secuencias for cadena in (serie, serie[::-1])
           for i in range(len(cadena) - 2)):
        errores.append('Evita secuencias como 123, 321, abc o cba.')
    return errores


def registrar_usuario(nombre, clave, confirmacion, archivo=DATABASE):
    nombre = nombre.strip()
    errores = validar_registro(nombre, clave, confirmacion)
    if errores:
        raise ValueError('\n'.join(errores))
    usuarios = cargar_diccionario(archivo)
    if nombre in usuarios:
        raise ValueError('Ese usuario ya está registrado.')
    usuarios[nombre] = hash_password(clave)
    guardar_diccionario(usuarios, archivo)


def verificar_login(nombre, clave, archivo=DATABASE):
    nombre = nombre.strip()
    if not nombre or not clave:
        raise ValueError('Completa el usuario y la contraseña.')
    usuarios = cargar_diccionario(archivo)
    if nombre not in usuarios:
        raise ValueError('Usuario no encontrado.')
    if hash_password(clave) != usuarios[nombre]:
        raise ValueError('Contraseña incorrecta.')
    return nombre
