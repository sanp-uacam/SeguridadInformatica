# -*- coding: utf-8 -*-
"""
Pruebas unitarias del algoritmo híbrido RSA + AES.
Ejecutar con: python3 -m unittest pruebas_hibrido.py -v
"""

import unittest
from hibrido_rsa_aes import (
    generar_par_rsa,
    get_Msj_And_Key,
    decifrar_mensaje,
    Cifrado_AES_enviar_mensaje,
    _descifrar_aes,
)


class PruebasAlgoritmoHibrido(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Un solo par de claves para todas las pruebas (más rápido)
        cls.priv, cls.pub = generar_par_rsa(2048)

    def test_01_roundtrip_mensaje_corto(self):
        """El mensaje descifrado debe ser idéntico al original (caso típico)."""
        mensaje = b"Hola mundo"
        paquete = get_Msj_And_Key(mensaje, self.pub)
        recuperado = decifrar_mensaje(
            paquete["mensajeCifrado_AES"], paquete["iv_cifrado_RSA"],
            paquete["clave_cifrada_RSA"], self.priv
        )
        self.assertEqual(mensaje, recuperado)

    def test_02_roundtrip_mensaje_vacio(self):
        """Caso límite: mensaje de longitud 0."""
        mensaje = b""
        paquete = get_Msj_And_Key(mensaje, self.pub)
        recuperado = decifrar_mensaje(
            paquete["mensajeCifrado_AES"], paquete["iv_cifrado_RSA"],
            paquete["clave_cifrada_RSA"], self.priv
        )
        self.assertEqual(mensaje, recuperado)

    def test_03_roundtrip_mensaje_largo(self):
        """Mensaje mayor a un bloque AES (16 bytes) para validar el padding."""
        mensaje = ("Este es un mensaje deliberadamente largo para verificar "
                   "que el cifrado en modo CBC maneja correctamente varios "
                   "bloques y el relleno PKCS7. " * 5).encode()
        paquete = get_Msj_And_Key(mensaje, self.pub)
        recuperado = decifrar_mensaje(
            paquete["mensajeCifrado_AES"], paquete["iv_cifrado_RSA"],
            paquete["clave_cifrada_RSA"], self.priv
        )
        self.assertEqual(mensaje, recuperado)

    def test_04_iv_y_clave_son_aleatorios_en_cada_llamada(self):
        """Dos cifrados del mismo mensaje no deben producir el mismo texto cifrado."""
        mensaje = b"mensaje repetido"
        paquete1 = get_Msj_And_Key(mensaje, self.pub)
        paquete2 = get_Msj_And_Key(mensaje, self.pub)
        self.assertNotEqual(
            paquete1["mensajeCifrado_AES"], paquete2["mensajeCifrado_AES"]
        )
        self.assertNotEqual(
            paquete1["iv_cifrado_RSA"], paquete2["iv_cifrado_RSA"]
        )

    def test_05_clave_privada_incorrecta_falla(self):
        """Descifrar con una clave privada distinta debe fallar, no dar datos falsos."""
        otra_priv, _ = generar_par_rsa(2048)
        mensaje = b"dato confidencial"
        paquete = get_Msj_And_Key(mensaje, self.pub)
        with self.assertRaises(ValueError):
            decifrar_mensaje(
                paquete["mensajeCifrado_AES"], paquete["iv_cifrado_RSA"],
                paquete["clave_cifrada_RSA"], otra_priv
            )

    def test_06_mensaje_cifrado_alterado_falla(self):
        """Si un atacante modifica un byte del texto cifrado, el padding debe
        fallar (detección de manipulación) en vez de entregar datos corruptos
        silenciosamente."""
        mensaje = b"informacion sensible de la practica"
        paquete = get_Msj_And_Key(mensaje, self.pub)
        cifrado_alterado = bytearray(paquete["mensajeCifrado_AES"])
        cifrado_alterado[-1] ^= 0xFF  # se voltean los bits del último byte
        with self.assertRaises(ValueError):
            decifrar_mensaje(
                bytes(cifrado_alterado), paquete["iv_cifrado_RSA"],
                paquete["clave_cifrada_RSA"], self.priv
            )

    def test_07_funcion_auxiliar_cifrado_aes_es_determinista_con_mismo_iv(self):
        """Cifrado_AES_enviar_mensaje debe ser determinista si se reutiliza el
        mismo IV y clave (verifica que la función auxiliar es una envoltura
        correcta de AES-CBC)."""
        from Crypto.Random import get_random_bytes
        clave = get_random_bytes(32)
        iv = get_random_bytes(16)
        mensaje = b"prueba de determinismo"
        c1 = Cifrado_AES_enviar_mensaje(mensaje, clave, iv)
        c2 = Cifrado_AES_enviar_mensaje(mensaje, clave, iv)
        self.assertEqual(c1, c2)
        self.assertEqual(_descifrar_aes(c1, clave, iv), mensaje)


if __name__ == "__main__":
    unittest.main(verbosity=2)
