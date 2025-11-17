# backup_utils.py
import os
from encryption_utils import rsa_encrypt_key, rsa_decrypt_key, load_or_create_aes_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import hashlib


# ============================================================
# Encrypt SQL Backup using Hybrid Encryption (AES + RSA)
# ============================================================
def encrypt_backup(input_sql_file, output_enc_file):
    aes_key = load_or_create_aes_key()
    iv = os.urandom(16)

    with open(input_sql_file, "rb") as f:
        data = f.read()

    # AES Encrypt data
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded) + encryptor.finalize()

    # RSA Encrypt AES key
    encrypted_key = rsa_encrypt_key(aes_key)

    with open(output_enc_file, "wb") as f:
        f.write(encrypted_key + b"---" + iv + encrypted_data)


# ============================================================
# Decrypt Encrypted Backup (RSA + AES)
# ============================================================
def decrypt_backup(input_enc_file, output_sql_file):
    with open(input_enc_file, "rb") as f:
        blob = f.read()

    encrypted_key, payload = blob.split(b"---", 1)

    aes_key = rsa_decrypt_key(encrypted_key)
    iv = payload[:16]
    encrypted_data = payload[16:]

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    with open(output_sql_file, "wb") as f:
        f.write(decrypted)


# ============================================================
# Generate SHA-256 integrity hash for backup file
# ============================================================
def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify_backup_hash(file_path, stored_hash):
    current_hash = sha256_file(file_path)
    return current_hash == stored_hash
