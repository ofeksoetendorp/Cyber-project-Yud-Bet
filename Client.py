from ChatClient import ChatClient
from VideoClient import VideoClient
from AudioClient import AudioClient
import threading
import customtkinter as ctk
import os



class LoginPage(ctk.CTkFrame):
    """A class for the login page."""

    def __init__(self, parent, app):
        """Initialize the login page with input fields and a start button."""
        #מקבלת את העמוד שיפתח אותה
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

        self.client_ip_label = ctk.CTkLabel(content_frame, text="Client IP")
        self.client_ip_label.pack(pady=3)
        self.client_ip_entry = ctk.CTkEntry(content_frame)
        self.client_ip_entry.pack(pady=3)

        self.client_video_port_label = ctk.CTkLabel(content_frame, text="Client Video Port")
        self.client_video_port_label.pack(pady=3)
        self.client_video_port_entry = ctk.CTkEntry(content_frame)
        self.client_video_port_entry.pack(pady=3)

        self.client_audio_port_label = ctk.CTkLabel(content_frame, text="Client Audio Port")
        self.client_audio_port_label.pack(pady=3)
        self.client_audio_port_entry = ctk.CTkEntry(content_frame)
        self.client_audio_port_entry.pack(pady=3)
        self.name_label = ctk.CTkLabel(content_frame, text="Username")
        self.name_label.pack(pady=3)
        self.name_entry = ctk.CTkEntry(content_frame)
        self.name_entry.pack(pady=3)

        self.password_label = ctk.CTkLabel(content_frame, text="Password")
        self.password_label.pack(pady=3)
        self.password_entry = ctk.CTkEntry(content_frame, show="*")
        self.password_entry.pack(pady=3)

        self.submit_button = ctk.CTkButton(content_frame, text="Submit", command=self.submit)
        self.submit_button.pack(pady=5)

    def submit(self):
        #פונקציה שצופעל כשהלקוח ילחץ על הכפתור submit, ותפעיל את הלקוח צ'אט. היא תשלח את הססמא ואם הססמא נכונה תפתח את עמוד הmain
        #ואם לא תעבור לעמוד השגיאה ותסגור את הלקוח צ'אט
        server_ip = self.server_ip_entry.get()
        server_port = int(self.server_chat_port_entry.get())
        name = self.name_entry.get()
        password = self.password_entry.get()

        chat_client = ChatClient(server_ip, server_port, name, password)
        chat_client.app = self.app  # Pass the app instance to the chat client
        if chat_client.start():
            self.app.show_main_page(chat_client)
        else:
            self.app.show_error_page()

class ErrorPage(ctk.CTkFrame):
    #עמוד למקרה שהלקוח מכניס ססמא לא נכונה לססמא
    def __init__(self, parent, app):
        #מקבלת את העמוד שיפתח את העמוד הזה
        #תיצור את עמוד השגיאה וכפתור חזרה אחורה
        super().__init__(parent)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        # Create a frame for content
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(expand=True)

        self.label = ctk.CTkLabel(content_frame, text="Invalid information. Please try again.")
        self.label.pack(pady=20)

        self.back_button = ctk.CTkButton(content_frame, text="Back to Login", command=self.app.show_login_page)
        self.back_button.pack(pady=20)



class MainPage(ctk.CTkFrame):
    #העמוד המרכזי שאליו נגיע לאחר הכנסת מידע נכון
    def __init__(self, parent, app, chat_client):
        #מקבלים את הפרטים לUI שדרכו נפתח את זה, ואת הchat client שנריץ את הפונקציית main שלו
        #נריץ גם את שני הלקוחות השונים ונציג ונשמיע הכל
        super().__init__(parent)

        self.app = app
        self.chat_client = chat_client
        self.grid(row=0, column=0, sticky="nsew")
        # Configure grid rows
        self.grid_rowconfigure(0, weight=1)  # Allocate more space to the video display
        self.grid_rowconfigure(1, weight=15)  # Allocate less space to the message display
        self.grid_rowconfigure(2, weight=1)  # Allocate less space to the message entry

        # Create a frame to hold the video display
        self.video_frame = ctk.CTkFrame(self)
        self.video_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(fill="both", expand=True)
        self.video_client = VideoClient(self.app.login_page.server_ip_entry.get(), int(self.app.login_page.server_video_port_entry.get()), self.app.login_page.client_ip_entry.get(), int(self.app.login_page.client_video_port_entry.get()), self.app.login_page.name_entry.get(), self.video_label)
        self.audio_client = AudioClient(self.app.login_page.server_ip_entry.get(), int(self.app.login_page.server_audio_port_entry.get()),self.app.login_page.client_ip_entry.get(), int(self.app.login_page.client_audio_port_entry.get()))

        # Create a frame to hold the message display
        self.message_display_frame = ctk.CTkFrame(self)
        self.message_display_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        self.message_display = ctk.CTkTextbox(self.message_display_frame, state=ctk.DISABLED)
        self.message_display.pack(fill="both", expand=True)

        # Create a frame to hold the message entry
        self.message_entry_frame = ctk.CTkFrame(self)
        self.message_entry_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.message_entry = ctk.CTkEntry(self.message_entry_frame)
        self.message_entry.pack(fill="x", expand=True)

        self.chat_client.message_display = self.message_display
        self.chat_client.message_entry = self.message_entry
        self.message_entry.bind("<Return>", self.chat_client._send_message_from_entry)

        self.chat_client.on_exit_callback = self.app.on_closing  # Set the exit callback




        threading.Thread(target=self.chat_client.main).start()
        threading.Thread(target=self.video_client.main).start()
        threading.Thread(target=self.audio_client.main).start()





class ClientApp(ctk.CTk):
    #מחלקת הUI הבסיסית
    def __init__(self):
        #ניצור את העמוד וגודלו, ואת שאר העמודים
        #נתחיל בפתיחת העמוד הראשי
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
        #פתח את עמוד Login
        self.login_page.tkraise()

    def show_error_page(self):
        #פתח את עמוד error

        self.error_page.tkraise()

    def show_main_page(self, chat_client):
        #פתח את עמוד mainPage

        if self.main_page is not None:
            self.main_page.destroy()
        self.main_page = MainPage(self, self, chat_client)
        self.main_page.tkraise()

    def on_closing(self):
        #פונקצייה שתקרא כשהלקוח יכניס את המילה exit לצ'אט או שהלקוח ילחץ על כפתור הסגירה בעמודים האחרים ויסגור את הלקוח ועמוד
        if self.main_page is not None:

            self.main_page.chat_client.__del__()
            self.main_page.video_client.__del__()
            self.main_page.audio_client.__del__()

        self.destroy()
        os._exit(0)


if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()