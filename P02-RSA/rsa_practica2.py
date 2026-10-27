# -*- coding: utf-8 -*-
"""
=============================================================================
 Practica 2 - Algoritmo RSA
 Asignatura: Seguridad Informatica
 Universidad Autonoma de Campeche - Facultad de Ingenieria

 Alumno: Kevin del Jesus Gonzalez Maas
-----------------------------------------------------------------------------
 Descripcion:
   Programa que reproduce paso a paso el algoritmo RSA con los datos de
   entrada de la practica (p = 67, q = 83), genera el par de claves
   (publica y privada) y descifra el mensaje proporcionado por el docente.

   Todas las operaciones aritmeticas relevantes (MCD, algoritmo extendido de
   Euclides, inverso multiplicativo y exponenciacion modular) se implementaron
   de forma explicita para poder documentar el procedimiento y compararlo
   con el desarrollo manual.

 Uso:
   python3 rsa_practica2.py
=============================================================================
"""

# ---------------------------------------------------------------------------
# DATOS DE ENTRADA DE LA PRACTICA
# ---------------------------------------------------------------------------
P = 67
Q = 83
POSICION_E = 4  # Se debe tomar el CUARTO candidato valido de e

CRIPTOGRAMA = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]


# ---------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------
def mcd(a, b):
    """Maximo comun divisor por el algoritmo de Euclides (version iterativa)."""
    while b != 0:
        a, b = b, a % b
    return a


def euclides_extendido(a, b):
    """
    Algoritmo extendido de Euclides.
    Devuelve la terna (g, x, y) tal que:  a*x + b*y = g = mcd(a, b)
    """
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = euclides_extendido(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return (g, x, y)


def inverso_multiplicativo(e, phi):
    """
    Calcula d = e^-1 (mod phi) usando el algoritmo extendido de Euclides.
    Se verifica que exista el inverso (mcd(e, phi) == 1).
    """
    g, x, _ = euclides_extendido(e, phi)
    if g != 1:
        raise ValueError("No existe inverso multiplicativo: mcd(e, phi) != 1")
    return x % phi


def exponenciacion_modular(base, exponente, modulo):
    """
    Exponenciacion modular rapida (metodo de cuadrados sucesivos).
    Equivale a (base ** exponente) % modulo, pero sin numeros gigantes.
    """
    resultado = 1
    base = base % modulo
    while exponente > 0:
        if exponente & 1:              # bit menos significativo == 1
            resultado = (resultado * base) % modulo
        base = (base * base) % modulo  # se eleva la base al cuadrado
        exponente >>= 1                # se desplaza al siguiente bit
    return resultado


def buscar_candidatos_e(phi, cantidad):
    """
    Recorre los enteros e en el rango 1 < e < phi y conserva aquellos que
    cumplen mcd(e, phi) = 1. Devuelve los primeros 'cantidad' candidatos.
    """
    candidatos = []
    e = 2
    while len(candidatos) < cantidad and e < phi:
        if mcd(e, phi) == 1:
            candidatos.append(e)
        e += 1
    return candidatos


def linea(caracter="=", ancho=68):
    print(caracter * ancho)


# ---------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    linea()
    print(" PRACTICA 2 - ALGORITMO RSA")
    print(" Seguridad Informatica | Facultad de Ingenieria - UACAM")
    print(" Alumno: Kevin del Jesus Gonzalez Maas")
    linea()

    # --- Datos de entrada ---------------------------------------------------
    print("\nDATOS DE ENTRADA")
    print("  p = %d" % P)
    print("  q = %d" % Q)

    # --- Paso 1: calcular n -------------------------------------------------
    n = P * Q
    print("\nPASO 1: Calcular n")
    print("  n = p * q = %d * %d = %d" % (P, Q, n))

    # --- Paso 2: calcular phi(n) -------------------------------------------
    phi = (P - 1) * (Q - 1)
    print("\nPASO 2: Calcular phi(n)")
    print("  phi(n) = (p-1)*(q-1) = %d * %d = %d" % (P - 1, Q - 1, phi))

    # --- Paso 3: elegir e ---------------------------------------------------
    print("\nPASO 3: Elegir e (clave publica)")
    print("  Condiciones: 1 < e < phi(n)   y   mcd(e, phi(n)) = 1")
    print("  Candidatos probados:")
    print("  %-6s %-10s %-12s %s" % ("e", "mcd", "Valido", "Observacion"))
    e = None
    encontrados = 0
    for cand in range(2, 20):
        g = mcd(cand, phi)
        valido = (g == 1)
        obs = ""
        if valido:
            encontrados += 1
            obs = "candidato #%d" % encontrados
            if encontrados == POSICION_E:
                e = cand
                obs += "  <-- SELECCIONADO"
        print("  %-6d %-10d %-12s %s" % (cand, g, "SI" if valido else "NO", obs))
        if e is not None:
            break
    print("\n  e = %d  (cuarto candidato valido)" % e)

    # --- Paso 4: calcular d -------------------------------------------------
    print("\nPASO 4: Calcular d (clave privada)")
    g, x, y = euclides_extendido(e, phi)
    d = inverso_multiplicativo(e, phi)
    print("  Algoritmo extendido de Euclides sobre (e, phi(n)) = (%d, %d)" % (e, phi))
    print("  Identidad de Bezout: %d*(%d) + %d*(%d) = %d" % (e, x, phi, y, g))
    print("  d = %d mod %d = %d" % (x, phi, d))
    print("  Verificacion: e * d mod phi(n) = %d * %d mod %d = %d"
          % (e, d, phi, (e * d) % phi))

    # --- Claves generadas ---------------------------------------------------
    print("\nCLAVES GENERADAS")
    print("  Clave publica  KU = (e, n) = (%d, %d)" % (e, n))
    print("  Clave privada  KR = (d, n) = (%d, %d)" % (d, n))

    # --- Paso 5: descifrar --------------------------------------------------
    print("\nPASO 5: Descifrar el mensaje con la clave privada")
    print("  Formula:  M = C^d mod n = C^%d mod %d\n" % (d, n))
    print("  %-4s %-10s %-14s %-8s %s" % ("#", "C", "M = C^d mod n", "ASCII", "Verif."))
    linea("-")

    mensaje = ""
    for i, c in enumerate(CRIPTOGRAMA, start=1):
        m = exponenciacion_modular(c, d, n)
        # Verificacion cruzada: se vuelve a cifrar M con la clave publica
        verificacion = "OK" if exponenciacion_modular(m, e, n) == c else "ERROR"
        caracter = chr(m)
        mensaje += caracter
        mostrado = "(espacio)" if caracter == " " else caracter
        print("  %-4d %-10d %-14d %-8s %s" % (i, c, m, mostrado, verificacion))

    linea("-")
    print("\nMENSAJE DESCIFRADO: \"%s\"" % mensaje)
    print("Codigos ASCII: %s" % ", ".join(str(ord(ch)) for ch in mensaje))

    # --- Comprobacion final: recifrar el mensaje completo -------------------
    recifrado = [exponenciacion_modular(ord(ch), e, n) for ch in mensaje]
    print("\nCOMPROBACION FINAL (se vuelve a cifrar con la clave publica)")
    print("  Criptograma original : %s" % CRIPTOGRAMA)
    print("  Criptograma obtenido : %s" % recifrado)
    print("  Coinciden: %s" % ("SI" if recifrado == CRIPTOGRAMA else "NO"))
    linea()


if __name__ == "__main__":
    main()
