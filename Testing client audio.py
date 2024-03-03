# Welcome to PyShine
# This is client code to receive video and audio frames over UDP

import socket
import threading, wave, pyaudio, time, queue

host_name = socket.gethostname()
host_ip = "10.0.0.22"#server ip address, sometimes can use socket.gethostbyname(host_name) but better to just do ipconfig
print(host_ip)
port = 9633
# For details visit: www.pyshine.com
q = queue.Queue(maxsize=2000)


def audio_stream_UDP():
    BUFF_SIZE = 65536#Maybe reduce buffer size to reduce delay
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    p = pyaudio.PyAudio()
    CHUNK = 1024#original code was 10 * 1024 but then the audio was less smooth
    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True,
                    frames_per_buffer=CHUNK)

    # create socket
    message = b'Hello'
    client_socket.sendto(message, (host_ip, port))
    socket_address = (host_ip, port)

    def getAudioData():
        while True:
            frame, _ = client_socket.recvfrom(BUFF_SIZE)
            q.put(frame)
            print('Queue size...', q.qsize())
            """Maybe should move these lines to lines 42,49 (into the other infinite while loop) like seen below to avoid errors of reading and writing
            to the queue at the same time. Could be better, just something to think about"""

    t1 = threading.Thread(target=getAudioData, args=())
    t1.start()
    #time.sleep(5)
    print('Now Playing...')
    """frame, _ = client_socket.recvfrom(BUFF_SIZE)
    q.put(frame)
    print('Queue size...', q.qsize())"""
    while True:
        frame = q.get()
        stream.write(frame)
        """frame, _ = client_socket.recvfrom(BUFF_SIZE)
            q.put(frame)
            print('Queue size...', q.qsize())"""

    client_socket.close()
    print('Audio closed')
    os._exit(1)


t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()

