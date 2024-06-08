from basicClasses import ServerSocket
import base64
import cv2
import numpy as np
import time
import threading


class VideoServer(ServerSocket):
    #המחלקה מנהלת קבלת תמונות מהלקוחות השונים, מיזוג של התמונות ושליחתם חזרה ללקוחות
    _TARGET_HEIGHT = 300
    _TARGET_WIDTH = 500
    _FINAL_HEIGHT = 500
    _FINAL_WIDTH = 1000

    def __init__(self, server_ip, server_port):
        #הפונקצייה מקבלת את כתובת הIP של השרת הזה, והפורט הרצוי, ומעבירה אותם לServerSocket
        #מאחר והשרת רץ בUDP אז לא צריך להעביר מידע זה כי באופן דיפולטיבי שרת יוגדר כUDP
        #בנוסף נשמור מילון שבו נאחסן את התמונות הכי חדשות של  כל אחד מהלקוחות
        ServerSocket.__init__(self, server_ip, server_port)
        self._images = {}#Key will be address and value will be the most recent image from the client

    def set_close_threads(self, value):
        #פונקציית set לclose_Threads
        self._close_threads = value

    def __del__(self):
        #פונקציית דיסטרקטור שתגדיר את close threads ל true וכך תגרום לפונקציות המפתח להפסיק לרוץ. היא ממתינה זמן בטוח, ואז סוגרת את הסוקט
        self._close_threads = True
        time.sleep(1)
        print("Closing Video Server")
        self._close()

    def _resize_image(self,img, target_height, target_width):
        #הפונקצייה מקבלת תמונה והמידות הרוצים לתמונה, ומחזירה תמונה עם גודל מעודכן
        return cv2.resize(img, (target_width, target_height))

    def _combine_images(self,images,target_height, target_width, final_height, final_width):
        #הפונקציה מקבלת מערך של תמונות, ומדידות שונות לתמונה הרוצים. הפונקצייה לוקחת את התמונות ומסדרת אותם בצורה של grid
        #כך שהשורה האחרונה היא היחידה שריקה. היא מחזירה את התמונה הממוזגת
        max_height = 0
        total_width = 0

        # Load images and find the maximum height and total width
        for img in images:

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
        #הפונקצייה מקבלת תמונה מקודדת ומחזירה ממנה תמונה
        npdata = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)
        return frame

    def _process_frame(self,frame):
        #הפונקצייה מקבלת תמונה ומעבדת אותה, ומחזירה אותה לאחר העיבוד
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        message = base64.b64encode(buffer)
        return message

    def _send_to_client(self,data,client_addr):
        #הפונקצייה מקבלת תמונה וכתובת של לקוח, מעבדת את התמונה ושולחת את המידע המעובד ללקוח, ומחזירה את התמונה ששולחים
        frame = data
        message = self._process_frame(frame)
        self._my_socket.sendto(message, client_addr)
        return frame

    def _handle_client(self):
        #הפונקצייה רצה בלולאה כל עוד לא רוצים לסגור את המערכת. היא קולטת בכל פעם הודעות, מוסיפה לקוח אם הוא חדש, או מעדכת את התמונה של לקוח אם הוא מוכר
        data = None
        try:
            while not self._close_threads:
                # Receive message from client
                try:
                    data,client_addr = self._recv()
                    if not data:
                        break
                    if data == b"Exit": #אם הלקוח שולח הודעה זו הוא רוצה להתנתק
                        print(f"User disconnected from {client_addr}!!!!")
                        if client_addr in self._clients:
                            self._clients.remove(client_addr)
                        if client_addr in self._images.keys():
                            del self._images[client_addr]

                    # Decrypt and decode message
                    else:
                        data = base64.b64decode(data, ' /')
                        decrypted_data = self._decrypt_data(data)
                        if client_addr not in self._clients:
                            self._clients.append(client_addr)
                        self._images[client_addr] = decrypted_data
                except:
                    print("Error")

        except:
            print("Error")
            # If client disconnects, remove from clients dictionary and broadcast the departure

    def _send_broadcast_messages(self):
        #הפונקצייה עוברת בלולאה כל עוד לא רוצים לסגור את התוכנית ,עוברת על התמונות של כל הלקוחות, מעתיקה אותם (בשביל למנוע שינוי בזמן השילוב), משלבת אותן ושולחת לכל הלקוחות את התמונה המועדכנת.
        while not self._close_threads:
            if self._images:
                # Broadcast message to all connected clients
                images_copy = list(self._images.values()).copy() #This is better that just sending the values to the function directly because doesn't collapse
                combined_image = self._combine_images(images_copy,VideoServer._TARGET_HEIGHT,VideoServer._TARGET_WIDTH,VideoServer._FINAL_HEIGHT,VideoServer._FINAL_WIDTH)#self._combine_images(self._images.values(),VideoServer._TARGET_HEIGHT,VideoServer._TARGET_WIDTH,VideoServer._FINAL_HEIGHT,VideoServer._FINAL_WIDTH)
                for client_addr in self._clients:
                    self._send_to_client(combined_image,client_addr)

    def main(self):
        #הפונקצייה המרכזית של המחלקה. הפונקצייה עושה bind לכתובת הרצויה ומתחילה בחוטים נפרדים את פונקציות הקבלה והשליחה של השרת
        self.start()
        # Start a thread to broadcast messages to clients
        broadcast_thread = threading.Thread(target=self._send_broadcast_messages)
        broadcast_thread.start()
        client_thread = threading.Thread(target=self._handle_client)
        client_thread.start()

