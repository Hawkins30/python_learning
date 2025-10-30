# encryption_demo.py
# Simple encryption and decryption demo using Fernet

from cryptography.fernet import Fernet

def generate_key():
    """Generate and save a key to a file."""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("🔑 Key generated and saved to secret.key\n")

def load_key():
    """Load the saved key."""
    return open("secret.key", "rb").read()

def encrypt_message(message):
    """Encrypt a message using the loaded key."""
    key = load_key()
    f = Fernet(key)
    encrypted = f.encrypt(message.encode())
    print(f"🔒 Encrypted message:\n{encrypted.decode()}\n")

def decrypt_message(encrypted_message):
    """Decrypt a message using the loaded key."""
    key = load_key()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_message.encode())
    print(f"🔓 Decrypted message:\n{decrypted.decode()}\n")

# --- Menu ---
while True:
    print("=== Fernet Encryption Demo ===")
    print("1. Generate Key")
    print("2. Encrypt Message")
    print("3. Decrypt Message")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        generate_key()
    elif choice == "2":
        message = input("Enter message to encrypt: ")
        encrypt_message(message)
    elif choice == "3":
        encrypted = input("Enter encrypted message to decrypt: ")
        decrypt_message(encrypted)
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")
