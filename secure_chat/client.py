# client.py - Secure Chat Client

import socket
from cryptography.fernet import Fernet

HOST = "127.0.0.1"
PORT = 5001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("✅ Connected to server.")

# Receive encryption key
key = client.recv(4096)
fernet = Fernet(key)

while True:
    msg = input("You: ")
    enc_msg = fernet.encrypt(msg.encode())
    client.send(enc_msg)

    enc_reply = client.recv(4096)
    if not enc_reply:
        break

    try:
        reply = fernet.decrypt(enc_reply).decode()
        print(f"Server: {reply}")
    except Exception:
        print("⚠️ Message could not be decrypted.")
        break

client.close()
