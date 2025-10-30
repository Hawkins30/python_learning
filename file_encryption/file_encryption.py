# file_encryption.py
# Encrypt and decrypt text files using Fernet symmetric encryption

from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    """Generate and save a key to a file (if it doesn't exist)."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        print("🔑 Key generated and saved to secret.key\n")
    else:
        print("✅ Key already exists.\n")

def load_key():
    """Load the saved encryption key."""
    return open(KEY_FILE, "rb").read()

def encrypt_file(filename):
    """Encrypt the contents of a file."""
    key = load_key()
    f = Fernet(key)

    with open(filename, "rb") as file:
        original = file.read()

    encrypted = f.encrypt(original)

    with open(filename, "wb") as encrypted_file:
        encrypted_file.write(encrypted)

    print(f"🔒 File '{filename}' encrypted successfully.\n")

def decrypt_file(filename):
    """Decrypt the contents of a file."""
    key = load_key()
    f = Fernet(key)

    with open(filename, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()

    decrypted = f.decrypt(encrypted_data)

    with open(filename, "wb") as decrypted_file:
        decrypted_file.write(decrypted)

    print(f"🔓 File '{filename}' decrypted successfully.\n")

# --- Menu ---
while True:
    print("=== File Encryption Tool ===")
    print("1. Generate Key")
    print("2. Encrypt File")
    print("3. Decrypt File")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        generate_key()
    elif choice == "2":
        filename = input("Enter filename to encrypt: ")
        if os.path.exists(filename):
            encrypt_file(filename)
        else:
            print("⚠️ File not found.\n")
    elif choice == "3":
        filename = input("Enter filename to decrypt: ")
        if os.path.exists(filename):
            decrypt_file(filename)
        else:
            print("⚠️ File not found.\n")
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")
