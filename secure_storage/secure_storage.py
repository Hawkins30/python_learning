# secure_storage.py
# Multi-user encrypted file storage system

import os
import json
import hashlib
import binascii
from cryptography.fernet import Fernet

USERS_FILE = "users.json"

def hash_password(password, salt):
    """Combine salt + password and return SHA256 hash."""
    return hashlib.sha256(salt + password.encode()).hexdigest()

def register_user():
    username = input("Choose a username: ")
    password = input("Choose a password: ")

    # Generate salt
    salt = os.urandom(16)
    hashed_pw = hash_password(password, salt)
    salt_hex = binascii.hexlify(salt).decode()

    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)

    if username in users:
        print("⚠️ User already exists.\n")
        return

    # Generate unique encryption key for this user
    key = Fernet.generate_key().decode()

    users[username] = {"salt": salt_hex, "hash": hashed_pw, "key": key}

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
        print("✅ Login successful!\n")
        return username, Fernet(user_data["key"].encode())
    else:
        print("❌ Incorrect password.\n")
        return None

def encrypt_user_file(username, fernet):
    filename = input("Enter filename to encrypt: ")
    if not os.path.exists(filename):
        print("⚠️ File not found.\n")
        return

    with open(filename, "rb") as file:
        data = file.read()
    encrypted = fernet.encrypt(data)

    enc_filename = f"{username}_{os.path.basename(filename)}.enc"
    with open(enc_filename, "wb") as enc_file:
        enc_file.write(encrypted)

    print(f"🔒 File '{filename}' encrypted as '{enc_filename}'.\n")

def decrypt_user_file(username, fernet):
    filename = input("Enter filename to decrypt: ")
    if not os.path.exists(filename):
        print("⚠️ File not found.\n")
        return

    with open(filename, "rb") as enc_file:
        encrypted_data = enc_file.read()
    decrypted = fernet.decrypt(encrypted_data)

    dec_filename = f"DECRYPTED_{os.path.basename(filename).replace('.enc', '')}"
    with open(dec_filename, "wb") as dec_file:
        dec_file.write(decrypted)

    print(f"🔓 File '{filename}' decrypted as '{dec_filename}'.\n")

# --- Menu ---
while True:
    print("=== Multi-User Encrypted File Storage ===")
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
                print("1. Encrypt File")
                print("2. Decrypt File")
                print("3. Logout")
                sub_choice = input("Choose an option: ")

                if sub_choice == "1":
                    encrypt_user_file(username, fernet)
                elif sub_choice == "2":
                    decrypt_user_file(username, fernet)
                elif sub_choice == "3":
                    print(f"👋 Logged out from {username}.\n")
                    break
                else:
                    print("Invalid option.\n")
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")
