import base64

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def _b64(value: bytes) -> str:
	return base64.b64encode(value).decode("ascii")


def _unb64(value: str) -> bytes:
	return base64.b64decode(value.encode("ascii"))


def Cifrado_AES_enviar_mensaje(texto: str, iv: bytes, key: bytes) -> str:
	if len(key) != 32 or len(iv) != AES.block_size:
		raise ValueError("AES-256 necesita una clave de 32 bytes e IV de 16 bytes")
	cipher = AES.new(key, AES.MODE_CBC, iv=iv)
	return _b64(cipher.encrypt(pad(texto.encode("utf-8"), AES.block_size)))


def descifrar_aes(ciphertext: str, key: bytes, iv: bytes) -> str:
	cipher = AES.new(key, AES.MODE_CBC, iv=iv)
	return unpad(cipher.decrypt(_unb64(ciphertext)), AES.block_size).decode("utf-8")


def get_key(size: int = 32) -> bytes:
	if size != 32:
		raise ValueError("La clave AES debe tener 32 bytes")
	return get_random_bytes(size)


def get_iv() -> bytes:
	return get_random_bytes(AES.block_size)
