from basicClasses import ServerSocket,CHUNK,CHANNELS,FS,FRAMES_PER_BUFFER,SAMPLE_FORMAT
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

#Maybe send every piece of audio immediately instead of trying to combine them
#Have dictionary where each key is the address of a client and each value is a queue of the sounds of the clients
#After sound is read we need to remove(maybe remove just values and maybe clear entire dictionary) it. Also make sure that the combining function receives an array without None
#Maybe if we clear every time there won't be a None in there
class AudioServer(ServerSocket):

    def __init__(self, server_ip, server_port):
        ServerSocket.__init__(self, server_ip, server_port)
        self._audio_bits = {}#Key is client address and value the last audio bit of each client maybe later change to#Have dictionary where each key is the address of a client and each value is a queue of the sounds of the clients

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
        combined = audio_segments[0]
        for audio_segment in audio_segments[1:]:
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
                    """"#This may be actively harmful consudering when this is called
                    print("\nBad guy who disconnected = ",client_addr,f"\n number of clients = {len(self._clients)},number of images = {len(self._images)}\n")
                    if client_addr in self._clients:
                        self._clients.remove(client_addr)
                    if client_addr in self._images.keys():
                        del self._images[client_addr]
                    print(f"\n number of clients = {len(self._clients)},number of images = {len(self._images)}\n")"""


                # Add else case that will be error
        except:
            print("Error")
            # If client disconnects, remove from clients dictionary and broadcast the departure

    def _send_broadcast_messages(self):
        while True:
            print()
            if self._audio_bits:
                # Broadcast message to all connected clients
                sounds_copy = list(self._audio_bits.values()).copy()#maybe later it will be the queue.head()).copy() #This may be better that just sending the values to the function directly
                self._audio_bits.clear()
                combined_sound = self._combine_audios(sounds_copy,sample_rate = FS,sample_width=2,channels=CHANNELS).raw_data#Very important to add raw data
                for client_addr in self._clients:
                    self._send_to_client(combined_sound,client_addr)

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


