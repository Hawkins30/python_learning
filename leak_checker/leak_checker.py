# leak_checker.py
# Password Leak Checker using Have I Been Pwned API

import hashlib
import requests

def check_password_leak(password):
    """
    Checks if a password has been leaked in known data breaches.
    Uses the Have I Been Pwned API with k-anonymity for privacy.
    """
    # Convert password to SHA-1 hash
    sha1password = hashlib.sha1(password.encode()).hexdigest().upper()
    first5, tail = sha1password[:5], sha1password[5:]

    # API only needs the first 5 characters (privacy-safe)
    url = f"https://api.pwnedpasswords.com/range/{first5}"
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError(f"Error fetching data: {response.status_code}")

    # Compare returned hashes with your password’s tail
    for line in response.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == tail:
            return int(count)
    return 0

if __name__ == "__main__":
    print("=== Password Leak Checker ===")
    password = input("Enter a password to check: ")
    count = check_password_leak(password)

    if count:
        print(f"⚠️  This password has been found {count:,} times in known breaches!")
        print("Please choose a stronger, unique password.\n")
    else:
        print("✅ This password has NOT been found in any known breaches. Great choice!\n")
