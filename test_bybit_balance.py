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

def get_bybit_signature_v3(api_key, api_secret, method, url, params=None, data=None):
    """Generate signature for Bybit V3 API request"""
    timestamp = str(int(time.time() * 1000))
    
    # Separate params for signature (without recvWindow) and request
    signature_params = {}
    request_params = {}
    
    if params:
        for key, value in params.items():
            request_params[key] = value
            # Exclude recvWindow from signature for GET requests
            if not (method.upper() == "GET" and key == "recvWindow"):
                signature_params[key] = value
        # Sort signature parameters and create query string
        sorted_signature_params = sorted(signature_params.items())
        query_string = urlencode(sorted_signature_params)
    else:
        query_string = ""
        request_params = {}
    
    if data:
        body = json.dumps(data, separators=(",", ":"))
    else:
        body = ""
    
    # For GET requests, the signature data is timestamp + api_key + query_string
    # For POST requests, it's timestamp + api_key + query_string + body
    if method.upper() == "GET":
        signature_data = timestamp + api_key + query_string
    else:  # POST
        signature_data = timestamp + api_key + query_string + body
    
    signature = hmac.new(
        bytes(api_secret, "utf-8"),
        bytes(signature_data, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return signature, timestamp

def make_bybit_request(api_key, api_secret, method, endpoint, params=None, data=None):
    """Make authenticated request to Bybit API"""
    try:
        url = f"{BYBIT_API_URL}{endpoint}"
        
        # Generate timestamp
        timestamp = str(int(time.time() * 1000))
        
        # Add recv_window parameter to prevent timestamp errors (Bybit specific)
        if params is None:
            params = {}
        params['recvWindow'] = 10000  # 10 seconds (Bybit uses camelCase)
        
        # Generate signature
        signature, _ = get_bybit_signature_v3(api_key, api_secret, method, url, params, data)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": "10000"  # Bybit header for recv window
        }
        
        # Make API request
        if method.upper() == "GET":
            response = requests.get(url, params=params, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, params=params, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Bybit API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error making Bybit request: {e}")
        return None

def test_bybit_balance():
    """Test Bybit balance API call"""
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
        print("Calling Bybit wallet balance API...")
        balance_data = get_bybit_wallet_balance(api_key, api_secret)
        
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
    test_bybit_balance()