from ChatServer import ChatServer
from VideoServer import VideoServer
from AudioServer import AudioServer
import threading
import customtkinter as ctk
import concurrent.futures
#Maybe make threads here more compatible with the Client counterpart
#Maybe use asynco instead

class Server:
    def __init__(self,server_ip,password, server_port1,server_port2,server_port3):
    #Maybe client could have attribute name which will be passed to chatclient,videoclient
        self._chat_server = ChatServer(server_ip,server_port1,password)
        self._video_server = VideoServer(server_ip,server_port2)
        self._audio_server = AudioServer(server_ip,server_port3)

    def __del__(self):
        self._chat_server.__del__()
        self._video_server.__del__()
        self._audio_server.__del__()

    def main(self):
        """with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self._chat_server.main)
            executor.submit(self._video_server.main)"""
        chat_thread = threading.Thread(target=self._chat_server.main)
        chat_thread.start()

        # while True:
        # address = self.connect()

        # Start a new thread to handle the client
        # client_thread = threading.Thread(target=self._handle_client)
        # client_thread.start()
        video_thread = threading.Thread(target=self._video_server.main)
        video_thread.start()
        audio_thread = threading.Thread(target=self._audio_server.main)
        audio_thread.start()


class ServerPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        # Create a frame for content
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(expand=True)

        self.server_ip_label = ctk.CTkLabel(content_frame, text="Server IP")
        self.server_ip_label.pack(pady=3)
        self.server_ip_entry = ctk.CTkEntry(content_frame)
        self.server_ip_entry.pack(pady=3)

        self.server_chat_port_label = ctk.CTkLabel(content_frame, text="Server Chat Port")
        self.server_chat_port_label.pack(pady=3)
        self.server_chat_port_entry = ctk.CTkEntry(content_frame)
        self.server_chat_port_entry.pack(pady=3)

        self.server_video_port_label = ctk.CTkLabel(content_frame, text="Server Video Port")
        self.server_video_port_label.pack(pady=3)
        self.server_video_port_entry = ctk.CTkEntry(content_frame)
        self.server_video_port_entry.pack(pady=3)

        self.server_audio_port_label = ctk.CTkLabel(content_frame, text="Server Audio Port")
        self.server_audio_port_label.pack(pady=3)
        self.server_audio_port_entry = ctk.CTkEntry(content_frame)
        self.server_audio_port_entry.pack(pady=3)

        self.password_label = ctk.CTkLabel(content_frame, text="Password")
        self.password_label.pack(pady=3)
        self.password_entry = ctk.CTkEntry(content_frame, show="*")
        self.password_entry.pack(pady=3)

        self.submit_button = ctk.CTkButton(content_frame, text="Confirm", command=self.confirm)
        self.submit_button.pack(pady=5)

    def confirm(self):
        server_ip = self.server_ip_entry.get()
        server_chat_port = int(self.server_chat_port_entry.get())
        password = self.password_entry.get()
        server = Server(server_ip,password,server_chat_port,int(self.server_video_port_entry.get()),int(self.server_audio_port_entry.get()))
        #chat_server = ChatServer(server_ip, server_port,password)
        #video_server = VideoServer(server_ip,int(self.server_video_port_entry.get()))
        #audio_server = AudioServer(server_ip,int(self.server_audio_port_entry.get()))
        #chat_thread = threading.Thread(target=chat_server.main)
        #chat_thread.start()

        # while True:
        # address = self.connect()

        # Start a new thread to handle the client
        # client_thread = threading.Thread(target=self._handle_client)
        # client_thread.start()
        #video_thread = threading.Thread(target=video_server.main)
        #video_thread.start()
        #audio_thread = threading.Thread(target=audio_server.main)
        #audio_thread.start()
        #chat_client.app = self.app  # Pass the app instance to the chat client
        server.main()

        self.app.show_server_running_page(server)



"""
class ClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1024x768")
        self.title("Chat Client")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.login_page = LoginPage(self, self)
        self.error_page = ErrorPage(self, self)
        self.main_page = None

        self.login_page.tkraise()

    def show_login_page(self):
        self.login_page.tkraise()

    def show_error_page(self):
        self.error_page.tkraise()

    def show_main_page(self, chat_client):
        if self.main_page is not None:
            self.main_page.destroy()
        self.main_page = MainPage(self, self, chat_client)
        self.main_page.tkraise()

    def on_closing(self):
        if self.main_page is not None:
            #self.main_page.chat_client.set_close_threads(True)
            #self.chat_page.video_client.set_close_threads(True)
            #self.chat_page.audio_client.set_close_threads(True)
            self.main_page.chat_client.__del__()
            self.main_page.video_client.__del__()
            self.main_page.audio_client.__del__()

        self.destroy()"""


class ServerRunningPage(ctk.CTkFrame):
    def __init__(self, parent, app, server):
        super().__init__(parent)
        self.app = app
        self.server = server
        self.grid(row=0, column=0, sticky="nsew")

        self.label = ctk.CTkLabel(self, text="Server is running...")
        self.label.pack(pady=20)

        self.stop_button = ctk.CTkButton(self, text="Close Server", command=self.on_closing)
        self.stop_button.pack(pady=20)
    """def stop_server(self):
        # Implement logic to stop the server if necessary
        print("Stopping the server")
        if self.server is not None:
            # self.main_page.chat_client.set_close_threads(True)
            # self.chat_page.video_client.set_close_threads(True)
            # self.chat_page.audio_client.set_close_threads(True)
            self.server.__del__()
        self.destroy()"""
    def on_closing(self):
        if self.server is not None:
            self.server.__del__()

            #self.chat_page.video_client.__del__()
            #self.chat_page.audio_client.__del__()

        self.destroy()
        exit()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1024x768")
        self.title("Server Control Panel")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.server_page = ServerPage(self, self)
        self.server_running_page = None

        self.server_page.tkraise()

    def show_server_page(self):
        self.server_page.tkraise()

    def show_server_running_page(self, server):
        if self.server_running_page is not None:
            self.server_running_page.destroy()
        self.server_running_page = ServerRunningPage(self, self, server)
        self.server_running_page.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()