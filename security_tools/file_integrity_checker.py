# file_integrity_checker.py
# Checks if a file has changed by comparing SHA256 hashes.

import hashlib

def get_file_hash(filename):
    """Return the SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filename, "rb") as f:  # rb = read in binary mode
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def compare_files(file1, file2):
    """Compare two files and print whether they're identical."""
    hash1 = get_file_hash(file1)
    hash2 = get_file_hash(file2)

    print(f"\nHash of {file1}: {hash1}")
    print(f"Hash of {file2}: {hash2}")

    if hash1 == hash2:
        print("\n✅ Files are identical (no change detected).")
    else:
        print("\n⚠️  Files are different (possible tampering).")

# ---- Main program ----
print("=== File Integrity Checker ===")
file_a = input("Enter the first file path: ")
file_b = input("Enter the second file path: ")

compare_files(file_a, file_b)
