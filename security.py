from cryptography.fernet import Fernet

# Generate once and keep constant
KEY = b'gLDYEP8PeQg_Hg1ow47JAjB34-hr_Jbj83or1UpMFPM='

cipher = Fernet(KEY)

def encrypt_message(message: str) -> bytes:
    return cipher.encrypt(message.encode())

def decrypt_message(encrypted: bytes) -> str:
    return cipher.decrypt(encrypted).decode()