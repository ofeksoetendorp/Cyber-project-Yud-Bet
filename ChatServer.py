import socket
import hashlib
import json
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Encryption key (must be 16 bytes long)
key = b'This is a key!!!'  # 16 bytes

# Global variables to store client information
clients = {}  # {client_socket: (username, address)}
broadcast_messages = []  # List to store messages to be broadcasted


def verify_password(password):
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    # Compare with stored hashed password
    stored_password = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    return hashed_password == stored_password


def handle_client(client_socket, address):
    username = None
    try:
        while True:
            # Receive message from client
            data = client_socket.recv(1024)
            if not data:
                break

            # Decrypt and decode message
            decrypted_data = decrypt_message(data)
            message = json.loads(decrypted_data)

            # Process message based on type
            message_type = message.get("type")
            if message_type == "PWD":
                password = message.get("payload")
                if verify_password(password):
                    response = {"type": "ACK", "payload": "Password verified. Send your username."}
                    send_message(client_socket, response)
                else:
                    response = {"type": "ERR", "payload": "Invalid password. Connection closed."}
                    send_message(client_socket, response)
                    return
            elif message_type == "USR":
                username = message.get("payload")
                print(f"User '{username}' connected from {address}")
                clients[client_socket] = (username, address)
                send_notification(f"User '{username}' joined the chat.")
            elif message_type == "MSG":
                chat_message = message.get("payload")
                sender_username = clients.get(client_socket)[0]

                broadcast_messages.append((sender_username, chat_message))
            elif message_type == "EXIT":
                chat_message = message.get("payload")
                sender_username = clients.get(client_socket)[0]
                print(f"User '{sender_username}' disconnected from {address}")
                send_message(client_socket, {"type": "ACK", "payload": "You disconnected. Have a good day."})
                break  # Exit loop and close connection
            #Add else case that will be error
    finally:
        # If client disconnects, remove from clients dictionary and broadcast the departure
        if username:
            del clients[client_socket]
            send_notification(f"User '{username}' left the chat.")
            #send_remaining_clients(f"User '{username}' left the chat.")
        client_socket.close() #Removing this line seems to work.Nevermind.


def send_notification(notification_message):
    broadcast_messages.append(("System", notification_message))


#def send_remaining_clients(message):
#    for client_socket, _ in clients.items():
#        send_message(client_socket, {"type": "SYS", "payload": message})


def send_broadcast_messages():
    while True:
        if broadcast_messages:
            messages_to_send = broadcast_messages.copy()  # Copy the list to avoid race condition
            broadcast_messages.clear()  # Clear the original list
            # Broadcast message to all connected clients
            for client_socket, (username, _) in clients.items():
                for sender_username, message in messages_to_send:
                    if sender_username == "System":
                        send_message(client_socket, {"type": "SYS", "payload": message})
                    else:
                        send_message(client_socket, {"type": "MSG", "payload": f"{sender_username}: {message}"})


def decrypt_message(encrypted_message):
    cipher = AES.new(key, AES.MODE_CBC, encrypted_message[:16])
    decrypted_message = unpad(cipher.decrypt(encrypted_message[16:]), AES.block_size)
    return decrypted_message.decode()


def send_message(client_socket, message):
    serialized_message = json.dumps(message)
    encrypted_message = encrypt_message(serialized_message)
    client_socket.send(encrypted_message)


def encrypt_message(message):
    cipher = AES.new(key, AES.MODE_CBC)
    padded_message = pad(message.encode(), AES.block_size)
    encrypted_message = cipher.iv + cipher.encrypt(padded_message)
    return encrypted_message


def main():
    host = "127.0.0.1"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Server listening on port:", port)

    # Start a thread to broadcast messages to clients
    broadcast_thread = threading.Thread(target=send_broadcast_messages)
    broadcast_thread.start()

    while True:
        client_socket, address = server_socket.accept()
        print("Connection from:", address)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()


if __name__ == "__main__":
    main()
