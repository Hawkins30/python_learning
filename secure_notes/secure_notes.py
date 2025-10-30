# secure_notes.py
# Secure Notes App - Encrypted Text Storage

import os
import json
import base64
from getpass import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

NOTES_FILE = "notes.json"
SALT_FILE = "notes_salt.bin"

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
        iterations=400000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# -------------------------------
# Load or initialize notes
# -------------------------------
def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return {}

# -------------------------------
# Save notes to file
# -------------------------------
def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=4)

# -------------------------------
# Create a new encrypted note
# -------------------------------
def add_note(notes, fernet):
    title = input("Enter note title: ")
    content = input("Enter note content: ")
    encrypted = fernet.encrypt(content.encode()).decode()
    notes[title] = encrypted
    save_notes(notes)
    print(f"✅ Note '{title}' added securely.\n")

# -------------------------------
# View decrypted note
# -------------------------------
def view_note(notes, fernet):
    title = input("Enter note title to view: ")
    if title not in notes:
        print("⚠️ Note not found.\n")
        return

    decrypted = fernet.decrypt(notes[title].encode()).decode()
    print(f"\n📓 {title}\n{'-'*len(title)}\n{decrypted}\n")

# -------------------------------
# Edit existing note
# -------------------------------
def edit_note(notes, fernet):
    title = input("Enter note title to edit: ")
    if title not in notes:
        print("⚠️ Note not found.\n")
        return

    decrypted = fernet.decrypt(notes[title].encode()).decode()
    print(f"Current content:\n{decrypted}\n")
    new_content = input("Enter new content: ")
    notes[title] = fernet.encrypt(new_content.encode()).decode()
    save_notes(notes)
    print(f"✏️ Note '{title}' updated successfully.\n")

# -------------------------------
# Delete a note
# -------------------------------
def delete_note(notes):
    title = input("Enter note title to delete: ")
    if title in notes:
        del notes[title]
        save_notes(notes)
        print(f"🗑️ Note '{title}' deleted.\n")
    else:
        print("⚠️ Note not found.\n")

# -------------------------------
# List all notes
# -------------------------------
def list_notes(notes):
    if not notes:
        print("📭 No notes found.\n")
        return

    print("=== 🧾 Your Notes ===")
    for title in notes.keys():
        print(f"- {title}")
    print()

# -------------------------------
# Main Menu
# -------------------------------
def main():
    print("=== Secure Notes App ===")
    password = getpass("Enter your master password: ")
    key = derive_key(password)
    fernet = Fernet(key)

    notes = load_notes()

    while True:
        print("1. Add Note")
        print("2. View Note")
        print("3. Edit Note")
        print("4. Delete Note")
        print("5. List Notes")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_note(notes, fernet)
        elif choice == "2":
            view_note(notes, fernet)
        elif choice == "3":
            edit_note(notes, fernet)
        elif choice == "4":
            delete_note(notes)
        elif choice == "5":
            list_notes(notes)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    main()
