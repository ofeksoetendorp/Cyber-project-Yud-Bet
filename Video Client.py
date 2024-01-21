import cv2
import io
import socket
import struct
import time
import pickle
import zlib

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.0.0.8', 8485))
connection = client_socket.makefile('wb')

cam = cv2.VideoCapture(0)

cam.set(3, 200)
cam.set(4, 200)

img_counter = 0

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

while True:
    ret, frame = cam.read()
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    data = pickle.dumps(frame, 0)
    compressed_data = zlib.compress(data,9) #compresses by about 10% each image
    size = len(data)
    compressed_data_size = len(compressed_data)

    print("Original size = {}, compressed size = {}".format(size,len(compressed_data)))
    print("{}: {}".format(img_counter, compressed_data_size))
    client_socket.sendall(struct.pack(">L", compressed_data_size) + compressed_data)
    img_counter += 1

cam.release()

#class Client:
#    def __init__(self):
