# secure_email.py
# Secure Email System: Encryption + Digital Signatures

import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

USERS_DIR = "users"
MAILBOX = "mailbox.json"

os.makedirs(USERS_DIR, exist_ok=True)

# -----------------------------
# Key Management
# -----------------------------
def generate_keys(username):
    """Generate RSA key pair for email encryption/signing."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    priv_path = os.path.join(USERS_DIR, f"{username}_private.pem")
    pub_path = os.path.join(USERS_DIR, f"{username}_public.pem")

    with open(priv_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(pub_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    print(f"✅ Keys generated for {username}.\n")

# -----------------------------
# Load Keys
# -----------------------------
def load_private_key(username):
    try:
        with open(os.path.join(USERS_DIR, f"{username}_private.pem"), "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        print("⚠️ Private key not found.\n")
        return None

def load_public_key(username):
    try:
        with open(os.path.join(USERS_DIR, f"{username}_public.pem"), "rb") as f:
            return serialization.load_pem_public_key(f.read())
    except FileNotFoundError:
        print("⚠️ Public key not found.\n")
        return None

# -----------------------------
# Send Encrypted Email
# -----------------------------
def send_email(sender, recipient, subject, message):
    """Encrypt and sign an email."""
    recipient_pub = load_public_key(recipient)
    sender_priv = load_private_key(sender)

    if not recipient_pub or not sender_priv:
        return

    # Generate symmetric key for the email
    fernet_key = Fernet.generate_key()
    fernet = Fernet(fernet_key)

    # Encrypt the message
    encrypted_message = fernet.encrypt(message.encode())

    # Encrypt the Fernet key with recipient’s public key
    encrypted_key = recipient_pub.encrypt(
        fernet_key,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )

    # Sign the encrypted message with sender’s private key
    signature = sender_priv.sign(
        encrypted_message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )

    # Store email
    email_data = {
        "from": sender,
        "to": recipient,
        "subject": subject,
        "encrypted_key": encrypted_key.hex(),
        "encrypted_message": encrypted_message.hex(),
        "signature": signature.hex(),
    }

    inbox = []
    if os.path.exists(MAILBOX):
        with open(MAILBOX, "r") as f:
            inbox = json.load(f)

    inbox.append(email_data)
    with open(MAILBOX, "w") as f:
        json.dump(inbox, f, indent=4)

    print("📤 Email encrypted, signed, and sent successfully.\n")

# -----------------------------
# Receive/Read Email
# -----------------------------
def read_emails(username):
    """Decrypt and verify all emails for a user."""
    if not os.path.exists(MAILBOX):
        print("📭 No emails found.\n")
        return

    with open(MAILBOX, "r") as f:
        emails = json.load(f)

    user_emails = [e for e in emails if e["to"] == username]
    if not user_emails:
        print("📭 No new emails for you.\n")
        return

    priv_key = load_private_key(username)

    print(f"\n=== 📬 Inbox for {username} ===")
    for mail in user_emails:
        sender_pub = load_public_key(mail["from"])
        if not sender_pub or not priv_key:
            continue

        try:
            # Decrypt Fernet key
            decrypted_key = priv_key.decrypt(
                bytes.fromhex(mail["encrypted_key"]),
                padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
            )
            fernet = Fernet(decrypted_key)

            # Decrypt message
            decrypted_message = fernet.decrypt(bytes.fromhex(mail["encrypted_message"])).decode()

            # Verify signature
            sender_pub.verify(
                bytes.fromhex(mail["signature"]),
                bytes.fromhex(mail["encrypted_message"]),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )

            print(f"\nFrom: {mail['from']}")
            print(f"Subject: {mail['subject']}")
            print(f"Message: {decrypted_message}")
            print("✅ Signature verified.\n")

        except Exception as e:
            print(f"❌ Could not verify email from {mail['from']} — message may be tampered.\n")

# -----------------------------
# Main Menu
# -----------------------------
while True:
    print("=== Secure Email System ===")
    print("1. Generate Keys")
    print("2. Send Encrypted Email")
    print("3. Read My Emails")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        username = input("Enter username: ")
        generate_keys(username)
    elif choice == "2":
        sender = input("Sender username: ")
        recipient = input("Recipient username: ")
        subject = input("Subject: ")
        message = input("Message: ")
        send_email(sender, recipient, subject, message)
    elif choice == "3":
        username = input("Enter your username: ")
        read_emails(username)
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")
