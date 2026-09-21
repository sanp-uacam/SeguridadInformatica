from pathlib import Path

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def generar_claves(publica: str, privada: str, bits: int = 2048) -> None:
	key = RSA.generate(bits)
	Path(privada).write_bytes(key.export_key())
	Path(publica).write_bytes(key.publickey().export_key())


def cargar_publica(filename: str):
	return RSA.import_key(Path(filename).read_bytes())


def cargar_privada(filename: str):
	return RSA.import_key(Path(filename).read_bytes())


def cifrar(public_key, data: bytes) -> bytes:
	return PKCS1_OAEP.new(public_key).encrypt(data)


def descifrar(private_key, data: bytes) -> bytes:
	return PKCS1_OAEP.new(private_key).decrypt(data)