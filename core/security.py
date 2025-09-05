# Thêm các import mới từ cryptography
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
import os
import base64

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from core.config import settings

# Thêm các hằng số cho hashing
SALT_SIZE = 16
ITERATIONS = 390000 # Số vòng lặp khuyến nghị bởi OWASP

# JWT settings - Taken from config.py settings object
SECRET_KEY = settings.secret_key # Changed to lowercase
ALGORITHM = settings.algorithm # Changed to lowercase

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    # Tách salt và hash từ hashed_password
    try:
        salt_b64 = hashed_password[:24] # Salt là 16 bytes = 24 ký tự base64
        actual_hash_b64 = hashed_password[24:]

        salt = base64.b64decode(salt_b64)
        actual_hash = base64.b64decode(actual_hash_b64)
    except Exception:
        return False # Định dạng hash không hợp lệ

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # Chiều dài khóa (hash)
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    try:
        # Derive key (hash) from plain password using the same salt and iterations
        derived_key = kdf.derive(plain_password.encode('utf-8'))
        return derived_key == actual_hash
    except Exception:
        return False # Lỗi trong quá trình băm hoặc so sánh

def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    salt = os.urandom(SALT_SIZE) # Tạo salt ngẫu nhiên
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # Chiều dài khóa (hash)
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    key = kdf.derive(password.encode('utf-8'))

    # Kết hợp salt và hash, sau đó mã hóa base64 để lưu trữ
    hashed_password = base64.b64encode(salt).decode('utf-8') + base64.b64encode(key).decode('utf-8')
    return hashed_password

# Giữ nguyên các hàm JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()

    # Convert 'sub' to string if it's not already
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"]) # Ensure subject is a string

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes) # Changed to lowercase
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decode a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        print("Debug: JWTError occurred during token decoding.")
        return None
