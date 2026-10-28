

import string

ESPECIALES = "!@#$%^&*()-_=+[]{};:'\",.<>/?\\|`~ "
LONGITUD_MINIMA = 8
LARGO_SECUENCIA = 3


def _tiene_secuencia(password, largo=LARGO_SECUENCIA):
    """Detecta secuencias ascendentes o descendentes: 'abc', '123', 'cba', '987'."""
    texto = password.lower()
    for i in range(len(texto) - largo + 1):
        bloque = texto[i:i + largo]

        # Solo se evaluan bloques 100% alfabeticos o 100% numericos
        if not (bloque.isalpha() or bloque.isdigit()):
            continue

        diferencias = {ord(bloque[j + 1]) - ord(bloque[j]) for j in range(largo - 1)}
        if diferencias == {1} or diferencias == {-1}:
            return True
    return False


def validar(password, username=""):
    """Regresa una lista con los mensajes de las reglas que NO se cumplieron.
    Lista vacia = contrasena valida."""
    alertas = []

    if len(password) < LONGITUD_MINIMA:
        alertas.append(f"Debe tener al menos {LONGITUD_MINIMA} caracteres.")

    if not any(c.isupper() for c in password):
        alertas.append("Debe incluir al menos una letra mayuscula.")

    if not any(c.islower() for c in password):
        alertas.append("Debe incluir al menos una letra minuscula.")

    if _tiene_secuencia(password):
        alertas.append("No debe contener secuencias alfabeticas o numericas (ej. abc, 123).")

    if not any(c in ESPECIALES for c in password):
        alertas.append("Debe incluir al menos un caracter especial (ej. ! @ # $ % & *).")

    if username and username.lower() in password.lower():
        alertas.append("No debe contener el nombre de usuario.")

    return alertas


def es_valida(password, username=""):
    return len(validar(password, username)) == 0


def fuerza(password):
    """Indicador simple de fuerza para mostrar en la interfaz."""
    puntos = 0
    if len(password) >= LONGITUD_MINIMA:
        puntos += 1
    if len(password) >= 12:
        puntos += 1
    if any(c.isupper() for c in password) and any(c.islower() for c in password):
        puntos += 1
    if any(c.isdigit() for c in password):
        puntos += 1
    if any(c in ESPECIALES for c in password):
        puntos += 1
    if _tiene_secuencia(password):
        puntos -= 1

    if puntos <= 2:
        return "Debil", "#f44336"
    if puntos <= 3:
        return "Media", "#ff9800"
    return "Fuerte", "#4CAF50"
