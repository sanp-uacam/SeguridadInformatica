
import os
import unittest

from hibrido_rsa_aes import (
    generar_par_claves_rsa,
    get_Msj_And_Key,
    decifrar_mensaje,
    Cifrado_AES_enviar_mensaje,
    _descifrar_aes_cbc,
    _derivar_iv_aes,
    AES_KEY_SIZE_BYTES,
    AES_BLOCK_SIZE_BYTES,
    IV_SIZE_BYTES,
)


class TestAlgoritmoHibrido(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Un solo par de claves RSA para todas las pruebas (es más rápido)
        cls.privada, cls.publica = generar_par_claves_rsa()


    # Caso bueno: cifrar y descifrar debe devolver el mensaje original
    def test_ciclo_completo_cifrado_descifrado(self):
        mensaje = "Hola, este es un mensaje de prueba para la práctica 2."

        paquete = get_Msj_And_Key(mensaje, self.publica)
        mensaje_recuperado = decifrar_mensaje(
            paquete.mensajeCifrado_AES,
            paquete.iv_cifrado_RSA,
            paquete.clave_aes_cifrada_RSA,
            self.privada,
        )

        self.assertEqual(mensaje, mensaje_recuperado)


    # El texto cifrado no debe ser igual ni contener el texto plano
    def test_mensaje_cifrado_no_es_texto_plano(self):
        mensaje = "informacion secreta 12345"
        paquete = get_Msj_And_Key(mensaje, self.publica)

        self.assertNotEqual(paquete.mensajeCifrado_AES, mensaje.encode())
        self.assertNotIn(mensaje.encode(), paquete.mensajeCifrado_AES)


    # Aleatoriedad: cifrar el mismo mensaje dos veces debe dar resultados distintos
    def test_cifrados_distintos_para_mismo_mensaje(self):
        mensaje = "mismo mensaje"
        paquete1 = get_Msj_And_Key(mensaje, self.publica)
        paquete2 = get_Msj_And_Key(mensaje, self.publica)

        self.assertNotEqual(paquete1.mensajeCifrado_AES, paquete2.mensajeCifrado_AES)
        self.assertNotEqual(paquete1.clave_aes_cifrada_RSA, paquete2.clave_aes_cifrada_RSA)


    # Mensajes largos (varios bloques AES) y mensajes vacíos
    def test_mensaje_largo(self):
        mensaje = "A" * 5000  # fuerza múltiples bloques de 16 bytes
        paquete = get_Msj_And_Key(mensaje, self.publica)
        recuperado = decifrar_mensaje(
            paquete.mensajeCifrado_AES,
            paquete.iv_cifrado_RSA,
            paquete.clave_aes_cifrada_RSA,
            self.privada,
        )
        self.assertEqual(mensaje, recuperado)

    def test_mensaje_vacio(self):
        mensaje = ""
        paquete = get_Msj_And_Key(mensaje, self.publica)
        recuperado = decifrar_mensaje(
            paquete.mensajeCifrado_AES,
            paquete.iv_cifrado_RSA,
            paquete.clave_aes_cifrada_RSA,
            self.privada,
        )
        self.assertEqual(mensaje, recuperado)

    def test_mensaje_con_unicode(self):
        mensaje = "Mensaje con acentos: ñáéíóú y emojis 🔒🔑"
        paquete = get_Msj_And_Key(mensaje, self.publica)
        recuperado = decifrar_mensaje(
            paquete.mensajeCifrado_AES,
            paquete.iv_cifrado_RSA,
            paquete.clave_aes_cifrada_RSA,
            self.privada,
        )
        self.assertEqual(mensaje, recuperado)


    # La función auxiliar Cifrado_AES_enviar_mensaje funciona sola
    def test_funcion_auxiliar_aes(self):
        clave_aes = os.urandom(AES_KEY_SIZE_BYTES)
        iv = os.urandom(IV_SIZE_BYTES)  # 32 bytes, como exige la práctica
        mensaje = "prueba de la función auxiliar"

        cifrado = Cifrado_AES_enviar_mensaje(mensaje, clave_aes, iv)
        descifrado = _descifrar_aes_cbc(cifrado, clave_aes, iv)

        self.assertEqual(mensaje, descifrado)


    # El IV real de AES se deriva correctamente del IV extendido
    def test_derivacion_iv_extendido_a_iv_aes(self):
        iv_extendido = os.urandom(IV_SIZE_BYTES)
        iv_aes = _derivar_iv_aes(iv_extendido)

        self.assertEqual(len(iv_aes), AES_BLOCK_SIZE_BYTES)
        self.assertEqual(iv_aes, iv_extendido[:AES_BLOCK_SIZE_BYTES])

        # Debe ser determinista: mismo IV extendido -> mismo IV derivado
        self.assertEqual(_derivar_iv_aes(iv_extendido), iv_aes)


    # Validaciones de seguridad: tamaños de IV/clave incorrectos
    def test_iv_invalido_lanza_error(self):
        clave_aes = os.urandom(AES_KEY_SIZE_BYTES)
        # Ahora el IV DEBE medir 32 bytes (requisito explícito del profesor);
        # cualquier otro tamaño (incluyendo el bloque "nativo" de AES de
        # 16 bytes) debe ser rechazado por la validación de la función.
        for tamano_invalido in (16, 24, 31, 33, 64):
            with self.assertRaises(ValueError):
                Cifrado_AES_enviar_mensaje(
                    "texto", clave_aes, os.urandom(tamano_invalido)
                )

    def test_clave_aes_invalida_lanza_error(self):
        clave_invalida = os.urandom(10)
        iv = os.urandom(AES_BLOCK_SIZE_BYTES)
        with self.assertRaises(ValueError):
            Cifrado_AES_enviar_mensaje("texto", clave_invalida, iv)


    # Descifrado con la clave privada equivocada debe fallar
    def test_descifrado_con_clave_privada_incorrecta_falla(self):
        otra_privada, _ = generar_par_claves_rsa()
        mensaje = "mensaje que solo el receptor legítimo debe leer"
        paquete = get_Msj_And_Key(mensaje, self.publica)

        with self.assertRaises(Exception):
            decifrar_mensaje(
                paquete.mensajeCifrado_AES,
                paquete.iv_cifrado_RSA,
                paquete.clave_aes_cifrada_RSA,
                otra_privada,  # clave privada que NO corresponde al par usado
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
