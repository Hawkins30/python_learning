import hashlib

def hash_password(password):
    """Return a SHA256 hash of the given password."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user():
    username = input("Choose a username: ")
    password = input("Choose a password: ")
    hashed_pw = hash_password(password)

    with open("users.txt", "a") as f:
        f.write(f"{username},{hashed_pw}\n")
    print("✅ User registered successfully!\n")

def login_user():
    username = input("Username: ")
    password = input("Password: ")
    hashed_pw = hash_password(password)

    try:
        with open("users.txt", "r") as f:
            for line in f:
                saved_user, saved_hash = line.strip().split(",")
                if username == saved_user and hashed_pw == saved_hash:
                    print("✅ Login successful!\n")
                    return
        print("❌ Invalid username or password.\n")
    except FileNotFoundError:
        print("⚠️ No users registered yet.\n")

# ---- Menu ----
while True:
    print("=== Secure Login System ===")
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
import hashlib

password = "hello123"

hashed = hashlib.sha256(password.encode()).hexdigest()

print("Original password:", password)
print("SHA256 hash:", hashed)
