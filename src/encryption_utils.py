import os
import base64
import bcrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding


# =====================================================
#  LOADING RSA KEYS
# =====================================================
def load_public_key():
    with open("rsa_keys/public.pem", "rb") as f:
        return serialization.load_pem_public_key(f.read())


def load_private_key():
    with open("rsa_keys/private.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


# =====================================================
#  AES ENCRYPTION (FOR PII)
# =====================================================

AES_KEY_FILE = "aes.key"

def load_or_create_aes_key():
    if os.path.exists(AES_KEY_FILE):
        with open(AES_KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = os.urandom(32)  # AES-256
        with open(AES_KEY_FILE, "wb") as f:
            f.write(key)
        return key

AES_KEY = load_or_create_aes_key()


def aes_encrypt(plain_text: str) -> str:
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv))
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded = padder.update(plain_text.encode()) + padder.finalize()

    encrypted = encryptor.update(padded) + encryptor.finalize()

    return base64.b64encode(iv + encrypted).decode()


def aes_decrypt(encrypted_text: str) -> str:
    raw = base64.b64decode(encrypted_text)
    iv = raw[:16]
    ciphertext = raw[16:]

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv))
    decryptor = cipher.decryptor()

    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    return decrypted.decode()


# =====================================================
#  RSA ENCRYPTION (FOR AES KEY SHARING)
# =====================================================
def rsa_encrypt_key(aes_key: bytes) -> bytes:
    public_key = load_public_key()

    return public_key.encrypt(
        aes_key,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def rsa_decrypt_key(enc_key: bytes) -> bytes:
    private_key = load_private_key()

    return private_key.decrypt(
        enc_key,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


# =====================================================
#  PASSWORD HASHING (BCRYPT)
# =====================================================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
