# salted_login.py
# Secure login system with hashing, salting, and JSON storage

import hashlib
import os
import json
import binascii

USERS_FILE = "users.json"

def hash_password(password, salt):
    """Combine password + salt and hash the result."""
    return hashlib.sha256(salt + password.encode()).hexdigest()

def register_user():
    username = input("Choose a username: ")
    password = input("Choose a password: ")

    # Generate 16 random bytes for salt
    salt = os.urandom(16)
    hashed_pw = hash_password(password, salt)
    salt_hex = binascii.hexlify(salt).decode()

    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)

    users[username] = {"salt": salt_hex, "hash": hashed_pw}

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

    print("✅ User registered securely!\n")

def login_user():
    username = input("Username: ")
    password = input("Password: ")

    if not os.path.exists(USERS_FILE):
        print("⚠️  No users found. Please register first.\n")
        return

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if username not in users:
        print("❌ User not found.\n")
        return

    salt = binascii.unhexlify(users[username]["salt"])
    saved_hash = users[username]["hash"]

    if hash_password(password, salt) == saved_hash:
        print("✅ Login successful!\n")
    else:
        print("❌ Incorrect password.\n")

# --- Menu ---
while True:
    print("=== Salted JSON Login System ===")
    print("1. Register")
    print("2. Login")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        register_user()
    elif choice == "2":
        login_user()
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid choice.\n")
