import unittest

from utils.rsa import descrypt, encrypt, get_public_private_keys


class RSADidacticoTests(unittest.TestCase):
    def test_muestra_mensaje_cifrado_rsa(self):
        publica, privada, n = get_public_private_keys(67, 83, 4)
        original = "RSA"
        cifrado = [encrypt(publica, privada, n, ord(letra)) for letra in original]
        recuperado = "".join(
            chr(descrypt(publica, privada, n, numero)) for numero in cifrado
        )
        print(f"\n[TEST RSA] Texto: {original} | Cifrado: {cifrado}")
        self.assertEqual(recuperado, original)

    def test_cifra_y_descifra_un_entero(self):
        publica, privada, n = get_public_private_keys(67, 83, 4)
        original = ord("R")
        cifrado = encrypt(publica, privada, n, original)
        self.assertNotEqual(cifrado, original)
        self.assertEqual(descrypt(publica, privada, n, cifrado), original)

    def test_descifra_ejemplo_comentado_original(self):
        publica, privada, n = get_public_private_keys(67, 83, 4)
        secretos = [1058, 2597, 4955, 4201, 3162, 4343, 2754, 2497, 336, 2597]
        texto = "".join(chr(descrypt(publica, privada, n, item)) for item in secretos)
        self.assertEqual(texto, "HOLA MUNDO")

    def test_rechaza_mensaje_fuera_del_modulo(self):
        publica, privada, n = get_public_private_keys(67, 83, 4)
        with self.assertRaises(ValueError):
            encrypt(publica, privada, n, n)


if __name__ == "__main__":
    unittest.main()
