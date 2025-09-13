import json
import base64
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_cipher_suite():
    """Get cipher suite with the encryption key from .env"""
    env_key = os.getenv("ENCRYPTION_KEY")
    if env_key:
        try:
            # Try to use the key directly as Fernet key
            cipher_suite = Fernet(env_key.encode())
            return cipher_suite
        except Exception as e:
            print(f"Error initializing cipher suite: {e}")
    return None

def encrypt_data(data: str, cipher_suite) -> str:
    """Encrypt data with the cipher suite"""
    if not data:
        return ""
    try:
        encrypted_data = cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return ""

def reencrypt_user_data():
    """Re-encrypt user data with the new encryption key"""
    try:
        # Get cipher suite
        cipher_suite = get_cipher_suite()
        if not cipher_suite:
            print("Failed to initialize cipher suite")
            return
        
        # Load user data
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)
        
        # Get user ID (first user in the file)
        user_id = list(user_data.keys())[0]
        print(f"Re-encrypting data for user ID: {user_id}")
        
        # Get current encrypted API keys
        encrypted_api_key = user_data[user_id]['bybit_api_key']
        encrypted_api_secret = user_data[user_id]['bybit_api_secret']
        
        print(f"Current encrypted API Key: {encrypted_api_key}")
        print(f"Current encrypted API Secret: {encrypted_api_secret}")
        
        # Since we can't decrypt the old keys, we'll use the plain text keys from .env
        # Load plain text keys from .env
        plain_api_key = os.getenv("BYBIT_API_KEY")
        plain_api_secret = os.getenv("BYBIT_API_SECRET")
        
        if not plain_api_key or not plain_api_secret:
            print("ERROR: Plain text API keys not found in .env")
            return
        
        print(f"Plain API Key: {plain_api_key}")
        print(f"Plain API Secret: {plain_api_secret}")
        
        # Encrypt with new key
        new_encrypted_api_key = encrypt_data(plain_api_key, cipher_suite)
        new_encrypted_api_secret = encrypt_data(plain_api_secret, cipher_suite)
        
        print(f"New encrypted API Key: {new_encrypted_api_key}")
        print(f"New encrypted API Secret: {new_encrypted_api_secret}")
        
        # Update user data
        user_data[user_id]['bybit_api_key'] = new_encrypted_api_key
        user_data[user_id]['bybit_api_secret'] = new_encrypted_api_secret
        
        # Save updated user data
        with open('user_data.json', 'w') as f:
            json.dump(user_data, f, indent=2)
        
        print("User data successfully re-encrypted!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reencrypt_user_data()