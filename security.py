import base64
import os
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_encryption_key():
    """
    Generate a secure encryption key
    
    For production use:
    1. Generate a truly random 32-byte key
    2. Store it securely (environment variable, key management service, etc.)
    3. Never hardcode it in the source code
    """
    # Try to get key from environment variable
    env_key = os.getenv("ENCRYPTION_KEY")
    if env_key:
        # Convert from hex string to bytes
        try:
            return base64.urlsafe_b64encode(bytes.fromhex(env_key))
        except Exception:
            pass
    
    # Generate a proper Fernet key
    return Fernet.generate_key()

# Generate the encryption key
ENCRYPTION_KEY = generate_encryption_key()
try:
    cipher_suite = Fernet(ENCRYPTION_KEY)
except ValueError:
    # If the key is still invalid, generate a proper one
    proper_key = Fernet.generate_key()
    cipher_suite = Fernet(proper_key)

# Functions for encryption/decryption
def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data
    
    Args:
        data (str): The data to encrypt
        
    Returns:
        str: Base64 encoded encrypted data
    """
    if not data:
        return ""
    try:
        encrypted_data = cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return ""

def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data
    
    Args:
        encrypted_data (str): Base64 encoded encrypted data
        
    Returns:
        str: Decrypted data
    """
    if not encrypted_data:
        return ""
    try:
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return ""

def generate_secure_key():
    """
    Generate a cryptographically secure random key for production use
    
    Returns:
        str: Hex representation of a 32-byte random key
    """
    return secrets.token_hex(32)