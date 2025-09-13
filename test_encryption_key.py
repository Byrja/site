import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables
load_dotenv()

def test_encryption_key():
    """Test the encryption key from .env"""
    env_key = os.getenv("ENCRYPTION_KEY")
    print(f"ENCRYPTION_KEY from .env: {env_key}")
    print(f"Length: {len(env_key) if env_key else 0}")
    
    try:
        # Try to create a Fernet instance with the key
        cipher_suite = Fernet(env_key.encode())
        print("Successfully created Fernet cipher suite")
        
        # Test encryption/decryption
        test_data = "test_data_123"
        encrypted = cipher_suite.encrypt(test_data.encode())
        print(f"Encrypted test data: {encrypted}")
        
        decrypted = cipher_suite.decrypt(encrypted)
        print(f"Decrypted test data: {decrypted.decode()}")
        
        if test_data == decrypted.decode():
            print("Encryption/Decryption test PASSED")
        else:
            print("Encryption/Decryption test FAILED")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_encryption_key()