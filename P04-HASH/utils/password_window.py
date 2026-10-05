import tkinter as tk
from tkinter import messagebox

from utils import saveJson


class PasswordWindow:
    def __init__(self, parent, username, users, hash_password, validate_password, users_file):
        self.parent = parent
        self.username = username
        self.users = users
        self.hash_password = hash_password
        self.validate_password = validate_password
        self.users_file = users_file
        self.background_color = '#242424'
        self.text_color = '#f2f2f2'
        self.input_color = '#333333'

    def show(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title('Cambiar contraseña')
        dialog.geometry('430x260')
        dialog.configure(bg=self.background_color)
        dialog.transient(self.parent)
        dialog.grab_set()

        frame = tk.Frame(dialog, bg=self.background_color, padx=25, pady=20)
        frame.pack(expand=True, fill='both')

        fields = []
        labels = ('Nueva contraseña:', 'Confirmar contraseña:')
        for row, label_text in enumerate(labels):
            tk.Label(
                frame, text=label_text, font=('Arial', 11),
                bg=self.background_color, fg=self.text_color
            ).grid(row=row, column=0, sticky='w', padx=(0, 10), pady=8)
            entry = tk.Entry(
                frame, width=22, show='*', font=('Arial', 11),
                bg=self.input_color, fg='#ffffff', insertbackground='#ffffff',
                relief='flat', bd=0
            )
            entry.grid(row=row, column=1, pady=8, ipady=4)
            fields.append(entry)

        show_password = tk.BooleanVar(value=False)

        def toggle_password_visibility():
            entry_visibility = '' if show_password.get() else '*'
            for entry in fields:
                entry.configure(show=entry_visibility)

        tk.Checkbutton(
            frame,
            text='Ver contraseña',
            variable=show_password,
            command=toggle_password_visibility,
            font=('Arial', 10),
            bg=self.background_color,
            fg=self.text_color,
            activebackground=self.background_color,
            activeforeground=self.text_color,
            selectcolor=self.background_color,
            anchor='w'
        ).grid(row=2, column=1, pady=(0, 5), sticky='w')

        def save_password():
            new_password, confirmation = (entry.get() for entry in fields)
            if new_password != confirmation:
                messagebox.showerror(
                    'Error', 'Las nuevas contraseñas no coinciden', parent=dialog
                )
                return

            password_errors = self.validate_password(self.username, new_password)
            if password_errors:
                messagebox.showerror(
                    'Contraseña insegura',
                    'La contraseña debe:\n' + '\n'.join(
                        f'- {error}' for error in password_errors
                    ),
                    parent=dialog
                )
                return

            old_hash = self.users[self.username]
            self.users[self.username] = self.hash_password(new_password)
            if saveJson.guardar_diccionario(self.users, self.users_file):
                messagebox.showinfo(
                    'Éxito', 'Contraseña actualizada correctamente', parent=dialog
                )
                dialog.destroy()
            else:
                self.users[self.username] = old_hash

        tk.Button(
            frame, text='Guardar', font=('Arial', 11, 'bold'),
            bg='#363636', fg='#111111', width=16, relief='flat', bd=0,
            command=save_password
        ).grid(row=3, column=0, columnspan=2, pady=(10, 0), ipady=3)

        fields[0].focus_set()
        return dialog
