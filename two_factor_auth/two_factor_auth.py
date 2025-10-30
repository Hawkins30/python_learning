# two_factor_auth.py
# Two-Factor Authentication (2FA) system using pyotp

import os
import json
import hashlib
import binascii
import pyotp
from time import sleep

USERS_FILE = "users.json"

def hash_password(password, salt):
    """Hash password using SHA-256 with a salt."""
    return hashlib.sha256(salt + password.encode()).hexdigest()

def register_user():
    username = input("Choose a username: ")
    password = input("Choose a password: ")

    salt = os.urandom(16)
    hashed_pw = hash_password(password, salt)
    salt_hex = binascii.hexlify(salt).decode()

    # Generate a secret key for OTP
    otp_secret = pyotp.random_base32()

    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)

    if username in users:
        print("⚠️ User already exists.\n")
        return

    users[username] = {
        "salt": salt_hex,
        "hash": hashed_pw,
        "otp_secret": otp_secret
    }

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

    print(f"✅ User '{username}' registered successfully.")
    print(f"🔐 Save this secret key to use with an Authenticator app: {otp_secret}\n")

def login_user():
    username = input("Username: ")
    password = input("Password: ")

    if not os.path.exists(USERS_FILE):
        print("⚠️ No users registered yet.\n")
        return

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if username not in users:
        print("❌ User not found.\n")
        return

    user_data = users[username]
    salt = binascii.unhexlify(user_data["salt"])
    hashed_pw = hash_password(password, salt)

    if hashed_pw != user_data["hash"]:
        print("❌ Incorrect password.\n")
        return

    # OTP Verification
    otp_secret = user_data["otp_secret"]
    totp = pyotp.TOTP(otp_secret)

    print("📲 Please enter your 6-digit authentication code.")
    otp = input("OTP: ")

    if totp.verify(otp):
        print("✅ 2FA successful! You are now logged in.\n")
    else:
        print("❌ Invalid or expired OTP.\n")

def show_current_code(username):
    """Debug helper: shows current OTP (simulating a real Authenticator app)."""
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    if username not in users:
        print("❌ User not found.\n")
        return
    otp_secret = users[username]["otp_secret"]
    totp = pyotp.TOTP(otp_secret)
    print(f"🔢 Current OTP for {username}: {totp.now()} (valid for ~30s)\n")

# --- Menu ---
while True:
    print("=== Two-Factor Authentication System ===")
    print("1. Register")
    print("2. Login")
    print("3. Show Current OTP (for testing)")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        register_user()
    elif choice == "2":
        login_user()
    elif choice == "3":
        username = input("Enter username to view OTP: ")
        show_current_code(username)
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")

