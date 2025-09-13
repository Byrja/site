import os
import sys
import json
import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BYBIT_API_URL
from security import decrypt_data

def get_bybit_signature_final(api_key, api_secret, timestamp, params=None):
    """
    Generate signature according to Bybit documentation
    """
    # For wallet balance endpoint, parameters are not included in signature string
    param_str = ""
    
    # Signature = hex(HMAC_SHA256(timestamp + api_key + param_str))
    signature_data = timestamp + api_key + param_str
    signature = hmac.new(
        bytes(api_secret, "utf-8"),
        bytes(signature_data, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return signature

def get_bybit_wallet_balance_final(api_key, api_secret):
    """Get wallet balance from Bybit API with final approach"""
    endpoint = "/v5/account/wallet-balance"
    url = f"{BYBIT_API_URL}{endpoint}"
    
    # Generate timestamp
    timestamp = str(int(time.time() * 1000))
    
    # Parameters
    params = {
        'accountType': 'UNIFIED'
    }
    
    # Generate signature
    signature = get_bybit_signature_final(api_key, api_secret, timestamp, params)
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": signature,
        "X-BAPI-RECV-WINDOW": "10000"
    }
    
    # Make API request
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Bybit API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error making Bybit request: {e}")
        return None

def test_bybit_final():
    """Test Bybit balance API call with final method"""
    # Load user data
    try:
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)
        
        # Get user ID (first user in the file)
        user_id = list(user_data.keys())[0]
        print(f"Testing for user ID: {user_id}")
        
        # Decrypt API keys
        encrypted_api_key = user_data[user_id]['bybit_api_key']
        encrypted_api_secret = user_data[user_id]['bybit_api_secret']
        
        api_key = decrypt_data(encrypted_api_key)
        api_secret = decrypt_data(encrypted_api_secret)
        
        print(f"API Key: {api_key}")
        
        # Test the balance API
        print("Calling Bybit wallet balance API with final method...")
        balance_data = get_bybit_wallet_balance_final(api_key, api_secret)
        
        if balance_data:
            print(f"Response code: {balance_data.get('retCode')}")
            if balance_data.get('retCode') == 0:
                print("SUCCESS: API call worked!")
            else:
                print(f"Error: {balance_data.get('retMsg', 'Unknown error')}")
        else:
            print("No response data")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bybit_final()