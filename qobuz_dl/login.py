import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

def clear_placeholder(event):
    event.widget.delete(0, 'end')

class Login(ttk.Window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_view()

    def init_view(self):
        self.title('Qobuz Login')
        self.geometry('400x120')

        # Création d'un cadre pour organiser les widgets
        layout = ttk.Frame(self)
        layout.grid(padx=10, pady=10)

        self.text_email = ttk.Entry(layout, bootstyle='info')
        self.text_email.insert(0, 'Enter your e-mail')
        self.text_email.bind("<FocusIn>", clear_placeholder)
        self.text_email.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.text_pass = ttk.Entry(layout, bootstyle='info', show='*')
        self.text_pass.insert(0, 'Enter your password')
        self.text_pass.bind("<FocusIn>", clear_placeholder)
        self.text_pass.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.btn_login = ttk.Button(layout, text='Login', command=self.handle_login, bootstyle='primary')
        self.btn_login.grid(row=2, column=0, padx=5, pady=5, sticky='ew')

        # Configuration de la colonne pour qu'elle s'étende avec la fenêtre
        layout.columnconfigure(0, weight=1)

    def handle_login(self):
        if self.text_email.get() == "" or self.text_pass.get() == "":
            Messagebox.show_warning('Error', 'Login information is required')
        else:
            self.destroy()

# Exemple d'utilisation
if __name__ == '__main__':
    login = Login()
    login.mainloop()
