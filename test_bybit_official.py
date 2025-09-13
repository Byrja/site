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

def get_bybit_signature_official(api_key, api_secret, timestamp, params=None):
    """
    Generate signature according to Bybit official documentation
    """
    # For wallet balance endpoint, parameters are not included in signature
    query_string = ""
    
    # Signature = hex(HMAC_SHA256(timestamp + api_key + query_string))
    signature_data = timestamp + api_key + query_string
    signature = hmac.new(
        bytes(api_secret, "utf-8"),
        bytes(signature_data, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return signature

def get_bybit_wallet_balance_official(api_key, api_secret):
    """Get wallet balance from Bybit API using official method"""
    endpoint = "/v5/account/wallet-balance"
    url = f"{BYBIT_API_URL}{endpoint}"
    
    # Generate timestamp
    timestamp = str(int(time.time() * 1000))
    
    # Parameters
    params = {
        'accountType': 'UNIFIED'
    }
    
    # Generate signature
    signature = get_bybit_signature_official(api_key, api_secret, timestamp, params)
    
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

def test_bybit_official():
    """Test Bybit balance API call with official method"""
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
        print(f"API Secret length: {len(api_secret)}")
        
        # Test the balance API
        print("Calling Bybit wallet balance API with official method...")
        balance_data = get_bybit_wallet_balance_official(api_key, api_secret)
        
        print(f"Response: {json.dumps(balance_data, indent=2)}")
        
        if balance_data and balance_data.get('retCode') == 0:
            result = balance_data.get('result', {})
            balance_list = result.get('list', [])
            
            if balance_list and len(balance_list) > 0:
                balances = balance_list[0].get('coin', [])
                print(f"Found {len(balances)} coins in wallet")
                
                total_balance = 0
                for coin in balances:
                    coin_name = coin.get('coin', 'Unknown')
                    coin_balance = float(coin.get('walletBalance', 0))
                    coin_usd_value = float(coin.get('usdValue', 0))
                    total_balance += coin_usd_value
                    
                    if coin_balance > 0:
                        print(f"  {coin_name}: {coin_balance:.4f} (≈ ${coin_usd_value:.2f})")
                
                print(f"Total balance: ${total_balance:.2f}")
            else:
                print("No balances found in wallet")
        else:
            print("Failed to get balance data")
            if balance_data:
                print(f"Error: {balance_data.get('retMsg', 'Unknown error')}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bybit_official()