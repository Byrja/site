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
        # If env_key is a hex string, convert it to bytes and then to Fernet key
        try:
            # First try to treat it as a hex string
            key_bytes = bytes.fromhex(env_key)
            if len(key_bytes) == 32:
                # If it's 32 bytes, encode it as base64 for Fernet
                return base64.urlsafe_b64encode(key_bytes)
        except Exception:
            pass
        
        # If that fails, try to treat it as a base64 encoded key
        try:
            key_bytes = base64.urlsafe_b64decode(env_key)
            if len(key_bytes) == 32:
                # If it's a valid base64 encoded 32-byte key, use it as is
                return env_key.encode() if isinstance(env_key, str) else env_key
        except Exception:
            pass
    
    # Generate a proper Fernet key
    return Fernet.generate_key()

# Generate the encryption key
ENCRYPTION_KEY = generate_encryption_key()
try:
    cipher_suite = Fernet(ENCRYPTION_KEY)
except ValueError as e:
    print(f"Error initializing cipher suite: {e}")
    # If the key is still invalid, generate a proper one
    proper_key = Fernet.generate_key()
    ENCRYPTION_KEY = proper_key
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
        import traceback
        traceback.print_exc()
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
        import traceback
        traceback.print_exc()
        # Return a special marker to indicate decryption failure
        return "__DECRYPTION_FAILED__"

def generate_secure_key():
    """
    Generate a cryptographically secure random key for production use
    
    Returns:
        str: Base64 encoded 32-byte random key suitable for Fernet
    """
    # Generate a proper Fernet key
    key = Fernet.generate_key()
    # Return as string (base64 encoded)
    return key.decode()
