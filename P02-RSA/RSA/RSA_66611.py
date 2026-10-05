def mcd(a, b):
    if b == 0:
        return a
    return mcd(b, a % b)


def calcularD(e, phi):
    d = 1
    while (d * e) % phi != 1:
        d += 1
    return d


def descifrar(c, d, n):
    m = 1
    # (c^d) % n
    for i in range(d):
        m = (m * c) % n
    return chr(m)


def descifrarMensaje(mensajeCifrado, d, n):
    mensajeDescifrado = []
    for c in mensajeCifrado:
        mensajeDescifrado.append(descifrar(c, d, n))
    return mensajeDescifrado


# Verifica que todos los caracteres se puedan usar en ASCII (32-126)
def esTextoValido(texto):
    for c in texto:
        if ord(c) < 32 or ord(c) > 126:
            return False
    return True


def main():
    p = 67
    q = 83

    n = p * q
    phi = (p - 1) * (q - 1)

    print("n = " + str(n))
    print("phi(n) = " + str(phi) + "\n")

    mensajeCifrado = [
        1058, 2597, 4955, 4201, 3162,
        4343, 2754, 2497, 336, 2597
    ]

    contador = 0
    encontrado = False

    e = 2
    while e < phi and not encontrado:

        if mcd(e, phi) != 1:
            e += 1
            continue  # ni se cuenta ni se prueba

        contador += 1
        d = calcularD(e, phi)

        print("Candidato #" + str(contador) + ": e = " + str(e) + ", d = " + str(d))

        intento = descifrarMensaje(mensajeCifrado, d, n)

        # imprimir texto descifrado
        print("Mensaje descifrado:")
        print("".join(intento) + "\n")

        # imprimir si el texto descifrado es válido (ASCII 32-126)
        if esTextoValido(intento):
            print("Funciona. Usamos e = " + str(e) + "\n")

            print("Clave pública: (" + str(e) + ", " + str(n) + ")")
            print("Clave privada: (" + str(d) + ", " + str(n) + ")")
            print("Mensaje cifrado:")
            for valor in mensajeCifrado:
                print(str(valor) + " ", end="")
            print("\n")

            print("Mensaje descifrado:")
            print("".join(intento) + "\n")

            encontrado = True
        else:
            print("No funciona (texto no legible).\n")

        e += 1


if __name__ == "__main__":
    main()