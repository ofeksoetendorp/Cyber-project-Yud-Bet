from basicClasses import ClientSocket
import base64
import cv2
import numpy as np
import time
import imutils
import threading
#Need to add threading here
#Very likely that program tries to call destructor twice. Handle it. Maybe like we did in chat
#Maybe should add .decode somewhere
#Do both threads end? what to do to close? will the destructor be enough

class VideoClient(ClientSocket):
    _WIDTH = 400

    def __init__(self, server_ip, port,name):
        ClientSocket.__init__(self, server_ip, port)
        self._name = name
        self._fps, self._st, self._frames_to_count, self._cnt = (0, 0, 20, 0)
        self._vid = cv2.VideoCapture(0)

    def __del__(self):
        self._my_socket.sendto(b"Exit", (self._server_ip, self._port))
        self._vid.release()
        self._close()

    def _handle_data_from_server(self,data):
        data = base64.b64decode(data, ' /')
        npdata = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)
        frame = cv2.putText(frame, 'FPS: ' + str(self._fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        #Maybe make these measurements constant variables
        cv2.imshow("RECEIVING VIDEO", frame)

    def _handle_server_receptions(self):
        while True:
            data = self._receive_data()
            self._handle_data_from_server(data)
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

    def _add_name_to_image(self,img, position=(10, 30), font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(0, 0, 0),
                          thickness=2):
        cv2.putText(img, self._name, position, font, font_scale, color, thickness)

    def _get_frame(self):
        _,frame = self._vid.read()
        self._add_name_to_image(frame)
        return frame

    def _process_frame(self,frame):
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        #self._add_text_to_image(buffer) - doesn't work when the line is here, but does work in _get_data
        message = base64.b64encode(buffer)
        return message

    def _send_to_server(self,data):
        frame = data
        message = self._process_frame(frame)
        self._my_socket.sendto(message, (self._server_ip, self._port))
        return frame

    def _handle_sending_to_server(self):
        while self._vid.isOpened():
            frame = self._get_frame()
            frame = imutils.resize(frame, width=VideoClient._WIDTH)
            self._send_to_server(frame)
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

    def main(self):
        threads = []
        threads_closed = True
        self.connect()
        # Start threads for sending and receiving messages
        receive_thread = threading.Thread(target=self._handle_server_receptions)
        send_thread = threading.Thread(target=self._handle_sending_to_server )
        threads.append(receive_thread)
        threads.append(send_thread)
        receive_thread.start()
        send_thread.start()

        # Wait for both threads to finish
        receive_thread.join()
        send_thread.join()
        for thread in threads:
            if thread.is_alive():
                threads_closed = False
        if threads_closed:
            #self._close()
            pass

