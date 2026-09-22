import os
import unittest

from cryptography.hazmat.primitives import serialization

from utils import Cifrado_AES_enviar_mensaje, decifrar_mensaje
from utils import generar_claves_rsa, get_Msj_And_Key


class CifradoHibridoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.publica, cls.privada = generar_claves_rsa()

    def test_muestra_mensaje_cifrado_hibrido(self):
        original = "Mensaje de prueba AES + RSA"
        sobre, cifrado = get_Msj_And_Key(self.publica, original)
        recuperado = decifrar_mensaje(cifrado, sobre, self.privada)
        print(f"\n[TEST HÍBRIDO] Texto: {original}")
        print(f"[TEST HÍBRIDO] Sobre RSA: {sobre.hex()}")
        print(f"[TEST HÍBRIDO] Cifrado AES + HMAC: {cifrado.hex()}")
        self.assertEqual(recuperado, original)

    def test_vuelta_completa_con_unicode(self):
        original = "Mensaje híbrido: áéíóú 🔐"
        sobre, cifrado = get_Msj_And_Key(self.publica, original)
        self.assertEqual(decifrar_mensaje(cifrado, sobre, self.privada), original)

    def test_mensaje_vacio(self):
        sobre, cifrado = get_Msj_And_Key(self.publica, "")
        self.assertEqual(decifrar_mensaje(cifrado, sobre, self.privada), "")

    def test_cada_cifrado_es_aleatorio(self):
        primero = get_Msj_And_Key(self.publica, "igual")
        segundo = get_Msj_And_Key(self.publica, "igual")
        self.assertNotEqual(primero, segundo)

    def test_detecta_modificacion_del_mensaje(self):
        sobre, cifrado = get_Msj_And_Key(self.publica, "íntegro")
        alterado = bytes([cifrado[0] ^ 1]) + cifrado[1:]
        with self.assertRaisesRegex(ValueError, "alterado"):
            decifrar_mensaje(alterado, sobre, self.privada)

    def test_detecta_modificacion_del_sobre_rsa(self):
        sobre, cifrado = get_Msj_And_Key(self.publica, "íntegro")
        alterado = bytes([sobre[0] ^ 1]) + sobre[1:]
        with self.assertRaises(ValueError):
            decifrar_mensaje(cifrado, alterado, self.privada)

    def test_otra_clave_privada_no_abre_el_sobre(self):
        sobre, cifrado = get_Msj_And_Key(self.publica, "secreto")
        _, otra_privada = generar_claves_rsa()
        with self.assertRaises(ValueError):
            decifrar_mensaje(cifrado, sobre, otra_privada)

    def test_acepta_claves_pem(self):
        publica_pem = self.publica.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        privada_pem = self.privada.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        sobre, cifrado = get_Msj_And_Key(publica_pem, "desde PEM")
        self.assertEqual(decifrar_mensaje(cifrado, sobre, privada_pem), "desde PEM")

    def test_auxiliar_aes_valida_tamanos(self):
        with self.assertRaisesRegex(ValueError, "IV"):
            Cifrado_AES_enviar_mensaje("mensaje", os.urandom(32), os.urandom(32))
        with self.assertRaisesRegex(ValueError, "clave"):
            Cifrado_AES_enviar_mensaje("mensaje", os.urandom(16), os.urandom(16))


if __name__ == "__main__":
    unittest.main()
