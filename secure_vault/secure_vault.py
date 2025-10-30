# secure_vault.py
# Password-Protected Secure File Vault

import os
import json
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from getpass import getpass

VAULT_FILE = "vault.json"
SALT_FILE = "vault_salt.bin"

# -------------------------------
# Derive encryption key from password
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
        iterations=480000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# -------------------------------
# Encrypt and store file
# -------------------------------
def add_file(vault, key):
    filepath = input("Enter file path to encrypt: ")

    if not os.path.exists(filepath):
        print("⚠️ File not found.\n")
        return

    with open(filepath, "rb") as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    filename = os.path.basename(filepath)
    vault[filename] = encrypted.decode()

    with open(VAULT_FILE, "w") as f:
        json.dump(vault, f, indent=4)

    print(f"✅ Encrypted and added '{filename}' to vault.\n")

# -------------------------------
# Decrypt file from vault
# -------------------------------
def extract_file(vault, key):
    filename = input("Enter filename to decrypt: ")

    if filename not in vault:
        print("⚠️ File not found in vault.\n")
        return

    fernet = Fernet(key)
    decrypted = fernet.decrypt(vault[filename].encode())

    with open(f"DECRYPTED_{filename}", "wb") as f:
        f.write(decrypted)

    print(f"🔓 Decrypted '{filename}' → 'DECRYPTED_{filename}'\n")

# -------------------------------
# View files in vault
# -------------------------------
def list_vault(vault):
    if not vault:
        print("📂 Vault is empty.\n")
        return

    print("=== 📦 Files in Vault ===")
    for filename in vault.keys():
        print(f"- {filename}")
    print()

# -------------------------------
# Main menu
# -------------------------------
def main():
    password = getpass("Enter vault password: ")
    key = derive_key(password)

    # Load or initialize vault
    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, "r") as f:
            vault = json.load(f)
    else:
        vault = {}

    while True:
        print("=== Secure File Vault ===")
        print("1. Add File to Vault")
        print("2. Extract File from Vault")
        print("3. View Vault Contents")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_file(vault, key)
        elif choice == "2":
            extract_file(vault, key)
        elif choice == "3":
            list_vault(vault)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

if __name__ == "__main__":
    main()
