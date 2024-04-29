import socket
import hashlib
import json
import threading
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from basicClasses import ServerSocket
#How to get the message to the other sockets when user types exit to end
#Add end server option
#Maybe connect should be done in constructor

class ChatServer(ServerSocket):
    _KEY = b'This is a key!!!'  # 16 bytes
    __PASSWORD = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    def __init__(self, server_ip, server_port):
        ServerSocket.__init__(self, server_ip, server_port, "tcp")
        self._broadcast_messages = []  # List to store messages to be broadcasted
        #clients = {}  # {client_socket: (username, address)}

    def _verify_password(self,password):
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Compare with stored hashed password
        stored_password = self.__PASSWORD
        return hashed_password == stored_password

    def _handle_client(self,client_socket, address):
        username = None
        try:
            while True:
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
                # Add else case that will be error
        finally:
            # If client disconnects, remove from clients dictionary and broadcast the departure
            if username:
                del self._clients[client_socket]
                if username != ["Error"]:
                    self._send_notification(f"User '{username}' left the chat.")
                    # send_remaining_clients(f"User '{username}' left the chat.")
            client_socket.close()  # Removing this line seems to work.Nevermind.

    def _send_notification(self,notification_message):
        self._broadcast_messages.append(("System", notification_message))

    # def send_remaining_clients(message):
    #    for client_socket, _ in clients.items():
    #        send_message(client_socket, {"type": "SYS", "payload": message})

    def _send_broadcast_messages(self):
        while True:
            print() #SEEMS THAT you can print anything and make it better #In both the ChatServer and AudioServer for some reason adding print seems to make the video become much faster
            #time.sleep(1) Maybe use sleep instead? Could be that the IO time is what saves us here from huge amount of iterations but that doesn't make sense since most of the time the list is empty and doesn't enter if statement
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
        cipher = AES.new(self._KEY, AES.MODE_CBC, encrypted_message[:16])
        decrypted_message = unpad(cipher.decrypt(encrypted_message[16:]), AES.block_size)
        return decrypted_message.decode()

    def _send_message(self,client_socket, message):
        serialized_message = json.dumps(message)
        encrypted_message = self._encrypt_message(serialized_message)
        client_socket.send(encrypted_message)

    def _encrypt_message(self,message):
        cipher = AES.new(self._KEY, AES.MODE_CBC)
        padded_message = pad(message.encode(), AES.block_size)
        encrypted_message = cipher.iv + cipher.encrypt(padded_message)
        return encrypted_message

    def main(self):
        self.start()


        # Start a thread to broadcast messages to clients
        broadcast_thread = threading.Thread(target=self._send_broadcast_messages)
        broadcast_thread.start()

        while True:
            client_socket,address = self.connect()

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=self._handle_client, args=(client_socket, address))
            client_thread.start()
