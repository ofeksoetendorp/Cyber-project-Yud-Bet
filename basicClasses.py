import socket
import pyaudio
import abc


BUFF_SIZE = 65536
CHUNK = 1024  # original code was 10 * 1024 but then the audio was less smooth
CHANNELS = 1#Was originally 2 but that caused some problems on another computer. Changing it to 1 seems to have fixed it
FS = 44100
OUTPUT = True
INPUT = True
FRAMES_PER_BUFFER = CHUNK
SAMPLE_FORMAT = pyaudio.paInt16  # 16 bits per sample.Maybe use bigger amount of bits per sample
MAX_CLIENTS = 50


class Socket(abc.ABC):
    #מחלקת הסוקטים הבסיסית, שהיא מחלקה אבסטרקטית וממנה יירשו מחלקות סוקטים יותר מתקדמות ויותר ספציפיות בעתיד
    @abc.abstractmethod
    def __init__(self, server_ip, server_port, socket_type="UDP"):
        # המחלקה מקבלת את כתובת השרת אליו רוצים להתחבר, הפורט של השרת אליו רוצים להתחבר, וסוג הסוקט שרוצים לפתוח
        # נעשה פיצול לפתיחת הסוקט לפי סוג הסוקט הרצוי
        self._server_ip = server_ip # שומר את הכתובת IP של השרת, נשתמש בזה בהמשך בהתחברות
        self._server_port = server_port # נשמור את הפורט שאליו רוצים להתחבר בשרת ואליו נשלח מידע/ממנו נתחבר
        self._socket_type = socket_type.lower() #סוג הסוקט שנרצה לפתוח, ולפי הערך הזה נפתח TCP או UDP
        if self._socket_type == "udp":
            self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
        elif self._socket_type == "tcp":
            self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            pass
            #error"Socket must be either tcp or udp"

    def connect(self):
        #פונקציית connect לא מקבלת כלום ולא עושה כלום. נבנתה כתזכורת לממש במחלקות הבאות
        pass

    def _close(self):
        #הפונקצייה לא מקבלת שום ערך, ולא מחזירה כלום, אך סוגרת את הסוקט הפתוח ומדפיסה זאת
        self._my_socket.close()
        print("Socket Closed:)")



    @abc.abstractmethod
    def main(self):
        #פונקצייה abstract שמחייבת את המחלקות היורשות לממש פונקציה שכזאת
        pass


class ServerSocket(Socket):
    #מחלקת הסרבר הבסיסית. עליה ייבנו מחלקות השרתים המתקדמות יותר. היא משמשת ליצור פונקציונלית בסיסית לשרתים המתקדמים
    def __init__(self, server_ip, server_port, socket_type="UDP"):
        #מקבל את כך התתכונות התכונות שנדרשות למחלקת הסוקט הבסיסית -המחלקה מקבלת את כתובת השרת אליו רוצים להתחבר, הפורט של השרת אליו רוצים להתחבר, וסוג הסוקט שרוצים לפתוח
        Socket.__init__(self, server_ip, server_port, socket_type)
        self._close_threads = False #תכונה זו נועדה לעזור לעצירת הרצת השרת. תכונה זו מתחילה כFalse ותהפוך לtrue ברגע שנרצה לעצור את הריצה
        #נשמור גם תכונה של _client שעוזרת לשרת לאחסן את כל הלקוחות המחוברים אליו. אם סוג השרת הוא UDP אז נשמור במערך שבו יישמרו הכתובות של הלקוחות, בעוד שאם מדובר בשרת TCP אז נשמור מילון שבו המפתח יהיה הסוקט הפתוח בין השרת ללקוח, והמפתח יהיה השם והכתובת של הלקוח
        if self._socket_type == "udp":
            self._clients = []
        elif self._socket_type == "tcp":
            self._clients = {}  # {client_socket: (username, address)}
        else:
            #error
            pass

    def start(self):
        #הפונקצייה לא מקבלת כלום ולא מחזירה כלום אך עושה התחלה לשרת  - עושה bind לכתובת הרצויה, מדפיסה עדכון זה למסך, ובמידה ומדובר בסוקט מסוג TCP, גם תתחיל להקשיב למקסימום של 50 משתתפים בשיחה
        self._my_socket.bind((self._server_ip, self._server_port))
        print(f"Server listening on {self._server_ip}:{self._server_port}")
        if self._socket_type == "tcp":
            self._my_socket.listen(MAX_CLIENTS)

    def connect(self):
        #הפוקצייה לא מקבלת כלום אך מאפשרת התחברות של לקוח לשרת. הפונקצייה מחברת את הלקוח החדש,מוסיפה למבנה הנתונים המתאים בהתאם לסוגה את הלקוח, ואז מחזירה את כתובת הלקוח ובמידה וזה סוג TCP גם את הסוקט הפתוח החדש בין השרת והלקוח
        if self._socket_type == "udp":
            msg, client_addr = self._recv()
            self._clients.append(client_addr)
            print('GOT connection from ', client_addr, msg)  # Maybe remove message from here
            return client_addr
        elif self._socket_type == "tcp":
            client_socket, client_addr = self._my_socket.accept()
            print("Connection from:", client_addr)
            self._clients[client_socket] = ("Currently no name entered", client_addr)
            return client_socket,client_addr

    def _recv(self):
        #הפונקצייה לא מקבלת כלום (כקלט) ולא מחזירה, אך קולטת מהסוקט את מספר הבתים הקבוע שנקבע
        return self._my_socket.recvfrom(BUFF_SIZE)


class ClientSocket(Socket):
    #מחלקת הלקוח הבסיסית. עליה ייבנו מחלקות הלקוחות המתקדמות יותר. היא משמשת ליצור פונקציונלית בסיסית ללקוחות המתקדמים

    def __init__(self, server_ip, server_port, client_ip=None, client_port=None, socket_type="UDP"):
        #מקבל את כך התתכונות שנדרשות למחלקת הסוקט הבסיסית -המחלקה מקבלת את כתובת השרת אליו רוצים להתחבר, הפורט של השרת אליו רוצים להתחבר, וסוג הסוקט שרוצים לפתוח.בנוסף היא מקבלת גם את כתובת הIP של הלקוח למקרה וסוג השרת הוא UDP ואז יש צורך לעשות bind לכתובת הלקוח
        #גם מחלקה זו שומרת תכונת
        Socket.__init__(self, server_ip, server_port, socket_type)
        self._close_threads = False         #גם מחלקה זו שומרת תכונה זו בשביל לדעת מתי לעצור את הקוד
        if self._socket_type == "udp":
            self._client_ip = client_ip #כתובת הIP של הלקוח למקרה שזה סוקט UDP
            self._client_port = client_port #הפורט של הלקוח שבו רוצים להשתמש למקרה שזה סוקט UDP
            if self._client_ip is None or self._client_port is None:
                raise ValueError("When the socket is UDP, client ip and client port must be actual values.")

    def connect(self):
        #הפונקצייה לא מקבלת כלום ולא מחזירה כלום אך עושה אתחול מסויים של הלקוח, במקרה של UDP עושים bind לכתובת שלו, ובמקרה של TCP מתחברים לשרת
        if self._socket_type == "udp":
            self._my_socket.bind((self._client_ip, self._client_port))
        elif self._socket_type == "tcp":
            self._my_socket.connect((self._server_ip, self._server_port))


    def _send_data(self,data):
        #הפוקצייה מקבלת מידע שרוצים לשלוח ולא מחזירה כלום. היא שולחת את המידע לשרת תוך התחשבות בסוג הסוקט ובפונקציות שצריך להשתמש בהתאם
        if self._socket_type == "udp":
            self._my_socket.sendto(data, (self._server_ip, self._server_port))
        elif self._socket_type == "tcp":
            self._my_socket.send(data)

    def _receive_data(self):
        #הפוקצייה לא מקבלת כלום, אך קולטת מהסוקט מידע בהתאם לסוג הסוקט הפתוח ומחזירה את המידע המתקבל
        if self._socket_type == "udp":
            packet,_ = self._my_socket.recvfrom(BUFF_SIZE)
        elif self._socket_type == "tcp":
            packet = self._my_socket.recv(1024)
        return packet


class AudioManager:
    #מחלקה הנועדה לנהל את הקלטת והשמעת הקול בצד הלקוח של שיחת הקול
    def __init__(self):
        #הפונקצייה לא מקבלת כלום, ומאתחלת את התכונות השונות של המחלקה. יש שימוש בשני streams בשביל אפשרות למקביליות שיהיה אפשר להקליט ולהשמיע קול באותו הזמן
        self._p = pyaudio.PyAudio()  #בעזרת התכונה הזאת ניצור את הstreams השונים
        self._input_stream = self._p.open(format=SAMPLE_FORMAT,
                    channels=CHANNELS,
                    rate=FS,
                    frames_per_buffer=CHUNK,
                    input=INPUT)# באמצעות הstream הזה נקלוט מהלקוח את הקול שלו. נפתח את זה לפי קבועים שהוחלטו

        # Open output stream
        self._output_stream = self._p.open(format=SAMPLE_FORMAT,
                               channels=CHANNELS,
                               rate=FS,
                               output=OUTPUT,
                               frames_per_buffer=CHUNK) #בעזרת הstream הזה נשמיע ללקוח את הקול שהוא מקבל נפתח את זה לפי קבועים שהוחלט

    def __del__(self):
        #הפוקצייה לא מקבלת ולא מחזירה כלום וסוגרת את כל החלקים שהתחלקו במחלקה
        print("Closing audio manager")
        self._input_stream.stop_stream()
        self._input_stream.close()
        self._output_stream.stop_stream()
        self._output_stream.close()
        self._p.terminate()

    def read(self):
        #המחלקה לא מקבלת כלום וקוראת מהמיקרופון גודל קבוע, אותו היא מחזירה
        return self._input_stream.read(CHUNK)

    def write(self,data):
        #כותבים את המידע הניתן כפרמטר לפונצייה לאמצעי פלט הקיים. לא מחזירים כלום
        self._output_stream.write(data)


