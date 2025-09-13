import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security import encrypt_data, decrypt_data

def test_security_functions():
    """Test encryption/decryption functions directly"""
    try:
        # Test with simple data
        test_data = "test_data_123"
        print(f"Original data: {test_data}")
        
        # Encrypt
        encrypted = encrypt_data(test_data)
        print(f"Encrypted data: {encrypted}")
        
        # Decrypt
        decrypted = decrypt_data(encrypted)
        print(f"Decrypted data: {decrypted}")
        
        if test_data == decrypted:
            print("Encryption/Decryption test PASSED")
        else:
            print("Encryption/Decryption test FAILED")
            
        # Test with actual API key format
        api_key = "tR48LMGCJo6l0OH7Xq"
        print(f"\nAPI Key: {api_key}")
        
        # Encrypt
        encrypted_key = encrypt_data(api_key)
        print(f"Encrypted API Key: {encrypted_key}")
        
        # Decrypt
        decrypted_key = decrypt_data(encrypted_key)
        print(f"Decrypted API Key: {decrypted_key}")
        
        if api_key == decrypted_key:
            print("API Key Encryption/Decryption test PASSED")
        else:
            print("API Key Encryption/Decryption test FAILED")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_security_functions()