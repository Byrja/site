import json
from security import decrypt_data

def test_decryption():
    """Test decryption of API keys"""
    try:
        # Load user data
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)
        
        # Get user ID (first user in the file)
        user_id = list(user_data.keys())[0]
        print(f"Testing for user ID: {user_id}")
        
        # Get encrypted API keys
        encrypted_api_key = user_data[user_id]['bybit_api_key']
        encrypted_api_secret = user_data[user_id]['bybit_api_secret']
        
        print(f"Encrypted API Key: {encrypted_api_key}")
        print(f"Encrypted API Secret: {encrypted_api_secret}")
        
        # Decrypt API keys
        api_key = decrypt_data(encrypted_api_key)
        api_secret = decrypt_data(encrypted_api_secret)
        
        print(f"Decrypted API Key: {api_key}")
        print(f"Decrypted API Secret: {api_secret}")
        print(f"API Key length: {len(api_key)}")
        print(f"API Secret length: {len(api_secret)}")
        
        # Check for decryption errors
        if api_key == "__DECRYPTION_FAILED__":
            print("ERROR: Failed to decrypt API Key")
        if api_secret == "__DECRYPTION_FAILED__":
            print("ERROR: Failed to decrypt API Secret")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_decryption()