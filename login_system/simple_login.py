# simple_login.py
# A very simple login system using a text file for user storage.

def register_user():
    """Register a new username and password."""
    username = input("Choose a username: ")
    password = input("Choose a password: ")

    with open("users.txt", "a") as f:
        f.write(f"{username},{password}\n")

    print("✅ User registered successfully!\n")


def login_user():
    """Check username and password against saved users."""
    username = input("Username: ")
    password = input("Password: ")

    try:
        with open("users.txt", "r") as f:
            for line in f:
                saved_user, saved_pass = line.strip().split(",")
                if username == saved_user and password == saved_pass:
                    print("✅ Login successful!\n")
                    return
        print("❌ Invalid username or password.\n")
    except FileNotFoundError:
        print("⚠️  No users registered yet. Try registering first.\n")


# ---- Main menu ----
while True:
    print("=== Simple Login System ===")
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
