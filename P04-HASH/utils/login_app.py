import hashlib
import hmac
import re
import secrets
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from .saveJson import cargar_diccionario, guardar_diccionario

USERS_FILE = Path(__file__).resolve().parents[1] / "users.json"


def password_rules(username, password):
	sequences = any(
		password[i:i + 3].isalnum() and (
			ord(password[i + 1]) == ord(password[i]) + 1 and
			ord(password[i + 2]) == ord(password[i + 1]) + 1 or
			ord(password[i + 1]) == ord(password[i]) - 1 and
			ord(password[i + 2]) == ord(password[i + 1]) - 1
		)
		for i in range(len(password) - 2)
	)
	return [
		len(password) >= 8,
		bool(re.search(r"[A-Z]", password) and re.search(r"[a-z]", password)),
		not sequences,
		bool(re.search(r"[^A-Za-z0-9]", password)),
		bool(username) and username.lower() not in password.lower(),
	]


def hash_password(password, salt=None):
	salt = salt or secrets.token_bytes(16)
	digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
	return f"{salt.hex()}${digest.hex()}"


def verify_password(password, stored):
	salt_hex, digest_hex = stored.split("$", 1)
	calculated = hash_password(password, bytes.fromhex(salt_hex)).split("$", 1)[1]
	return hmac.compare_digest(calculated, digest_hex)


class LoginApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Sistema de Login")
		self.root.geometry("440x360")
		self.users = cargar_diccionario(str(USERS_FILE))
		self.users = self.users if isinstance(self.users, dict) else {}
		self.create_widgets()

	def create_widgets(self):
		frame = tk.Frame(self.root, padx=24, pady=20)
		frame.pack(expand=True)
		tk_title = tk.Label(frame, text="Inicio de sesión", font=("Arial", 18, "bold"))
		tk_title.pack(pady=(0, 20))
		fields = tk.Frame(frame)
		fields.pack()
		tk.Label(fields, text="Usuario:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
		self.user_entry = tk.Entry(fields, width=24)
		self.user_entry.grid(row=0, column=1, padx=6, pady=6)
		tk.Label(fields, text="Contraseña:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
		self.pass_entry = tk.Entry(fields, width=24, show="*")
		self.pass_entry.grid(row=1, column=1, padx=6, pady=6)
		self.pass_entry.bind("<Return>", lambda _: self.login())
		buttons = tk.Frame(frame)
		buttons.pack(pady=14)
		tk.Button(buttons, text="Iniciar sesión", command=self.login).pack(side="left", padx=4)
		tk.Button(buttons, text="Registrarse", command=self.signin).pack(side="left", padx=4)
		tk.Button(buttons, text="Limpiar", command=self.clear_fields).pack(side="left", padx=4)
		self.user_entry.focus()

	def signin(self):
		window = tk.Toplevel(self.root)
		window.title("Registro")
		window.geometry("430x360")
		frame = tk.Frame(window, padx=20, pady=20)
		frame.pack(expand=True)
		tk.Label(frame, text="Crear usuario", font=("Arial", 16, "bold")).pack(pady=8)
		user = tk.Entry(frame, width=28)
		user.pack(pady=5)
		password = tk.Entry(frame, width=28, show="*")
		password.pack(pady=5)
		status = [tk.Label(frame, anchor="w", width=42) for _ in range(5)]
		for label in status:
			label.pack()

		def update_status(*_):
			rules = password_rules(user.get().strip(), password.get())
			texts = ["8 caracteres mínimo", "Mayúsculas y minúsculas",
					 "Sin secuencia alfanumérica", "Un carácter especial",
					 "No contiene el usuario"]
			for label, text, valid in zip(status, texts, rules):
				label.config(text=("OK " if valid else "NO ") + text,
								fg="#16803c" if valid else "#b42318")

		def register():
			username = user.get().strip()
			secret = password.get()
			if not username or username in self.users:
				messagebox.showerror("Error", "Usuario vacío o ya registrado", parent=window)
				return
			if not all(password_rules(username, secret)):
				messagebox.showerror("Error", "La contraseña no cumple los requisitos", parent=window)
				return
			self.users[username] = hash_password(secret)
			guardar_diccionario(self.users, str(USERS_FILE))
			messagebox.showinfo("Registro", "Usuario registrado", parent=window)
			window.destroy()

		user.bind("<KeyRelease>", update_status)
		password.bind("<KeyRelease>", update_status)
		tk.Button(frame, text="Guardar", command=register).pack(pady=12)
		update_status()

	def login(self):
		username = self.user_entry.get().strip()
		stored = self.users.get(username)
		if stored and verify_password(self.pass_entry.get(), stored):
			messagebox.showinfo("Acceso", f"Bienvenido, {username}")
		else:
			messagebox.showerror("Error", "Usuario o contraseña incorrectos")

	def clear_fields(self):
		self.user_entry.delete(0, tk.END)
		self.pass_entry.delete(0, tk.END)
		self.user_entry.focus()


def main():
	root = tk.Tk()
	LoginApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()