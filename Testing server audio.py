# This is server code to send video and audio frames over UDP

import socket
import threading, wave, pyaudio, time

host_name = socket.gethostname()
host_ip = "10.76.104.239"#server ip address, sometimes can use socket.gethostbyname(host_name) but better to just do ipconfig
print(host_ip)
port = 9633
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
print('Recording')


# For details visit: www.pyshine.com

def audio_stream_UDP():
    BUFF_SIZE = 65536 #Maybe reduce buffer size to reduce delay
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

    server_socket.bind((host_ip, (port)))
    CHUNK = 1024#original code was 10 * 1024 but then the audio was less smooth
    #wf = wave.open("temp.wav")
    p = pyaudio.PyAudio()
    print('server listening at', (host_ip, (port)), fs)#wf.getframerate())
    """stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    input=True,
                    frames_per_buffer=CHUNK)"""
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=CHUNK,
                    input=True)

    data = None
    sample_rate = fs#wf.getframerate()
    while True:
        msg, client_addr = server_socket.recvfrom(BUFF_SIZE)
        print('GOT connection from ', client_addr, msg)

        while True:
            data = stream.read(CHUNK)
            server_socket.sendto(data, client_addr)
            time.sleep(0.8 * CHUNK / sample_rate)


t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()

