# digital_signatures.py
# Digital Signature and Message Authentication System

import os
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

USERS_DIR = "users"
SIGNED_MESSAGES_FILE = "signed_messages.json"

os.makedirs(USERS_DIR, exist_ok=True)

# -----------------------------
# Key Management
# -----------------------------
def generate_keys(username):
    """Generate RSA key pair for signing and verification."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    priv_path = os.path.join(USERS_DIR, f"{username}_private.pem")
    pub_path = os.path.join(USERS_DIR, f"{username}_public.pem")

    with open(priv_path, "wb") as priv_file:
        priv_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(pub_path, "wb") as pub_file:
        pub_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    print(f"✅ Keys generated for {username}.\n")

def load_private_key(username):
    """Load user's private key."""
    try:
        with open(os.path.join(USERS_DIR, f"{username}_private.pem"), "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        print("⚠️ Private key not found.\n")
        return None

def load_public_key(username):
    """Load user's public key."""
    try:
        with open(os.path.join(USERS_DIR, f"{username}_public.pem"), "rb") as f:
            return serialization.load_pem_public_key(f.read())
    except FileNotFoundError:
        print("⚠️ Public key not found.\n")
        return None

# -----------------------------
# Signing & Verification
# -----------------------------
def sign_message(sender, message):
    """Create a digital signature for the message."""
    private_key = load_private_key(sender)
    if not private_key:
        return

    signature = private_key.sign(
        message.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )

    messages = []
    if os.path.exists(SIGNED_MESSAGES_FILE):
        with open(SIGNED_MESSAGES_FILE, "r") as f:
            messages = json.load(f)

    msg_entry = {
        "from": sender,
        "message": message,
        "signature": signature.hex(),
    }

    messages.append(msg_entry)

    with open(SIGNED_MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=4)

    print(f"🪶 Message signed by {sender} and stored.\n")

def verify_messages(recipient):
    """Verify all stored messages."""
    if not os.path.exists(SIGNED_MESSAGES_FILE):
        print("📭 No signed messages found.\n")
        return

    with open(SIGNED_MESSAGES_FILE, "r") as f:
        messages = json.load(f)

    if not messages:
        print("📭 No messages available.\n")
        return

    print(f"\n=== 🔍 Verifying Messages ===")
    for msg in messages:
        sender = msg["from"]
        public_key = load_public_key(sender)
        if not public_key:
            continue

        try:
            public_key.verify(
                bytes.fromhex(msg["signature"]),
                msg["message"].encode(),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            print(f"✅ Verified message from {sender}: {msg['message']}")
        except Exception:
            print(f"❌ Verification failed for message from {sender}. (Signature invalid or tampered.)")
    print()

# -----------------------------
# Main Menu
# -----------------------------
while True:
    print("=== Digital Signatures & Authentication ===")
    print("1. Generate Keys")
    print("2. Sign Message")
    print("3. Verify Messages")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        username = input("Enter username: ")
        generate_keys(username)
    elif choice == "2":
        sender = input("Enter your username: ")
        message = input("Enter your message: ")
        sign_message(sender, message)
    elif choice == "3":
        recipient = input("Enter your username: ")
        verify_messages(recipient)
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")
