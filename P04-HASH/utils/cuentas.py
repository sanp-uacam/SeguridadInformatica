"""Validación, registro y comprobación de credenciales para la práctica."""
import hashlib
import hmac
import re

from .archivo_json import ARCHIVO, leer_usuarios, escribir_usuarios

REGLAS = (
    "8 caracteres como mínimo",
    "Una letra mayúscula y una minúscula",
    "Un símbolo, por ejemplo #, ! o @",
    "Sin secuencias como abc, cba, 123 o 321",
    "Sin el nombre de usuario dentro de la clave",
    "Sin espacios",
)


def sha256(texto):
    # SHA-256 recibe bytes y devuelve una huella de 64 caracteres hexadecimales.
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def hay_secuencia(clave):
    clave = clave.lower()
    alfabetos = ("abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnñopqrstuvwxyz", "0123456789")
    for posicion in range(len(clave) - 2):
        grupo = clave[posicion:posicion + 3]
        for alfabeto in alfabetos:
            if grupo in alfabeto or grupo in alfabeto[::-1]:
                return True
    return False


def revisar_clave(usuario, clave):
    nombre = usuario.strip().casefold()
    return (
        len(clave) >= 8,
        any(letra.isupper() for letra in clave) and any(letra.islower() for letra in clave),
        any(not letra.isalnum() and not letra.isspace() for letra in clave),
        not hay_secuencia(clave),
        bool(nombre) and nombre not in clave.casefold(),
        bool(clave) and not any(letra.isspace() for letra in clave),
    )


def buscar_nombre(datos, usuario):
    for nombre in datos:
        if nombre.casefold() == usuario.strip().casefold():
            return nombre
    return None


def registrar(usuario, clave, repeticion, ruta=ARCHIVO):
    usuario = usuario.strip()
    if not re.fullmatch(r"[a-zA-Z0-9_]{3,20}", usuario):
        raise ValueError("Usuario: usa entre 3 y 20 letras sin acentos, números o guion bajo.")
    if not all(revisar_clave(usuario, clave)):
        raise ValueError("La contraseña no cumple las reglas. Revisa la lista de la derecha.")
    if clave != repeticion:
        raise ValueError("La confirmación no coincide con la contraseña.")
    datos = leer_usuarios(ruta)
    if buscar_nombre(datos, usuario) is not None:
        raise ValueError("El usuario ya existe. Elige otro nombre.")
    datos[usuario] = sha256(clave)
    escribir_usuarios(datos, ruta)
    return usuario


def comprobar(usuario, clave, ruta=ARCHIVO):
    if not usuario.strip() or not clave:
        raise ValueError("Escribe tu usuario y tu contraseña.")
    datos = leer_usuarios(ruta)
    nombre = buscar_nombre(datos, usuario)
    calculado = sha256(clave)
    almacenado = datos[nombre] if nombre is not None else "0" * 64
    coincide = hmac.compare_digest(almacenado, calculado)
    if nombre is None or not coincide:
        print("Acceso rechazado: las credenciales no coinciden.")
        return None
    print("Acceso aceptado: los hashes SHA-256 coinciden.")
    return nombre, almacenado, calculado
