import json
import tempfile
from pathlib import Path

import rsa
from hibrido import decifrar_mensaje, get_Msj_And_Key


def test_cifrado_descifrado():
	with tempfile.TemporaryDirectory() as folder:
		publica = Path(folder) / "publica.pem"
		privada = Path(folder) / "privada.pem"
		rsa.generar_claves(str(publica), str(privada))
		mensaje = "Mensaje de prueba: áéñ 🔐"
		cifrado = get_Msj_And_Key(rsa.cargar_publica(str(publica)), mensaje)
		resultado = decifrar_mensaje(
			cifrado["mensajeCifrado_AES"],
			cifrado["iv_cifrado_RSA"],
			cifrado["clave_cifrada_RSA"],
			rsa.cargar_privada(str(privada)),
		)
		assert resultado == mensaje
		assert json.loads(json.dumps(cifrado)) == cifrado


if __name__ == "__main__":
	test_cifrado_descifrado()
	print("Prueba RSA-AES: OK")