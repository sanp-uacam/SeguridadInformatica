import base64

import aes
import rsa


def _b64(data: bytes) -> str:
	return base64.b64encode(data).decode("ascii")


def _unb64(data: str) -> bytes:
	return base64.b64decode(data.encode("ascii"))


def get_Msj_And_Key(RSA_Publica, mensaje: str | None = None) -> dict[str, str]:
	if mensaje is None:
		mensaje = input("Mensaje: ")
	clave_aes = aes.get_key()
	iv = aes.get_iv()
	return {
		"clave_cifrada_RSA": _b64(rsa.cifrar(RSA_Publica, clave_aes)),
		"iv_cifrado_RSA": _b64(rsa.cifrar(RSA_Publica, iv)),
		"mensajeCifrado_AES": aes.Cifrado_AES_enviar_mensaje(mensaje, iv, clave_aes),
	}


def decifrar_mensaje(mensajeCifrado_AES: str, iv_cifrado_RSA: str,
						clave_cifrada_RSA: str, RSA_Privada) -> str:
	clave_aes = rsa.descifrar(RSA_Privada, _unb64(clave_cifrada_RSA))
	iv = rsa.descifrar(RSA_Privada, _unb64(iv_cifrado_RSA))
	return aes.descifrar_aes(mensajeCifrado_AES, clave_aes, iv)
