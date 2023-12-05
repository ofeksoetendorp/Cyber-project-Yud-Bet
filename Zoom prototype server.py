import cv2, socket, struct, pickle
import numpy as np
FRAME_SHAPE = (480, 640, 3)
FRAME_DTYPE = np.uint8
FRAME_BYTE_SIZE = 921600
PORT = 8485
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', PORT))
server_socket.listen(10)

connection, addr = server_socket.accept()
camera = cv2.VideoCapture(0)  # Use 0 for built-in camera or provide a video file path

while True:
    framebytes = connection.recv(FRAME_BYTE_SIZE)
    #framebytes = np.frombuffer(connection.recv(FRAME_BYTE_SIZE))
    frame = np.ndarray(FRAME_SHAPE,FRAME_DTYPE,framebytes)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # After the loop release the cap object
#vid.release()
    # Destroy all the windows
cv2.destroyAllWindows()


connection.close()
server_socket.close()
