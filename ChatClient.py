import socket
import json
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import threading
from basicClasses import ClientSocket
# Encryption key (must be 16 bytes long)
#How to get the message to the other sockets when user types exit to end
#Maybe connect should be done in constructor
# Should maybe turn self_close_threads into True in receive message break
class ChatClient(ClientSocket):
    _KEY = b'This is a key!!!'  # 16 bytes

    def __init__(self, server_ip, server_port,name):
        ClientSocket.__init__(self, server_ip, server_port, socket_type="tcp")
        self._name = name #Maybe should be passed as parameter as well

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
                print("" + message["payload"])
            elif message_type == "SYS":
                print("[System]:", message["payload"])
            elif message_type == "ACK":
                print("[System]:", message["payload"])
                #Should maybe turn self_close_threads into True here?
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

        # Send password to server
        password = input("Enter your password: ")
        self._send_message("PWD", password)

        # Receive verification message from server
        verification_message = self._receive_message()
        print(verification_message)
        if "Password verified" in verification_message["payload"]:
            return True
        self._close_threads = True
        return False

    def main(self):

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
