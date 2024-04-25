from basicClasses import ServerSocket
import base64
import cv2
import numpy as np
import time
import imutils
import threading
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

class VideoServer(ServerSocket):
    _TARGET_HEIGHT = 300
    _TARGET_WIDTH = 500
    _FINAL_HEIGHT = 500
    _FINAL_WIDTH = 1000

    def __init__(self, server_ip, port):
        ServerSocket.__init__(self, server_ip, port)
        #self._fps, self._st, self._frames_to_count, self._cnt = (0, 0, 20, 0)
        self._images = {}#Key will be address and value will be the most recent image from the client

    def _resize_image(self,img, target_height, target_width):
        return cv2.resize(img, (target_width, target_height))

    def _combine_images(self,images,target_height, target_width, final_height, final_width):
        max_height = 0
        total_width = 0

        # Load images and find the maximum height and total width
        for img in images:
            print("_combine_images type = ",type(img))
            if type(img) == tuple:
                print(img)
            max_height = max(max_height, img.shape[0])
            total_width += img.shape[1]

        # If target height or width is not specified, use the maximum height and width of the input images
        if target_height is None:
            target_height = max_height
        if target_width is None:
            target_width = total_width // len(images)

        # Calculate the number of rows and columns for the grid
        num_images = len(images)
        num_rows = int(np.sqrt(num_images))
        num_cols = (num_images + num_rows - 1) // num_rows  # Calculate number of columns such that each row but the last is filled

        # Resize images to fit into grid cells
        resized_images = []
        for img in images:
            resized_img = self._resize_image(img, target_height, target_width)
            resized_images.append(resized_img)

        # Create a blank canvas for stitching images
        stitched_height = num_rows * target_height
        stitched_width = num_cols * target_width
        stitched_image = np.zeros((stitched_height, stitched_width, 3), dtype=np.uint8)

        # Paste resized images onto the canvas
        row = 0
        col = 0
        for img in resized_images:
            if col == num_cols:
                col = 0
                row += 1
            y_offset = row * target_height
            x_offset = col * target_width
            stitched_image[y_offset:y_offset + target_height, x_offset:x_offset + target_width] = img
            col += 1

        # Resize the stitched image to the final specified size
        if final_height is not None and final_width is not None:
            stitched_image = self._resize_image(stitched_image, final_height, final_width)
        # Save the stitched image
        return stitched_image


    def _decrypt_data(self,data):
        #data = base64.b64decode(data, ' /')
        npdata = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)
        return frame
        #Maybe make these measurements constant variables

    def _process_frame(self,frame):
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        #self._add_text_to_image(buffer) - doesn't work when the line is here, but does work in _get_data
        message = base64.b64encode(buffer)
        return message

    def _send_to_client(self,data,client_addr):
        frame = data
        message = self._process_frame(frame)
        self._my_socket.sendto(message, client_addr)
        return frame

    def _handle_client(self):
        data = None
        try:
            while True:
                # Receive message from client
                data,client_addr = self._recv()
                if not data:
                    break
                if data == b"Exit": #Maybe should be b"Exit"
                    print(f"User disconnected from {client_addr}")
                    break  # Exit loop and close connection

                # Decrypt and decode message
                #elif data maybe handle case client sends hello
                else:
                    data = base64.b64decode(data, ' /')
                    decrypted_data = self._decrypt_data(data)
                    print("_handle_client type = ",type(decrypted_data))
                    if client_addr not in self._clients:
                        self._clients.append(client_addr)
                    self._images[client_addr] = decrypted_data

                # Add else case that will be error
        finally:
            # If client disconnects, remove from clients dictionary and broadcast the departure
            if data:
                if client_addr in self._clients:
                    self._clients.remove(client_addr)
                if client_addr in self._images.keys():
                    del self._images[client_addr]

    # def send_remaining_clients(message):
    #    for client_socket, _ in clients.items():
    #        send_message(client_socket, {"type": "SYS", "payload": message})

    def _send_broadcast_messages(self):
        while True:
            if self._images:
                # Broadcast message to all connected clients
                images_copy = list(self._images.values()).copy() #This may be better that just sending the values to the function directly
                combined_image = self._combine_images(images_copy,VideoServer._TARGET_HEIGHT,VideoServer._TARGET_WIDTH,VideoServer._FINAL_HEIGHT,VideoServer._FINAL_WIDTH)#self._combine_images(self._images.values(),VideoServer._TARGET_HEIGHT,VideoServer._TARGET_WIDTH,VideoServer._FINAL_HEIGHT,VideoServer._FINAL_WIDTH)
                for client_addr in self._clients:
                    self._send_to_client(combined_image,client_addr)



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


