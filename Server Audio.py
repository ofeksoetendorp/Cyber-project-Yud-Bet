import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new
import zlib
import pyaudio

HOST=''
PORT=8485
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn,addr=s.accept()

data = b""
payload_size = struct.calcsize(">L")
p = pyaudio.PyAudio()

stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                    output=True)
print("payload_size: {}".format(payload_size))
while True:
    
    print(data)
    # Read data in chunks

    # Play the sound by writing the audio data to the stream
    data = conn.recv(chunk) #probably works when receiving a different size like 4096 bytes
    stream.write(data)

    # Close and terminate the stream

stream.close()
p.terminate()

