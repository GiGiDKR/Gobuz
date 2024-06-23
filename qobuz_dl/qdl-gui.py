import os
import configparser
import ttkbootstrap as ttk
from ttkbootstrap import Scrollbar, Progressbar
from ttkbootstrap.dialogs import MessageDialog
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap import Style
import logging
import threading
import requests
import hashlib
import sys
from datetime import datetime
import json
from qobuz_dl.core import QobuzDL
from ttkbootstrap.toast import ToastNotification

# Set up logging
logging.basicConfig(level=logging.INFO)


def resolve_path(file_name):
    if getattr(sys, "frozen", False):
        base_path = os.path.abspath(os.path.join(sys._MEIPASS))
    else:
        base_path = os.path.abspath(os.path.join(os.getcwd()))

    config_dir = os.path.join(base_path, '.config')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    resolved_path = os.path.join(config_dir, file_name)

    return resolved_path


class SettingsWindow:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app_instance = app_instance
        self.parent.title("Settings")

        self.email_label = ttk.Label(parent, text="Email :")
        self.email_label.grid(row=0, column=0, padx=10, pady=10)
        self.email_entry = ttk.Entry(parent, style='dark.TEntry')
        self.email_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = ttk.Label(parent, text="Password :")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = ttk.Entry(parent, style='dark.TEntry')
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        #self.limit_label = ttk.Label(parent, text="Limit :")
        #self.limit_label.grid(row=2, column=0, padx=10, pady=10)
        ##self.limit_spinbox = ttk.Spinbox(parent, from_=1, to=100, increment=1)
        #self.limit_spinbox.set(app_instance.limit)
        #self.limit_spinbox.grid(row=2, column=1, padx=10, pady=10)

        self.submit_button = ttk.Button(parent, text="Save", command=self.save_settings)
        self.submit_button.grid(row=3, columnspan=2, padx=10, pady=10)

    def save_settings(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        # Encodage du mot de passe en utilisant hashlib
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        # Création ou mise à jour du fichier de configuration
        config = configparser.ConfigParser()
        config.read(self.app_instance.config_path)  # Assurez-vous que config_path est défini dans app_instance
        config['Credentials']['email'] = email
        config['Credentials']['password'] = hashed_password
        #self.app_instance.limit = int(self.limit_spinbox.get())

        # Écriture des modifications dans le fichier 'config.ini'
        with open(self.app_instance.config_path, 'w') as configfile:
            config.write(configfile)

        #messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
        self.parent.destroy()


def update_credentials(resolved_path):
    url = "https://raw.githubusercontent.com/GiGiDKR/qobuz-dl-gui/main/qobuz_dl/.config/config.ini"
    filename = resolved_path("config.ini")
    r = requests.get(url)
    f = open(filename, 'wb')
    f.write(r.content)
    #messagebox.showinfo("Credentials", "Up-to-date Qobuz credentials downloded")


def load_translation(language):
    translation_file = resolve_path(f"{language}.json")

    with open(translation_file, 'r', encoding='utf-8') as f:
        translations = json.load(f)
    return translations


def translate(text, translations):
    return translations.get(text, text)


def update_widget_text(widget, text):
    widget.config(text=text)


class QobuzDLApp:
    def __init__(self, root, results, resolved_path):
        self.root = root
        self.results = results
        self.root.title("Qobuz Downloader")
        self.widgets_to_update = []
        self.translations = load_translation('en')
        self.qobuz = QobuzDL()

        self.limit = 20

        self.create_widgets()

        self.load_credentials(resolve_path)
        self.config_path = ".config\\config.ini"
        self.preferences_file = resolved_path("preferences.ini")
        self.config_file = resolved_path("config.ini")
        self.config = configparser.ConfigParser()
        self.load_config()
        self.load_user_preferences()

    def load_config(self):
        # Charger le fichier de configuration
        self.config.read(self.config_file)

    def place_window_center(self):
        self.root.update_idletasks()
        w_height = self.root.winfo_height()
        w_width = self.root.winfo_width()
        s_height = self.root.winfo_screenheight()
        s_width = self.root.winfo_screenwidth()
        xpos = (s_width - w_width) // 2
        ypos = (s_height - w_height) // 2
        self.root.geometry(f'+{xpos}+{ypos}')

    def user_update_credentials(self, resolved_path):
        url = "https://raw.githubusercontent.com/GiGiDKR/qobuz-dl-gui/main/qobuz_dl/.config/config.ini"
        filename = resolved_path("config.ini")
        r = requests.get(url)
        f = open(filename, 'wb')
        f.write(r.content)
        self.load_credentials(resolve_path)

    def load_credentials(self, resolved_path):
        path_config = resolved_path("config.ini")
        config = configparser.ConfigParser()
        config.read(path_config)
        if "Credentials" in config:
            self.email = config["Credentials"].get("email", "")
            self.password = config["Credentials"].get("password", "")
            self.expiration_date = config["Credentials"].get("expirationdate", "")
            self.update_email_date_label()
        else:
            update_credentials(resolve_path)

    def update_email_date_label(self):
        email_label_text = f"{self.email}"
        self.email_label.config(text=email_label_text)

        expirationdate = datetime.strptime(self.expiration_date, "%d/%m/%Y")
        dateactual = datetime.now()
        difference = expirationdate - dateactual
        date_label_text = f"Expire : {difference.days}"
        self.date_label.config(text=date_label_text)

    def load_user_preferences(self):
        config = configparser.ConfigParser()

        if not self.preferences_file:
            config['Preferences'] = {
                'theme': 'superhero',
            }
            with open(self.preferences_file, 'w') as configfile:
                config.write(configfile)
        else:
            config.read(self.preferences_file)
            theme = config.get('Preferences', 'theme', fallback='superhero')
            self.change_theme(theme)

    def save_user_preferences(self, theme_name):
        config = configparser.ConfigParser()
        config['Preferences'] = {
            'theme': theme_name,
        }
        with open(self.preferences_file, 'w') as configfile:
            config.write(configfile)

    def create_widgets(self):
        self.search_type_label = ttk.Label(self.root, text="Search Type :")
        self.search_type_label.grid(row=0, column=0, padx=10, pady=10)
        self.search_type_combobox = ttk.Combobox(self.root, style='dark.TCombobox',
                                                 values=["album", "track", "artist", "playlist"])
        self.search_type_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.search_type_combobox.current(0)  # Default to "album"
        self.search_type_tooltip = ToolTip(self.search_type_combobox,
                                           text="Search albums, tracks, artists and playlists",
                                           bootstyle="info")

        self.search_query_label = ttk.Label(self.root, text="Search :")
        self.search_query_label.grid(row=1, column=0, padx=10, pady=10)
        self.search_query_entry = ttk.Entry(self.root, style='dark.TEntry')
        self.search_query_entry.grid(row=1, column=1, padx=10, pady=10)
        self.search_query_tooltip = ToolTip(self.search_query_entry, text="Enter your search", bootstyle="info")

        current_value = ttk.IntVar(value=20)

        def get_current_value():
            return current_value.get()

        def slider_changed(event):
            value_label.configure(text=get_current_value())
            self.limit = current_value.get()

        self.limit_label = ttk.Label(text='Limit : ')
        self.limit_label.grid(row=3, columnspan=1, padx=10, pady=10)

        self.slider = ttk.Scale(
            from_=1,
            to=100,
            takefocus=1,
            bootstyle="primary",
            variable=current_value,
            command=slider_changed
        )
        self.slider.grid(row=3, columnspan=2, padx=10, pady=10)
        self.slider_tooltip = ToolTip(self.slider, text="Limit of search results", bootstyle="info")

        value_label = ttk.Label(
            text=get_current_value()
        )
        value_label.grid(row=3, columnspan=2, padx=10, pady=10)

        self.search_button = ttk.Button(self.root, text="Search", bootstyle="toolbutton, outline", takefocus=1,
                                        command=self.start_search)
        self.search_button.grid(row=4, columnspan=2, padx=10, pady=10)

        self.quality_label = ttk.Label(self.root, text="Quality :")
        self.quality_label.grid(row=2, column=0, padx=10, pady=10)
        self.quality_combobox = ttk.Combobox(self.root, style='dark.TCombobox', values=list(Qualities.values()))
        self.quality_combobox.grid(row=2, column=1, padx=10, pady=10)
        self.quality_combobox.current(1)  # Default to "6 - 16 bit, 44.1kHz"
        self.quality_tooltip = ToolTip(self.quality_combobox, text="Max audio quality for downloads",
                                       bootstyle="warning")
        self.results_listbox = ScrolledFrame(self.root, autohide=True)
        self.results_listbox.grid(row=5, columnspan=2, padx=10, pady=10)

        self.download_button = ttk.Checkbutton(self.root, text="Download", bootstyle="success-toolbutton",
                                               takefocus=1, command=self.download_selected)

        self.download_button.grid(row=6, columnspan=2, padx=10, pady=10)

        self.progressbar = Progressbar(self.root, mode='determinate')
        self.progressbar.grid(row=7, columnspan=2, padx=10, pady=10)

        #sizegrip = ttk.Sizegrip(bootstyle="light")
        #sizegrip.grid(row=8, columnspan=2, sticky="e")

        self.email_label = ttk.Label(self.root, text="", bootstyle="light")
        self.email_label.grid(row=8, columnspan=1, padx=10, pady=10, sticky="w")
        self.date_label = ttk.Label(self.root, text="", bootstyle="light")
        self.date_label.grid(row=8, columnspan=2, padx=10, pady=10, sticky="e")

        self.search_query_entry.bind("<Return>", lambda event: self.start_search())

        self.create_menu()

    def create_menu(self):
        self.menu_bar = ttk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.update_menu()

        theme_menu = ttk.Menu(self.menu_bar, tearoff=0)
        for theme in style.theme_names():
            theme_menu.add_command(label=theme, command=lambda t=theme: self.change_theme(t))
        self.menu_bar.add_cascade(label="Themes", menu=theme_menu)

        language_menu = ttk.Menu(self.menu_bar, tearoff=0)
        language_menu.add_command(label="English", command=lambda: self.update_all_widgets('en'))
        language_menu.add_command(label="French", command=lambda: self.update_all_widgets('fr'))

        self.menu_bar.add_cascade(label="Language", menu=language_menu)

        self.widgets_to_update.append((self.search_type_label, "Search Type :"))
        self.widgets_to_update.append((self.search_type_tooltip, "Search albums, tracks, artists and playlists"))
        self.widgets_to_update.append((self.search_query_label, "Search :"))
        self.widgets_to_update.append((self.search_query_tooltip, "Enter your search"))
        self.widgets_to_update.append((self.limit_label, "Limit :"))
        self.widgets_to_update.append((self.slider_tooltip, "Limit of search results"))
        self.widgets_to_update.append((self.search_button, "Search"))
        self.widgets_to_update.append((self.quality_tooltip, "Max audio quality for downloads"))
        self.widgets_to_update.append((self.quality_label, "Quality :"))
        self.widgets_to_update.append((self.download_button, "Download Selected"))
        
    def update_menu(self):
        for menu in self.menu_bar.winfo_children():
            menu.destroy()

        file_menu = ttk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label=translate("Update Credentials", self.translations),
                              command=self.user_update_credentials(resolve_path))
        file_menu.add_separator()
        file_menu.add_command(label=translate("Settings", self.translations), command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label=translate("Exit", self.translations), command=self.quit_application)
        self.menu_bar.add_cascade(label=translate("File", self.translations), menu=file_menu)

    def update_all_widgets(self, language):
        self.translations = load_translation(language)
        for widget, text in self.widgets_to_update:
            translated_text = translate(text, self.translations)
            if isinstance(widget, ToolTip):
                widget.text = translated_text
            else:
                update_widget_text(widget, translated_text)
        self.create_menu()

    def quit_application(self):
        self.root.quit()

    def change_theme(self, theme_name):
        style.theme_use(theme_name)
        self.save_user_preferences(theme_name)

    def show_settings(self):
        self.settings_window = ttk.Toplevel(self.root)
        SettingsWindow(self.settings_window, self)

    def start_search(self):
        #self.load_credentials(resolve_path)
        search_type = self.search_type_combobox.get()
        query = self.search_query_entry.get()

        if not query:
            translated_text = translate("Please enter a search query", self.translations)
            md_query = MessageDialog(message=translated_text)
            md_query.show()
            return

        try:
            self.qobuz.get_tokens()
            self.qobuz.initialize_client(self.email, self.password, self.qobuz.app_id, self.qobuz.secrets)
            results = self.qobuz.search_by_type(query, search_type, limit=self.limit, lucky=False)

            if results:
                for result in results:
                    ttk.Checkbutton(self.results_listbox, bootstyle="round-toggle",
                                    text=f"{result['text']}").pack(anchor=W)
                self.search_results = results
            else:
                translated_text = translate("No results found for the given query", self.translations)
                md_results = MessageDialog(message=translated_text)
                md_results.show()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_progressbar_complete(self):
        self.progressbar.stop()
        self.progressbar['value'] = 100

    def download_selected(self):
        selected_indices = [index for index, child in enumerate(self.results_listbox.winfo_children())
                            if child.instate(['selected'])]
        if not selected_indices:
            translated_text = translate("Please select at least one item to download", self.translations)
            md_download = MessageDialog(message=translated_text)
            md_download.show()
            return

        quality = self.quality_combobox.current() + 5
        self.qobuz.quality = quality

        selected_items = [self.search_results[i] for i in selected_indices]
        selected_urls = [item['url'] for item in selected_items]

        self.progressbar.start()

        threading.Thread(target=self.download_thread, args=(selected_items, selected_urls)).start()

    def download_thread(self, selected_items, selected_urls):
        try:
            downloaded_items = []
            for item, url in zip(selected_items, selected_urls):
                self.qobuz.download_list_of_urls([url])
                downloaded_items.append(item)
                toast = ToastNotification(
                    title="Download Complete",
                    message=f"Download complete : {item['text']}",
                    duration=5000,
                    position=(500, 100, 's')
                )
                toast.show_toast()
                #messagebox.showinfo("Download Complete", f"Download complete : {item['text']}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.update_progressbar_complete()



Qualities = {
    5: "MP3",
    6: "16 bit, 44.1kHz",
    7: "24 bit, <96kHz",
    27: "24 bit, >96kHz",
}

if __name__ == "__main__":
    style = Style()
    root = style.master
    root.geometry("330x590")
    results = [...]
    app_instance = QobuzDLApp(root, results, resolve_path)
    #app = QobuzDLApp(root, results, resolve_path)
    app_instance.place_window_center()
    root.mainloop()
