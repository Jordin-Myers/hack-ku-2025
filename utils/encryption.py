from cryptography.fernet import Fernet
import base64
import hashlib

def encrypt_key(secret: str, password: str) -> str:
    # Derive key from password
    key = hashlib.sha256(password.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key[:32])
    f = Fernet(fernet_key)
    encrypted = f.encrypt(secret.encode())
    return encrypted.decode()