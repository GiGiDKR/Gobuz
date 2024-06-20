import tkinter as tk
from ttkbootstrap import ttk


class Login(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_view()

    def init_view(self):
        self.title('Qobuz Login')
        self.geometry('400x120')

        self.text_email = ttk.Entry(self)
        self.text_email.set_placeholder('Enter your e-mail')

        self.text_pass = ttk.Entry(self)
        self.text_pass.set_placeholder('Enter your password')
        self.text_pass.set_show('*')  # to hide the password

        self.btn_login = ttk.Button(self, text='Login', command=self.handle_login)

        self.text_email.pack(padx=10, pady=5, fill='x')
        self.text_pass.pack(padx=10, pady=5, fill='x')
        self.btn_login.pack(padx=10, pady=5)

    def handle_login(self):
        if self.text_email.get() == "" or self.text_pass.get() == "":
            ttk.messagebox.warning(self, 'Error', 'Login information is required')
        else:
            self.destroy()
