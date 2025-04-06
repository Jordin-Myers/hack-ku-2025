from cryptography.fernet import Fernet
import base64
import hashlib

def derive_fernet_key(password: str) -> bytes:
    sha256 = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(sha256)

def encrypt_key(secret: str, password: str) -> str:
    fernet_key = derive_fernet_key(password)
    f = Fernet(fernet_key)
    encrypted = f.encrypt(secret.encode())
    return encrypted.decode()

def decrypt_key(token: str, password: str) -> str:
    fernet_key = derive_fernet_key(password)
    f = Fernet(fernet_key)
    decrypted = f.decrypt(token.encode())
    return decrypted.decode()