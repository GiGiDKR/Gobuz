import os
import configparser
import time
import tkinter
from ttkbootstrap.constants import *
from ttkbootstrap.publisher import Publisher
from ttkbootstrap.style import Style
from ttkbootstrap.icons import Icon
from ttkbootstrap import utility
import ttkbootstrap as ttk
from tkinter import messagebox, Listbox
from ttkbootstrap import Scrollbar, Progressbar
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap import Style
from ttkbootstrap import Window
import logging
import threading
import hashlib
import requests
from time import sleep
from os import getcwd
from pathlib import Path
from login import Login
import sys

from qobuz_dl.bundle import Bundle
from qobuz_dl.core import QobuzDL


if os.name == "nt":
    OS_CONFIG = os.environ.get("APPDATA")
else:
    OS_CONFIG = os.path.join(os.environ["HOME"], ".config")

CONFIG_PATH = os.path.join(OS_CONFIG, "qobuz-dl")
CONFIG_FILE = os.path.join(CONFIG_PATH, "config.ini")

QOBUZ_DB = os.path.join(CONFIG_PATH, "qobuz_dl.db")

def reset_config(config_file):
    logging.info(f"{YELLOW}Creating config file: {config_file}")
    config = configparser.ConfigParser()
    config["Credentials"]["email"] = ""
    config["Credentials"]["password"] = ""
    config["Credentials"]["expirationdate"] = ""
    config["DEFAULT"]["default_folder"] = "Qobuz Downloads"
    config["DEFAULT"]["default_quality"] = "6"
    config["DEFAULT"]["default_limit"] = "20"
    config["DEFAULT"]["no_m3u"] = "false"
    config["DEFAULT"]["albums_only"] = "false"
    config["DEFAULT"]["no_fallback"] = "false"
    config["DEFAULT"]["og_cover"] = "false"
    config["DEFAULT"]["embed_art"] = "false"
    config["DEFAULT"]["no_cover"] = "false"
    config["DEFAULT"]["no_database"] = "false"
    logging.info(f"{YELLOW}Getting tokens. Please wait...")
    bundle = Bundle()
    config["DEFAULT"]["app_id"] = str(bundle.get_app_id())
    config["DEFAULT"]["secrets"] = ",".join(bundle.get_secrets().values())
    config["DEFAULT"]["folder_format"] = DEFAULT_FOLDER
    config["DEFAULT"]["track_format"] = DEFAULT_TRACK
    config["DEFAULT"]["smart_discography"] = "false"
    with open(config_file, "w") as configfile:
        config.write(configfile)
    logging.info(
        f"{GREEN}Config file updated. Edit more options in {config_file}"
        "\nso you don't have to call custom flags every time you run "
        "a qobuz-dl command."
    )

def check_config_init():
    if not os.path.isdir(CONFIG_PATH) or not os.path.isfile(CONFIG_FILE):
        os.makedirs(CONFIG_PATH, exist_ok=True)
        reset_config(CONFIG_FILE)

def login(config, config_path):
    login_window = Login()

    try:
        email = config["DEFAULT"]["email"]
        password = config["DEFAULT"]["password"]
    except (KeyError, UnicodeDecodeError, configparser.Error) as error:
        logging.info(f"{RED}Your config file is corrupted: {error}!")
        return

    if email == "" or password == "":
        if login_window.exec_() == QtWidgets.QDialog.Accepted:
            email = login_window.text_email.text()
            password = login_window.text_pass.text()

            config["DEFAULT"]["email"] = email
            config["DEFAULT"]["password"] = hashlib.md5(
                password.encode("utf-8")).hexdigest()

            with open(config_path, "w") as config_file:
                config.write(config_file)

    default_folder = config["DEFAULT"]["default_folder"]
    default_limit = int(config["DEFAULT"]["default_limit"])
    default_quality = int(config["DEFAULT"]["default_quality"])


# Set up logging
logging.basicConfig(level=logging.INFO)


def resolve_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path


class OptionsWindow:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app_instance = app_instance
        self.parent.title("Options")

        self.limit_label = ttk.Label(parent, text="Limit :")
        self.limit_label.grid(row=0, column=0, padx=10, pady=10)
        self.limit_spinbox = ttk.Spinbox(parent, from_=1, to=100, increment=1)
        self.limit_spinbox.set(app_instance.limit)
        self.limit_spinbox.grid(row=0, column=1, padx=10, pady=10)

        self.submit_button = ttk.Button(parent, text="Save", command=self.save_options)
        self.submit_button.grid(row=1, columnspan=2, padx=10, pady=10)

    def save_options(self):
        self.app_instance.limit = int(self.limit_spinbox.get())
        messagebox.showinfo("Options Saved", "Options have been saved successfully.")
        self.parent.destroy()


class QobuzDLApp:
    def __init__(self, root, results, resolved_path):
        self.root = root
        self.results = results
        self.root.title("Qobuz Downloader")

        # Load or initialize QobuzDL instance
        self.qobuz = QobuzDL()

        # Default limit value
        self.limit = 20

        # Create widgets for user input
        self.create_widgets()

        # Load credentials from file
        self.load_credentials(resolve_path)

        self.preferences_file = resolved_path("user_preferences.ini")

    def user_update_credentials(self, resolved_path):
        url = "https://raw.githubusercontent.com/GiGiDKR/qobuz-dl-gui/main/qobuz_dl/config.ini"
        filename = resolved_path("config.ini")
        r = requests.get(url)
        f = open(filename, 'wb')
        f.write(r.content)
        self.load_credentials(resolve_path)

    def load_credentials(self, resolved_path):
        path_config = resolved_path("config.ini")
        self.credentials_file = path_config
        config = configparser.ConfigParser()
        config.read(self.credentials_file)
        if "Credentials" in config:
            self.email = config["Credentials"].get("email", "")
            self.password = config["Credentials"].get("password", "")
            self.expiration_date = config["Credentials"].get("expirationdate", "")
            self.update_email_date_label()
        else:
            self.update_credentials(resolve_path)

    def update_credentials(self, resolved_path):
        url = "https://raw.githubusercontent.com/GiGiDKR/qobuz-dl-gui/main/qobuz_dl/config.ini"
        filename = resolved_path("config.ini")
        r = requests.get(url)
        f = open(filename, 'wb')
        f.write(r.content)
        #messagebox.showinfo("Credentials", "Up-to-date Qobuz credentials downloded")

    def update_email_date_label(self):
        # Update email label with loaded email and expiration date
        email_label_text = f"{self.email}"
        self.email_label.config(text=email_label_text)
        date_label_text = f"{self.expiration_date}"
        self.date_label.config(text=date_label_text)

    def load_user_preferences(self):
        config = configparser.ConfigParser()

        # Vérifier si le fichier de préférences existe
        if not self.preferences_file:
            # Définir les préférences par défaut
            config['Preferences'] = {
                'theme': 'superhero',
            }
            # Créer le fichier de préférences
            with open(self.preferences_file, 'w') as configfile:
                config.write(configfile)
        else:
            # Charger les préférences existantes
            config.read(self.preferences_file)
            theme = config.get('Preferences', 'theme')
            # Appliquer les préférences chargées
            self.change_theme(theme)

    def save_user_preferences(self, theme_name):
        config = configparser.ConfigParser()
        config['Preferences'] = {
            'theme': theme_name,
        }
        with open(self.preferences_file, 'w') as configfile:
            config.write(configfile)

    def create_widgets(self):

        # Search type selection
        self.search_type_label = ttk.Label(self.root, text="Search Type :")
        self.search_type_label.grid(row=0, column=0, padx=10, pady=10)
        self.search_type_combobox = ttk.Combobox(self.root, style='dark.TCombobox',
                                                 values=["album", "track", "artist", "playlist"])
        self.search_type_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.search_type_combobox.current(0)  # Default to "album"
        ToolTip(self.search_type_combobox, text="Download albums, tracks, artists, playlists and labels",
                                                bootstyle="info")

        # Search query input
        self.search_query_label = ttk.Label(self.root, text="Search :")
        self.search_query_label.grid(row=1, column=0, padx=10, pady=10)
        self.search_query_entry = ttk.Entry(self.root, style='dark.TEntry')
        self.search_query_entry.grid(row=1, column=1, padx=10, pady=10)
        ToolTip(self.search_query_entry, text="Enter your search", bootstyle="info")

        # Slider
        current_value = ttk.IntVar(value=20)

        def get_current_value():
            return current_value.get()

        def slider_changed(event):
            value_label.configure(text=get_current_value())
            self.limit = current_value.get()

        # value label
        limit_label = ttk.Label(text='Limit : ')
        limit_label.grid(row=3, columnspan=1, padx=10, pady=10)

        self.slider = ttk.Scale(
            from_=1,
            to=100,
            takefocus=1,
            bootstyle="primary",
            variable=current_value,
            command=slider_changed
        )
        self.slider.grid(row=3, columnspan=2, padx=10, pady=10)
        ToolTip(self.slider, text="Limit of search results (1>100)", bootstyle="info")

        # value label
        value_label = ttk.Label(
            text=get_current_value()
        )
        value_label.grid(row=3, columnspan=2, padx=10, pady=10)

        # Start search button
        self.search_button = ttk.Button(self.root, text="Search", bootstyle="toolbutton, outline", takefocus=1,
                                        command=self.start_search)
        self.search_button.grid(row=4, columnspan=2, padx=10, pady=10)

        # Quality selection
        self.quality_label = ttk.Label(self.root, text="Quality :")
        self.quality_label.grid(row=2, column=0, padx=10, pady=10)
        self.quality_combobox = ttk.Combobox(self.root, style='dark.TCombobox', values=list(Qualities.values()))
        self.quality_combobox.grid(row=2, column=1, padx=10, pady=10)
        self.quality_combobox.current(1)  # Default to "6 - 16 bit, 44.1kHz"
        ToolTip(self.quality_combobox, text="Select audio quality for download", bootstyle="warning")

        # Results listbox with scrollbar
        self.results_listbox = ScrolledFrame(self.root, autohide=True)
        self.results_listbox.grid(row=5, columnspan=2, padx=10, pady=10)

        # Download selected button
        self.download_button = ttk.Checkbutton(self.root, text="Download Selected", bootstyle="success-toolbutton",
                                               takefocus=1, command=self.download_selected)

        self.download_button.grid(row=6, columnspan=2, padx=10, pady=10)

        self.progressbar = Progressbar(self.root, mode='determinate')
        self.progressbar.grid(row=7, columnspan=2, padx=10, pady=10)

        #sizegrip = ttk.Sizegrip(bootstyle="light")
        #sizegrip.grid(row=8, columnspan=2, sticky="e")

        # Email label
        self.email_label = ttk.Label(self.root, text="", bootstyle="light")
        self.email_label.grid(row=8, columnspan=1, padx=10, pady=10, sticky="w")
        self.date_label = ttk.Label(self.root, text="", bootstyle="light")
        self.date_label.grid(row=8, columnspan=2, padx=10, pady=10, sticky="e")

        self.search_query_entry.bind("<Return>", lambda event: self.start_search())

        # Create menu
        self.create_menu()

    def create_menu(self):
        menu_bar = ttk.Menu(self.root)
        self.root.config(menu=menu_bar)
        theme_menu = ttk.Menu(menu_bar, tearoff=0)
        for theme in style.theme_names():
            theme_menu.add_command(label=theme, command=lambda t=theme: self.change_theme(t))
        menu_bar.add_cascade(label="Themes", menu=theme_menu)
        file_menu = ttk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Reset Credentials", command=self.load_credentials(resolve_path))
        file_menu.add_command(label="Update Credentials", command=self.user_update_credentials(resolve_path))
        file_menu.add_command(label="Options", command=self.show_options)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_application)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def quit_application(self):
        self.root.quit()

    def change_theme(self, theme_name):
        style.theme_use(theme_name)
        self.save_user_preferences(theme_name)

    def show_options(self):
        self.options_window = ttk.Toplevel(self.root)
        OptionsWindow(self.options_window, self)

    def start_search(self):
        self.load_credentials(resolve_path)
        search_type = self.search_type_combobox.get()
        query = self.search_query_entry.get()

        if not query:
            messagebox.showerror("Input Error", "Please enter a search query.")
            return

        try:
            self.qobuz.get_tokens()
            self.qobuz.initialize_client(self.email, self.password, self.qobuz.app_id, self.qobuz.secrets)
            results = self.qobuz.search_by_type(query, search_type, limit=self.limit, lucky=False)

            if results:
                for result in results:
                    ttk.Checkbutton(self.results_listbox, bootstyle="round-toggle",
                                    text=f"{result['text']}").pack(anchor=W)

                   # self.results_listbox.insert("end", result['text'])
                self.search_results = results
            else:
                messagebox.showinfo("No Results", "No results found for the given query.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_progressbar_complete(self):
        self.progressbar.stop()
        self.progressbar['value'] = 100

    def download_selected(self):
        selected_indices = [index for index, child in enumerate(self.results_listbox.winfo_children())
                            if child.instate(['selected'])]
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select at least one item to download.")
            return

        quality = self.quality_combobox.current() + 5  # Mapping to the quality values
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
                messagebox.showinfo("Download Complete", f"Download complete : {item['text']}")
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


def place_window_center(self):
    self.update_idletasks()
    w_height = self.winfo_height()
    w_width = self.winfo_width()
    s_height = self.winfo_screenheight()
    s_width = self.winfo_screenwidth()
    xpos = (s_width - w_width) // 2
    ypos = (s_height - w_height) // 2
    self.geometry(f'+{xpos}+{ypos}')


position_center = place_window_center

if __name__ == "__main__":
    style = Style()
    root = style.master
    #root = Window(alpha=1, size=(330, 570))
    #root.position_center()
    results = [...]  # Définir vos résultats ici
    app = QobuzDLApp(root, results, resolve_path)
    root.mainloop()
