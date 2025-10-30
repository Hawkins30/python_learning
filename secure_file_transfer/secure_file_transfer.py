# secure_file_transfer.py
# Combines encryption, digital signatures, and verification

import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# -----------------------------
# Key Generation
# -----------------------------
def generate_rsa_keys(username):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    os.makedirs("keys", exist_ok=True)

    with open(f"keys/{username}_private.pem", "wb") as priv_file:
        priv_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(f"keys/{username}_public.pem", "wb") as pub_file:
        pub_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    print(f"✅ Keys generated for {username}.\n")

# -----------------------------
# Encryption and Signing
# -----------------------------
def encrypt_and_sign_file(sender, recipient_pubkey, filepath):
    """Encrypt file contents and sign them with sender's private key."""
    if not os.path.exists(filepath):
        print("⚠️ File not found.")
        return

    # Load recipient public key
    with open(recipient_pubkey, "rb") as f:
        recipient_key = serialization.load_pem_public_key(f.read())

    # Generate a random symmetric key
    fernet_key = Fernet.generate_key()
    fernet = Fernet(fernet_key)

    # Encrypt file contents
    with open(filepath, "rb") as f:
        encrypted_data = fernet.encrypt(f.read())

    # Encrypt the Fernet key with recipient's RSA public key
    encrypted_fernet_key = recipient_key.encrypt(
        fernet_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )

    # Load sender's private key
    with open(f"keys/{sender}_private.pem", "rb") as f:
        sender_priv = serialization.load_pem_private_key(f.read(), password=None)

    # Sign the encrypted data
    signature = sender_priv.sign(
        encrypted_data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )

    # Save transfer package
    transfer_data = encrypted_fernet_key + b"||" + signature + b"||" + encrypted_data
    with open("transfer_package.bin", "wb") as out:
        out.write(transfer_data)

    print("📦 File encrypted, signed, and saved as transfer_package.bin\n")

# -----------------------------
# Verification and Decryption
# -----------------------------
def decrypt_and_verify_file(recipient, sender_pubkey, output_file="received_output.txt"):
    """Decrypt the transfer package and verify the signature."""
    if not os.path.exists("transfer_package.bin"):
        print("⚠️ No transfer package found.")
        return

    # Load data
    with open("transfer_package.bin", "rb") as f:
        data = f.read()

    parts = data.split(b"||")
    if len(parts) != 3:
        print("⚠️ Invalid package format.")
        return

    encrypted_fernet_key, signature, encrypted_data = parts

    # Load recipient private key
    with open(f"keys/{recipient}_private.pem", "rb") as f:
        recipient_priv = serialization.load_pem_private_key(f.read(), password=None)

    # Decrypt Fernet key
    fernet_key = recipient_priv.decrypt(
        encrypted_fernet_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )

    # Load sender public key
    with open(sender_pubkey, "rb") as f:
        sender_pub = serialization.load_pem_public_key(f.read())

    # Verify signature
    try:
        sender_pub.verify(
            signature,
            encrypted_data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        print("✅ Signature verified successfully.")
    except Exception:
        print("❌ Signature verification failed.")
        return

    # Decrypt the file
    fernet = Fernet(fernet_key)
    decrypted_data = fernet.decrypt(encrypted_data)

    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    print(f"📂 File decrypted and saved as {output_file}\n")

# -----------------------------
# Main Menu
# -----------------------------
while True:
    print("=== Secure File Transfer System ===")
    print("1. Generate RSA Keys")
    print("2. Encrypt & Sign File")
    print("3. Decrypt & Verify File")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        user = input("Enter username: ")
        generate_rsa_keys(user)
    elif choice == "2":
        sender = input("Enter your username: ")
        recipient_pub = input("Enter recipient's public key path: ")
        file = input("Enter path to file to encrypt: ")
        encrypt_and_sign_file(sender, recipient_pub, file)
    elif choice == "3":
        recipient = input("Enter your username: ")
        sender_pub = input("Enter sender's public key path: ")
        decrypt_and_verify_file(recipient, sender_pub)
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid option.\n")

