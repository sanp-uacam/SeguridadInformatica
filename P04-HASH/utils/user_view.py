import tkinter as tk

from utils.password_window import PasswordWindow


class UserView:
    def __init__(self, username, users, hash_password, validate_password, users_file):
        self.username = username
        self.users = users
        self.hash_password = hash_password
        self.validate_password = validate_password
        self.users_file = users_file
        self.background_color = '#242424'
        self.text_color = '#f2f2f2'

    def run(self):
        dashboard = tk.Tk()
        dashboard.title('Dashboard Principal')
        dashboard.geometry('500x430')
        dashboard.configure(bg=self.background_color)

        frame = tk.Frame(dashboard, bg=self.background_color, padx=30, pady=35)
        frame.pack(expand=True, fill='both')

        tk.Label(
            frame,
            text=f'Bienvenido al Sistema, {self.username}!',
            font=('Arial', 22, 'bold'),
            bg=self.background_color,
            fg=self.text_color
        ).pack(pady=(35, 30))

        self._button(frame, 'Cambiar Contraseña', lambda: self._open_password_window(dashboard)).pack(
            pady=6, ipady=3
        )
        self._button(frame, 'Cerrar Sesión', dashboard.destroy).pack(pady=6, ipady=3)
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

    @staticmethod
    def _button(parent, text, command):
        return tk.Button(
            parent,
            text=text,
            font=('Arial', 12),
            bg='#363636',
            fg='#111111',
            activebackground='#4a4a4a',
            activeforeground='#111111',
            width=20,
            height=1,
            relief='flat',
            bd=0,
            highlightthickness=0,
            command=command
        )
