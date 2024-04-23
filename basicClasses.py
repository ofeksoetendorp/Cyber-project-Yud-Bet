import socket
import threading
import base64
import cv2
import numpy as np
import time
import imutils
import pyaudio
import abc
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

BUFF_SIZE = 65536
CHUNK = 1024  # original code was 10 * 1024 but then the audio was less smooth
CHANNELS = 2
RATE = 44100
OUTPUT = True
FRAMES_PER_BUFFER = CHUNK
MAX_CLIENTS = 50 #Maybe not necessary
#maybe add virtual class for socket classes with the basic functions that are shared
# by the server,client classes
#Make all attributes protected or private
#Maybe add my_ip for basic Socket and then add an attribute server_ip for Client and also won't have to use
#server_ip for Server attribute
#Maybe add some more broad Video,Audio classes
#Add main_loop for all classes (Client, Server more specifically)
#Maybe make instances of VideoServer,AudioServer static (singleton) so there will only be 1 instance of them
#Vid needs to be an attribute of VideoServer Class
#Maybe in close function of Server add disconnecting from each client also (maybe in the other socket for RTCP)
#Create main loop function for both Client and Server class in a way that their children won't have to rewrite it.
#Maybe add class for Audio and audio server,client will inherit it as well as Client,Server class
#Maybe make it so every server class has a list of Client Class, and that each client has a name, and each Server has it's own password which is a private attribute
#When connecting the chat to the other code note that the way currently to disconnect is press q, but we want it to be to press on some close button or type exit (we want to be able to use q for something other that exiting).
#Maybe in the chat get the password from a and not directly written in the python file. That way it's more safe
#Maybe add an exception class
#For sending video, first check that you can add name(text) when it is sent by the server code right now
#Connect the chat to the other code and add parameter name which will be used by the server for the images
#Make sure that the pictures create a grid and not a row.
#Add requesting username as a part of the process
#Now that we have chat server,client classes maybe socket shouldn't have udp socket since these are tcp sockets
#Split code to different classes , or use an if everywhere
#Maybe should add else case to all function if socket_type isn't udp or tcp
#Write chatClient,chatServer as classes. Then write final class, and find some way to get the names to the client/server classes of tje video class
#What to do with chat server clients variable? Maybe make just basic class dictionary, or maybe make a change in the server code somehow
#Add self and make all funcs protected chat server

#You didn't handle it on the server side and didn't send a message from the server when a client disconnected. Also, the program doesn't stop on the client side when the user inputs exit. ALso printing order still weird.
#Add else case that will be error for server handle client function
#Make sure that you can select the password as the server and that it isn't always the word password
#Maybe when the system message is that you are connecting, don't print it
#Removing last line in handle_client server code seems to help - nevermind now
#Add UI to the chat.Also copy ti into chatclient,chatserver
#Printing order in client side


class Socket(abc.ABC):
    @abc.abstractmethod
    def __init__(self, server_ip, port,socket_type="UDP"):
        self._server_ip = server_ip
        self._port = port
        self._socket_type = socket_type.lower()
        if self._socket_type == "udp":
            self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
        elif self._socket_type == "tcp":
            self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            pass
            #error"Socket must be either tcp or udp"

    def _connect(self):
        pass

    def _close(self):
        self._my_socket.close()
        print("Socket Closed:)")

    """@abc.abstractmethod
    def _main_loop(self):
        pass
    """

    @abc.abstractmethod
    def main(self):
        pass


class ServerSocket(Socket):
    def __init__(self, server_ip, port,socket_type="UDP"):
        Socket.__init__(self,server_ip, port,socket_type)
        if self._socket_type == "udp":
            self._clients = []
        elif self._socket_type == "tcp":
            self._clients = {}  # {client_socket: (username, address)}
        else:
            #error
            pass

    def start(self):#Maybe should be protected and instead used in a function like main loop
        self._my_socket.bind((self._server_ip, self._port))
        print(f"Server listening on {self._server_ip}:{self._port}")
        if self._socket_type == "tcp":
            self._my_socket.listen(MAX_CLIENTS)
        #Add connecting to server and checking password here

    def connect(self):#Maybe should be protected and instead used in a function like main loop
        if self._socket_type == "udp":
            msg, client_addr = self._my_socket.recvfrom(BUFF_SIZE)
            self._clients.append(client_addr)
            print('GOT connection from ', client_addr, msg)  # Maybe remove message from here
        elif self._socket_type == "tcp":
            client_socket, client_addr = self._my_socket.accept()
            print("Connection from:", client_addr)
            self._clients[client_socket] = ("Currently no name entered", client_addr)
            return client_socket,client_addr
""""
    @abc.abstractmethod
    def _get_data(self):
        pass

    @abc.abstractmethod
    def _handle_client(self, data,client_addr):
        pass

    @abc.abstractmethod
    def handle_all_clients(self):
        pass
"""

class ClientSocket(Socket):
    def __init__(self, server_ip, port,socket_type="UDP"):
        Socket.__init__(self,server_ip,port,socket_type)

    def connect(self): #Maybe should be protected and instead used in a function like main loop
        if self._socket_type == "udp":
            message = b'Hello'
            self._my_socket.sendto(message, (self._server_ip, self._port))
        elif self._socket_type == "tcp":
            self._my_socket.connect((self._server_ip, self._port))
        #connect to server. Maybe add a way to check if the data that is received is from the
        #actual server and maybe instead of sending "Hello" send password or maybe username and password
        #That is encoded in some way and saved in the server Database. Talk to Alon about these options

    """def send(self, data):
        self.client_socket.sendall(data.encode())"""
    def _send_data(self,data):
        if self._socket_type == "udp":
            self._my_socket.sendto(data, (self._server_ip, self._port))
        elif self._socket_type == "tcp":
            self._my_socket.send(data)
        #Maybe should be written differently, and maybe should be abstract method

    def _receive_data(self):
        if self._socket_type == "udp":
            packet,_ = self._my_socket.recvfrom(BUFF_SIZE)
        elif self._socket_type == "tcp":
            packet = self._my_socket.recv(1024)
        return packet
"""
    @abc.abstractmethod
    def _handle_data(self,data):
        pass

    @abc.abstractmethod
    def handle_server(self):
        pass
        #Change and add more
"""


class VideoClient(ClientSocket):
    def __init__(self, server_ip, port):
        ClientSocket.__init__(self, server_ip, port)
        self._fps,self._st,self._frames_to_count,self._cnt = (0,0,20,0)

    def _handle_data(self,data):
        data = base64.b64decode(data, ' /')
        npdata = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)
        frame = cv2.putText(frame, 'FPS: ' + str(self._fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        #Maybe make these measurements constant variables
        cv2.imshow("RECEIVING VIDEO", frame)

    def handle_server(self):
        while True:
            data = self._receive_data()
            self._handle_data(data)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self._close()
                break
            if self._cnt == self._frames_to_count:
                try:
                    self._fps = round(self._frames_to_count / (time.time() - self._st))
                    self._st = time.time()
                    self._cnt = 0
                except:
                    pass
            self._cnt += 1


class AudioClient(ClientSocket):
    def __init__(self, server_ip, port):
        ClientSocket.__init__(self, server_ip, port)
        self._fps, self._st, self._frames_to_count, self._cnt = (0, 0, 20, 0)

    def _handle_data(self, data):
        data = base64.b64decode(data, ' /')
        npdata = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)
        frame = cv2.putText(frame, 'FPS: ' + str(self._fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        # Maybe make these measurements constant variables
        cv2.imshow("RECEIVING VIDEO", frame)

    def handle_server(self):
        while True:
            data = self._receive_data()
            self._handle_data(data)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self._close()
                break
            if self._cnt == self._frames_to_count:
                try:
                    self._fps = round(self._frames_to_count / (time.time() - self._st))
                    self._st = time.time()
                    self._cnt = 0
                except:
                    pass
            self._cnt += 1


class VideoServer(ServerSocket):
    WIDTH = 400

    def __init__(self, server_ip, port):
        ServerSocket.__init__(self, server_ip, port)
        self._fps, self._st, self._frames_to_count, self._cnt = (0, 0, 20, 0)
        self._vid = cv2.VideoCapture(0)

    def _get_data(self):
        _,frame = self._vid.read()
        self._add_text_to_image(frame)
        return frame

    def _process_frame(self,frame):
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

        #self._add_text_to_image(buffer) - doesn't work when the line is here, but does work in _get_data
        message = base64.b64encode(buffer)
        return message

    def _add_text_to_image(self,img, text="Bob", position=(10, 30), font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(0, 0, 0),
                          thickness=2):
        cv2.putText(img, text, position, font, font_scale, color, thickness)

    def _handle_client(self,data, client_addr):
        frame = data
        message = self._process_frame(frame)
        self._my_socket.sendto(message, client_addr)
        return frame

    def handle_all_clients(self):
        while self._vid.isOpened():
            frame =self._get_data()
            frame = imutils.resize(frame, width=VideoServer.WIDTH)
            for client_addr in self._clients:
                self._handle_client(frame,client_addr)
            frame = cv2.putText(frame, 'FPS: ' + str(self._fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('TRANSMITTING VIDEO', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self._close()
                break
            if self._cnt == self._frames_to_count:
                try:
                    self._fps = round(self._frames_to_count / (time.time() - self._st))
                    self._st = time.time()
                    self._cnt = 0
                except:
                    pass
            self._cnt += 1


class Audio(abc.ABC):
    def __init__(self):
        self._p = pyaudio.PyAudio()


class AudioServer(ServerSocket):
    pass


class ChatClient(ClientSocket):
    _KEY = b'This is a key!!!'  # 16 bytes

    def __init__(self, server_ip, port):
        ClientSocket.__init__(self, server_ip, port,"tcp")
        self._name = input("Enter your username: ")

    def get_name(self):
        return self._name


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
        while True:
            message = self._receive_message()
            message_type = message.get("type")
            if message_type == "MSG":
                print("" + message["payload"])
            elif message_type == "SYS":
                print("[System]:", message["payload"])
            elif message_type == "ACK":
                print("[System]:", message["payload"])
                break

    def _send_messages(self):
        while True:
            message = input("Enter your message (type 'exit' to quit): ")
            if message.lower() == "exit":
                self._send_message("EXIT", "exit")
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
        return False

    def main(self):

        threads = []
        threads_closed = True
        verified = self.start()
        yield verified
        if verified:

            self._send_message("USR", self._name)

            # Start threads for sending and receiving messages
            receive_thread = threading.Thread(target=self._receive_messages)
            send_thread = threading.Thread(target=self._send_messages,)
            threads.append(receive_thread)
            threads.append(send_thread)
            receive_thread.start()
            send_thread.start()

            # Wait for both threads to finish
            receive_thread.join()
            send_thread.join()
        for thread in threads:
            if thread.is_alive():
                threads_closed = False
        if threads_closed:
            self._close()


class ChatServer(ServerSocket):
    _KEY = b'This is a key!!!'  # 16 bytes
    __PASSWORD = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    def __init__(self, server_ip, port):
        ServerSocket.__init__(self, server_ip, port,"tcp")
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

"""
class Client:
    def __init__(self,server_ip, port):
        self._chat_client = chatClient
        generator = self._chatClient.main()
        valid = next(verified,None)

        if not valid:
            exit()
        else:
            self._video_client = VideoClient(server_ip, port,self._chatClient.getName())
            self._audio_client = AudioClient(server_ip, port)
            next(generator,None)
            threads

    def


class Server:
    pass

"""
"""
if __name__ == "__main__":
    server = Server('127.0.0.1', 8888)
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    client1 = Client('127.0.0.1', 8888)
    client1.connect()
    client1.send("Hello from client 1")

    client2 = Client('127.0.0.1', 8888)
    client2.connect()
    client2.send("Hello from client 2")

    client1.close()
    client2.close()

    server_thread.join()
"""

"""
basic tests server:

from basicClasses import VideoServer
inst = VideoServer("10.0.0.16",9999)
inst.start()
inst.connect()
inst.handle_all_clients()


basic tests client:

from basicClasses import VideoClient
inst = VideoClient("10.0.0.16",9999)
inst.connect()
inst.handle_server()

"""
