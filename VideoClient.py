from basicClasses import ClientSocket
import base64
import cv2
import numpy as np
import imutils
import threading
import time
import customtkinter as ctk
from PIL import Image, ImageTk

#Please note that if the video has problems passing through the WIFI changing (making it smaller) the height and width in the VideoServer,VideoCLient classes can probably solve it
#Please note that if the video has problems passing through the WIFI changing (making it smaller) the height and width in the VideoServer,VideoCLient classes can probably solve it
#Please note that if the video has problems passing through the WIFI changing (making it smaller) the height and width in the VideoServer,VideoCLient classes can probably solve it
#Please note that if the video has problems passing through the WIFI changing (making it smaller) the height and width in the VideoServer,VideoCLient classes can probably solve it


class VideoClient(ClientSocket):
    # המחלקה מנהלת את שליחת, קבלת הווידאו וחלקית משמשת להצגתו
    _WIDTH = 800
    _HEIGHT = 600

    def __init__(self, server_ip, server_port,client_ip,client_port, name,video_label):
        # המחלקה מקבלת את כל התכונות של CientSocket - הserver_ip,server_port
        # המחלקה מעבירה גם לClientSocket את סוג הסוקט שבמקרה זה הוא udp
        #מאחר והסוקט הוא UDP אז המחלקה מקבלת גם את כתובת הלקוח, והפורט הרצוי, ומקבלת את השם אותו הלקוח יצרף לכל התמונות שלו
        #הוא יקבל גם video_labe שישמש בUI להצגת הווידאו המתקבל מהשרת
        ClientSocket.__init__(self, server_ip, server_port,client_ip,client_port)
        self._name = name
        self._vid = cv2.VideoCapture(0)
        self.video_label = video_label



    def set_close_threads(self,value):
        #פונקציית set לclose_thread
        self._close_threads = value

    def __del__(self):
        #פונקציית דיסטרקטור שלא מקבלת כלום ולר דוחה כלו. היא מגדירה את close threads להיות false ואז ממתינה שנייה בשביל שהתקשורת עם השרת והלולאות יסתיימו, ואז סוגרת את הלקוח בביטחון
        self._close_threads = True
        time.sleep(1)
        print("deleting video client")
        self._my_socket.sendto(b"Exit", (self._server_ip, self._server_port)) #שולחת הודעה זו כהודעה שבאמצעותה השרת ידע שהלקוח מתנתק מהשיחה
        self._vid.release()
        self._close()

    def _handle_data_from_server(self,data):
        #הפונקציה מקבלת תמונה שמוצפנת באמצעות base64 ואז מפענחת את ההצפנה הזאת, ומציגה את התמונה
        data = base64.b64decode(data, ' /')
        npdata = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)

        self._show_frame(frame)

    def _handle_server_receptions(self):
        #הפונקצייה לא מקבלת ולא מחזירה כלום ועוברדת בלולאה לקבל מהשרת את התמונה של כל הלקוחות ביחד, וקוראת לפונקציה שתפענח ותציג את התמונות בכל פעם
        while not self._close_threads:
            data = self._receive_data()
            self._handle_data_from_server(data)
            key = cv2.waitKey(1) & 0xFF
            #Seems like it is important to keep the waitkey around

    def _add_name_to_image(self,img, position=(10, 30), font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(0, 0, 0),
                          thickness=2):
        #הפונקצייה מקבלת פרמטרים רבים לבחירת המיקום, הפונט, והתמונה, ומוסיפה את שם הלקוח לתמונה
        cv2.putText(img, self._name, position, font, font_scale, color, thickness)

    def _get_frame(self):
        #הפונקצייה קוראת מהמצלמה את תמונה, מוסיפה את השם של הלקוח ומחזירה את התמונה הזאת
        _,frame = self._vid.read()
        self._add_name_to_image(frame)
        return frame

    def _process_frame(self,frame):
        #הפונקצייה מקבלת תמונה, עושה עיבוד שלה (מקודדת לjpg, ומורידה את איכות התמונה ל10%), מקודדת בbase64 ומחזירה את התוצר
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 10])
        message = base64.b64encode(buffer)
        return message

    def _send_to_server(self,data):
        #הפוקצייה מקבלת תמונה, שולחת אותה לעיבודה ושולחת אותה לשרת. היא מחזירה את התמונה אותה היא שלחה
        frame = data
        message = self._process_frame(frame)
        self._my_socket.sendto(message, (self._server_ip, self._server_port))
        return frame

    def _handle_sending_to_server(self):
        #הפונקצייה לא מקבלת כלום ורצה בלולאה כל עוד המצלמה פתוחה וכל עוד לא רוצים לסגור את הסוקט. היא מקבלת בכל פעם תמונה, משנה את הגודל שלה, ושולחת את זה לשרת
        while self._vid.isOpened() and (not self._close_threads):
            frame = self._get_frame()
            frame = imutils.resize(frame, width=VideoClient._WIDTH)
            self._send_to_server(frame)

            key = cv2.waitKey(1) & 0xFF
            #Seems like it is important to keep the waitkey around

    def _show_frame(self,frame):
        #הפונקצעעה מקבלת תמונה, לא מחזירה כלום, ומציגה אותה
        if frame is not None:

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.video_label.configure(image=ctk_img)
            self.video_label.image = ctk_img

    def main(self):
        #הפונקצייה המרכזית של המחלקה. עושה bind לכתובת והפורט של הלקוח, וומתחילה חוטים נפרדים לשליחה וקבלה של הלקוח
        self.connect()
        receive_thread = threading.Thread(target=self._handle_server_receptions)
        send_thread = threading.Thread(target=self._handle_sending_to_server )

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()
