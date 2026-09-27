"""Pruebas ejecutables: python -m unittest -v."""
import secrets
import unittest
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from hibrido import (AlgoritmoHibrido, get_Msj_And_Key, decifrar_mensaje,
                     Cifrado_AES_enviar_mensaje, _oaep, _iv_cbc)


class PruebasHibrido(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.privada = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        cls.publica = cls.privada.public_key()
        cls.otra = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def envio(self, texto="Mensaje de prueba"):
        return get_Msj_And_Key(self.publica, texto)

    def comprobar_texto(self, texto):
        sobre, cifrado = self.envio(texto)
        self.assertEqual(decifrar_mensaje(cifrado, sobre, self.privada), texto)

    def test_01_mensaje_basico(self):
        self.comprobar_texto("Mensaje")

    def test_02_unicode(self):
        self.comprobar_texto("¡México! áéíóú, ñ, 中文, 🔐\nSegunda línea")

    def test_03_mensaje_vacio(self):
        self.comprobar_texto("")

    def test_04_limites_bloque(self):
        for n in (1, 15, 16, 17, 31, 32, 33):
            with self.subTest(n=n):
                self.comprobar_texto("x" * n)

    def test_05_mensaje_largo(self):
        self.comprobar_texto("a" * 100000)

    def test_06_aleatoriedad(self):
        a, b = self.envio(), self.envio()
        self.assertNotEqual(a[0], b[0])
        self.assertNotEqual(a[1], b[1])

    def test_07_clave_incorrecta(self):
        sobre, cifrado = self.envio()
        with self.assertRaisesRegex(ValueError, "No se pudo"):
            decifrar_mensaje(cifrado, sobre, self.otra)

    def test_08_manipulacion(self):
        sobre, cifrado = self.envio()
        for parte in ("sobre", "cifrado", "etiqueta"):
            with self.subTest(parte=parte):
                s, c = bytearray(sobre), bytearray(cifrado)
                if parte == "sobre":
                    s[0] ^= 1
                else:
                    c[0 if parte == "cifrado" else -1] ^= 1
                with self.assertRaisesRegex(ValueError, "No se pudo"):
                    decifrar_mensaje(bytes(c), bytes(s), self.privada)

    def test_09_truncamientos(self):
        sobre, cifrado = self.envio()
        for s, c in ((sobre[:-1], cifrado), (sobre, cifrado[:-1]), (sobre, b"")):
            with self.subTest(longitudes=(len(s), len(c))):
                with self.assertRaises(ValueError):
                    decifrar_mensaje(c, s, self.privada)

    def test_10_mezcla_sesiones(self):
        sobre, _ = self.envio()
        _, cifrado = self.envio()
        with self.assertRaises(ValueError):
            decifrar_mensaje(cifrado, sobre, self.privada)

    def test_11_formato_y_descifrado_independiente(self):
        sobre, cifrado = self.envio("Mensaje")
        paquete = self.privada.decrypt(sobre, _oaep())
        self.assertEqual(len(sobre), 384)
        self.assertEqual(len(paquete), 100)
        self.assertEqual(paquete[:4], b"P2H1")
        clave, material = paquete[4:36], paquete[36:68]
        d = Cipher(algorithms.AES(clave), modes.CBC(_iv_cbc(material))).decryptor()
        self.assertEqual(d.update(cifrado[:-32]) + d.finalize(), b"Mensaje" + b"\x09" * 9)

    def test_12_auxiliar_y_reuso(self):
        contexto = AlgoritmoHibrido()
        iv = secrets.token_bytes(32)
        self.assertEqual(len(contexto.Cifrado_AES_enviar_mensaje("Mensaje", iv)), 48)
        with self.assertRaises(ValueError):
            contexto.Cifrado_AES_enviar_mensaje("Otro", iv)
        self.assertEqual(len(Cifrado_AES_enviar_mensaje("Mensaje", secrets.token_bytes(32))), 48)

    def test_13_entradas_invalidas(self):
        for iv in (b"", b"x" * 16, "x" * 32):
            with self.subTest(iv=iv):
                with self.assertRaises(ValueError):
                    AlgoritmoHibrido().Cifrado_AES_enviar_mensaje("Mensaje", iv)
        with self.assertRaises(TypeError):
            self.envio(123)
        with self.assertRaises(ValueError):
            get_Msj_And_Key("clave inválida", "Mensaje")

    def test_14_firma_original_por_teclado(self):
        with patch("builtins.input", return_value="Mensaje interactivo"):
            sobre, cifrado = get_Msj_And_Key(self.publica)
        self.assertEqual(decifrar_mensaje(cifrado, sobre, self.privada), "Mensaje interactivo")

    def test_15_receptor_independiente(self):
        sobre, cifrado = AlgoritmoHibrido().get_Msj_And_Key(self.publica, "Independiente")
        self.assertEqual(AlgoritmoHibrido().decifrar_mensaje(cifrado, sobre, self.privada), "Independiente")


if __name__ == "__main__":
    unittest.main(verbosity=2)
