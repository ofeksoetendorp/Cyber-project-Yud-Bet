from basicClasses import ServerSocket,CHUNK,CHANNELS,FS,FRAMES_PER_BUFFER,SAMPLE_FORMAT#,AudioManager
import base64
import cv2
import numpy as np
import time
import imutils
import threading
from pydub import AudioSegment
import pyaudio

#Need to add threading here
#How to handle client trying to disconnect correctly
#Maybe should open combinedpicture here to see what's going on
#How to handle case where client tries to connect with a message that isn't exit or pic
#Maybe should add .decode somewhere
#Maybe the check for Exit should be b"Exit" instead. Not sure how the message is passed
#Split code into parts
#Maybe using copy function on self.images.values is better than sendung them as they are to the function combineimages
#Handle clients disconnecting
#Maybe the problem is that the client socket is closed after it sends the final message and before the server receives the message, which may be problematic
#Is it taking out the wrong guy(the one who sent the message before it? Is the exception working? Maybe we should use a flag on client side?
#Why is it only an error when the same computer that runs the server tries to exit?
#Is it wise to collapse the program knowing that it sometimes blames the wrong guy
#Maybe open combined images here as well. Also clean up the mess from closing client
#Handle closing server
#Maybe add option of closing server. Very similar to client disconnect probably
#Maybe connect should be done in constructor
#If you can't sound multiple sounds at once maybe add to a stack and sound one at a time
#Is the audio okay when connecting from multiple clients but without video,chat? If so there may be a problem there. Otherwise it's probably here and maybe the problem is we are using the first audio to deetemine length

#Maybe send every piece of audio immediately instead of trying to combine them
#Have dictionary where each key is the address of a client and each value is a queue of the sounds of the clients
#After sound is read we need to remove(maybe remove just values and maybe clear entire dictionary) it. Also make sure that the combining function receives an array without None
#Maybe if we clear every time there won't be a None in there
# Maybe add sleep on server side

"""class AudioServer(ServerSocket):

    def __init__(self, server_ip, server_port):
        ServerSocket.__init__(self, server_ip, server_port)
        self._audio_bits = {}#Key is client address and value the last audio bit of each client maybe later change to#Have dictionary where each key is the address of a client and each value is a queue of the sounds of the clients
        #self._audio_manager = AudioManager()

    def _combine_audios(self,audio_data_list,sample_rate, sample_width, channels):
        audio_segments = []

        for audio_data in audio_data_list:
            # Convert audio data to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16)

            # Create AudioSegment from numpy array
            audio_segment = AudioSegment(
                audio_np.tobytes(),
                frame_rate=sample_rate,
                sample_width=sample_width,
                channels=channels
            )
            audio_segments.append(audio_segment)

        # Combine audio segments by overlaying
        longest_segment = max(audio_segments, key=len)

        # Initialize the combined audio with the longest segment
        combined = longest_segment

        # Overlay the other segments on the longest segment
        for audio_segment in audio_segments:
            if audio_segment is not longest_segment:
                combined = combined.overlay(audio_segment)

        return combined

    def _send_to_client(self,data,client_addr):
        frame = data
        message = base64.b64encode(frame)
        self._my_socket.sendto(message, client_addr)
        return frame

    def _handle_client(self):
        data = None
        try:
            while True:
                # Receive message from client
                try:
                    data,client_addr = self._recv()
                    if not data:
                        break
                    if data == b"Exit": #Maybe should be b"Exit"
                        print(f"User disconnected from {client_addr}!!!!!!!!!!!!!!")
                        if client_addr in self._clients:
                            self._clients.remove(client_addr)
                        if client_addr in self._audio_bits.keys():
                            del self._audio_bits[client_addr]

                    # Decrypt and decode message
                    #elif data maybe handle case client sends hello
                    else:
                        decrypted_data = base64.b64decode(data, ' /')
                        #print("_handle_client type = ",type(decrypted_data))
                        if client_addr not in self._clients:
                            self._clients.append(client_addr)
                        self._audio_bits[client_addr] = decrypted_data
                except:
                    print("Error")                    


                # Add else case that will be error
        except:
            print("Error")
            # If client disconnects, remove from clients dictionary and broadcast the departure

    def _send_broadcast_messages(self):
        while True:
            print()#In both the ChatServer and AudioServer for some reason adding print(or sleep) seems to make the video become much faster
            if self._audio_bits:
                # Broadcast message to all connected clients
                sounds_copy = list(self._audio_bits.values()).copy()#maybe later it will be the queue.head()).copy() #This may be better that just sending the values to the function directly
                self._audio_bits.clear()
                combined_sound = self._combine_audios(sounds_copy,sample_rate = FS,sample_width=2,channels=CHANNELS).raw_data#Very important to add raw data

                for client_addr in self._clients:
                    #for audio in sounds_copy:
                    #    self._send_to_client(audio, client_addr)
                    self._send_to_client(combined_sound,client_addr)
                #Maybe add sleep on server side
                time.sleep(0.2 * CHUNK / FS)  # Maybe should remove this or put it on server side as well or in _handle_server_receptions

                #self._audio_manager.write(combined_sound)


    def main(self):
        self.start()
        #self.connect()
        # Start a thread to broadcast messages to clients
        broadcast_thread = threading.Thread(target=self._send_broadcast_messages)
        broadcast_thread.start()

        #while True:
            #address = self.connect()

            # Start a new thread to handle the client
            #client_thread = threading.Thread(target=self._handle_client)
            #client_thread.start()
        client_thread = threading.Thread(target=self._handle_client)
        client_thread.start()

"""


from basicClasses import ServerSocket, CHUNK, CHANNELS, FS, FRAMES_PER_BUFFER, SAMPLE_FORMAT
import base64
import numpy as np
import time
import threading
from pydub import AudioSegment
import queue

class AudioServer(ServerSocket):

    def __init__(self, server_ip, server_port):
        super().__init__(server_ip, server_port)
        self._audio_bits = {}
        self._audio_queues = {}
        self._lock = threading.Lock()

    def set_close_threads(self, value):
        self._close_threads = value

    def __del__(self):
        self._close_threads = True
        time.sleep(1)
        print("Closing Audio Server")
        self._close()

    def _combine_audios(self, audio_data_list, sample_rate, sample_width, channels):
        audio_segments = []

        for audio_data in audio_data_list:
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            audio_segment = AudioSegment(
                audio_np.tobytes(),
                frame_rate=sample_rate,
                sample_width=sample_width,
                channels=channels
            )
            audio_segments.append(audio_segment)



        combined = audio_segments[0]
        for audio_segment in audio_segments[1:]:
            combined = combined.overlay(audio_segment)

        return combined.raw_data

    def _send_to_client(self, data, client_addr):
        message = base64.b64encode(data)
        self._my_socket.sendto(message, client_addr)

    def _handle_client(self):
        while not self._close_threads:
            try:
                data, client_addr = self._recv()
                if not data:
                    break
                if data == b"Exit":
                    with self._lock:
                        if client_addr in self._clients:
                            self._clients.remove(client_addr)
                        if client_addr in self._audio_queues:
                            del self._audio_queues[client_addr]
                else:
                    decrypted_data = base64.b64decode(data, ' /')
                    with self._lock:
                        if client_addr not in self._clients:
                            self._clients.append(client_addr)
                        if client_addr not in self._audio_queues:
                            self._audio_queues[client_addr] = queue.Queue()
                        self._audio_queues[client_addr].put(decrypted_data)
            except Exception as e:
                print(f"Error handling client {client_addr}: {e}")

    def _send_broadcast_messages(self):
        while not self._close_threads:
            with self._lock:
                audio_data_list = []
                for client_addr, audio_queue in self._audio_queues.items():
                    if not audio_queue.empty():
                        audio_data_list.append(audio_queue.get())

            if audio_data_list:
                combined_sound = self._combine_audios(audio_data_list, sample_rate=FS, sample_width=2, channels=CHANNELS)
                with self._lock:
                    for client_addr in self._clients:
                        self._send_to_client(combined_sound, client_addr)

            time.sleep(0.2 * CHUNK / FS)  # Adjust sleep time for better real-time performance

    def main(self):
        self.start()
        broadcast_thread = threading.Thread(target=self._send_broadcast_messages)
        broadcast_thread.start()

        client_thread = threading.Thread(target=self._handle_client)
        client_thread.start()


"""from basicClasses import ServerSocket, CHUNK, CHANNELS, FS, FRAMES_PER_BUFFER, SAMPLE_FORMAT
import base64
import numpy as np
import threading
from pydub import AudioSegment
import queue
import time

class AudioServer(ServerSocket):

    def __init__(self, server_ip, server_port):
        super().__init__(server_ip, server_port)
        self._audio_queues = {}
        self._clients = []
        self._lock = threading.Lock()

    def _combine_audios(self, audio_data_list, sample_rate, sample_width, channels):
        audio_segments = []

        for audio_data in audio_data_list:
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            audio_segment = AudioSegment(
                audio_np.tobytes(),
                frame_rate=sample_rate,
                sample_width=sample_width,
                channels=channels
            )
            audio_segments.append(audio_segment)

        if not audio_segments:
            return AudioSegment.silent(duration=100, frame_rate=sample_rate).raw_data

        combined = audio_segments[0]
        for audio_segment in audio_segments[1:]:
            combined = combined.overlay(audio_segment)

        return combined.raw_data

    def _send_to_client(self, data, client_addr):
        message = base64.b64encode(data)
        self._my_socket.sendto(message, client_addr)

    def _handle_client(self):
        while True:
            try:
                data, client_addr = self._recv()
                if not data:
                    break
                if data == b"Exit":
                    with self._lock:
                        if client_addr in self._clients:
                            self._clients.remove(client_addr)
                        if client_addr in self._audio_queues:
                            del self._audio_queues[client_addr]
                else:
                    decrypted_data = base64.b64decode(data, ' /')
                    with self._lock:
                        if client_addr not in self._clients:
                            self._clients.append(client_addr)
                        if client_addr not in self._audio_queues:
                            self._audio_queues[client_addr] = queue.Queue()
                        self._audio_queues[client_addr].put(decrypted_data)
            except Exception as e:
                print(f"Error handling client {client_addr}: {e}")

    def _send_broadcast_messages(self):
        while True:
            with self._lock:
                audio_data_list = []
                for client_addr, audio_queue in self._audio_queues.items():
                    if not audio_queue.empty():
                        audio_data_list.append(audio_queue.get())

            if audio_data_list:
                combined_sound = self._combine_audios(audio_data_list, sample_rate=FS, sample_width=2, channels=CHANNELS)
                with self._lock:
                    for client_addr in self._clients:
                        self._send_to_client(combined_sound, client_addr)

            time.sleep(0.02)  # Adjust sleep time for better real-time performance

    def main(self):
        self.start()
        broadcast_thread = threading.Thread(target=self._send_broadcast_messages)
        broadcast_thread.start()

        client_thread = threading.Thread(target=self._handle_client)
        client_thread.start()
"""

"""from basicClasses import ServerSocket, CHUNK, CHANNELS, FS, FRAMES_PER_BUFFER, SAMPLE_FORMAT
import base64
import numpy as np
import time
import threading
from pydub import AudioSegment
import queue

class AudioServer(ServerSocket):

    def __init__(self, server_ip, server_port):
        super().__init__(server_ip, server_port)
        self._audio_bits = {}
        self._audio_queues = {}
        self._lock = threading.Lock()

    def _combine_audios(self, audio_data_list, sample_rate, sample_width, channels):
        if not audio_data_list:
            return np.zeros(CHUNK, dtype=np.int16).tobytes()

        combined_audio = np.zeros(CHUNK, dtype=np.int16)

        for audio_data in audio_data_list:
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            combined_audio[:len(audio_np)] += audio_np

        # Ensure combined audio does not exceed the maximum value for int16
        combined_audio = np.clip(combined_audio, -32768, 32767)
        return combined_audio.tobytes()

    def _send_to_client(self, data, client_addr):
        message = base64.b64encode(data)
        self._my_socket.sendto(message, client_addr)

    def _handle_client(self):
        while True:
            try:
                data, client_addr = self._recv()
                if not data:
                    break
                if data == b"Exit":
                    with self._lock:
                        if client_addr in self._clients:
                            self._clients.remove(client_addr)
                        if client_addr in self._audio_queues:
                            del self._audio_queues[client_addr]
                else:
                    decrypted_data = base64.b64decode(data, ' /')
                    with self._lock:
                        if client_addr not in self._clients:
                            self._clients.append(client_addr)
                        if client_addr not in self._audio_queues:
                            self._audio_queues[client_addr] = queue.Queue()
                        self._audio_queues[client_addr].put(decrypted_data)
            except Exception as e:
                print(f"Error handling client {client_addr}: {e}")

    def _send_broadcast_messages(self):
        while True:
            with self._lock:
                audio_data_list = []
                for client_addr, audio_queue in self._audio_queues.items():
                    if not audio_queue.empty():
                        audio_data_list.append(audio_queue.get())

            if audio_data_list:
                combined_sound = self._combine_audios(audio_data_list, sample_rate=FS, sample_width=2, channels=CHANNELS)
                with self._lock:
                    for client_addr in self._clients:
                        self._send_to_client(combined_sound, client_addr)

            time.sleep(0.2 * CHUNK / FS)  # Adjust sleep time for better real-time performance

    def main(self):
        self.start()
        broadcast_thread = threading.Thread(target=self._send_broadcast_messages)
        broadcast_thread.start()

        client_thread = threading.Thread(target=self._handle_client)
        client_thread.start()

"""