# server.py - Secure Chat Server

import socket
from cryptography.fernet import Fernet

HOST = "127.0.0.1"
PORT = 5001

# Load or generate encryption key
key = Fernet.generate_key()
fernet = Fernet(key)

print("🔐 Secure Chat Server started.")
print("Waiting for connection...")

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

conn, addr = server.accept()
print(f"✅ Connected with {addr}")

# Send key to client
conn.send(key)

while True:
    # Receive encrypted message
    enc_message = conn.recv(4096)
    if not enc_message:
        break

    try:
        message = fernet.decrypt(enc_message).decode()
        print(f"Client: {message}")
    except Exception:
        print("⚠️ Decryption failed.")
        break

    # Send response
    reply = input("You: ")
    enc_reply = fernet.encrypt(reply.encode())
    conn.send(enc_reply)

conn.close()
server.close()
