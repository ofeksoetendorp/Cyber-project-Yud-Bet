import socket
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import threading
# Encryption key (must be 16 bytes long)
key = b'This is a key!!!'  # 16 bytes

def send_message(sock, message_type, payload):
    message = {"type": message_type, "payload": payload}
    serialized_message = json.dumps(message)
    encrypted_message = encrypt_message(serialized_message)
    sock.send(encrypted_message)

def receive_message(sock):
    data = sock.recv(1024)
    decrypted_data = decrypt_message(data)
    return json.loads(decrypted_data)

def encrypt_message(message):
    cipher = AES.new(key, AES.MODE_CBC)
    padded_message = pad(message.encode(), AES.block_size)
    encrypted_message = cipher.iv + cipher.encrypt(padded_message)
    return encrypted_message

def decrypt_message(encrypted_message):
    cipher = AES.new(key, AES.MODE_CBC, encrypted_message[:16])
    decrypted_message = unpad(cipher.decrypt(encrypted_message[16:]), AES.block_size)
    return decrypted_message.decode()

def receive_messages(sock):
    while True:
        message = receive_message(sock)
        message_type = message.get("type")
        if message_type == "MSG":
            print("" + message["payload"])
        elif message_type == "SYS":
            print("[System]:", message["payload"])
        elif message_type == "ACK":
            print("[System]:", message["payload"])
            break

def send_messages(sock):
    while True:
        message = input("Enter your message (type 'exit' to quit): ")
        if message.lower() == "exit":
            send_message(sock, "EXIT", "exit")
            break
        if len(json.dumps({"type": "MSG", "payload": message})) > 1024:
            print("Message too long. Please send a shorter message.")
            continue
        send_message(sock, "MSG", message)

def main():
    host = "127.0.0.1"
    port = 12345
    threads = []
    threads_closed = True
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Send password to server
    password = input("Enter your password: ")
    send_message(client_socket, "PWD", password)

    # Receive verification message from server
    verification_message = receive_message(client_socket)
    print(verification_message)

    # If password is verified, send username
    if "Password verified" in verification_message["payload"]:
        username = input("Enter your username: ")
        send_message(client_socket, "USR", username)

        # Start threads for sending and receiving messages
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        send_thread = threading.Thread(target=send_messages, args=(client_socket,))
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
        client_socket.close()

if __name__ == "__main__":
    main()
