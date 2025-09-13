import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import json
import os
import requests
import hmac
import hashlib
import time
from datetime import datetime
from urllib.parse import urlencode
from config import TELEGRAM_BOT_TOKEN, USER_DATA_FILE, USER_STATES_FILE, BYBIT_API_URL
from security import encrypt_data, decrypt_data

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# File to store user data
DATA_FILE = USER_DATA_FILE
USER_STATES = USER_STATES_FILE

# Load or create user data
def load_user_data():
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
                    else:
                        data[user_id]['bybit_api_key'] = decrypted_key
                if 'bybit_api_secret' in data[user_id]:
                    decrypted_secret = decrypt_data(data[user_id]['bybit_api_secret'])
                    # Check if decryption failed
                    if decrypted_secret == "__DECRYPTION_FAILED__":
                        # Reset the secret if decryption failed
                        data[user_id]['bybit_api_secret'] = ''
                    else:
                        data[user_id]['bybit_api_secret'] = decrypted_secret
            return data
    else:
        return {}

# Save user data
def save_user_data(data):
    # Encrypt API keys before saving
    data_to_save = {}
    for user_id in data:
        data_to_save[user_id] = data[user_id].copy()
        if 'bybit_api_key' in data_to_save[user_id]:
            # Don't encrypt the error marker
            if data_to_save[user_id]['bybit_api_key'] != "__DECRYPTION_FAILED__":
                data_to_save[user_id]['bybit_api_key'] = encrypt_data(data_to_save[user_id]['bybit_api_key'])
        if 'bybit_api_secret' in data_to_save[user_id]:
            # Don't encrypt the error marker
            if data_to_save[user_id]['bybit_api_secret'] != "__DECRYPTION_FAILED__":
                data_to_save[user_id]['bybit_api_secret'] = encrypt_data(data_to_save[user_id]['bybit_api_secret'])
    
    with open(DATA_FILE, 'w') as f:
        json.dump(data_to_save, f, indent=2)

# Load or create user states
def load_user_states():
    if os.path.exists(USER_STATES):
        with open(USER_STATES, 'r') as f:
            return json.load(f)
    else:
        return {}

# Save user states
def save_user_states(states):
    with open(USER_STATES, 'w') as f:
        json.dump(states, f, indent=2)

# Bybit API functions
def get_bybit_signature(api_key, api_secret, params, timestamp):
    """Generate signature for Bybit API request"""
    param_str = f"{timestamp}{api_key}{''}{urlencode(sorted(params.items()))}"
    signature = hmac.new(
        bytes(api_secret, "utf-8"),
        bytes(param_str, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature


def get_bybit_signature_v3(api_key, api_secret, method, url, params=None, data=None):
    """Generate signature for Bybit V3 API request"""
    timestamp = str(int(time.time() * 1000))
    
    if params:
        query_string = urlencode(sorted(params.items()))
    else:
        query_string = ""
    
    if data:
        body = json.dumps(data, separators=(",", ":"))
    else:
        body = ""
    
    signature_data = timestamp + api_key + query_string + body
    signature = hmac.new(
        bytes(api_secret, "utf-8"),
        bytes(signature_data, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return signature, timestamp

def get_bybit_wallet_balance(api_key, api_secret):
    """Get wallet balance from Bybit API"""
    params = {'accountType': 'UNIFIED'}
    return make_bybit_request(api_key, api_secret, "GET", "/v5/account/wallet-balance", params=params)

def get_bybit_positions(api_key, api_secret):
    """Get positions from Bybit API"""
    params = {'category': 'linear'}
    return make_bybit_request(api_key, api_secret, "GET", "/v5/position/list", params=params)

def make_bybit_request(api_key, api_secret, method, endpoint, params=None, data=None):
    """Make authenticated request to Bybit API"""
    try:
        url = f"{BYBIT_API_URL}{endpoint}"
        
        # Generate signature
        signature, timestamp = get_bybit_signature_v3(api_key, api_secret, method, url, params, data)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature
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
            logger.error(f"Bybit API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error making Bybit request: {e}")
        return None

# Main menu
def main_menu():
    keyboard = [
        [InlineKeyboardButton('💰 Крипта', callback_data='crypto_menu'), InlineKeyboardButton(' Мос Копилка', callback_data='piggy_bank_menu')],
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Function to delete user message for privacy
def delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> None:
    try:
        import asyncio
        asyncio.create_task(context.bot.delete_message(chat_id=chat_id, message_id=message_id))
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    # Delete user's message for privacy
    # if update.message:
    #     delete_message(context, update.effective_chat.id, update.message.message_id)
    
    # Initialize user data if not exists
    if user_id not in user_data:
        user_data[user_id] = {
            'bybit_api_key': '',
            'bybit_api_secret': '',
            'piggy_banks': {},
            'shopping_list': {
                'Продукты': [],
                'Аптека': [],
                'Остальное': []
            }
        }
        save_user_data(user_data)
    else:
        # Ensure shopping list structure exists for existing users
        if 'shopping_list' not in user_data[user_id]:
            user_data[user_id]['shopping_list'] = {
                'Продукты': [],
                'Аптека': [],
                'Остальное': []
            }
        else:
            # Ensure all categories exist
            categories = ['Продукты', 'Аптека', 'Остальное']
            for category in categories:
                if category not in user_data[user_id]['shopping_list']:
                    user_data[user_id]['shopping_list'][category] = []
        save_user_data(user_data)
    
    if user_id in user_states:
        del user_states[user_id]
        save_user_states(user_states)
    
    # Create a comprehensive menu with all functionality
    keyboard = [
        [InlineKeyboardButton('💰 Крипта', callback_data='crypto_menu'), InlineKeyboardButton(' Мос Копилка', callback_data='piggy_bank_menu')],
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu')],
        [InlineKeyboardButton('⚙️ Настройки', callback_data='settings_menu'), InlineKeyboardButton('ℹ️ Помощь', callback_data='help_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        'Добро пожаловать в финансовый бот! 🤖\n\n'
        'Здесь вы можете управлять своими финансами, криптовалютными активами, '
        'копилками и списками покупок.\n\n'
        'Выберите нужный раздел:'
    )
    
    # Send the menu with buttons
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )

# Function to show main menu
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create a comprehensive menu with all functionality
    keyboard = [
        [InlineKeyboardButton('💰 Крипта', callback_data='crypto_menu'), InlineKeyboardButton(' Мос Копилка', callback_data='piggy_bank_menu')],
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu')],
        [InlineKeyboardButton('⚙️ Настройки', callback_data='settings_menu'), InlineKeyboardButton('ℹ️ Помощь', callback_data='help_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        'Главное меню:',
        reply_markup=reply_markup
    )

# Callback versions of menu functions
async def show_main_menu_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create a comprehensive menu with all functionality
    keyboard = [
        [InlineKeyboardButton('💰 Крипта', callback_data='crypto_menu'), InlineKeyboardButton(' Мос Копилка', callback_data='piggy_bank_menu')],
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu')],
        [InlineKeyboardButton('⚙️ Настройки', callback_data='settings_menu'), InlineKeyboardButton('ℹ️ Помощь', callback_data='help_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        'Главное меню:',
        reply_markup=reply_markup
    )

# Handle all text messages
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
        
    text = update.message.text
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    # Delete user's message for privacy
    # delete_message(context, update.effective_chat.id, update.message.message_id)
    
    # Handle different states
    if user_id in user_states:
        state = user_states[user_id]
        
        # Handle API key input
        if state == 'WAITING_API_KEY':
            await handle_api_key_input(update, context)
            return
        elif state == 'WAITING_API_SECRET':
            await handle_api_secret_input(update, context)
            return
        # Handle piggy bank creation
        elif state == 'CREATING_PIGGY_NAME':
            await handle_piggy_name_input(update, context)
            return
        elif state.startswith('CREATING_PIGGY_TARGET_'):
            await handle_piggy_target_input(update, context)
            return
        # Handle deposit/withdraw
        elif state.startswith('DEPOSITING_') or state.startswith('WITHDRAWING_'):
            await handle_amount_input(update, context)
            return
        # Handle shopping list item addition
        elif state.startswith('ADDING_ITEM_'):
            await handle_add_shopping_item(update, context)
            return
        # Handle piggy bank editing
        elif state.startswith('EDITING_PIGGY_NAME_'):
            await handle_edit_piggy_name_input(update, context)
            return
        elif state.startswith('EDITING_PIGGY_TARGET_'):
            await handle_edit_piggy_target_input(update, context)
            return
    
    # Clear user state if not in a specific flow
    if user_id in user_states:
        should_clear_state = True
        # Don't clear state for specific flows
        if not text.startswith(('➕ Создать копилку', '✏️ Редактировать', '💰 Положить', '💸 Снять')):
            if text not in ['🔑 Ввести API ключи', '➕ Добавить']:
                del user_states[user_id]
                save_user_states(user_states)
    
    # Handle menu selections
    if text == '💰 Крипта':
        await handle_crypto_menu(update, context)
    elif text in [' Мос Копилка', ' Мос Копилка', ' Мос Копилка']:  # Handle variations
        await handle_piggy_bank_menu(update, context)
    elif text == '🛒 Список покупок':
        await handle_shopping_list_menu(update, context)
    elif text == '🏠 Главная':
        await start(update, context)  # Make this async call
    elif text.startswith(' Мос '):
        # Handle piggy bank selection
        piggy_name = text[2:].strip()
        await handle_piggy_bank_actions(update, context, piggy_name)
    elif text in ['📊 Статистика', '💰 Баланс', '⚙️ Настройки']:
        await handle_crypto_submenu(update, context, text)
    elif text in ['🍎 Продукты', '