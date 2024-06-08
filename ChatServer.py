import socket
import hashlib
import json
import threading
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from basicClasses import ServerSocket


class ChatServer(ServerSocket):
    # המחלקה מנהלת את שליחת, קבלת הודעות של השרת

    _KEY = b'This is a key!!!'  # 16 bytes
    def __init__(self, server_ip, server_port,password):
        # הפונקצייה מקבלת את הפרמטריםserver_ip,server_port לServerSocket ומעבירה גם את סוג הסוקט שהוא TCP . הפונקצייה מקבלת גם את הססמא הרצויה
        ServerSocket.__init__(self, server_ip, server_port, "tcp")
        self._broadcast_messages = []  # List to store messages to be broadcasted
        self.__password = password #הססמא שנבחרה

    def set_close_threads(self, value):
        #פונקציית set ל close_threads
        self._close_threads = value

    def __del__(self):
        #פונקצייה סגירה למחלקה. משנים את ערך close threads לfalse בשביל שהפונקציות יפסיקו לרוץ, ואז סוגרים את השרת
        self._close_threads = True
        time.sleep(1)
        print("Closing Chat Server")
        self._close()

    def _verify_password(self,password):
        #הפונקציה מקבלת ססמא ובודקת האם זו הססמא הנכונה, דבר שהיא מחזירה
        return self.__password == password

    def _handle_client(self,client_socket, address):
        #הפונקצייה מקבלת את הסוקט הפתוח עם הלקוח, והכתובת שלו. היא רצה בלולאה כל עוד לא רוצים לסגור את את השרת,מקבלת ממנו הודעות ופועלת בהתאם לפרוטוקול. הפונקציה גם מעבירה הודעות שצריך להפיץ לפנוקציה שתטפל בכך
        username = None
        try:
            while not self._close_threads:
                # Receive message from client
                data = client_socket.recv(1024)
                if not data:
                    break

                # Decrypt and decode message
                decrypted_data = self._decrypt_message(data)
                message = json.loads(decrypted_data)

                # Process message based on type
                message_type = message.get("type")
                if message_type == "PWD":
                    password = message.get("payload")
                    if self._verify_password(password):
                        response = {"type": "ACK", "payload": "Password verified. Send your username."}
                        self._send_message(client_socket, response)
                    else:
                        username = ["Error"]  # "Error".Make this the username so that no user can actually usr this but also it passed the test of not being None
                        response = {"type": "ERR", "payload": "Invalid password. Connection closed."}
                        self._send_message(client_socket, response)
                        return
                elif message_type == "USR":
                    username = message.get("payload")
                    print(f"User '{username}' connected from {address}")
                    self._clients[client_socket] = (username, address)
                    self._send_notification(f"User '{username}' joined the chat.")
                elif message_type == "MSG":
                    chat_message = message.get("payload")
                    sender_username = self._clients.get(client_socket)[0]

                    self._broadcast_messages.append((sender_username, chat_message))
                elif message_type == "EXIT":
                    chat_message = message.get("payload")
                    sender_username = self._clients.get(client_socket)[0]
                    print(f"User '{sender_username}' disconnected from {address}")
                    self._send_message(client_socket, {"type": "ACK", "payload": "You disconnected. Have a good day."})
                    break  # Exit loop and close connection
        finally:
            # If client disconnects, remove from clients dictionary and broadcast the departure
            if username:
                del self._clients[client_socket]
                if username != ["Error"]:
                    self._send_notification(f"User '{username}' left the chat.")
                    # send_remaining_clients(f"User '{username}' left the chat.")
            client_socket.close()  # Removing this line seems to work.Nevermind.

    def _send_notification(self,notification_message):
        #הפונקציה מקבלת הודעה ומסווגת אותה כהודעת מערכת. לא מחזירה כלום
        self._broadcast_messages.append(("System", notification_message))


    def _send_broadcast_messages(self):
        #הפונקציה רצה בלולאה כל עוד לא סוגרים את השרת, ושולחת את כל ההודעות שצריך להפיץ לכלל הלקוחות. לא מחזירה כלום
        while not self._close_threads:
            print() #SEEMS THAT you can print anything and make it better #In both the ChatServer and AudioServer for some reason adding print seems to make the video become much faster
            if self._broadcast_messages:
                messages_to_send = self._broadcast_messages.copy()  # Copy the list to avoid race condition
                self._broadcast_messages.clear()  # Clear the original list
                # Broadcast message to all connected clients
                for client_socket, (username, _) in self._clients.items():
                    for sender_username, message in messages_to_send:
                        if sender_username == "System":
                            self._send_message(client_socket, {"type": "SYS", "payload": message})
                        else:
                            self._send_message(client_socket, {"type": "MSG", "payload": f"{sender_username}: {message}"})

    def _decrypt_message(self,encrypted_message):
        #מקבלת הודעה מקודדת ומפענחת אותה. מחזיקה הודעה מפוענחת
        cipher = AES.new(self._KEY, AES.MODE_CBC, encrypted_message[:16])
        decrypted_message = unpad(cipher.decrypt(encrypted_message[16:]), AES.block_size)
        return decrypted_message.decode()

    def _send_message(self,client_socket, message):
        #מקבלת את הסוקט הפתוח, והודעה, ממירה את ההודעה לשלב שאפשר לשלוח, מצפינה אותה, ושולח לשרת
        serialized_message = json.dumps(message)
        encrypted_message = self._encrypt_message(serialized_message)
        client_socket.send(encrypted_message)

    def _encrypt_message(self,message):
        #מקבלת הודעה ומצפינה אותה. מחזירה את ההודעה המוצפנת
        cipher = AES.new(self._KEY, AES.MODE_CBC)
        padded_message = pad(message.encode(), AES.block_size)
        encrypted_message = cipher.iv + cipher.encrypt(padded_message)
        return encrypted_message

    def main(self):
        #הפונקצייה לא מקבלת או מחזירה כלום. הפונקציה בעצם מריצה את כל תהליך השרת. היא עושה bind לכתובת, מתחילה את החוטים לשליחת ההודעות ללקוחות ולקבלת המידע מהלקוחות השונים (קבלת הלקוחות תהיה בלולאה ולכל לקוח ייפתח סוקט)
        self.start()


        # Start a thread to broadcast messages to clients
        broadcast_thread = threading.Thread(target=self._send_broadcast_messages)
        broadcast_thread.start()

        while not self._close_threads:
            try:
                client_socket,address = self.connect()

                # Start a new thread to handle the client
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket, address))
                client_thread.start()
            except OSError as e:
                print(f"OSError: {e}")
                if self._close_threads:
                    quit()

