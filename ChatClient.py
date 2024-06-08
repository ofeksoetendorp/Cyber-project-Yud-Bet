
import time
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import threading
from basicClasses import ClientSocket
import customtkinter as ctk

class ChatClient(ClientSocket):
    #  המחלקה מנהלת את שליחת, קבלת הודעות וחלקית משמשת להצגת הודעות אלה ודרך הקליטה של הלקוח

    _KEY = b'This is a key!!!'  # 16 bytes

    def __init__(self, server_ip, server_port, name, password, message_display=None, message_entry=None,on_exit_callback = None):
        # המחלקה מקבלת את כל התכונות של CientSocket - הserver_ip,server_port
        # המחלקה מעבירה גם לClientSocket את סוג הסוקט שבמקרה זה הוא tcp
        #המחלקה מקבלת גם את שם הלקוח, והססמא הרצויה,ו3 פרמטרים נוספים עבור הUI - הmessage_display,message_entry,on_exit_callbacl
        super().__init__(server_ip, server_port, socket_type="tcp")
        self._name = name #שם הלקוח
        self.__password = password #מה שחושבים שהיא הססמא
        self.message_display = message_display #החלון שבו נציג את ההודעות
        self.message_entry = message_entry#החלון שממנו נקלוט את ההודעות
        self._close_threads = False
        self.on_exit_callback = on_exit_callback #פונקציה שתקרא כשהמערכת תסגר


    def set_close_threads(self, value):
        #פונקציית set לפclosethreads
        self._close_threads = value

    def __del__(self):
        #פונקציית הdestructor, לא מקבלת ולא מחזירה כלום וסוגרת הכל
        self._close_threads = True
        time.sleep(1)
        print("Closing client")
        self._close()

    def _send_message(self, message_type, payload):
        #הודעה ששלוחת הודעה לפי הפרוטוקול. מקבלת ההודעה בשני חלקיה, מחברת אותם, מצפינה ושולחת. לא מחזירה כלום
        message = {"type": message_type, "payload": payload}
        serialized_message = json.dumps(message)
        encrypted_message = self._encrypt_message(serialized_message)
        self._my_socket.send(encrypted_message)

    def _receive_message(self):
        #פונקציה לא מקבלת כלום. הפונקציה קולטת הודעה מוצפנת מהשרת, מפענחת אותה ומחזירה אותה.
        data = self._my_socket.recv(1024)
        decrypted_data = self._decrypt_message(data)
        return json.loads(decrypted_data)

    def _encrypt_message(self, message):
        #פונקציה המקודדת הודעה. מקבלת הודעה ומצפינה אותה, מחזירה את ההודעה המוצפנת.
        cipher = AES.new(self._KEY, AES.MODE_CBC)
        padded_message = pad(message.encode(), AES.block_size)
        encrypted_message = cipher.iv + cipher.encrypt(padded_message)
        return encrypted_message

    def _decrypt_message(self, encrypted_message):
        #פונקצייה מקבלת הודעה מוצפנת ומפענחת אותה,ומחזירה את ההודעה המוצפנת
        cipher = AES.new(self._KEY, AES.MODE_CBC, encrypted_message[:16])
        decrypted_message = unpad(cipher.decrypt(encrypted_message[16:]), AES.block_size)
        return decrypted_message.decode()

    def _receive_messages(self):
        #פונקצייה שלא מחזירה ומקבלת כלום כפרמטרים, אך מריצה לולאה שתפקידה לקלוט ולהציג את ההודעות שהשרת שולח ללקוח
        print("Starting to receive messages")
        while not self._close_threads:
            try:
                message = self._receive_message()
                message_type = message.get("type")
                if message_type == "MSG":
                    self._display_message(message["payload"])
                elif message_type == "SYS":
                    self._display_message(f"[System]: {message['payload']}")
                elif message_type == "ACK":
                    self._display_message(f"[System]: {message['payload']}")
                    self._close_threads = True
                    break
            except Exception as e:
                print(f"Error receiving messages: {e}")
                break
        print("Stopped receiving messages")

    def start(self):
        #פונקצייה העושה את השלב הראשון בהתחברות. היא לא מקבלת פרמטרים, שולחת את הססמא הרצויה וסוגרת את התשיחה במידה שהססמא שגויה.
        try:
            self.connect()
            print("Connected to server")

            # Send password to server
            self._send_message("PWD", self.__password)

            # Receive verification message from server
            verification_message = self._receive_message()
            print(f"Verification message received: {verification_message}")
            if "Password verified" in verification_message["payload"]:
                return True
            self._close_threads = True
            return False
        except Exception as e:
            print(f"Error starting chat client: {e}")
            return False

    def _send_message_from_entry(self, event):
        #הפונקציה רצה במקרה של לחיצת enter ושליחת הודעה. הפונקצייה לא מחזירה כלום אך שולחת הודעה לשרת ומשנה את סוג ההודעה בהתאם לטיבה ולפי הפרוטוקול
        if not self._close_threads:
            message = self.message_entry.get()
            self.message_entry.delete(0, ctk.END)
            if message.lower() == "exit":
                self._send_message("EXIT", "exit")
                self._close_threads = True
                if self.on_exit_callback:
                    self.on_exit_callback()  # Trigger the callback to close the window
                return
            if len(json.dumps({"type": "MSG", "payload": message})) > 1024:
                self._display_message("Message too long. Please send a shorter message.")
                return
            self._send_message("MSG", message)

    def _display_message(self, message):
        #הפונקצייה מקבלת הודעה, לא מחזירה כלום, ומציגה אותה
        self.message_display.configure(state=ctk.NORMAL)
        self.message_display.insert(ctk.END, message + "\n")
        self.message_display.configure(state=ctk.DISABLED)
        self.message_display.see(ctk.END)

    def main(self):
        #הפונקצייה המנהלת את הריצה לאחר שליחת הססמא הנכונה. מתחילה חוטים שונים לקבלה ושליחת הודעות.
        print("Chat client main started")
        verified = True
        if verified:
            print("Password verified, starting message threads")
            self._send_message("USR", self._name)

            # Start threads for  receiving messages
            receive_thread = threading.Thread(target=self._receive_messages, name="ReceiveThread")
            receive_thread.start()

            # Wait for thread to finish
            receive_thread.join()
        print("Chat client main finished")


