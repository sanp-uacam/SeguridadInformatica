# Pruebas del algoritmo hibrido
# se corren con:  python pruebas.py

import unittest

from Crypto.Random import get_random_bytes

import hibrido_rsa_aes as hib
from hibrido_rsa_aes import (
    Cifrado_AES_enviar_mensaje,
    Descifrado_AES_recibir_mensaje,
    decifrar_mensaje,
    generar_par_llaves,
    get_Msj_And_Key,
)


class PruebasHibrido(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # se generan una sola vez porque tardan
        cls.privada, cls.publica = generar_par_llaves()
        cls.otra_privada, cls.otra_publica = generar_par_llaves()

    def test_cifrar_y_descifrar(self):
        msj = "Mensaje de prueba para la practica 2."
        iv_rsa, ct = get_Msj_And_Key(self.publica, msj)
        self.assertEqual(decifrar_mensaje(ct, iv_rsa, self.privada), msj)

    def test_mensajes_de_distinto_tamano(self):
        # el vacio y el de 16 son los casos raros por el relleno
        for msj in ["", "a", "1234567890123456", "x" * 17, "y" * 1000]:
            with self.subTest(largo=len(msj)):
                iv_rsa, ct = get_Msj_And_Key(self.publica, msj)
                self.assertEqual(decifrar_mensaje(ct, iv_rsa, self.privada), msj)
                self.assertEqual(len(ct) % 16, 0)

    def test_acentos_y_emojis(self):
        msj = "Canción en español ñÑ áéíóú 你好 🔐"
        iv_rsa, ct = get_Msj_And_Key(self.publica, msj)
        self.assertEqual(decifrar_mensaje(ct, iv_rsa, self.privada), msj)

    def test_el_cifrado_no_trae_el_texto(self):
        iv_rsa, ct = get_Msj_And_Key(self.publica, "SECRETO")
        self.assertNotIn(b"SECRETO", ct)

    def test_cifrar_dos_veces_da_distinto(self):
        # como la clave y el IV son nuevos cada vez, no se repite la salida
        iv1, ct1 = get_Msj_And_Key(self.publica, "mismo mensaje")
        iv2, ct2 = get_Msj_And_Key(self.publica, "mismo mensaje")
        self.assertNotEqual(ct1, ct2)
        self.assertNotEqual(iv1, iv2)

    def test_la_clave_es_de_256_bits(self):
        get_Msj_And_Key(self.publica, "hola")
        self.assertEqual(len(hib.clave_actual), 32)

    def test_con_otra_clave_privada_no_abre(self):
        iv_rsa, ct = get_Msj_And_Key(self.publica, "confidencial")
        with self.assertRaises(ValueError):
            decifrar_mensaje(ct, iv_rsa, self.otra_privada)

    def test_si_alteran_el_mensaje_no_sale(self):
        # CBC no detecta siempre el cambio, pero el texto ya no se recupera
        original = "transferir 100 pesos"
        iv_rsa, ct = get_Msj_And_Key(self.publica, original)
        alterado = bytearray(ct)
        alterado[0] ^= 0xFF
        try:
            salida = decifrar_mensaje(bytes(alterado), iv_rsa, self.privada)
        except Exception:
            salida = None
        self.assertNotEqual(salida, original)

    def test_si_alteran_el_paquete_rsa_truena(self):
        iv_rsa, ct = get_Msj_And_Key(self.publica, "hola")
        alterado = bytearray(iv_rsa)
        alterado[0] ^= 0x01
        with self.assertRaises(ValueError):
            decifrar_mensaje(ct, bytes(alterado), self.privada)

    def test_funcion_auxiliar(self):
        clave = get_random_bytes(32)
        iv = get_random_bytes(32)
        ct = Cifrado_AES_enviar_mensaje("Mensaje", iv, clave)
        self.assertEqual(Descifrado_AES_recibir_mensaje(ct, iv, clave), "Mensaje")

    def test_cambiando_el_iv_cambia_todo(self):
        clave = get_random_bytes(32)
        ct1 = Cifrado_AES_enviar_mensaje("Mensaje", get_random_bytes(32), clave)
        ct2 = Cifrado_AES_enviar_mensaje("Mensaje", get_random_bytes(32), clave)
        self.assertNotEqual(ct1, ct2)

    def test_iv_muy_corto(self):
        with self.assertRaises(ValueError):
            Cifrado_AES_enviar_mensaje("Mensaje", b"corto", get_random_bytes(32))

    def test_clave_de_tamano_raro(self):
        with self.assertRaises(ValueError):
            Cifrado_AES_enviar_mensaje("Mensaje", get_random_bytes(32), b"1234")

    def test_usa_la_clave_de_la_sesion(self):
        # si no se le pasa clave, agarra la que dejo get_Msj_And_Key
        get_Msj_And_Key(self.publica, "primero")
        iv = get_random_bytes(32)
        ct = Cifrado_AES_enviar_mensaje("segundo mensaje", iv)
        self.assertEqual(Descifrado_AES_recibir_mensaje(ct, iv), "segundo mensaje")


if __name__ == "__main__":
    unittest.main(verbosity=2)
