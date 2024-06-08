
from basicClasses import ServerSocket, CHUNK, CHANNELS, FS, FRAMES_PER_BUFFER, SAMPLE_FORMAT
import base64
import numpy as np
import time
import threading
from pydub import AudioSegment
import queue

class AudioServer(ServerSocket):
    #המחלקה מנהלת קבלת קטעי קול מהלקוחות השונים, מיזוג של הקטעים האלה ושליחתם חזרה ללקוחות

    def __init__(self, server_ip, server_port):
        # הפונקצייה מקבלת את כתובת הIP של השרת הזה, והפורט הרצוי, ומעבירה אותם לServerSocket
        # מאחר והשרת רץ בUDP אז לא צריך להעביר מידע זה כי באופן דיפולטיבי שרת יוגדר כUDP
        # בנוסף נשמור מילון שבו המפתח יהיה הכתובת של הלקוח והערך יהיה מילון שבו נאחסן את את כל קטעי הקול של הלקוח שלא השתמשנו בהם עדיין
        #בנוסף נשתמש במנעול בשביל שהשימוש יהיה בטוח
        super().__init__(server_ip, server_port)
        self._audio_queues = {}
        self._lock = threading.Lock()

    def set_close_threads(self, value):
        #פונקציית set לclose_threads
        self._close_threads = value

    def __del__(self):
        #פונקציית דיסטרקטור שתגדיר את close threads ל true וכך תגרום לפונקציות המפתח להפסיק לרוץ. היא ממתינה זמן בטוח, ואז סוגרת את הסוקט

        self._close_threads = True
        time.sleep(1)
        print("Closing Audio Server")
        self._close()

    def _combine_audios(self, audio_data_list, sample_rate, sample_width, channels):
        #הפונקצייה מקבלת רשימת קטעי קול, וגם פרמטרים שונים על דרך העבודה עם הקוד
        #הפונקצייה ממזגת את קטעי הקול הנ"ל באמצעות עשיית overlay שלהם ואז מחזירה את קטע הקול המשולב
        audio_segments = [] #מערך שאליו נכניס את כל קטעי הקול לאחר המרתם לסוג AudioSegment
        # ההמרה המתוארת
        for audio_data in audio_data_list:
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            audio_segment = AudioSegment(
                audio_np.tobytes(),
                frame_rate=sample_rate,
                sample_width=sample_width,
                channels=channels
            )
            audio_segments.append(audio_segment)


        #כעת נעשה  overlay לקטעי הקול השונים. מתחילים מהראשון ומוסיפים עליו. נוסיף לציין שבשיטה זו קטעי הקול האחרים נחתכים
        #אחרי הקטע קול הראשון, אך מניסויים שלי זה לא משנה וחוסך חישוב מיותר
        combined = audio_segments[0]
        for audio_segment in audio_segments[1:]:
            combined = combined.overlay(audio_segment)
        #נחזיר את המידע הraw של הקטכ קול
        return combined.raw_data

    def _send_to_client(self, data, client_addr):
        #הפונקצייה מקבלת קטע קול וכתובת של לקוח, מעבדת את הקטע ושולחת את המידע המעובד ללקוח, ולא מחזירה כלום
        message = base64.b64encode(data)
        self._my_socket.sendto(message, client_addr)

    def _handle_client(self):
        #הפונקצייה רצה בלולאה כל עוד לא רוצים לסגור את המערכת. היא קולטת בכל פעם הודעות, מוסיפה לקוח אם הוא חדש, או מוסיפה קטע קול חדש לסוף התור של לקוח אם הוא מוכר

        while not self._close_threads:
            try:
                data, client_addr = self._recv()
                if not data:
                    break
                if data == b"Exit":
                    with self._lock:
                        if client_addr in self._clients:
                            self._clients.remove(client_addr)
                        if client_addr in self._audio_queues:
                            del self._audio_queues[client_addr]
                else:
                    decrypted_data = base64.b64decode(data, ' /')
                    with self._lock:
                        if client_addr not in self._clients:
                            self._clients.append(client_addr)
                        if client_addr not in self._audio_queues:
                            self._audio_queues[client_addr] = queue.Queue()
                        self._audio_queues[client_addr].put(decrypted_data)
            except Exception as e:
                print(f"Error handling client {client_addr}: {e}")

    def _send_broadcast_messages(self):
        #הפונקצייה עוברת בלולאה כל עוד לא רוצים לסגור את התוכנית ,עוברת על קטעי הקול הכי ישנים של כל הלקוחות, מעתיקה אותם (בשביל למנוע שינוי בזמן השילוב), משלבת אותן ושולחת לכל הלקוחות את הקטע הממוזג.

        while not self._close_threads:
            with self._lock:
                audio_data_list = []
                for client_addr, audio_queue in self._audio_queues.items():
                    if not audio_queue.empty():
                        audio_data_list.append(audio_queue.get())

            if audio_data_list:
                combined_sound = self._combine_audios(audio_data_list, sample_rate=FS, sample_width=2, channels=CHANNELS)
                with self._lock:
                    for client_addr in self._clients:
                        self._send_to_client(combined_sound, client_addr)

            time.sleep(0.2 * CHUNK / FS)  # Adjust sleep time for better real-time performance

    def main(self):
        #הפונקצייה המרכזית של המחלקה. הפונקצייה עושה bind לכתובת הרצויה ומתחילה בחוטים נפרדים את פונקציות הקבלה והשליחה של השרת

        self.start()
        broadcast_thread = threading.Thread(target=self._send_broadcast_messages)
        broadcast_thread.start()

        client_thread = threading.Thread(target=self._handle_client)
        client_thread.start()


