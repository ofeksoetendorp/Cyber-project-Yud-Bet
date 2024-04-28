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
FS = 44100
OUTPUT = True
INPUT = True
FRAMES_PER_BUFFER = CHUNK
SAMPLE_FORMAT = pyaudio.paInt16  # 16 bits per sample.Maybe use bigger amount of bits per sample
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
#When disconnecting from chat we want to disconnect the rest of the program (videoclient,audioclient).Maybe use command to close program and use destructor to end nicely
#Write destructor for all the classes
#Maybe adjust size of images on client size to decrease size of each image, and then resize it on server side
#Maybe the size of the final image the server sends should be the same but the size of the pics in it changes based on the amount of clients
#Maybe on the client size do resize using cv2.resize and not imutils
#Maybe resize pics again for the client so that it fits well on the screen.Need to get screen width and height
#Decide what to do with the current client image resize that is happeninng right now
#What to do if someone doesn't have a camera? Not include him, or is it beyond the scope of the project
#Maybe these values should be const self._fps, self._st, self._frames_to_count, self._cnt = (0, 0, 20, 0)
##How to handle client trying to disconnect correctly in video,audio classes
#Handle clients disconnecting video,audio clients,server, client bind.
#Maybe use while loop until correct variables are entered clientSocket init function and maybe elsewhere
#Do you need to bind client socket? If so make necessary changes. Also do we need to send hello and if so how to handle it
#First check chat on other device, then combine video and chat, and then rewrite audio and then combine all three
#Clean up mess video both client and server and run on shahar's computer to check
# Maybe client could have attribute name which will be passed to chatclient,videoclient
#Add error class
#Handle closing server video and others
#Maybe add option of closing server video and others. Very similar to client disconnect probably
#Check chat with new changes
#Maybe connect should be done in constructor
#VideoCapture0 should maybe be in connect
#Differences between chatClient and VideoClient ending threads
#Add destructor to each class but particularly ChatClient
#Maybe don't use set function may not be safe
#Handle fps and what else
#For some reason the q is very important for video client to work
#Very serious problem on Shahar's computer maybe requiring ffget
#Very serious problem on Shahar's computer maybe requiring ffget
#Very serious problem on Shahar's computer maybe requiring ffget
#Audio Manager may need to inherit from abc.ABC and maybe not (maybe just needs () in the definition or nothinh)
#Maybe don't need to call destructor in audio client for audio manager
#Seems like there is a problem when connecting with wrong password, then right one, and then quitting
#Very weird seems to convert audioclient closethreads to true (or call destructor) without calling it. Makes sense actually. If it isn't a part of main then when the rest closes the audioclient will close as well

#You didn't handle it on the server side and didn't send a message from the server when a client disconnected. Also, the program doesn't stop on the client side when the user inputs exit. ALso printing order still weird.
#Add else case that will be error for server handle client function
#Make sure that you can select the password as the server and that it isn't always the word password
#Maybe when the system message is that you are connecting, don't print it
#Removing last line in handle_client server code seems to help - nevermind now
#Add UI to the chat.Also copy ti into chatclient,chatserver
#Printing order in client side
#Password make sure you can choose and that you can't see it in the code.Maybe make  it environment variable
#How to get the message to the other sockets when user types exit to end
#Very serious problem on Shahar's computer maybe requiring ffget

class Socket(abc.ABC):
    @abc.abstractmethod
    def __init__(self, server_ip, server_port, socket_type="UDP"):
        self._server_ip = server_ip
        self._server_port = server_port
        self._socket_type = socket_type.lower()
        if self._socket_type == "udp":
            self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
        elif self._socket_type == "tcp":
            self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            pass
            #error"Socket must be either tcp or udp"

    def connect(self):
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
    def __init__(self, server_ip, server_port, socket_type="UDP"):
        Socket.__init__(self, server_ip, server_port, socket_type)
        if self._socket_type == "udp":
            self._clients = []
        elif self._socket_type == "tcp":
            self._clients = {}  # {client_socket: (username, address)}
        else:
            #error
            pass

    def start(self):#Maybe should be protected and instead used in a function like main loop
        self._my_socket.bind((self._server_ip, self._server_port))
        print(f"Server listening on {self._server_ip}:{self._server_port}")
        if self._socket_type == "tcp":
            self._my_socket.listen(MAX_CLIENTS)
        #Add connecting to server and checking password here

    def connect(self):#Maybe should be protected and instead used in a function like main loop
        if self._socket_type == "udp":
            msg, client_addr = self._recv()
            self._clients.append(client_addr)
            print('GOT connection from ', client_addr, msg)  # Maybe remove message from here
            return client_addr
        elif self._socket_type == "tcp":
            client_socket, client_addr = self._my_socket.accept()
            print("Connection from:", client_addr)
            self._clients[client_socket] = ("Currently no name entered", client_addr)
            return client_socket,client_addr

    def _recv(self):
        return self._my_socket.recvfrom(BUFF_SIZE)
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
    def __init__(self, server_ip, server_port, client_ip=None, client_port=None, socket_type="UDP"):
        Socket.__init__(self, server_ip, server_port, socket_type)
        self._close_threads = False
        if self._socket_type == "udp":
            self._client_ip = client_ip
            self._client_port = client_port
            if self._client_ip is None or self._client_port is None:#Maybe use while loop until correct variables are entered
                raise ValueError("When the socket is UDP, client ip and client port must be actual values.")
                #Add except classes
    def connect(self): #Maybe should be protected and instead used in a function like main loop
        if self._socket_type == "udp":
            #message = b'Hello'
            #self._my_socket.sendto(message, (self._server_ip, self._port))
            #Maybe sending hello is necessary
            self._my_socket.bind((self._client_ip, self._client_port)) #Obviously this is temporary and may have to change
        elif self._socket_type == "tcp":
            self._my_socket.connect((self._server_ip, self._server_port))
        #connect to server. Maybe add a way to check if the data that is received is from the
        #actual server and maybe instead of sending "Hello" send password or maybe username and password
        #That is encoded in some way and saved in the server Database. Talk to Alon about these options

    """def send(self, data):
        self.client_socket.sendall(data.encode())"""
    def _send_data(self,data):
        if self._socket_type == "udp":
            self._my_socket.sendto(data, (self._server_ip, self._server_port))
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


class AudioManager:
    def __init__(self):
        #Maybe cut out server and each client sends directly to other clients
        #Make sure to encode information
        #Maybe these need to be public for socket classes
        self._p = pyaudio.PyAudio() #Maybe server doesn't need an output stream
        self._input_stream = self._p.open(format=SAMPLE_FORMAT,
                    channels=CHANNELS,
                    rate=FS,
                    frames_per_buffer=CHUNK,
                    input=INPUT)

        # Open output stream
        # Maybe server doesn't need an output stream
        self._output_stream = self._p.open(format=SAMPLE_FORMAT,
                               channels=CHANNELS,
                               rate=FS,
                               output=OUTPUT,
                               frames_per_buffer=CHUNK)

    def __del__(self): #Make sure that this is called once at the end of the socket classes
        print("Closing audio manager")
        self._input_stream.stop_stream()
        self._input_stream.close()
        self._output_stream.stop_stream()
        self._output_stream.close()
        self._p.terminate()

    def read(self):
        return self._input_stream.read(CHUNK)

    def write(self,data):
        self._output_stream.write(data)


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