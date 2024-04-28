from ChatServer import ChatServer
from VideoServer import VideoServer
from AudioServer import AudioServer
import threading
import concurrent.futures
#Maybe make threads here more compatible with the Client counterpart
#Maybe use asynco instead

class Server:
    def __init__(self,server_ip, server_port1,server_port2,server_port3):
    #Maybe client could have attribute name which will be passed to chatclient,videoclient
        self._chat_server = ChatServer(server_ip,server_port1)
        self._video_server = VideoServer(server_ip,server_port2)
        self._audio_server = AudioServer(server_ip,server_port3)

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
