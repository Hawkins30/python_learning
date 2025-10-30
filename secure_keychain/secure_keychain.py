# secure_keychain.py
# Password-Protected Encrypted Password Manager

import os
import json
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from getpass import getpass

KEYCHAIN_FILE = "keychain.json"
SALT_FILE = "keychain_salt.bin"

# -------------------------------
# Derive encryption key from master password
# -------------------------------
def derive_key(password):
    if not os.path.exists(SALT_FILE):
        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
    else:
        with open(SALT_FILE, "rb") as f:
            salt = f.read()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# -------------------------------
# Load or initialize keychain
# -------------------------------
def load_keychain():
    if os.path.exists(KEYCHAIN_FILE):
        with open(KEYCHAIN_FILE, "r") as f:
            return json.load(f)
    return {}

# -------------------------------
# Save keychain
# -------------------------------
def save_keychain(keychain):
    with open(KEYCHAIN_FILE, "w") as f:
        json.dump(keychain, f, indent=4)

# -------------------------------
# Add new credential
# -------------------------------
def add_entry(keychain, fernet):
    account = input("Enter account name (e.g. Gmail): ")
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    encrypted_password = fernet.encrypt(password.encode()).decode()

    keychain[account] = {
        "username": username,
        "password": encrypted_password
    }

    save_keychain(keychain)
    print(f"✅ Added '{account}' to keychain.\n")

# -------------------------------
# View all stored accounts
# -------------------------------
def view_accounts(keychain):
    if not keychain:
        print("📭 No accounts saved yet.\n")
        return

    print("=== 🔑 Stored Accounts ===")
    for account in keychain.keys():
        print(f"- {account}")
    print()

# -------------------------------
# Retrieve a password
# -------------------------------
def get_password(keychain, fernet):
    account = input("Enter account name to retrieve: ")

    if account not in keychain:
        print("⚠️ Account not found.\n")
        return

    entry = keychain[account]
    decrypted = fernet.decrypt(entry["password"].encode()).decode()
    print(f"👤 Username: {entry['username']}")
    print(f"🔐 Password: {decrypted}\n")

# -------------------------------
# Delete an account
# -------------------------------
def delete_account(keychain):
    account = input("Enter account name to delete: ")

    if account in keychain:
        del keychain[account]
        save_keychain(keychain)
        print(f"🗑️ Deleted '{account}' from keychain.\n")
    else:
        print("⚠️ Account not found.\n")

# -------------------------------
# Main menu
# -------------------------------
def main():
    print("=== Secure Keychain & Password Manager ===")
    master_password = getpass("Enter master password: ")
    key = derive_key(master_password)
    fernet = Fernet(key)

    keychain = load_keychain()

    while True:
        print("1. Add New Account")
        print("2. View Accounts")
        print("3. Retrieve Password")
        print("4. Delete Account")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_entry(keychain, fernet)
        elif choice == "2":
            view_accounts(keychain)
        elif choice == "3":
            get_password(keychain, fernet)
        elif choice == "4":
            delete_account(keychain)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

if __name__ == "__main__":
    main()
