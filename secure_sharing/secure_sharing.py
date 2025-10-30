# secure_sharing.py
# Multi-user file sharing with encryption and access logging

import os
import json
import hashlib
import binascii
from datetime import datetime
from cryptography.fernet import Fernet

USERS_FILE = "users.json"
LOG_FILE = "access_log.json"

# -----------------------------
# Utility Functions
# -----------------------------
def hash_password(password, salt):
    """Combine salt + password and return SHA256 hash."""
    return hashlib.sha256(salt + password.encode()).hexdigest()

def log_event(username, action, filename):
    """Log user actions to access_log.json."""
    event = {
        "user": username,
        "action": action,
        "filename": filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)

    logs.append(event)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

# -----------------------------
# Authentication
# -----------------------------
def register_user():
    username = input("Choose a username: ")
    password = input("Choose a password: ")

    salt = os.urandom(16)
    hashed_pw = hash_password(password, salt)
    salt_hex = binascii.hexlify(salt).decode()
    key = Fernet.generate_key().decode()

    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)

    if username in users:
        print("⚠️ User already exists.\n")
        return

    users[username] = {"salt": salt_hex, "hash": hashed_pw, "key": key}

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

    print(f"✅ User '{username}' registered successfully.\n")

def login_user():
    username = input("Username: ")
    password = input("Password: ")

    if not os.path.exists(USERS_FILE):
        print("⚠️ No users found.\n")
        return None

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if username not in users:
        print("❌ User not found.\n")
        return None

    user_data = users[username]
    salt = binascii.unhexlify(user_data["salt"])
    hashed_pw = hash_password(password, salt)

    if hashed_pw == user_data["hash"]:
        print("✅ Login successful!\n")
        return username, Fernet(user_data["key"].encode())
    else:
        print("❌ Incorrect password.\n")
        return None

# -----------------------------
# File Sharing Functions
# -----------------------------
def encrypt_file(username, fernet):
    filename = input("Enter filename to encrypt: ")
    if not os.path.exists(filename):
        print("⚠️ File not found.\n")
        return

    with open(filename, "rb") as f:
        data = f.read()

    encrypted = fernet.encrypt(data)
    encrypted_filename = f"{username}_{os.path.basename(filename)}.enc"

    with open(encrypted_filename, "wb") as f:
        f.write(encrypted)

    log_event(username, "encrypt", encrypted_filename)
    print(f"🔒 File encrypted as '{encrypted_filename}'.\n")

def decrypt_file(username, fernet):
    filename = input("Enter filename to decrypt (.enc): ")
    if not os.path.exists(filename):
        print("⚠️ File not found.\n")
        return

    with open(filename, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted = fernet.decrypt(encrypted_data)
        decrypted_filename = f"DECRYPTED_{os.path.basename(filename).replace('.enc', '')}"

        with open(decrypted_filename, "wb") as f:
            f.write(decrypted)

        log_event(username, "decrypt", filename)
        print(f"🔓 File decrypted as '{decrypted_filename}'.\n")

    except Exception:
        print("❌ Decryption failed. Possibly shared by another user.\n")

def share_file(sender, recipient):
    """Share encrypted file key between users."""
    filename = input("Enter filename to share (.enc): ")

    if not os.path.exists(filename):
        print("⚠️ File not found.\n")
        return

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if recipient not in users:
        print("❌ Recipient not found.\n")
        return

    sender_key = users[sender]["key"]
    recipient_key = users[recipient]["key"]

    # Just record the intent of sharing for now
    log_event(sender, f"shared {filename} with {recipient}", filename)
    print(f"📤 '{filename}' shared with {recipient} (logged).\n")

def view_logs():
    """Display access log contents."""
    if not os.path.exists(LOG_FILE):
        print("⚠️ No logs found.\n")
        return

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    print("\n=== ACCESS LOGS ===")
    for log in logs:
        print(f"[{log['timestamp']}] {log['user']} - {log['action']} ({log['filename']})")
    print()

# -----------------------------
# Main Program
# -----------------------------
while True:
    print("=== Secure File Sharing System ===")
    print("1. Register")
    print("2. Login")
    print("3. View Logs")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        register_user()
    elif choice == "2":
        result = login_user()
        if result:
            username, fernet = result
            while True:
                print(f"--- Logged in as {username} ---")
                print("1. Encrypt File")
                print("2. Decrypt File")
                print("3. Share File")
                print("4. Logout")
                sub_choice = input("Choose an option: ")

                if sub_choice == "1":
                    encrypt_file(username, fernet)
                elif sub_choice == "2":
                    decrypt_file(username, fernet)
                elif sub_choice == "3":
                    recipient = input("Enter recipient username: ")
                    share_file(username, recipient)
                elif sub_choice == "4":
                    print(f"👋 Logged out from {username}.\n")
                    break
                else:
                    print("Invalid option.\n")
    elif choice == "3":
        view_logs()
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")
