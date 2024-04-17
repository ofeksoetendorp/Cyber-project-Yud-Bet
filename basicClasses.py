import socket
import threading
import base64
import cv2
import numpy as np
import time
import imutils
import abc
BUFF_SIZE = 65536
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


class Socket(abc.ABC):
    @abc.abstractmethod
    def __init__(self, server_ip, port):
        self._server_ip = server_ip
        self._port = port
        self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

    def _connect(self):
        pass

    def _close(self):
        self._my_socket.close()
        print("Socket Closed:)")

    """@abc.abstractmethod
    def _main_loop(self):
        pass
    """


class Server(Socket):
    def __init__(self, server_ip, port):
        Socket.__init__(self,server_ip, port)
        self._clients = []

    def start(self):#Maybe should be protected and instead used in a function like main loop
        self._my_socket.bind((self._server_ip, self._port))
        print(f"Server listening on {self._server_ip}:{self._port}")
        #Add connecting to server and checking password here

    def connect(self):#Maybe should be protected and instead used in a function like main loop
        msg, client_addr = self._my_socket.recvfrom(BUFF_SIZE)
        self._clients.append(client_addr)
        print('GOT connection from ', client_addr, msg) #Maybe remove message from here

    @abc.abstractmethod
    def _get_data(self):
        pass

    def _handle_client(self, data,client_addr):
        self._my_socket.sendto(data, client_addr)

    @abc.abstractmethod
    def handle_all_clients(self):
        pass


class Client(Socket):
    def __init__(self, server_ip, port):
        Socket.__init__(self,server_ip,port)

    def connect(self): #Maybe should be protected and instead used in a function like main loop
        message = b'Hello'
        self._my_socket.sendto(message, (self._server_ip, self._port))
        #connect to server. Maybe add a way to check if the data that is received is from the
        #actual server and maybe instead of sending "Hello" send password or maybe username and password
        #That is encoded in some way and saved in the server Database. Talk to Alon about these options

    """def send(self, data):
        self.client_socket.sendall(data.encode())"""

    def _receive_data(self):
        packet,_ = self._my_socket.recvfrom(BUFF_SIZE)
        return packet

    @abc.abstractmethod
    def _handle_data(self,data):
        pass

    @abc.abstractmethod
    def handle_server(self):
        pass
        #Change and add more


class VideoClient(Client):
    def __init__(self, server_ip, port):
        Client.__init__(self,server_ip,port)
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


class AudioClient(Client):
    pass


class VideoServer(Server):
    WIDTH = 400

    def __init__(self, server_ip, port):
        Server.__init__(self, server_ip, port)
        self._fps, self._st, self._frames_to_count, self._cnt = (0, 0, 20, 0)
        self._vid = cv2.VideoCapture(0)

    def _get_data(self):
        _,frame = self._vid.read()
        return frame

    def _process_frame(self,frame):
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        message = base64.b64encode(buffer)
        return message

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
class AudioServer(Server):
    pass
# Example usage:


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