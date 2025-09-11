import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os
import requests
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, USER_DATA_FILE, USER_STATES_FILE
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
                    data[user_id]['bybit_api_key'] = decrypt_data(data[user_id]['bybit_api_key'])
                if 'bybit_api_secret' in data[user_id]:
                    data[user_id]['bybit_api_secret'] = decrypt_data(data[user_id]['bybit_api_secret'])
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
            data_to_save[user_id]['bybit_api_key'] = encrypt_data(data_to_save[user_id]['bybit_api_key'])
        if 'bybit_api_secret' in data_to_save[user_id]:
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

# Main menu
def main_menu():
    keyboard = [
        [{'text': '💰 Крипта'}, {'text': '🏦 Копилка'}],
        [{'text': '🛒 Список покупок'}]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

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
    if update.message:
        delete_message(context, update.effective_chat.id, update.message.message_id)
    
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
    
    if user_id in user_states:
        del user_states[user_id]
        save_user_states(user_states)
    
    await update.message.reply_text(
        'Добро пожаловать в финансовый бот! 🤖\nВыберите нужный раздел:',
        reply_markup=main_menu()
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
    delete_message(context, update.effective_chat.id, update.message.message_id)
    
    # Handle different states
    if user_id in user_states:
        state = user_states[user_id]
        
        # Handle API key input
        if state == 'WAITING_API_KEY':
            handle_api_key_input(update, context)
            return
        elif state == 'WAITING_API_SECRET':
            handle_api_secret_input(update, context)
            return
        # Handle piggy bank creation
        elif state == 'CREATING_PIGGY_NAME':
            handle_piggy_name_input(update, context)
            return
        elif state.startswith('CREATING_PIGGY_TARGET_'):
            handle_piggy_target_input(update, context)
            return
        # Handle deposit/withdraw
        elif state.startswith('DEPOSITING_') or state.startswith('WITHDRAWING_'):
            handle_amount_input(update, context)
            return
        # Handle shopping list item addition
        elif state.startswith('ADDING_ITEM_'):
            handle_add_shopping_item(update, context)
            return
        # Handle piggy bank editing
        elif state.startswith('EDITING_PIGGY_NAME_'):
            handle_edit_piggy_name(update, context)
            return
        elif state.startswith('EDITING_PIGGY_TARGET_'):
            handle_edit_piggy_target(update, context)
            return
    
    # Clear user state if not in a specific flow
    if user_id in user_states and not text.startswith(('➕ Создать копилку', '✏️ Редактировать', '💰 Положить', '💸 Снять')):
        if text not in ['🔑 Ввести API ключи', '➕ Добавить']:
            del user_states[user_id]
            save_user_states(user_states)
    
    # Handle menu selections
    if text == '💰 Крипта':
        handle_crypto_menu(update, context)
    elif text == '🏦 Копилка':
        handle_piggy_bank_menu(update, context)
    elif text == '🛒 Список покупок':
        handle_shopping_list_menu(update, context)
    elif text == '🏠 Главная':
        start(update, context)
    elif text.startswith(' Мос '):
        # Handle piggy bank selection
        piggy_name = text[2:].strip()
        handle_piggy_bank_actions(update, context, piggy_name)
    elif text in ['📊 Статистика', '💰 Баланс', '⚙️ Настройки']:
        handle_crypto_submenu(update, context, text)
    elif text in ['🍎 Продукты', '💊 Аптека', '📦 Остальное']:
        handle_shopping_category(update, context, text[2:])  # Remove emoji
    elif text == '➕ Создать копилку':
        handle_create_piggy_bank(update, context)
    elif text == '🔑 Ввести API ключи':
        handle_enter_api_keys(update, context)
    elif text == '➕ Добавить':
        # This will be handled by state
        pass
    elif text.startswith('❌ ') and len(text) > 2:
        # Handle item deletion from shopping list
        item_to_delete = text[2:]  # Remove emoji
        handle_delete_shopping_item(update, context, item_to_delete)
    elif text == '🗑 Очистить':
        handle_clear_shopping_category(update, context)
    elif text.startswith('💰 Положить'):
        # Extract piggy bank name from state or message
        handle_deposit_to_piggy(update, context)
    elif text.startswith('💸 Снять'):
        handle_withdraw_from_piggy(update, context)
    elif text == '✏️ Редактировать':
        handle_edit_piggy_bank(update, context)
    elif text == '❌ Удалить':
        handle_delete_piggy_bank(update, context)
    else:
        # For any other text, show main menu
        update.message.reply_text('Пожалуйста, выберите действие из меню:', reply_markup=main_menu())

# Handle crypto menu
def handle_crypto_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [{'text': '📊 Статистика'}, {'text': '💰 Баланс'}],
        [{'text': '⚙️ Настройки'}, {'text': '🏠 Главная'}]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    # Check if API keys are set
    if not user_data.get(user_id, {}).get('bybit_api_key') or not user_data.get(user_id, {}).get('bybit_api_secret'):
        update.message.reply_text(
            'Для работы с криптой необходимо настроить API ключи Bybit.\nПожалуйста, перейдите в настройки.',
            reply_markup=reply_markup
        )
        return
    
    # Here we would normally fetch data from Bybit API
    # For now, let's show a placeholder message
    update.message.reply_text(
        '📈 Активные сделки:\n\n'
        'BTC/USDT: +2.5% ($120)\n'
        'ETH/USDT: -1.2% (-$45)\n\n'
        'Общий PnL: +$75\n\n'
        'Выберите действие:',
        reply_markup=reply_markup
    )

# Handle crypto submenu
def handle_crypto_submenu(update: Update, context: ContextTypes.DEFAULT_TYPE, selection: str) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if selection == '📊 Статистика':
        # Statistics submenu
        keyboard = [
            [{'text': '📅 День'}, {'text': '📆 Неделя'}],
            [{'text': '🗓 Месяц'}, {'text': 'FullYear'}],
            [{'text': '🏠 Главная'}]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text('Выберите период статистики:', reply_markup=reply_markup)
        
    elif selection == '💰 Баланс':
        # Show balance
        update.message.reply_text(
            '💰 Баланс кошелька:\n\n'
            'BTC: 0.0025 (≈ $150)\n'
            'ETH: 0.5 (≈ $1,200)\n'
            'USDT: 500\n'
            'BNB: 1.2 (≈ $350)\n\n'
            'Общий баланс: ≈ $2,200',
            reply_markup=ReplyKeyboardMarkup([
                [{'text': '🏠 Главная'}]
            ], resize_keyboard=True)
        )
        
    elif selection == '⚙️ Настройки':
        # Settings menu
        keyboard = [
            [{'text': '🔑 Ввести API ключи'}],
            [{'text': '🏠 Главная'}]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        api_info = ""
        if user_data.get(user_id, {}).get('bybit_api_key'):
            api_info = f"\nAPI Key: {user_data[user_id]['bybit_api_key'][:5]}...{user_data[user_id]['bybit_api_key'][-5:]}"
        
        update.message.reply_text(
            f'⚙️ Настройки Bybit:{api_info}\n\nВыберите действие:',
            reply_markup=reply_markup
        )

# Handle enter API keys
def handle_enter_api_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    
    user_states[user_id] = 'WAITING_API_KEY'
    save_user_states(user_states)
    
    update.message.reply_text(
        'Введите ваш API ключ Bybit:',
        reply_markup=ReplyKeyboardMarkup([
            [{'text': '🏠 Главная'}]
        ], resize_keyboard=True)
    )

# Handle API key input
def handle_api_key_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or user_states[user_id] != 'WAITING_API_KEY':
        return
        
    # Save API key
    if user_id not in user_data:
        user_data[user_id] = {}
    if 'bybit_api_key' not in user_data[user_id]:
        user_data[user_id]['bybit_api_key'] = ''
        
    user_data[user_id]['bybit_api_key'] = update.message.text
    save_user_data(user_data)
    
    del user_states[user_id]
    save_user_states(user_states)
    
    update.message.reply_text(
        '✅ API ключ сохранен!\nТеперь введите API Secret:',
        reply_markup=ReplyKeyboardMarkup([
            [{'text': '🏠 Главная'}]
        ], resize_keyboard=True)
    )
    
    # Set state to wait for secret
    user_states[user_id] = 'WAITING_API_SECRET'
    save_user_states(user_states)

# Handle API secret input
def handle_api_secret_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or user_states[user_id] != 'WAITING_API_SECRET':
        return
        
    # Save API secret
    if user_id not in user_data:
        user_data[user_id] = {}
    if 'bybit_api_secret' not in user_data[user_id]:
        user_data[user_id]['bybit_api_secret'] = ''
        
    user_data[user_id]['bybit_api_secret'] = update.message.text
    save_user_data(user_data)
    
    del user_states[user_id]
    save_user_states(user_states)
    
    update.message.reply_text(
        '✅ API Secret сохранен!\nНастройка Bybit завершена.',
        reply_markup=ReplyKeyboardMarkup([
            [{'text': '🏠 Главная'}]
        ], resize_keyboard=True)
    )

# Piggy bank section
def handle_piggy_bank_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    keyboard = [
        [{'text': '➕ Создать копилку'}]
    ]
    
    # Add existing piggy banks
    if user_id in user_data and user_data[user_id]['piggy_banks']:
        for name in user_data[user_id]['piggy_banks']:
            keyboard.append([{'text': f' Мос {name}'}])
    
    keyboard.append([{'text': '🏠 Главная'}])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if not user_data.get(user_id, {}).get('piggy_banks'):
        update.message.reply_text('🏠 Раздел копилки:\nУ вас пока нет копилок.', reply_markup=reply_markup)
    else:
        update.message.reply_text('🏠 Раздел копилок:', reply_markup=reply_markup)

# Handle piggy bank actions
def handle_piggy_bank_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, piggy_name: str) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data or piggy_name not in user_data[user_id]['piggy_banks']:
        update.message.reply_text('Копилка не найдена', reply_markup=main_menu())
        return
    
    piggy = user_data[user_id]['piggy_banks'][piggy_name]
    current = piggy['current']
    target = piggy['target']
    percentage = round((current / target) * 100, 1) if target > 0 else 0
    
    keyboard = [
        [{'text': '💰 Положить'}, {'text': '💸 Снять'}],
        [{'text': '✏️ Редактировать'}, {'text': '❌ Удалить'}],
        [{'text': ' Мос Копилка'}, {'text': '🏠 Главная'}]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        f' Мос Копилка: {piggy_name}\n'
        f'Цель: {target} руб.\n'
        f'Накоплено: {current} руб. ({percentage}%)\n\n'
        f'Выберите действие:',
        reply_markup=reply_markup
    )
    
    # Save current piggy bank name in state
    user_states = load_user_states()
    user_states[user_id] = f'CURRENT_PIGGY_{piggy_name}'
    save_user_states(user_states)

# Handle create piggy bank
def handle_create_piggy_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    
    user_states[user_id] = 'CREATING_PIGGY_NAME'
    save_user_states(user_states)
    
    update.message.reply_text(
        'Введите название для новой копилки:',
        reply_markup=ReplyKeyboardMarkup([
            [{'text': '🏠 Главная'}]
        ], resize_keyboard=True)
    )

# Handle piggy bank name input
def handle_piggy_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or user_states[user_id] != 'CREATING_PIGGY_NAME':
        return
    
    piggy_name = update.message.text
    
    # Save the name and ask for target amount
    user_states[user_id] = f'CREATING_PIGGY_TARGET_{piggy_name}'
    save_user_states(user_states)
    
    update.message.reply_text('Введите целевую сумму для копилки:')

# Handle piggy bank target input
def handle_piggy_target_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or not user_states[user_id].startswith('CREATING_PIGGY_TARGET_'):
        return
    
    try:
        target_amount = float(update.message.text)
        piggy_name = user_states[user_id].replace('CREATING_PIGGY_TARGET_', '')
        
        # Create piggy bank
        if user_id not in user_data:
            user_data[user_id] = {'piggy_banks': {}}
        if 'piggy_banks' not in user_data[user_id]:
            user_data[user_id]['piggy_banks'] = {}
            
        user_data[user_id]['piggy_banks'][piggy_name] = {
            'current': 0,
            'target': target_amount
        }
        save_user_data(user_data)
        
        del user_states[user_id]
        save_user_states(user_states)
        
        update.message.reply_text(
            f'✅ Копилка "{piggy_name}" создана!\nЦелевая сумма: {target_amount} руб.',
            reply_markup=ReplyKeyboardMarkup([
                [{'text': ' Мос Копилка'}],
                [{'text': '🏠 Главная'}]
            ], resize_keyboard=True)
        )
    except ValueError:
        update.message.reply_text('Пожалуйста, введите корректную сумму (число):')

# Handle deposit to piggy bank
def handle_deposit_to_piggy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    # Get current piggy bank from state
    if user_id not in user_states or not user_states[user_id].startswith('CURRENT_PIGGY_'):
        update.message.reply_text('Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
    
    if piggy_name not in user_data.get(user_id, {}).get('piggy_banks', {}):
        update.message.reply_text('Ошибка: копилка не найдена')
        return
    
    user_states[user_id] = f'DEPOSITING_{piggy_name}'
    save_user_states(user_states)
    
    update.message.reply_text(
        f'Введите сумму для пополнения копилки "{piggy_name}":',
        reply_markup=ReplyKeyboardMarkup([
            [{'text': '🏠 Главная'}]
        ], resize_keyboard=True)
    )

# Handle withdraw from piggy bank
def handle_withdraw_from_piggy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    # Get current piggy bank from state
    if user_id not in user_states or not user_states[user_id].startswith('CURRENT_PIGGY_'):
        update.message.reply_text('Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
    
    if piggy_name not in user_data.get(user_id, {}).get('piggy_banks', {}):
        update.message.reply_text('Ошибка: копилка не найдена')
        return
    
    user_states[user_id] = f'WITHDRAWING_{piggy_name}'
    save_user_states(user_states)
    
    update.message.reply_text(
        f'Введите сумму для снятия из копилки "{piggy_name}":',
        reply_markup=ReplyKeyboardMarkup([
            [{'text': '🏠 Главная'}]
        ], resize_keyboard=True)
    )

# Handle deposit/withdraw amount input
def handle_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or not user_states[user_id].startswith(('DEPOSITING_', 'WITHDRAWING_')):
        return
    
    try:
        amount = float(update.message.text)
        
        if user_states[user_id].startswith('DEPOSITING_'):
            # Deposit money
            piggy_name = user_states[user_id].replace('DEPOSITING_', '')
            if piggy_name in user_data[user_id]['piggy_banks']:
                user_data[user_id]['piggy_banks'][piggy_name]['current'] += amount
                save_user_data(user_data)
                
                # Show updated piggy bank
                handle_piggy_bank_actions(update, context, piggy_name)
                return
        else:
            # Withdraw money
            piggy_name = user_states[user_id].replace('WITHDRAWING_', '')
            if piggy_name in user_data[user_id]['piggy_banks']:
                user_data[user_id]['piggy_banks'][piggy_name]['current'] -= amount
                if user_data[user_id]['piggy_banks'][piggy_name]['current'] < 0:
                    user_data[user_id]['piggy_banks'][piggy_name]['current'] = 0
                save_user_data(user_data)
                
                # Show updated piggy bank
                handle_piggy_bank_actions(update, context, piggy_name)
                return
        
        del user_states[user_id]
        save_user_states(user_states)
        
    except ValueError:
        update.message.reply_text('Пожалуйста, введите корректную сумму (число):')

# Handle edit piggy bank
def handle_edit_piggy_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    # Get current piggy bank from state
    if user_id not in user_states or not user_states[user_id].startswith('CURRENT_PIGGY_'):
        update.message.reply_text('Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
    
    if piggy_name not in user_data.get(user_id, {}).get('piggy_banks', {}):
        update.message.reply_text('Ошибка: копилка не найдена')
        return
    
    keyboard = [
        [{'text': '✏️ Изменить название'}, {'text': '✏️ Изменить сумму'}],
        [{'text': f' Мос {piggy_name}'}, {'text': '🏠 Главная'}]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        f'Редактирование копилки "{piggy_name}":\nВыберите что изменить:',
        reply_markup=reply_markup
    )

# Handle delete piggy bank
def handle_delete_piggy_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    # Get current piggy bank from state
    if user_id not in user_states or not user_states[user_id].startswith('CURRENT_PIGGY_'):
        update.message.reply_text('Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
    
    if piggy_name in user_data.get(user_id, {}).get('piggy_banks', {}):
        del user_data[user_id]['piggy_banks'][piggy_name]
        save_user_data(user_data)
        
        update.message.reply_text(
            f'✅ Копилка "{piggy_name}" удалена',
            reply_markup=ReplyKeyboardMarkup([
                [{'text': ' Мос Копилка'}],
                [{'text': '🏠 Главная'}]
            ], resize_keyboard=True)
        )
    else:
        update.message.reply_text('Ошибка: копилка не найдена')
    
    # Clear state
    if user_id in user_states:
        del user_states[user_id]
        save_user_states(user_states)

# Handle edit piggy bank name
def handle_edit_piggy_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    
    # Set state to wait for new name
    if user_id in user_states and user_states[user_id].startswith('CURRENT_PIGGY_'):
        piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
        user_states[user_id] = f'EDITING_PIGGY_NAME_{piggy_name}'
        save_user_states(user_states)
        
        update.message.reply_text(
            f'Введите новое название для копилки "{piggy_name}":',
            reply_markup=ReplyKeyboardMarkup([
                [{'text': '🏠 Главная'}]
            ], resize_keyboard=True)
        )

# Handle edit piggy bank target
def handle_edit_piggy_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    
    # Set state to wait for new target
    if user_id in user_states and user_states[user_id].startswith('CURRENT_PIGGY_'):
        piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
        user_states[user_id] = f'EDITING_PIGGY_TARGET_{piggy_name}'
        save_user_states(user_states)
        
        update.message.reply_text(
            f'Введите новую целевую сумму для копилки "{piggy_name}":',
            reply_markup=ReplyKeyboardMarkup([
                [{'text': '🏠 Главная'}]
            ], resize_keyboard=True)
        )

# Handle piggy bank name edit input
def handle_edit_piggy_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or not user_states[user_id].startswith('EDITING_PIGGY_NAME_'):
        return
    
    new_name = update.message.text
    old_name = user_states[user_id].replace('EDITING_PIGGY_NAME_', '')
    
    # Rename piggy bank
    if old_name in user_data.get(user_id, {}).get('piggy_banks', {}):
        # Save the piggy bank data
        piggy_data = user_data[user_id]['piggy_banks'][old_name]
        # Remove old entry
        del user_data[user_id]['piggy_banks'][old_name]
        # Add with new name
        user_data[user_id]['piggy_banks'][new_name] = piggy_data
        save_user_data(user_data)
        
        update.message.reply_text(
            f'✅ Название копилки изменено с "{old_name}" на "{new_name}"',
            reply_markup=ReplyKeyboardMarkup([
                [{'text': f' Мос {new_name}'}],
                [{'text': ' Мос Копилка'}, {'text': '🏠 Главная'}]
            ], resize_keyboard=True)
        )
    else:
        update.message.reply_text('Ошибка: копилка не найдена')
    
    # Clear state
    if user_id in user_states:
        del user_states[user_id]
        save_user_states(user_states)

# Handle piggy bank target edit input
def handle_edit_piggy_target_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or not user_states[user_id].startswith('EDITING_PIGGY_TARGET_'):
        return
    
    try:
        new_target = float(update.message.text)
        piggy_name = user_states[user_id].replace('EDITING_PIGGY_TARGET_', '')
        
        # Update target
        if piggy_name in user_data.get(user_id, {}).get('piggy_banks', {}):
            user_data[user_id]['piggy_banks'][piggy_name]['target'] = new_target
            save_user_data(user_data)
            
            # Show updated piggy bank
            handle_piggy_bank_actions(update, context, piggy_name)
        else:
            update.message.reply_text('Ошибка: копилка не найдена')
        
        # Clear state
        if user_id in user_states:
            del user_states[user_id]
            save_user_states(user_states)
            
    except ValueError:
        update.message.reply_text('Пожалуйста, введите корректную сумму (число):')

# Shopping list section
def handle_shopping_list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [{'text': '🍎 Продукты'}, {'text': '💊 Аптека'}],
        [{'text': '📦 Остальное'}, {'text': '🏠 Главная'}]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text('🛒 Список покупок:\nВыберите категорию:', reply_markup=reply_markup)

# Handle shopping category
def handle_shopping_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    # Get items for this category
    items = user_data.get(user_id, {}).get('shopping_list', {}).get(category, [])
    
    # Create keyboard with items and action buttons
    keyboard = []
    
    # Add items
    for item in items:
        keyboard.append([{'text': f'❌ {item}'}])
    
    # Add action buttons
    keyboard.append([{'text': '➕ Добавить'}, {'text': '🗑 Очистить'}])
    keyboard.append([{'text': '🛒 Список покупок'}, {'text': '🏠 Главная'}])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if items:
        items_text = '\n'.join([f'• {item}' for item in items])
        message = f'{category}:\n{items_text}'
    else:
        message = f'{category}:\nСписок пуст'
    
    update.message.reply_text(
        f'{message}\n\nВыберите действие:',
        reply_markup=reply_markup
    )
    
    # Save state for adding items
    user_states = load_user_states()
    user_states[user_id] = f'ADDING_ITEM_{category}'
    save_user_states(user_states)

# Handle adding shopping item
def handle_add_shopping_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or not user_states[user_id].startswith('ADDING_ITEM_'):
        return
    
    category = user_states[user_id].replace('ADDING_ITEM_', '')
    item_text = update.message.text
    
    # Add item to category
    if user_id not in user_data:
        user_data[user_id] = {'shopping_list': {'Продукты': [], 'Аптека': [], 'Остальное': []}}
    if 'shopping_list' not in user_data[user_id]:
        user_data[user_id]['shopping_list'] = {'Продукты': [], 'Аптека': [], 'Остальное': []}
    if category not in user_data[user_id]['shopping_list']:
        user_data[user_id]['shopping_list'][category] = []
        
    user_data[user_id]['shopping_list'][category].append(item_text)
    save_user_data(user_data)
    
    # Show updated category
    handle_shopping_category(update, context, category)

# Handle deleting shopping item
def handle_delete_shopping_item(update: Update, context: ContextTypes.DEFAULT_TYPE, item_text: str) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    # Get category from state
    if user_id not in user_states or not user_states[user_id].startswith('ADDING_ITEM_'):
        return
    
    category = user_states[user_id].replace('ADDING_ITEM_', '')
    
    # Remove item from category
    if category in user_data.get(user_id, {}).get('shopping_list', {}):
        if item_text in user_data[user_id]['shopping_list'][category]:
            user_data[user_id]['shopping_list'][category].remove(item_text)
            save_user_data(user_data)
    
    # Show updated category
    handle_shopping_category(update, context, category)

# Handle clearing shopping category
def handle_clear_shopping_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    # Get category from state
    if user_id not in user_states or not user_states[user_id].startswith('ADDING_ITEM_'):
        return
    
    category = user_states[user_id].replace('ADDING_ITEM_', '')
    
    # Clear category
    if category in user_data.get(user_id, {}).get('shopping_list', {}):
        user_data[user_id]['shopping_list'][category] = []
        save_user_data(user_data)
    
    # Show updated category
    handle_shopping_category(update, context, category)

# Main function
def main() -> None:
    # Set console window title
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("Финансовый Telegram Бот")
    except:
        pass  # Ignore if not on Windows
    
    logger.info("Starting bot...")
    
    # Check if TELEGRAM_BOT_TOKEN is set
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        print("ОШИБКА: Не установлен TELEGRAM_BOT_TOKEN!")
        print("Пожалуйста, проверьте файл .env и убедитесь, что токен бота указан правильно.")
        return
    
    if TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error("Default TELEGRAM_BOT_TOKEN detected!")
        print("ОШИБКА: Обнаружен токен по умолчанию!")
        print("Пожалуйста, измените TELEGRAM_BOT_TOKEN в файле .env на реальный токен бота.")
        return
    
    try:
        # Create the Application and pass it your bot's token.
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
        
        logger.info("Bot started successfully!")
        print("Бот успешно запущен! Для остановки нажмите Ctrl+C")
        
        # Start the Bot
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"ОШИБКА: Не удалось запустить бота: {e}")
        print("Проверьте:")
        print("1. Правильность токена бота в файле .env")
        print("2. Подключение к интернету")
        print("3. Доступность Telegram API")
        return

if __name__ == '__main__':
    main()
