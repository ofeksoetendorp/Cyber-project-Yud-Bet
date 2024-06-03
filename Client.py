from ChatClient import ChatClient
from VideoClient import VideoClient
from AudioClient import AudioClient
import concurrent.futures
import threading
import asyncio
import customtkinter as ctk
import os
#Doesn't seem to be huge difference in speed when using 1 port or 2
#Problem closing video socket
#Doesn't seem to be large difference whem using video_client in normal thread type
#Error when disconnecting now in server side.Ingenreral disconnecting sucks and video is very slow
#Maybe use asynco instead
#Read more about Future objects
#Read about other version
#Maybe don't use set function may not be safe
#For some reason the q is very important for video client to work
"""class Client:
    def __init__(self,server_ip, server_port1,server_port2,server_port3,client_ip,client_port1,client_port2,name):
    #Maybe client could have attribute name which will be passed to chatclient,videoclient
        self._chat_client = ChatClient(server_ip,server_port1,name)
        self._video_client = VideoClient(server_ip,server_port2,client_ip,client_port1,name)
        self._audio_client = AudioClient(server_ip, server_port3, client_ip, client_port2)
    def main(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self._chat_client.main)
            flag = future.result()
            print("flag=", flag)
            flag = next(future.result(), None)
            print("flag=", flag)

            if flag:
                #video_thread = threading.Thread(target=self._video_client.main)
                #   threads.append(receive_thread)
                #   threads.append(send_thread)
                #video_thread.start()
                executor.submit(self._video_client.main)
                executor.submit(self._audio_client.main)

                flag = next(future.result(), None)
                print("flag=", flag)
                if flag == "exit":
                    #flag = next(future.result(), None)
                    #print("flag=", flag)
                    #self._video_client.__del__()
                    self._video_client.set_close_threads(True)#Maybe don't use set function may not be safe
                    self._audio_client.set_close_threads(True)
                    #executor.shutdown()

                # Wait for both threads to finish"""
                #video_thread.join()
"""        chat_thread = threading.Thread(target=self._chat_client.main)
        video_thread = threading.Thread(target=self._video_client.main)
        # threads.append(receive_thread)
        # threads.append(send_thread)
        chat_thread.start()
        video_thread.start()

        # Wait for both threads to finish
        chat_thread.join()
        video_thread.join()"""


"""generator = self._chat_client.main()
            valid = next(generator,None)

            if not valid:
                return
            else:
                valid = next(generator,None)
                if valid == "exit":
                    return
                #Once user decides to exit chat, all the other threads must end.Potential options: global variable which once the chatClient ends it executed closing all the other threads
                #Another option is like clientChat main function closing the threads in the same way.Write destructors for all the classes
                threads"""


class LoginPage(ctk.CTkFrame):
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
        #9999,9990,9995,"10.0.0.16",8888,8889
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
    def __init__(self, parent, app):
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
    def __init__(self, parent, app, chat_client):
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
        self.video_client = VideoClient(self.app.login_page.server_ip_entry.get(), int(self.app.login_page.server_video_port_entry.get()), self.app.login_page.client_ip_entry.get(), int(self.app.login_page.client_video_port_entry.get()), self.app.login_page.name_entry.get(), self.video_label)#May need to pass on_exit_callback here as well and change codeto fit it
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
        #self.video_client.on_exit_callback = self.app.on_closing  # Set the exit callback
        #self.audio_client.on_exit_callback = self.app.on_closing  # Set the exit callback



        threading.Thread(target=self.chat_client.main).start()
        threading.Thread(target=self.video_client.main).start()
        threading.Thread(target=self.audio_client.main).start()

        # receive_thread = threading.Thread(target=self._receive_messages, name="ReceiveThread")
        # send_thread = threading.Thread(target=self._send_messages, name="SendThread")
        # receive_thread.start()
        # send_thread.start()

        # Wait for both threads to finish
        # receive_thread.join()



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

        self.destroy()
        os._exit(0)


if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()