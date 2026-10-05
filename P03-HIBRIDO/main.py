import argparse
from pathlib import Path

import local_db
import rsa
from hibrido import decifrar_mensaje, get_Msj_And_Key


def generar_claves(publica: str, privada: str) -> None:
	rsa.generar_claves(publica, privada)
	print(f"Claves creadas: {publica}, {privada}")


def cifrar(entrada: str, salida: str, publica: str) -> None:
	data = local_db.load(entrada)
	cifrado = get_Msj_And_Key(rsa.cargar_publica(publica), data["mensaje"])
	local_db.save(cifrado, salida)
	print(f"Mensaje cifrado: {salida}")


def descifrar(entrada: str, salida: str, privada: str) -> None:
	data = local_db.load(entrada)
	mensaje = decifrar_mensaje(
		data["mensajeCifrado_AES"],
		data["iv_cifrado_RSA"],
		data["clave_cifrada_RSA"],
		rsa.cargar_privada(privada),
	)
	local_db.save({"mensaje": mensaje}, salida)
	print(f"Mensaje descifrado: {salida}")


def main() -> None:
	parser = argparse.ArgumentParser(description="Algoritmo híbrido RSA-AES")
	subparsers = parser.add_subparsers(dest="accion", required=True)

	claves = subparsers.add_parser("generar-claves")
	claves.add_argument("publica")
	claves.add_argument("privada")
	for accion in ("cifrar", "descifrar"):
		comando = subparsers.add_parser(accion)
		comando.add_argument("entrada")
		comando.add_argument("salida")
		comando.add_argument("clave_rsa")

	args = parser.parse_args()
	if args.accion == "generar-claves":
		generar_claves(args.publica, args.privada)
	elif args.accion == "cifrar":
		cifrar(args.entrada, args.salida, args.clave_rsa)
	else:
		descifrar(args.entrada, args.salida, args.clave_rsa)


if __name__ == "__main__":
	main()