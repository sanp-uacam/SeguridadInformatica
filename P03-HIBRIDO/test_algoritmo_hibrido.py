"""Pruebas funcionales, vector conocido y rechazo de alteraciones."""
import secrets
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import algoritmo_hibrido as a


class PruebasHibrido(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pub, cls.priv = a.generar_claves_RSA()
        _, cls.otra_priv = a.generar_claves_RSA()

    def test_01_texto_normal(self):
        sobre, paquete = a.get_Msj_And_Key(self.pub, "Mensaje")
        self.assertEqual(a.decifrar_mensaje(paquete, sobre, self.priv), "Mensaje")

    def test_02_unicode(self):
        texto = "¡Hola, México! ñ áéíóú 🔐\nSegunda línea\x00"
        s, p = a.get_Msj_And_Key(self.pub, texto)
        self.assertEqual(a.decifrar_mensaje(p, s, self.priv), texto)

    def test_03_vacio(self):
        s, p = a.get_Msj_And_Key(self.pub, "")
        self.assertEqual(a.decifrar_mensaje(p, s, self.priv), "")
        self.assertEqual(len(p), 52)

    def test_04_limites_bloque(self):
        for n in (1, 15, 16, 17, 31, 32, 33):
            with self.subTest(longitud=n):
                s, p = a.get_Msj_And_Key(self.pub, "a" * n)
                self.assertEqual(a.decifrar_mensaje(p, s, self.priv), "a" * n)
                self.assertEqual(len(p), 36 + 16 * (n // 16 + 1))

    def test_05_mensaje_largo(self):
        texto = "abcd" * 250000
        s, p = a.get_Msj_And_Key(self.pub, texto)
        self.assertEqual(a.decifrar_mensaje(p, s, self.priv), texto)

    def test_06_aleatoriedad(self):
        s1, p1 = a.get_Msj_And_Key(self.pub, "igual")
        s2, p2 = a.get_Msj_And_Key(self.pub, "igual")
        self.assertNotEqual(s1, s2)
        self.assertNotEqual(p1, p2)

    def test_07_clave_incorrecta(self):
        s, p = a.get_Msj_And_Key(self.pub, "secreto")
        with self.assertRaisesRegex(a.ErrorDescifrado, "paquete inválido"):
            a.decifrar_mensaje(p, s, self.otra_priv)

    def test_08_manipulacion(self):
        s, p = a.get_Msj_And_Key(self.pub, "Mensaje")
        for campo in ("sobre", "version", "ciphertext", "hmac"):
            with self.subTest(campo=campo):
                sobre, paquete = bytearray(s), bytearray(p)
                if campo == "sobre":
                    sobre[10] ^= 1
                else:
                    paquete[{"version": 0, "ciphertext": 5, "hmac": -1}[campo]] ^= 1
                with self.assertRaises(a.ErrorDescifrado):
                    a.decifrar_mensaje(bytes(paquete), bytes(sobre), self.priv)

    def test_09_truncamiento_y_tipos(self):
        s, p = a.get_Msj_And_Key(self.pub, "Mensaje")
        for paquete, sobre in ((p[:-1], s), (b"", s), (p, s[:-1]), (None, s), (p, "x")):
            with self.subTest(paquete=type(paquete).__name__, longitud=len(sobre)):
                with self.assertRaises(a.ErrorDescifrado):
                    a.decifrar_mensaje(paquete, sobre, self.priv)

    def test_10_iv_y_clave_invalidos(self):
        for iv in (b"", secrets.token_bytes(32)):
            with self.assertRaises(ValueError):
                a.Cifrado_AES_enviar_mensaje("Mensaje", iv)
        with self.assertRaises(ValueError):
            a.Cifrado_AES_enviar_mensaje("Mensaje", secrets.token_bytes(16), b"corta")

    def test_11_auxiliar_dos_argumentos(self):
        iv = secrets.token_bytes(16)
        clave, cifrado = a.Cifrado_AES_enviar_mensaje("Mensaje", iv)
        self.assertEqual(len(clave), 32)
        d = Cipher(algorithms.AES(clave), modes.CBC(iv)).decryptor()
        self.assertEqual(d.update(cifrado) + d.finalize(), b"Mensaje" + b"\x09" * 9)

    def test_12_llamada_original_interactiva(self):
        with patch("builtins.input", return_value="Mensaje"):
            s, p = a.get_Msj_And_Key(self.pub)
        self.assertEqual(a.decifrar_mensaje(p, s, self.priv), "Mensaje")

    def test_13_vector_nist_aes256_cbc(self):
        # NIST SP 800-38A, F.2.5. Primer bloque, sin padding en este vector.
        clave = bytes.fromhex("603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4")
        iv = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
        plano = bytes.fromhex("6bc1bee22e409f96e93d7e117393172a")
        esperado = bytes.fromhex("f58c4c04d6e5f1ba779eabfb5f7bfbd6")
        # El vector NIST es binario. Se prueba el núcleo AES-CBC directamente.
        e = Cipher(algorithms.AES(clave), modes.CBC(iv)).encryptor()
        self.assertEqual(e.update(plano) + e.finalize(), esperado)

    def test_14_sobre_incluye_todo(self):
        s, _ = a.get_Msj_And_Key(self.pub, "Mensaje")
        self.assertEqual(len(s), 256)
        self.assertEqual(len(self.priv.decrypt(s, a._oaep())), 80)

    def test_15_integridad_antes_de_aes(self):
        s, p = a.get_Msj_And_Key(self.pub, "Mensaje")
        adulterado = p[:-1] + bytes([p[-1] ^ 1])
        with patch("algoritmo_hibrido.Cipher") as cipher:
            with self.assertRaises(a.ErrorDescifrado):
                a.decifrar_mensaje(adulterado, s, self.priv)
            cipher.assert_not_called()

    def test_16_paquetes_cruzados(self):
        s1, _ = a.get_Msj_And_Key(self.pub, "uno")
        _, p2 = a.get_Msj_And_Key(self.pub, "dos")
        with self.assertRaises(a.ErrorDescifrado):
            a.decifrar_mensaje(p2, s1, self.priv)

    def test_17_rechazo_padding_con_mac_valido(self):
        s, _ = a.get_Msj_And_Key(self.pub, "Mensaje")
        material = self.priv.decrypt(s, a._oaep())
        e = Cipher(algorithms.AES(material[:32]), modes.CBC(material[32:48])).encryptor()
        ct = e.update(b"A" * 16) + e.finalize()  # No termina con PKCS7 válido.
        mac = hmac.HMAC(material[48:], hashes.SHA256())
        mac.update(a.VERSION + s + ct)
        with self.assertRaises(a.ErrorDescifrado):
            a.decifrar_mensaje(a.VERSION + ct + mac.finalize(), s, self.priv)


if __name__ == "__main__":
    unittest.main(verbosity=2)
