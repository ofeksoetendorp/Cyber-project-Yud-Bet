from ChatServer import ChatServer
from VideoServer import VideoServer
from AudioServer import AudioServer
import threading
import customtkinter as ctk
import concurrent.futures
#Maybe make threads here more compatible with the Client counterpart
#Maybe use asynco instead

import customtkinter as ctk
import threading
import tkinter as tk


class Server:
    def __init__(self, server_ip, password, server_port1, server_port2, server_port3):
        self._chat_server = ChatServer(server_ip, server_port1, password)
        self._video_server = VideoServer(server_ip, server_port2)
        self._audio_server = AudioServer(server_ip, server_port3)

    def __del__(self):
        self._chat_server.__del__()
        self._video_server.__del__()
        self._audio_server.__del__()

    def main(self):
        chat_thread = threading.Thread(target=self._chat_server.main)
        chat_thread.start()

        video_thread = threading.Thread(target=self._video_server.main)
        video_thread.start()

        audio_thread = threading.Thread(target=self._audio_server.main)
        audio_thread.start()


class App(ctk.CTk):
    """A class that represents the app with all its pages.
    Attributes:
        pages: A static attribute of dictionary that its values are the pages of the app, with the page name as the key.
        geometry: The size of the app screen.
        title: The app's title.
    """
    pages = {}

    @staticmethod
    def change_page(next_page):
        """A static method that changes the display to the given page."""
        for page in App.pages.keys():
            if page != next_page:
                App.pages[page].pack_forget()
            else:
                App.pages[page].pack(fill="both", expand=True)

    def __init__(self):
        """Initialize the app with the geometry and title, and display the home page."""
        super().__init__()
        self.geometry("1024x768")
        self.title("Server Management")

        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        App.pages["config_page"] = ConfigPage(main_container)
        App.pages["running_page"] = RunningPage(main_container)

        App.pages["config_page"].pack(fill="both", expand=True)


class ConfigPage(ctk.CTkFrame):
    """A class for the configuration page."""

    def __init__(self, container):
        """Initialize the configuration page with input fields and a start button."""
        super().__init__(container)

        self.server_ip_entry = ctk.CTkEntry(self, placeholder_text="Server IP")
        self.server_ip_entry.grid(row=0, column=0, padx=10, pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.grid(row=1, column=0, padx=10, pady=10)

        self.server_port1_entry = ctk.CTkEntry(self, placeholder_text="Chat Server Port")
        self.server_port1_entry.grid(row=2, column=0, padx=10, pady=10)

        self.server_port2_entry = ctk.CTkEntry(self, placeholder_text="Video Server Port")
        self.server_port2_entry.grid(row=3, column=0, padx=10, pady=10)

        self.server_port3_entry = ctk.CTkEntry(self, placeholder_text="Audio Server Port")
        self.server_port3_entry.grid(row=4, column=0, padx=10, pady=10)

        self.start_button = ctk.CTkButton(self, text="Start Server", command=self.start_server)
        self.start_button.grid(row=5, column=0, padx=10, pady=10)

    def start_server(self):
        server_ip = self.server_ip_entry.get()
        password = self.password_entry.get()
        server_port1 = int(self.server_port1_entry.get())
        server_port2 = int(self.server_port2_entry.get())
        server_port3 = int(self.server_port3_entry.get())

        app.server = Server(server_ip, password, server_port1, server_port2, server_port3)
        server_thread = threading.Thread(target=app.server.main)
        server_thread.start()

        App.change_page("running_page")


class RunningPage(ctk.CTkFrame):
    """A class for the running server page."""

    def __init__(self, container):
        """Initialize the running page with a status label and a stop button."""
        super().__init__(container)

        self.status_label = ctk.CTkLabel(self, text="Server Running...")
        self.status_label.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ctk.CTkButton(self, text="Stop Server", command=self.stop_server)
        self.stop_button.grid(row=1, column=0, padx=10, pady=10)

    def stop_server(self):
        if app.server:
            del app.server
            app.server = None
            app.quit()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = App()
    app.mainloop()
