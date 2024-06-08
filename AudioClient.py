
import base64
import threading
import time
from basicClasses import ClientSocket, AudioManager, CHUNK, FS

class AudioClient(ClientSocket):
    # המחלקה מנהלת את שליחת, קבלת והשמעת הקול של הלקוח
    def __init__(self, server_ip, server_port, client_ip, client_port):
        #הפונקציה מקבלת את כתובת הIP והפורט של השרת אליו הלקוח יתחבר, ומאחר וזה לקוח שרץ על UDP אז הוא יקבל גם את כתובת הIP והפורט הרצויה
        #הפונקצייה יוצרת אובייקט חדש של המחלקה
        super().__init__(server_ip, server_port, client_ip, client_port)
        self._audio_manager = AudioManager() #יצירת אובייקט מהסוג AudioManager שבאמצעותו ננהל את קריאת והשמעת הקול
        self._close_threads = False

    def set_close_threads(self, value):
        #פונקציית סט של close threads
        self._close_threads = value

    def __del__(self):
        #פונקציית דיסטרקטור שלא מקבלת כלום ולר דוחה כלו. היא מגדירה את close threads להיות false ואז ממתינה שנייה בשביל שהתקשורת עם השרת והלולאות יסתיימו, ואז סוגרת את הלקוח בביטחון
        self._close_threads = True
        time.sleep(1)
        print("deleting audio client")
        self._my_socket.sendto(b"Exit", (self._server_ip, self._server_port)) #שולחת הודעה זו כהודעה שבאמצעותה השרת ידע שהלקוח מתנתק מהשיחה
        self._close()

    def _handle_data_from_server(self, data):
        #הפונקציה מקבלת מידע מקודד, מפענחת אותו מbase64 ומשמיעה אותו באמצעות האמצעי פלט
        data = base64.b64decode(data, ' /')
        self._audio_manager.write(data)

    def _handle_server_receptions(self):
        #הפונקצייה לא מקבלת ולא מחזירה כלום ועוברדת בלולאה לקבל מהשרת את הקטעי קול של כל הלקוחות ביחד, וקוראת לפונקציה שתפענח ותשמיע את הקטע קול הממוזג בכל פעם
        while not self._close_threads:
            data = self._receive_data()
            if data:
                self._handle_data_from_server(data)


    def _get_audio_bit(self):
        #הפונקצייה לא מקבלת כלום, ומחזירה קטע שהיא קוראת מהמיקרופון בעזרת פונקציית עזר
        return self._audio_manager.read()

    def _process_audio_bit(self, audio_bit):
        #הפונקציה מקבלת קטע קול ומצפינה אותו בbase64 ומחזירה את זה
        return base64.b64encode(audio_bit)

    def _send_to_server(self, data):
        #הפונקצייה מקבלת קטע קול, מעבדת אותו ושולחת את זה לשרת
        message = self._process_audio_bit(data)
        self._my_socket.sendto(message, (self._server_ip, self._server_port))

    def _handle_sending_to_server(self):
        #הפונקצייה לא מקבלת כלום ורצה בלולאה כל עוד לא רוצים לסגור את הסוקט. היא קולטת כל פעם קטע קול, מעבדת אותו, ושולחת את זה לשרת
        while not self._close_threads:
            audio_bit = self._get_audio_bit()
            self._send_to_server(audio_bit)

    def main(self):
        #הפונקצייה המרכזית של המחלקה. עושה bind לכתובת והפורט של הלקוח, וומתחילה חוטים נפרדים לשליחה וקבלה של הלקוח
        self.connect()
        receive_thread = threading.Thread(target=self._handle_server_receptions)
        send_thread = threading.Thread(target=self._handle_sending_to_server)
        receive_thread.start()
        send_thread.start()
        receive_thread.join()
        send_thread.join()