import json
from pathlib import Path


def save(data: dict, filename: str = "mensaje_oculto.json") -> None:
	Path(filename).write_text(
		json.dumps(data, ensure_ascii=False, indent=2),
		encoding="utf-8",
	)


def load(filename: str = "mensaje_oculto.json") -> dict:
	return json.loads(Path(filename).read_text(encoding="utf-8"))


def save_key(key: bytes, filename: str) -> None:
	Path(filename).write_text(key.hex(), encoding="ascii")


def load_key(filename: str) -> bytes:
	return bytes.fromhex(Path(filename).read_text(encoding="ascii").strip())