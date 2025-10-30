# encrypted_messaging.py
# Secure messaging system using RSA public/private key encryption

import os
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

USERS_DIR = "users"
MESSAGES_FILE = "messages.json"

os.makedirs(USERS_DIR, exist_ok=True)

# -----------------------------
# Utility Functions
# -----------------------------
def generate_keys(username):
    """Generate RSA key pair for the user."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Save private key
    with open(os.path.join(USERS_DIR, f"{username}_private.pem"), "wb") as priv_file:
        priv_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    # Save public key
    with open(os.path.join(USERS_DIR, f"{username}_public.pem"), "wb") as pub_file:
        pub_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    print(f"✅ Keys generated for {username}.\n")

def load_public_key(username):
    """Load public key for encryption."""
    try:
        with open(os.path.join(USERS_DIR, f"{username}_public.pem"), "rb") as key_file:
            return serialization.load_pem_public_key(key_file.read())
    except FileNotFoundError:
        print("⚠️ Public key not found.\n")
        return None

def load_private_key(username):
    """Load private key for decryption."""
    try:
        with open(os.path.join(USERS_DIR, f"{username}_private.pem"), "rb") as key_file:
            return serialization.load_pem_private_key(key_file.read(), password=None)
    except FileNotFoundError:
        print("⚠️ Private key not found.\n")
        return None

# -----------------------------
# Messaging Functions
# -----------------------------
def send_message(sender, recipient, message):
    """Encrypt message with recipient's public key and store."""
    recipient_pub = load_public_key(recipient)
    if not recipient_pub:
        return

    encrypted = recipient_pub.encrypt(
        message.encode(),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )

    messages = []
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r") as f:
            messages = json.load(f)

    msg_entry = {
        "from": sender,
        "to": recipient,
        "message": encrypted.hex(),
    }

    messages.append(msg_entry)

    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=4)

    print(f"📤 Message encrypted and sent to {recipient}.\n")

def read_messages(username):
    """Decrypt messages sent to the user."""
    if not os.path.exists(MESSAGES_FILE):
        print("📭 No messages found.\n")
        return

    private_key = load_private_key(username)
    if not private_key:
        return

    with open(MESSAGES_FILE, "r") as f:
        messages = json.load(f)

    user_messages = [m for m in messages if m["to"] == username]

    if not user_messages:
        print("📭 No messages for you.\n")
        return

    print(f"\n=== 📬 Messages for {username} ===")
    for msg in user_messages:
        try:
            decrypted = private_key.decrypt(
                bytes.fromhex(msg["message"]),
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
            )
            print(f"From {msg['from']}: {decrypted.decode()}")
        except Exception:
            print(f"⚠️ Message from {msg['from']} could not be decrypted.")
    print()

# -----------------------------
# Main Menu
# -----------------------------
while True:
    print("=== Encrypted Messaging System ===")
    print("1. Generate Keys")
    print("2. Send Message")
    print("3. Read Messages")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        username = input("Enter username: ")
        generate_keys(username)
    elif choice == "2":
        sender = input("Sender username: ")
        recipient = input("Recipient username: ")
        message = input("Enter your message: ")
        send_message(sender, recipient, message)
    elif choice == "3":
        username = input("Enter your username: ")
        read_messages(username)
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")
