import tkinter as tk
from tkinter import messagebox

from utils import saveJson
from utils.password_window import PasswordWindow


class AdminView:
    def __init__(self, username, users, hash_password, validate_password, users_file):
        self.username = username
        self.users = users
        self.hash_password = hash_password
        self.validate_password = validate_password
        self.users_file = users_file
        self.background_color = '#242424'
        self.text_color = '#f2f2f2'
        self.input_color = '#333333'

    def run(self):
        dashboard = tk.Tk()
        dashboard.title('Panel de Administración')
        dashboard.geometry('760x700')
        dashboard.configure(bg=self.background_color)

        frame = tk.Frame(dashboard, bg=self.background_color, padx=35, pady=25)
        frame.pack(expand=True, fill='both')
        tk.Label(
            frame,
            text=f'Panel de Administración, {self.username}',
            font=('Arial', 20, 'bold'),
            bg=self.background_color,
            fg=self.text_color
        ).pack(pady=(5, 12))
        tk.Label(
            frame,
            text='Usuarios y hashes almacenados en users-db.json',
            font=('Arial', 11),
            bg=self.background_color,
            fg=self.text_color
        ).pack(pady=(0, 12))

        records = tk.Text(
            frame, height=15, width=78, font=('Courier', 11),
            bg=self.input_color, fg='#ffffff', insertbackground='#ffffff',
            relief='flat', bd=0, padx=12, pady=12
        )
        records.pack(fill='both', expand=True)
        self._refresh_records(records)

        tk.Label(
            frame,
            text='Selecciona un usuario para eliminarlo:',
            font=('Arial', 11), bg=self.background_color, fg=self.text_color
        ).pack(pady=(12, 5))
        user_list = tk.Listbox(
            frame, height=3, font=('Arial', 11), bg=self.input_color,
            fg='#ffffff', selectbackground='#666666', relief='flat', bd=0
        )
        user_list.pack(fill='x')
        self._refresh_user_list(user_list)

        controls = tk.Frame(frame, bg=self.background_color)
        controls.pack(pady=(10, 0))
        self._button(
            controls, 'Eliminar Usuario',
            lambda: self.delete_user(user_list, records)
        ).pack(side='left', padx=5, ipady=3)
        self._button(
            controls, 'Cambiar Contraseña',
            lambda: self._open_password_window(dashboard)
        ).pack(side='left', padx=5, ipady=3)
        self._button(controls, 'Cerrar Sesión', dashboard.destroy).pack(
            side='left', padx=5, ipady=3
        )
        dashboard.mainloop()

    def _open_password_window(self, parent):
        PasswordWindow(
            parent,
            self.username,
            self.users,
            self.hash_password,
            self.validate_password,
            self.users_file
        ).show()

    def delete_user(self, user_list, records):
        selection = user_list.curselection()
        if not selection:
            messagebox.showerror('Error', 'Selecciona un usuario', parent=user_list)
            return

        username = user_list.get(selection[0])
        if username.lower() == self.username.lower():
            messagebox.showerror(
                'Operación no permitida',
                'El administrador no puede eliminarse a sí mismo',
                parent=user_list
            )
            return
        if not messagebox.askyesno(
            'Confirmar eliminación',
            f"¿Eliminar definitivamente al usuario '{username}'?",
            parent=user_list
        ):
            return

        deleted_hash = self.users.pop(username)
        if not saveJson.guardar_diccionario(self.users, self.users_file):
            self.users[username] = deleted_hash
            return

        self._refresh_user_list(user_list)
        self._refresh_records(records)
        messagebox.showinfo(
            'Usuario eliminado', 'El usuario fue eliminado de la base de datos'
        )

    def _refresh_user_list(self, user_list):
        user_list.delete(0, tk.END)
        for username in self.users:
            user_list.insert(tk.END, username)

    def _refresh_records(self, records):
        records.configure(state='normal')
        records.delete('1.0', tk.END)
        records.insert(tk.END, 'Usuario                 Hash SHA-256\n')
        records.insert(tk.END, '-' * 70 + '\n')
        for username, password_hash in self.users.items():
            records.insert(tk.END, f'{username:<24}{password_hash}\n')
        records.insert(
            tk.END,
            '\nLas contraseñas en texto plano no se almacenan y no pueden recuperarse.\n'
        )
        records.configure(state='disabled')

    @staticmethod
    def _button(parent, text, command):
        return tk.Button(
            parent, text=text, font=('Arial', 11), bg='#363636', fg='#111111',
            activebackground='#4a4a4a', activeforeground='#111111', width=18,
            height=1, relief='flat', bd=0, highlightthickness=0, command=command
        )
