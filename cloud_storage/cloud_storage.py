# cloud_storage.py
# Secure cloud-like storage and key management system

import os
import json
import hashlib
import binascii
from datetime import datetime
from cryptography.fernet import Fernet

USERS_FILE = "users.json"
STORAGE_DIR = "cloud_storage"
KEY_DIR = "keys"

# --- Setup Directories ---
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)

def hash_password(password, salt):
    """Combine salt + password and return SHA256 hash."""
    return hashlib.sha256(salt + password.encode()).hexdigest()

def register_user():
    username = input("Choose a username: ")
    password = input("Choose a password: ")

    salt = os.urandom(16)
    hashed_pw = hash_password(password, salt)
    salt_hex = binascii.hexlify(salt).decode()

    # Generate key and store it separately
    key = Fernet.generate_key()
    key_path = os.path.join(KEY_DIR, f"{username}.key")
    with open(key_path, "wb") as key_file:
        key_file.write(key)

    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)

    if username in users:
        print("⚠️ User already exists.\n")
        return

    users[username] = {"salt": salt_hex, "hash": hashed_pw}
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

    print(f"✅ User '{username}' registered successfully.\n")

def login_user():
    username = input("Username: ")
    password = input("Password: ")

    if not os.path.exists(USERS_FILE):
        print("⚠️ No users found. Please register first.\n")
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
        key_path = os.path.join(KEY_DIR, f"{username}.key")
        if not os.path.exists(key_path):
            print("⚠️ Key file missing! Contact admin.\n")
            return None
        with open(key_path, "rb") as key_file:
            key = key_file.read()
        print("✅ Login successful!\n")
        return username, Fernet(key)
    else:
        print("❌ Incorrect password.\n")
        return None

def upload_file(username, fernet):
    filename = input("Enter filename to upload: ")
    if not os.path.exists(filename):
        print("⚠️ File not found.\n")
        return

    with open(filename, "rb") as file:
        data = file.read()

    encrypted = fernet.encrypt(data)
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    enc_filename = f"{username}_{os.path.basename(filename)}_{version}.enc"
    path = os.path.join(STORAGE_DIR, enc_filename)

    with open(path, "wb") as enc_file:
        enc_file.write(encrypted)

    print(f"☁️ File uploaded to cloud storage as '{enc_filename}'.\n")

def download_file(username, fernet):
    files = [f for f in os.listdir(STORAGE_DIR) if f.startswith(username)]
    if not files:
        print("⚠️ No files found for this user.\n")
        return

    print("Your available files:")
    for idx, file in enumerate(files, start=1):
        print(f"{idx}. {file}")

    choice = input("Select file number to download: ")
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(files):
            raise ValueError
    except ValueError:
        print("⚠️ Invalid selection.\n")
        return

    filename = files[idx]
    path = os.path.join(STORAGE_DIR, filename)

    with open(path, "rb") as enc_file:
        encrypted_data = enc_file.read()

    decrypted = fernet.decrypt(encrypted_data)

    output_name = f"DECRYPTED_{filename.replace('.enc', '')}"
    with open(output_name, "wb") as output:
        output.write(decrypted)

    print(f"⬇️ File '{filename}' downloaded and decrypted as '{output_name}'.\n")

def revoke_key(username):
    key_path = os.path.join(KEY_DIR, f"{username}.key")
    if os.path.exists(key_path):
        os.remove(key_path)
        print("🔒 Key revoked successfully.\n")
    else:
        print("⚠️ No key found to revoke.\n")

# --- Main Menu ---
while True:
    print("=== Secure Cloud Storage System ===")
    print("1. Register")
    print("2. Login")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        register_user()
    elif choice == "2":
        result = login_user()
        if result:
            username, fernet = result
            while True:
                print(f"--- Logged in as {username} ---")
                print("1. Upload File")
                print("2. Download File")
                print("3. Revoke Key")
                print("4. Logout")

                sub_choice = input("Choose an option: ")
                if sub_choice == "1":
                    upload_file(username, fernet)
                elif sub_choice == "2":
                    download_file(username, fernet)
                elif sub_choice == "3":
                    revoke_key(username)
                elif sub_choice == "4":
                    print(f"👋 Logged out from {username}.\n")
                    break
                else:
                    print("Invalid option.\n")
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")
