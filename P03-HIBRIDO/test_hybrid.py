import unittest

from rsa_aes_hybrid import (
    Cifrado_AES_enviar_mensaje,
    IV_BYTES,
    generar_par_claves_rsa,
    get_Msj_And_Key,
    decifrar_mensaje,
)


class PruebasAlgoritmoHibrido(unittest.TestCase):
    def setUp(self):
        self.privada, self.publica = generar_par_claves_rsa()

    def test_recupera_mensaje_ascii(self):
        mensaje = "Seguridad Informatica - Practica 2"
        paquete_rsa, cifrado_aes = get_Msj_And_Key(self.publica, mensaje)
        self.assertEqual(decifrar_mensaje(cifrado_aes, paquete_rsa, self.privada), mensaje)

    def test_recupera_unicode_y_multiples_bloques(self):
        mensaje = "Confidencial: autenticar, cifrar y verificar. " * 10 + "Mensaje final: ñáéíóú."
        paquete_rsa, cifrado_aes = get_Msj_And_Key(self.publica, mensaje)
        self.assertEqual(decifrar_mensaje(cifrado_aes, paquete_rsa, self.privada), mensaje)

    def test_iv_duplicado_es_rechazado_por_la_funcion_auxiliar(self):
        with self.assertRaises(ValueError):
            Cifrado_AES_enviar_mensaje("Hola", b"corto", b"x" * 32)

    def test_modificacion_del_ciphertext_no_se_descifra(self):
        paquete_rsa, cifrado_aes = get_Msj_And_Key(self.publica, "No modificar")
        alterado = bytearray(cifrado_aes)
        alterado[-1] ^= 1
        with self.assertRaises(ValueError):
            decifrar_mensaje(bytes(alterado), paquete_rsa, self.privada)


if __name__ == "__main__":
    unittest.main(verbosity=2)
