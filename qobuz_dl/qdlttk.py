import os
import configparser
import ttkbootstrap as ttk
from tkinter import messagebox, Listbox
from ttkbootstrap import Scrollbar, Progressbar
import logging
from qobuz_dl.core import QobuzDL
import threading
import hashlib
import requests
from os import getcwd


class CredentialWindow:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app_instance = app_instance
        self.parent.title("Enter Credentials")

        self.email_label = ttk.Label(parent, text="Email :")
        self.email_label.grid(row=0, column=0, padx=10, pady=10)
        self.email_entry = ttk.Entry(parent)
        self.email_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = ttk.Label(parent, text="Password :")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = ttk.Entry(parent, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.submit_button = ttk.Button(parent, text="Submit", command=self.submit_credentials)
        self.submit_button.grid(row=2, columnspan=2, padx=10, pady=10)

    def submit_credentials(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        # Save credentials to config file
        config = configparser.ConfigParser()
        config["Credentials"] = {"Email": email, "Password": hashlib.md5(password.encode("utf-8")).hexdigest()}

        with open("config.ini", "w") as configfile:
            config.write(configfile)

        messagebox.showinfo("Credentials Saved", "Credentials have been saved successfully.")
        self.parent.destroy()
        # Reload credentials
        self.app_instance.load_credentials()


# Set up logging
logging.basicConfig(level=logging.INFO)


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
    def __init__(self, root):
        self.root = root
        self.root.title("Qobuz Downloader")

        # Load or initialize QobuzDL instance
        self.qobuz = QobuzDL()

        # Default limit value
        self.limit = 20

        # Load credentials from file or ask user
        self.load_credentials()

        # Create widgets for user input
        self.create_widgets()

    def load_credentials(self):
        self.credentials_file = "config.ini"
        self.email = ""
        self.password = ""

        config = configparser.ConfigParser()

        if os.path.exists(self.credentials_file):
            config.read(self.credentials_file)
            if "Credentials" in config:
                self.email = config["Credentials"].get("Email", "")
                self.password = config["Credentials"].get("Password", "")

    def save_credentials(self):
        config = configparser.ConfigParser()
        config["Credentials"] = {"Email": self.email, "Password": hashlib.md5(self.password.encode("utf-8")).hexdigest()}

        with open(self.credentials_file, "w") as configfile:
            config.write(configfile)

    def reset_credentials(self):
        self.email = ""
        self.password = ""
        self.save_credentials()
        self.load_credentials()
        self.credential_window = ttk.Window(self.root)
        CredentialWindow(self.credential_window, self)

    def uptodate_credentials(self):
        url = "https://raw.githubusercontent.com/GiGiDKR/qobuz-dl-gui/main/qobuz_dl/config.ini"
        directory = getcwd()
        filename = os.path.join(getcwd(), 'config.ini')
        r = requests.get(url)

        f = open(filename, 'wb')
        f.write(r.content)
    def create_widgets(self):

        # Search type selection
        self.search_type_label = ttk.Label(self.root, text="Search Type :")
        self.search_type_label.grid(row=0, column=0, padx=10, pady=10)
        self.search_type_combobox = ttk.Combobox(self.root, style='dark.TCombobox',
                                                 values=["album", "track", "artist", "playlist"])
        self.search_type_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.search_type_combobox.current(0)  # Default to "album"

        # Search query input
        self.search_query_label = ttk.Label(self.root, text="Search :")
        self.search_query_label.grid(row=1, column=0, padx=10, pady=10)
        self.search_query_entry = ttk.Entry(self.root, style='dark.TEntry')
        self.search_query_entry.grid(row=1, column=1, padx=10, pady=10)

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
            bootstyle="primary",
            variable=current_value,
            command=slider_changed
        )
        self.slider.grid(row=3, columnspan=2, padx=10, pady=10)

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

        # Results listbox with scrollbar
        self.results_frame = ttk.Frame(self.root)
        self.results_frame.grid(row=5, columnspan=2, padx=10, pady=10)

        self.results_scrollbar = Scrollbar(self.results_frame, orient="vertical", bootstyle="primary-round")
        self.results_listbox = Listbox(self.results_frame, selectmode="multiple",
                                       yscrollcommand=self.results_scrollbar.set, height=15, width=50)
        self.results_scrollbar.config(command=self.results_listbox.yview)

        self.results_listbox.pack(side="left", fill="both", expand=True)
        self.results_scrollbar.pack(side="right", fill="y")

        # Download selected button
        self.download_button = ttk.Checkbutton(self.root, text="Download Selected", bootstyle="success-toolbutton",
                                               takefocus=1, command=self.download_selected)
        self.download_button.grid(row=6, columnspan=2, padx=10, pady=10)

        self.progressbar = Progressbar(self.root, mode='determinate')
        self.progressbar.grid(row=7, columnspan=2, padx=10, pady=10)

        # Create menu
        self.create_menu()

    def create_menu(self):
        menu_bar = ttk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = ttk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Reset Credentials", command=self.reset_credentials)
        file_menu.add_command(label="Up-to-date Credentials", command=self.uptodate_credentials)
        file_menu.add_command(label="Options", command=self.show_options)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_application)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def show_options(self):
        # Add functionality to show options here
        pass

    def quit_application(self):
        self.root.quit()

    def show_options(self):
        self.options_window = ttk.Toplevel(self.root)
        OptionsWindow(self.options_window, self)

    def start_search(self):
        search_type = self.search_type_combobox.get()
        query = self.search_query_entry.get()

        if not query:
            messagebox.showerror("Input Error", "Please enter a search query.")
            return

        try:
            self.qobuz.get_tokens()
            self.qobuz.initialize_client(self.email, self.password, self.qobuz.app_id, self.qobuz.secrets)
            results = self.qobuz.search_by_type(query, search_type, limit=self.limit, lucky=False)

            self.results_listbox.delete(0, "end")
            if results:
                for result in results:
                    self.results_listbox.insert("end", result['text'])
                self.search_results = results
            else:
                messagebox.showinfo("No Results", "No results found for the given query.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_progressbar_complete(self):
        self.progressbar.stop()
        self.progressbar['value'] = 100

    def remove_downloaded_items(self, downloaded_items):
        remaining_items = [item for item in self.search_results if item not in downloaded_items]
        self.search_results = remaining_items
        self.update_results_listbox(remaining_items)

    def download_selected(self):
        selected_indices = self.results_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select at least one item to download.")
            return

        quality = self.quality_combobox.current() + 5  # Mapping to the quality values
        self.qobuz.quality = quality

        selected_items = [self.search_results[i] for i in selected_indices]
        selected_urls = [item['url'] for item in selected_items]

        self.progressbar.start()

        # Démarre le téléchargement dans un thread séparé
        threading.Thread(target=self.download_thread, args=(selected_items, selected_urls)).start()

    def update_results_listbox(self, items):
        self.results_listbox.delete(0, "end")
        for item in items:
            self.results_listbox.insert("end", item['text'])

    def download_thread(self, selected_items, selected_urls):
        try:
            downloaded_items = []
            for item, url in zip(selected_items, selected_urls):
                self.qobuz.download_list_of_urls([url])
                downloaded_items.append(item)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.update_progressbar_complete()
            self.remove_downloaded_items(downloaded_items)
            messagebox.showinfo("Download Complete", f"Download complete : {item['text']}")


# Quality options mapping
Qualities = {
    5: "MP3",
    6: "16 bit, 44.1kHz",
    7: "24 bit, <96kHz",
    27: "24 bit, >96kHz",
}

if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = QobuzDLApp(root)
    root.mainloop()
