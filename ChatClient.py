import socket
import json
import time
import asyncio

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import threading
from basicClasses import ClientSocket
from VideoClient import VideoClient
import customtkinter as ctk
from AudioClient import AudioClient
# Encryption key (must be 16 bytes long)
#How to get the message to the other sockets when user types exit to end
#Maybe connect should be done in constructor
# Should maybe turn self_close_threads into True in receive message break
"""class ChatClient(ClientSocket):
    _KEY = b'This is a key!!!'  # 16 bytes

    def __init__(self, server_ip, server_port,name,password, message_display, message_entry):
        ClientSocket.__init__(self, server_ip, server_port, socket_type="tcp")
        self._name = name #Maybe should be passed as parameter as well
        self.__password = password
        self.message_display = message_display
        self.message_entry = message_entry
        self.message_entry.bind("<Return>", self._send_message_from_entry)


    def set_close_threads(self,value):
        self._close_threads = value

    def __del__(self):
        self._close_threads = True
        #Maybe add wait here so code doesn't collapse
        #time.sleep(1)
        print("Closing client")
        self._close()

    def _send_message(self, message_type, payload):
        message = {"type": message_type, "payload": payload}
        serialized_message = json.dumps(message)
        encrypted_message = self._encrypt_message(serialized_message)
        self._my_socket.send(encrypted_message)

    def _receive_message(self):
        data = self._my_socket.recv(1024)
        decrypted_data = self._decrypt_message(data)
        return json.loads(decrypted_data)

    def _encrypt_message(self,message):
        cipher = AES.new(self._KEY, AES.MODE_CBC)
        padded_message = pad(message.encode(), AES.block_size)
        encrypted_message = cipher.iv + cipher.encrypt(padded_message)
        return encrypted_message

    def _decrypt_message(self,encrypted_message):
        cipher = AES.new(self._KEY, AES.MODE_CBC, encrypted_message[:16])
        decrypted_message = unpad(cipher.decrypt(encrypted_message[16:]), AES.block_size)
        return decrypted_message.decode()

    def _receive_messages(self):
        while not self._close_threads:
            message = self._receive_message()
            message_type = message.get("type")
            if message_type == "MSG":
                self._display_message(message["payload"])
            elif message_type == "SYS":
                self._display_message(f"[System]: {message['payload']}")
            elif message_type == "ACK":

                self._display_message(f"[System]: {message['payload']}")
                self._close_threads = True
                break

    def _send_messages(self):
        while not self._close_threads:
            message = input("Enter your message (type 'exit' to quit): ")
            if message.lower() == "exit":
                self._send_message("EXIT", "exit")
                self._close_threads = True
                break
            if len(json.dumps({"type": "MSG", "payload": message})) > 1024:
                print("Message too long. Please send a shorter message.")
                continue
            self._send_message("MSG", message)

    def start(self):
        self.connect()
        print("Chat start")
        #self.message_entry.bind("<Return>", self._send_message_from_entry)


        # Send password to server
        #password = input("Enter your password: ")
        self._send_message("PWD", self.__password)

        # Receive verification message from server
        verification_message = self._receive_message()
        print(verification_message)
        if "Password verified" in verification_message["payload"]:
            return True
        self._close_threads = True
        return False

    def _send_message_from_entry(self, event):
        print("send message from entry")
        message = self.message_entry.get()
        self.message_entry.delete(0, ctk.END)
        if message.lower() == "exit":
            self._send_message("EXIT", "exit")
            self._close_threads = True
            return
        if len(json.dumps({"type": "MSG", "payload": message})) > 1024:
            self._display_message("Message too long. Please send a shorter message.")
            return
        self._send_message("MSG", message)

    def _display_message(self, message):
        print("display message")

        self.message_display.configure(state=ctk.NORMAL)
        self.message_display.insert(ctk.END, message + "\n")
        self.message_display.configure(state=ctk.DISABLED)
        self.message_display.see(ctk.END)

    #async def main(self):
    def main(self):
        print("Chat Main")

        #threads = []
        #threads_closed = True
        verified = self.start()
        yield verified
        if verified:

            self._send_message("USR", self._name)

            # Start threads for sending and receiving messages
            receive_thread = threading.Thread(target=self._receive_messages)
            send_thread = threading.Thread(target=self._send_messages)
         #   threads.append(receive_thread)
         #   threads.append(send_thread)
            receive_thread.start()
            send_thread.start()

            # Wait for both threads to finish
            receive_thread.join()
            send_thread.join()
        #for thread in threads:
        #    if thread.is_alive():
        #        threads_closed = False
        #if threads_closed:
        #    self._close()
        yield "exit"
        return



class App(ctk.CTk):
    def __init__(self,server_ip, server_port,client_ip,client_port, name,password):
        super().__init__()
        self.geometry("1024x768")
        self.title("Video Client")
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.top_frame = ctk.CTkFrame(main_container, fg_color="blue")
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.bottom_frame = ctk.CTkFrame(main_container, fg_color="red")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)

        self.video_label = ctk.CTkLabel(self.top_frame, text="")
        self.video_label.pack(padx=20, pady=20)

        self.chat_display = ctk.CTkTextbox(self.bottom_frame, state=ctk.DISABLED)
        self.chat_display.pack(side="top", fill="both", expand=True, padx=20, pady=5)

        self.message_entry = ctk.CTkEntry(self.bottom_frame)
        self.message_entry.pack(side="bottom", fill="x", padx=20, pady=5)

        #self.video_client = VideoClient(server_ip, server_port,client_ip,client_port, name,self.video_label)
        self.chat_client = ChatClient(server_ip, server_port, name,password,self.chat_display,self.message_entry)#, self.chat_display, self.message_entry)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        print("App __init__")


    def on_closing(self):
        #self.video_client.set_close_threads(True)
        self.chat_client.set_close_threads(True)
        #self.video_client.__del__()
        self.chat_client.__del__()
        self.destroy()

    def start_clients(self):
        #threading.Thread(target=self.video_client.main).start()
        print("Starting chat client main thread")
        #chat_thread = threading.Thread(target=self.chat_client.main, name="ChatClientMainThread")
        #chat_thread.start()
        verified = self.chat_client.main()
        flag = verified
        print("flag=", flag)
        flag = next(verified, None)
        print("flag=", flag)
        flag = next(verified, None)
        print("flag=", flag)
        print("Chat client main thread started")

    def main(self):
        print("App main")
        self.after(0, self.start_clients)

        self.mainloop()
"""



import socket
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import threading
from basicClasses import ClientSocket
import customtkinter as ctk

class ChatClient(ClientSocket):
    _KEY = b'This is a key!!!'  # 16 bytes

    def __init__(self, server_ip, server_port, name, password, message_display=None, message_entry=None,on_exit_callback = None):
        super().__init__(server_ip, server_port, socket_type="tcp")
        self._name = name
        self.__password = password
        self.message_display = message_display
        self.message_entry = message_entry
        self._close_threads = False
        self.on_exit_callback = on_exit_callback


    def set_close_threads(self, value):
        self._close_threads = value

    def __del__(self):
        self._close_threads = True
        time.sleep(1)
        print("Closing client")
        self._close()

    def _send_message(self, message_type, payload):
        message = {"type": message_type, "payload": payload}
        serialized_message = json.dumps(message)
        encrypted_message = self._encrypt_message(serialized_message)
        self._my_socket.send(encrypted_message)

    def _receive_message(self):
        data = self._my_socket.recv(1024)
        decrypted_data = self._decrypt_message(data)
        return json.loads(decrypted_data)

    def _encrypt_message(self, message):
        cipher = AES.new(self._KEY, AES.MODE_CBC)
        padded_message = pad(message.encode(), AES.block_size)
        encrypted_message = cipher.iv + cipher.encrypt(padded_message)
        return encrypted_message

    def _decrypt_message(self, encrypted_message):
        cipher = AES.new(self._KEY, AES.MODE_CBC, encrypted_message[:16])
        decrypted_message = unpad(cipher.decrypt(encrypted_message[16:]), AES.block_size)
        return decrypted_message.decode()

    def _receive_messages(self):
        print("Starting to receive messages")
        while not self._close_threads:
            try:
                message = self._receive_message()
                message_type = message.get("type")
                if message_type == "MSG":
                    self._display_message(message["payload"])
                elif message_type == "SYS":
                    self._display_message(f"[System]: {message['payload']}")
                elif message_type == "ACK":
                    self._display_message(f"[System]: {message['payload']}")
                    self._close_threads = True
                    break
            except Exception as e:
                print(f"Error receiving messages: {e}")
                break
        print("Stopped receiving messages")

    def _send_messages(self):
        print("Starting to send messages")
        while not self._close_threads:
            try:
                message = input("Enter your message (type 'exit' to quit): ")
                if message.lower() == "exit":
                    self._send_message("EXIT", "exit")
                    self._close_threads = True
                    break
                if len(json.dumps({"type": "MSG", "payload": message})) > 1024:
                    self._display_message("Message too long. Please send a shorter message.")
                    continue
                self._send_message("MSG", message)
            except Exception as e:
                print(f"Error sending messages: {e}")
                break
        print("Stopped sending messages")

    def start(self):
        try:
            self.connect()
            print("Connected to server")

            # Send password to server
            self._send_message("PWD", self.__password)

            # Receive verification message from server
            verification_message = self._receive_message()
            print(f"Verification message received: {verification_message}")
            if "Password verified" in verification_message["payload"]:
                return True
            self._close_threads = True
            return False
        except Exception as e:
            print(f"Error starting chat client: {e}")
            return False

    def _send_message_from_entry(self, event):
        if not self._close_threads:
            message = self.message_entry.get()
            self.message_entry.delete(0, ctk.END)
            if message.lower() == "exit":
                self._send_message("EXIT", "exit")
                self._close_threads = True
                #self.app.on_closing()  # Close the window
                if self.on_exit_callback:
                    self.on_exit_callback()  # Trigger the callback to close the window
                return
            if len(json.dumps({"type": "MSG", "payload": message})) > 1024:
                self._display_message("Message too long. Please send a shorter message.")
                return
            self._send_message("MSG", message)

    def _display_message(self, message):
        self.message_display.configure(state=ctk.NORMAL)
        self.message_display.insert(ctk.END, message + "\n")
        self.message_display.configure(state=ctk.DISABLED)
        self.message_display.see(ctk.END)

    def main(self):
        print("Chat client main started")
        #verified = self.start()
        verified = True
        if verified:
            print("Password verified, starting message threads")
            self._send_message("USR", self._name)

            # Start threads for sending and receiving messages
            receive_thread = threading.Thread(target=self._receive_messages, name="ReceiveThread")
            #send_thread = threading.Thread(target=self._send_messages, name="SendThread")
            receive_thread.start()
            #send_thread.start()

            # Wait for both threads to finish
            receive_thread.join()
            #send_thread.join()
        print("Chat client main finished")


"""class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        self.server_ip_label = ctk.CTkLabel(self, text="Server IP")
        self.server_ip_label.pack(pady=10)
        self.server_ip_entry = ctk.CTkEntry(self)
        self.server_ip_entry.pack(pady=10)

        self.server_port_label = ctk.CTkLabel(self, text="Server Port")
        self.server_port_label.pack(pady=10)
        self.server_port_entry = ctk.CTkEntry(self)
        self.server_port_entry.pack(pady=10)

        self.name_label = ctk.CTkLabel(self, text="Username")
        self.name_label.pack(pady=10)
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(pady=10)

        self.password_label = ctk.CTkLabel(self, text="Password")
        self.password_label.pack(pady=10)
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.pack(pady=10)

        self.submit_button = ctk.CTkButton(self, text="Submit", command=self.submit)
        self.submit_button.pack(pady=20)

    def submit(self):
        server_ip = self.server_ip_entry.get()
        server_port = int(self.server_port_entry.get())
        name = self.name_entry.get()
        password = self.password_entry.get()

        chat_client = ChatClient(server_ip, server_port, name, password)
        if chat_client.start():
            self.app.show_chat_page(chat_client)
        else:
            self.app.show_error_page()

class ErrorPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        self.label = ctk.CTkLabel(self, text="Password was wrong. Please try again.")
        self.label.pack(pady=20)

        self.back_button = ctk.CTkButton(self, text="Back to Login", command=self.app.show_login_page)
        self.back_button.pack(pady=20)

class ChatPage(ctk.CTkFrame):
    def __init__(self, parent, app, chat_client):
        super().__init__(parent)
        self.app = app
        self.chat_client = chat_client
        self.grid(row=0, column=0, sticky="nsew")

        self.message_display = ctk.CTkTextbox(self, state=ctk.DISABLED)
        self.message_display.pack(side="top", fill="both", expand=True, padx=20, pady=5)

        self.message_entry = ctk.CTkEntry(self)
        self.message_entry.pack(side="bottom", fill="x", padx=20, pady=5)

        self.chat_client.message_display = self.message_display
        self.chat_client.message_entry = self.message_entry
        self.message_entry.bind("<Return>", self.chat_client._send_message_from_entry)

        self.chat_client.on_exit_callback = self.app.on_closing  # Set the exit callback

        threading.Thread(target=self.chat_client.main).start()
        #receive_thread = threading.Thread(target=self._receive_messages, name="ReceiveThread")
        # send_thread = threading.Thread(target=self._send_messages, name="SendThread")
        #receive_thread.start()
        # send_thread.start()

        # Wait for both threads to finish
        #receive_thread.join()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1024x768")
        self.title("Chat Client")

        self.login_page = LoginPage(self, self)
        self.error_page = ErrorPage(self, self)
        self.chat_page = None

        self.login_page.tkraise()

    def show_login_page(self):
        self.login_page.tkraise()

    def show_error_page(self):
        self.error_page.tkraise()

    def show_chat_page(self, chat_client):
        if self.chat_page is not None:
            self.chat_page.destroy()
        self.chat_page = ChatPage(self, self, chat_client)
        self.chat_page.tkraise()

    def on_closing(self):
        if self.chat_page is not None:
            self.chat_page.chat_client.__del__()
        self.destroy()

"""

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

"""class ChatPage(ctk.CTkFrame):
    def __init__(self, parent, app, chat_client):
        super().__init__(parent)
        self.app = app
        self.chat_client = chat_client
        self.grid(row=0, column=0, sticky="nsew")

        # Create a frame to hold the chat display
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(side="top", fill="both", expand=True)

        # Create a frame to hold the message entry
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.pack(side="bottom", fill="x", padx=20, pady=5)

        self.message_display = ctk.CTkTextbox(self.top_frame, state=ctk.DISABLED)
        self.message_display.pack(side="top", fill="both", expand=True, padx=20, pady=5)

        #self.message_entry = ctk.CTkEntry(self.bottom_frame)
        self.message_entry = ctk.CTkEntry(self.top_frame)

        self.message_entry.pack(side="bottom", fill="x", padx=20, pady=5)

        self.chat_client.message_display = self.message_display
        self.chat_client.message_entry = self.message_entry
        self.message_entry.bind("<Return>", self.chat_client._send_message_from_entry)

        self.chat_client.on_exit_callback = self.app.on_closing  # Set the exit callback
        threading.Thread(target=self.chat_client.main).start()
        # receive_thread = threading.Thread(target=self._receive_messages, name="ReceiveThread")
        # send_thread = threading.Thread(target=self._send_messages, name="SendThread")
        # receive_thread.start()
        # send_thread.start()

        # Wait for both threads to finish
        # receive_thread.join()
"""

class ChatPage(ctk.CTkFrame):
    def __init__(self, parent, app, chat_client):
        """super().__init__(parent)
        self.app = app
        self.chat_client = chat_client
        self.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=7)
        self.grid_rowconfigure(1, weight=1)  # Make the bottom frame take four-fifths of the screen
        self.grid_columnconfigure(0, weight=1)

        # Create a frame to hold the chat display (top one-fifth)
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=5)
        self.video_label = ctk.CTkLabel(self.top_frame, text="")
        self.video_label.pack(padx=5, pady=5)
        #self.video_client = VideoClient("10.0.0.16", 9990, "10.0.0.16", 8888, "leb", self.top_frame)#May need to pass on_exit_callback here as well and change codeto fit it
        self.video_client = VideoClient("10.0.0.16", 9990, "10.0.0.16", 8888, "leb", self.video_label)#May need to pass on_exit_callback here as well and change codeto fit it
        self.audio_client = AudioClient("10.0.0.16",9995,"10.0.0.16",8889)
        #self.message_display = ctk.CTkTextbox(self.top_frame, state=ctk.DISABLED)
        #self.message_display.pack(fill="both", expand=True)

        # Create a frame to hold the message entry and make it red (bottom four-fifths)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="red")
        self.bottom_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)

        self.message_display = ctk.CTkTextbox(self.bottom_frame, state=ctk.DISABLED)
        self.message_display.pack(fill="both", expand=True)

        self.message_entry = ctk.CTkEntry(self.bottom_frame)
        self.message_entry.pack(fill="x", padx=20, pady=5)

        self.chat_client.message_display = self.message_display
        self.chat_client.message_entry = self.message_entry
        self.message_entry.bind("<Return>", self.chat_client._send_message_from_entry)

        self.chat_client.on_exit_callback = self.app.on_closing  # Set the exit callback
        threading.Thread(target=self.chat_client.main).start()
        threading.Thread(target=self.video_client.main).start()
        threading.Thread(target=self.audio_client.main).start()"""
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



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1024x768")
        self.title("Chat Client")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.login_page = LoginPage(self, self)
        self.error_page = ErrorPage(self, self)
        self.chat_page = None

        self.login_page.tkraise()

    def show_login_page(self):
        self.login_page.tkraise()

    def show_error_page(self):
        self.error_page.tkraise()

    def show_chat_page(self, chat_client):
        if self.chat_page is not None:
            self.chat_page.destroy()
        self.chat_page = ChatPage(self, self, chat_client)
        self.chat_page.tkraise()

    def on_closing(self):
        if self.chat_page is not None:
            self.chat_page.chat_client.set_close_threads(True)
            self.chat_page.video_client.set_close_threads(True)
            self.chat_page.audio_client.set_close_threads(True)

            #self.chat_page.video_client.__del__()
            #self.chat_page.audio_client.__del__()

        self.destroy()