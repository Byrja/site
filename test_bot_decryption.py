import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security import decrypt_data

def load_user_data():
    """Simulate the load_user_data function from bot.py"""
    DATA_FILE = "user_data.json"
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Decrypt API keys when loading
            for user_id in data:
                if 'bybit_api_key' in data[user_id]:
                    decrypted_key = decrypt_data(data[user_id]['bybit_api_key'])
                    # Check if decryption failed
                    if decrypted_key == "__DECRYPTION_FAILED__":
                        # Reset the key if decryption failed
                        data[user_id]['bybit_api_key'] = ''
                        print("Reset API key due to decryption failure")
                    else:
                        data[user_id]['bybit_api_key'] = decrypted_key
                        print(f"Decrypted API Key: {decrypted_key}")
                if 'bybit_api_secret' in data[user_id]:
                    decrypted_secret = decrypt_data(data[user_id]['bybit_api_secret'])
                    # Check if decryption failed
                    if decrypted_secret == "__DECRYPTION_FAILED__":
                        # Reset the secret if decryption failed
                        data[user_id]['bybit_api_secret'] = ''
                        print("Reset API secret due to decryption failure")
                    else:
                        data[user_id]['bybit_api_secret'] = decrypted_secret
                        print(f"Decrypted API Secret: {decrypted_secret}")
            return data
    else:
        return {}

def test_bot_decryption():
    """Test decryption as bot.py would do it"""
    try:
        print("Testing bot decryption...")
        user_data = load_user_data()
        
        # Get user ID (first user in the file)
        user_id = list(user_data.keys())[0]
        print(f"User ID: {user_id}")
        
        api_key = user_data[user_id].get('bybit_api_key', '')
        api_secret = user_data[user_id].get('bybit_api_secret', '')
        
        print(f"Final API Key: {api_key}")
        print(f"Final API Secret: {api_secret}")
        
        if api_key and api_key != "__DECRYPTION_FAILED__":
            print("API Key decryption SUCCESS")
        else:
            print("API Key decryption FAILED")
            
        if api_secret and api_secret != "__DECRYPTION_FAILED__":
            print("API Secret decryption SUCCESS")
        else:
            print("API Secret decryption FAILED")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bot_decryption()