"""from basicClasses import ClientSocket,AudioManager,CHUNK,CHANNELS,FS,FRAMES_PER_BUFFER,SAMPLE_FORMAT
import base64
import cv2
import numpy as np
import time
import imutils
import threading
import time
from queue import Queue

#Need to add threading here
#Very likely that program tries to call destructor twice. Handle it. Maybe like we did in chat
#Maybe should add .decode somewhere
#Do both threads end? what to do to close? will the destructor be enough
#Maybe on the client size do resize using cv2.resize and not imutils
#Handle clients disconnecting
#Maybe the problem is that the client socket is closed after it sends the final message and before the server receives the message, which may be problematic
# Maybe add closethreads set function so that when chat ends the rest can be closed easily as well
#bind client make better
#Maybe you can change it so that instead of just one key, if you enter "exit" it will end
#Since both of the displaying parts of the code access the same self._ variables it is possible there may be error in the values there. Also they are very similar so maybe should create a function for them.
#Maybe connect should be done in constructor
#VideoCapture0 should maybe be in connect or main
#Maybe add being able to disconnect in clinet using pressing q to see what happens when disconnecting and if destructor of audiomangager is called
#Audio quality very poor when there are 2 users connected. May need to change audiobits dictionary in clientAudio to have queues as values
#Audio quality very poor when there are 2 users connected. May need to change audiobits dictionary in clientAudio to have queues as values
#If you can't sound multiple sounds at once maybe add to a stack and sound one at a time
# May need to free queueu

#Is the audio okay when connecting from multiple clients but without video,chat? If so there may be a problem there. Otherwise it's probably here and maybe the problem is we are using the first audio to deetemine length

class AudioClient(ClientSocket):
    #Possibly need 4 threads. Read from server. Play from server.Read my mic.Send from mic
    def __init__(self, server_ip, server_port,client_ip,client_port):
        ClientSocket.__init__(self, server_ip, server_port,client_ip,client_port)
        self._audio_manager = AudioManager()
        self._audio_queue = Queue(maxsize = 0)

        #Maybe add closethreads set function so that when chat ends the rest can be closed easily as well

    def set_close_threads(self,value):
        self._close_threads = value

    def __del__(self):
        #May need to free queueu
        self._close_threads = True
        #Maybe add wait here so code doesn't collapse
        time.sleep(1)
        print("deleting audio client")
        self._my_socket.sendto(b"Exit", (self._server_ip, self._server_port))
        #self._audio_manager.__del__() #Maybe destructor will be called automatically
        self._close()

    def _handle_data_from_server(self,data):
        data = base64.b64decode(data, ' /')
        self._audio_manager.write(data)

    def _handle_playing_audio(self):
        while not self._close_threads:
            audio = self._audio_queue.get()
            print("Queue size when get = ",self._audio_queue.qsize())
            self._audio_manager.write(audio)

    def _handle_server_receptions(self):
        while not self._close_threads:
            data = self._receive_data()
            data = base64.b64decode(data, ' /')#Not originally in code, added with queue
            self._audio_manager.write(data)
            print("Queue size when put = ",self._audio_queue.qsize())
            if self._audio_queue.qsize()<=5:

                self._audio_queue.put(data)
            self._audio_manager.write(data)


            #time.sleep(0.2 * CHUNK / FS)

            #self._handle_data_from_server(data)

    def _get_audio_bit(self):
        return self._audio_manager.read()

    def _process_audio_bit(self,audio_bit):
        message = base64.b64encode(audio_bit)
        return message

    def _send_to_server(self,data):
        message = self._process_audio_bit(data)
        self._my_socket.sendto(message, (self._server_ip, self._server_port))
        time.sleep(0.2 * CHUNK / FS)#Maybe should remove this or put it on server side as well or in _handle_server_receptions

        return data

    def _handle_sending_to_server(self):
        while not self._close_threads:
            audio_bit = self._get_audio_bit()
            self._send_to_server(audio_bit)

    #async def main(self):
    def main(self):
        #threads = []
        #threads_closed = True
        self.connect()
        # Start threads for sending and receiving messages
        receive_thread = threading.Thread(target=self._handle_server_receptions)
        #play_audio_thread = threading.Thread(target=self._handle_playing_audio)
        send_thread = threading.Thread(target=self._handle_sending_to_server )
        #threads.append(receive_thread)
        #threads.append(send_thread)
        receive_thread.start()
        #play_audio_thread.start()
        send_thread.start()

        # Wait for both threads to finish
        receive_thread.join()
        #play_audio_thread.join()
        send_thread.join()
        #for thread in threads:
        #    if thread.is_alive():
        #        threads_closed = False
        #if threads_closed:
            #self._close()
            #Maybe should call destructor
        #    pass

"""

from basicClasses import ClientSocket,AudioManager,CHUNK,CHANNELS,FS,FRAMES_PER_BUFFER,SAMPLE_FORMAT
import base64
import cv2
import numpy as np
import time
import imutils
import threading
import time

#Need to add threading here
#Very likely that program tries to call destructor twice. Handle it. Maybe like we did in chat
#Maybe should add .decode somewhere
#Do both threads end? what to do to close? will the destructor be enough
#Maybe on the client size do resize using cv2.resize and not imutils
#Handle clients disconnecting
#Maybe the problem is that the client socket is closed after it sends the final message and before the server receives the message, which may be problematic
# Maybe add closethreads set function so that when chat ends the rest can be closed easily as well
#bind client make better
#Maybe you can change it so that instead of just one key, if you enter "exit" it will end
#Since both of the displaying parts of the code access the same self._ variables it is possible there may be error in the values there. Also they are very similar so maybe should create a function for them.
#Maybe connect should be done in constructor
#VideoCapture0 should maybe be in connect or main
#Maybe add being able to disconnect in clinet using pressing q to see what happens when disconnecting and if destructor of audiomangager is called
#Audio quality very poor when there are 2 users connected. May need to change audiobits dictionary in clientAudio to have queues as values
#Audio quality very poor when there are 2 users connected. May need to change audiobits dictionary in clientAudio to have queues as values

"""class AudioClient(ClientSocket):
    #Possibly need 4 threads. Read from server. Play from server.Read my mic.Send from mic
    def __init__(self, server_ip, server_port,client_ip,client_port):
        ClientSocket.__init__(self, server_ip, server_port,client_ip,client_port)
        self._audio_manager = AudioManager()
        self.start_time =time.time()
        self.current_time = self.start_time
        self.sending_amount = 0
        self.receiving_amount = 0

        #Maybe add closethreads set function so that when chat ends the rest can be closed easily as well

    def set_close_threads(self,value):
        self._close_threads = value

    def __del__(self):
        self._close_threads = True
        #Maybe add wait here so code doesn't collapse
        time.sleep(1)
        print("deleting audio client")
        self._my_socket.sendto(b"Exit", (self._server_ip, self._server_port))
        #self._audio_manager.__del__() #Maybe destructor will be called automatically
        self._close()

    def _handle_data_from_server(self,data):
        data = base64.b64decode(data, ' /')
        self._audio_manager.write(data)
        self.receiving_amount+=1

    def _handle_server_receptions(self):
        while not self._close_threads and (self.current_time-self.start_time< 10):
            data = self._receive_data()
            self._handle_data_from_server(data)
            self.current_time = time.time()
        print(f"sending amount = {self.sending_amount},receiving amount = {self.receiving_amount}")


    def _get_audio_bit(self):
        return self._audio_manager.read()

    def _process_audio_bit(self,audio_bit):
        message = base64.b64encode(audio_bit)
        return message

    def _send_to_server(self,data):
        message = self._process_audio_bit(data)
        self._my_socket.sendto(message, (self._server_ip, self._server_port))
        self.sending_amount+=1
        time.sleep(0.2 * CHUNK / FS)
        return data

    def _handle_sending_to_server(self):
        while not self._close_threads and (self.current_time-self.start_time< 10):
            audio_bit = self._get_audio_bit()
            self._send_to_server(audio_bit)
            self.current_time = time.time()
        print(f"sending amount = {self.sending_amount},receiving amount = {self.receiving_amount}")


    #async def main(self):
    def main(self):
        #threads = []
        #threads_closed = True
        self.connect()
        # Start threads for sending and receiving messages
        receive_thread = threading.Thread(target=self._handle_server_receptions)
        send_thread = threading.Thread(target=self._handle_sending_to_server )
        #threads.append(receive_thread)
        #threads.append(send_thread)
        receive_thread.start()
        send_thread.start()

        # Wait for both threads to finish
        receive_thread.join()
        send_thread.join()
        #for thread in threads:
        #    if thread.is_alive():
        #        threads_closed = False
        #if threads_closed:
            #self._close()
            #Maybe should call destructor
        #    pass
"""

import base64
import threading
import time
from basicClasses import ClientSocket, AudioManager, CHUNK, FS

class AudioClient(ClientSocket):

    def __init__(self, server_ip, server_port, client_ip, client_port):#,on_exit_callback = None):
        super().__init__(server_ip, server_port, client_ip, client_port)
        self._audio_manager = AudioManager()
        self._close_threads = False
        #self.on_exit_callback = on_exit_callback

    def set_close_threads(self, value):
        self._close_threads = value

    def __del__(self):
        self._close_threads = True
        time.sleep(1)
        print("deleting audio client")
        self._my_socket.sendto(b"Exit", (self._server_ip, self._server_port))
        self._close()

    def _handle_data_from_server(self, data):
        data = base64.b64decode(data, ' /')
        self._audio_manager.write(data)

    def _handle_server_receptions(self):
        while not self._close_threads:
            data = self._receive_data()
            if data:
                self._handle_data_from_server(data)
        #if self.on_exit_callback:
        #    self.on_exit_callback()

    def _get_audio_bit(self):
        return self._audio_manager.read()

    def _process_audio_bit(self, audio_bit):
        return base64.b64encode(audio_bit)

    def _send_to_server(self, data):
        message = self._process_audio_bit(data)
        self._my_socket.sendto(message, (self._server_ip, self._server_port))
        #time.sleep(0.2 * CHUNK / FS)  # Adjust sleep time for better real-time performance

    def _handle_sending_to_server(self):
        while not self._close_threads:
            audio_bit = self._get_audio_bit()
            self._send_to_server(audio_bit)

    def main(self):
        self.connect()
        receive_thread = threading.Thread(target=self._handle_server_receptions)
        send_thread = threading.Thread(target=self._handle_sending_to_server)
        receive_thread.start()
        send_thread.start()
        receive_thread.join()
        send_thread.join()
