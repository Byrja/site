import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import json
import os

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
DATA_FILE = "user_data.json"
USER_STATES_FILE = "user_states.json"

# Load or create user data
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Ensure notes structure exists for existing users
            for user_id in data:
                if 'notes' not in data[user_id]:
                    data[user_id]['notes'] = {}
            return data
    else:
        return {}

# Save user data
def save_user_data(data):
    # Ensure notes structure exists before saving
    for user_id in data:
        if 'notes' not in data[user_id]:
            data[user_id]['notes'] = {}
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Load or create user states
def load_user_states():
    if os.path.exists(USER_STATES_FILE):
        with open(USER_STATES_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

# Save user states
def save_user_states(states):
    with open(USER_STATES_FILE, 'w') as f:
        json.dump(states, f, indent=2)

# Main menu
def main_menu():
    keyboard = [
        [InlineKeyboardButton(' Мос Копилка', callback_data='piggy_bank_menu')],
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu')],
        [InlineKeyboardButton('📝 Заметки', callback_data='notes_menu')]
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
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    # Delete user's message for privacy
    # if update.message:
    #     delete_message(context, update.effective_chat.id, update.message.message_id)
    
    # Initialize user data if not exists
    if user_id not in user_data:
        user_data[user_id] = {
            'piggy_banks': {},
            'shopping_list': {
                'Продукты': [],
                'Аптека': [],
                'Остальное': []
            },
            'notes': {}
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
        
        # Ensure notes structure exists
        if 'notes' not in user_data[user_id]:
            user_data[user_id]['notes'] = {}
            
        save_user_data(user_data)
    
    if user_id in user_states:
        del user_states[user_id]
        save_user_states(user_states)
    
    # Create a comprehensive menu with all functionality
    keyboard = [
        [InlineKeyboardButton(' Мос Копилка', callback_data='piggy_bank_menu')],
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu')],
        [InlineKeyboardButton('📝 Заметки', callback_data='notes_menu')],
        [InlineKeyboardButton('⚙️ Настройки', callback_data='settings_menu'), InlineKeyboardButton('ℹ️ Помощь', callback_data='help_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        'Добро пожаловать в финансовый бот! 🤖\n\n'
        'Здесь вы можете управлять своими финансами, '
        'копилками, списками покупок и заметками.\n\n'
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
        [InlineKeyboardButton(' Мос Копилка', callback_data='piggy_bank_menu')],
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu')],
        [InlineKeyboardButton('📝 Заметки', callback_data='notes_menu')],
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
        [InlineKeyboardButton(' Мос Копилка', callback_data='piggy_bank_menu')],
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu')],
        [InlineKeyboardButton('📝 Заметки', callback_data='notes_menu')],
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
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    # Delete user's message for privacy
    # delete_message(context, update.effective_chat.id, update.message.message_id)
    
    # Handle different states
    if user_id in user_states:
        state = user_states[user_id]
        
        # Handle piggy bank creation
        if state == 'CREATING_PIGGY_NAME':
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
        # Handle note creation
        elif state == 'CREATING_NOTE_TITLE':
            await handle_note_title_input(update, context)
            return
        elif state.startswith('CREATING_NOTE_CONTENT_'):
            await handle_note_content_input(update, context)
            return
        # Handle note editing
        elif state.startswith('EDITING_NOTE_'):
            await handle_note_edit_input(update, context)
            return
    
    # Clear user state if not in a specific flow
    if user_id in user_states:
        should_clear_state = True
        # Don't clear state for specific flows
        if not text.startswith(('➕ Создать копилку', '✏️ Редактировать', '💰 Положить', '💸 Снять', '➕ Создать заметку', '✏️ Редактировать')):
            if text not in ['➕ Добавить']:
                del user_states[user_id]
                save_user_states(user_states)
    
    # Handle menu selections
    if text in [' Мос Копилка', ' Мос Копилка', ' Мос Копилка']:  # Handle variations
        await handle_piggy_bank_menu(update, context)
    elif text == '🛒 Список покупок':
        await handle_shopping_list_menu(update, context)
    elif text == '📝 Заметки':
        await handle_notes_menu(update, context)
    elif text == '🏠 Главная':
        await start(update, context)  # Make this async call
    elif text.startswith(' Мос '):
        # Handle piggy bank selection
        piggy_name = text[2:].strip()
        await handle_piggy_bank_actions(update, context, piggy_name)
    elif text in ['🍎 Продукты', 'Аптека', '📦 Остальное']:
        await handle_shopping_category(update, context, text)  # Keep emoji for proper matching
    elif text == '➕ Создать копилку':
        await handle_create_piggy_bank(update, context)
    elif text == '➕ Добавить':
        # This will be handled by state
        pass
    elif text.startswith('❌ ') and len(text) > 2:
        # Handle item deletion from shopping list
        item_to_delete = text[2:]  # Remove emoji
        await handle_delete_shopping_item(update, context, item_to_delete)
    elif text == '🗑 Очистить':
        await handle_clear_shopping_category(update, context)
    elif text.startswith('💰 Положить'):
        # Extract piggy bank name from state or message
        await handle_deposit_to_piggy(update, context)
    elif text.startswith('💸 Снять'):
        await handle_withdraw_from_piggy(update, context)
    elif text == '✏️ Редактировать':
        await handle_edit_piggy_bank(update, context)
    elif text == '❌ Удалить':
        await handle_delete_piggy_bank(update, context)
    elif text.startswith('✏️ Изменить название'):
        await handle_edit_piggy_name(update, context)
    elif text.startswith('✏️ Изменить сумму'):
        await handle_edit_piggy_target(update, context)
    elif text in [' mos Копилка', ' Мос Копилка', ' Мос Копилка']:  # Handle all variations
        await handle_piggy_bank_menu(update, context)
    elif text == ' mos Список покупок' or text == '🛒 Список покупок':  # Handle both variations
        await handle_shopping_list_menu(update, context)
    elif text == '⚙️ Настройки':  # Explicitly handle settings button
        await handle_settings_menu(update, context)
    elif text == 'ℹ️ Помощь':
        await handle_help_menu(update, context)
    else:
        # For any other text, show main menu
        await show_main_menu(update, context)

# Handle settings menu
async def handle_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    keyboard = [
        [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f'⚙️ Настройки бота:\n\n'
        f'Выберите действие:',
        reply_markup=reply_markup
    )

# Handle settings menu callback
async def handle_settings_menu_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(query.from_user.id)
    user_data = load_user_data()
    
    keyboard = [
        [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f'⚙️ Настройки бота:\n\n'
        f'Выберите действие:',
        reply_markup=reply_markup
    )

# Handle help menu
async def handle_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    keyboard = [
        [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    help_text = (
        'ℹ️ Помощь по боту:\n\n'
        ' Мос Копилка - создание и управление финансовыми копилками\n'
        '🛒 Список покупок - ведение списков покупок по категориям\n'
        '⚙️ Настройки - настройка параметров\n\n'
    )
    
    await update.message.reply_text(
        help_text,
        reply_markup=reply_markup
    )

# Handle help menu callback
async def handle_help_menu_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    help_text = (
        'ℹ️ Помощь по боту:\n\n'
        ' Мос Копилка - создание и управление финансовыми копилками\n'
        '🛒 Список покупок - ведение списков покупок по категориям\n'
        '⚙️ Настройки - настройка параметров\n\n'
    )
    
    await query.edit_message_text(
        help_text,
        reply_markup=reply_markup
    )

# Piggy bank section
async def handle_piggy_bank_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    keyboard = [
        [InlineKeyboardButton('➕ Создать копилку', callback_data='create_piggy_bank')]
    ]
    
    # Add existing piggy banks
    if user_id in user_data and user_data[user_id]['piggy_banks']:
        for name in user_data[user_id]['piggy_banks']:
            keyboard.append([InlineKeyboardButton(f'💰 {name}', callback_data=f'piggy_bank_{name}')])
    
    keyboard.append([InlineKeyboardButton('🏠 Главная', callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if not user_data.get(user_id, {}).get('piggy_banks'):
        await update.message.reply_text(' Мос Копилка:\nУ вас пока нет копилок. Создайте первую копилку!', reply_markup=reply_markup)
    else:
        await update.message.reply_text(' Мос Копилка:', reply_markup=reply_markup)

# Piggy bank section callback
async def handle_piggy_bank_menu_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(query.from_user.id)
    user_data = load_user_data()
    
    keyboard = [
        [InlineKeyboardButton('➕ Создать копилку', callback_data='create_piggy_bank')]
    ]
    
    # Add existing piggy banks
    if user_id in user_data and user_data[user_id]['piggy_banks']:
        for name in user_data[user_id]['piggy_banks']:
            keyboard.append([InlineKeyboardButton(f'💰 {name}', callback_data=f'piggy_bank_{name}')])
    
    keyboard.append([InlineKeyboardButton('🏠 Главная', callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if not user_data.get(user_id, {}).get('piggy_banks'):
        await query.edit_message_text(' Мос Копилка:\nУ вас пока нет копилок. Создайте первую копилку!', reply_markup=reply_markup)
    else:
        await query.edit_message_text(' Мос Копилка:', reply_markup=reply_markup)

# Handle piggy bank actions
async def handle_piggy_bank_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, piggy_name: str) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data or piggy_name not in user_data[user_id]['piggy_banks']:
        await update.message.reply_text('Копилка не найдена', reply_markup=main_menu())
        return
    
    piggy = user_data[user_id]['piggy_banks'][piggy_name]
    current = piggy['current']
    target = piggy['target']
    percentage = round((current / target) * 100, 1) if target > 0 else 0
    
    keyboard = [
        [InlineKeyboardButton('💰 Положить', callback_data=f'deposit_{piggy_name}'), InlineKeyboardButton('💸 Снять', callback_data=f'withdraw_{piggy_name}')],
        [InlineKeyboardButton('✏️ Редактировать', callback_data=f'edit_{piggy_name}'), InlineKeyboardButton('❌ Удалить', callback_data=f'delete_{piggy_name}')],
        [InlineKeyboardButton(' Bakanы', callback_data='piggy_bank_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]  # Use consistent text
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f'💰 Копилка: {piggy_name}\n'
        f'Цель: {target} руб.\n'
        f'Накоплено: {current} руб. ({percentage}%)\n\n'
        f'Выберите действие:',
        reply_markup=reply_markup
    )
    
    # Save current piggy bank name in state
    user_states = load_user_states()
    user_states[user_id] = f'CURRENT_PIGGY_{piggy_name}'
    save_user_states(user_states)

# Handle piggy bank actions callback
async def handle_piggy_bank_actions_callback(query, context: ContextTypes.DEFAULT_TYPE, piggy_name: str) -> None:
    user_id = str(query.from_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data or piggy_name not in user_data[user_id]['piggy_banks']:
        await query.edit_message_text('Копилка не найдена', reply_markup=main_menu())
        return
    
    piggy = user_data[user_id]['piggy_banks'][piggy_name]
    current = piggy['current']
    target = piggy['target']
    percentage = round((current / target) * 100, 1) if target > 0 else 0
    
    keyboard = [
        [InlineKeyboardButton('💰 Положить', callback_data=f'deposit_{piggy_name}'), InlineKeyboardButton('💸 Снять', callback_data=f'withdraw_{piggy_name}')],
        [InlineKeyboardButton('✏️ Редактировать', callback_data=f'edit_{piggy_name}'), InlineKeyboardButton('❌ Удалить', callback_data=f'delete_{piggy_name}')],
        [InlineKeyboardButton(' Bakanы', callback_data='piggy_bank_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]  # Use consistent text
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f'💰 Копилка: {piggy_name}\n'
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
async def handle_create_piggy_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    
    user_states[user_id] = 'CREATING_PIGGY_NAME'
    save_user_states(user_states)
    
    await update.message.reply_text(
        'Введите название для новой копилки:',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
        ])
    )

# Handle create piggy bank callback
async def handle_create_piggy_bank_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(query.from_user.id)
    user_states = load_user_states()
    
    user_states[user_id] = 'CREATING_PIGGY_NAME'
    save_user_states(user_states)
    
    await query.edit_message_text(
        '📝 Пожалуйста, введите название для новой копилки:\n\nНапример: "Отпуск", "Новый телефон", "Ремонт"',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
        ])
    )

# Handle piggy bank name input
async def handle_piggy_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or user_states[user_id] != 'CREATING_PIGGY_NAME':
        return
    
    piggy_name = update.message.text
    
    # Save the name and ask for target amount
    user_states[user_id] = f'CREATING_PIGGY_TARGET_{piggy_name}'
    save_user_states(user_states)
    
    await update.message.reply_text('💰 Теперь введите целевую сумму для копилки (в рублях):\n\nНапример: 10000')

# Handle piggy bank target input
async def handle_piggy_target_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
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
        
        keyboard = [
            [InlineKeyboardButton(' Bakanы', callback_data='piggy_bank_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f'✅ Копилка "{piggy_name}" успешно создана!\nЦелевая сумма: {target_amount} руб.\n\nТеперь вы можете пополнять эту копилку или создать еще одну.',
            reply_markup=reply_markup
        )
    except ValueError:
        await update.message.reply_text('⚠️ Пожалуйста, введите корректную сумму (число):')

# Handle shopping list menu
async def handle_shopping_list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton('🍎 Продукты', callback_data='category_Продукты'), InlineKeyboardButton('Аптека', callback_data='category_Аптека'), InlineKeyboardButton('📦 Остальное', callback_data='category_Остальное')],
        [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text('🛒 Список покупок:\nВыберите категорию:', reply_markup=reply_markup)

# Handle shopping list menu callback
async def handle_shopping_list_menu_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton('🍎 Продукты', callback_data='category_Продукты'), InlineKeyboardButton('Аптека', callback_data='category_Аптека'), InlineKeyboardButton('📦 Остальное', callback_data='category_Остальное')],
        [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text('🛒 Список покупок:', reply_markup=reply_markup)

# Handle shopping category
async def handle_shopping_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    # Get items for this category (remove emoji if present)
    clean_category = category[2:] if category.startswith(('🍎', 'Аптека', '📦')) else category
    items = user_data.get(user_id, {}).get('shopping_list', {}).get(clean_category, [])
    
    # Create keyboard with items and action buttons
    keyboard = []
    
    # Add items
    for item in items:
        keyboard.append([InlineKeyboardButton(f'❌ {item}', callback_data=f'delete_item_{clean_category}_{item}')])
    
    # Add action buttons
    keyboard.append([InlineKeyboardButton('➕ Добавить', callback_data=f'add_item_{clean_category}'), InlineKeyboardButton('🗑 Очистить', callback_data=f'clear_category_{clean_category}')])
    keyboard.append([InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')])  # Use consistent text
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if items:
        items_text = '\n'.join([f'• {item}' for item in items])
        message = f'{clean_category}:\n{items_text}'
    else:
        message = f'{clean_category}:\nСписок пуст. Добавьте первый элемент!'
    
    await update.message.reply_text(
        f'📋 {message}\n\nВыберите действие:',
        reply_markup=reply_markup
    )
    
    # Save state for adding items
    user_states = load_user_states()
    user_states[user_id] = f'ADDING_ITEM_{clean_category}'
    save_user_states(user_states)

# Handle shopping category callback
async def handle_shopping_category_callback(query, context: ContextTypes.DEFAULT_TYPE, category: str) -> None:
    user_id = str(query.from_user.id)
    user_data = load_user_data()
    
    # Get items for this category (remove emoji if present)
    clean_category = category[2:] if category.startswith(('🍎', 'Аптека', '📦')) else category
    items = user_data.get(user_id, {}).get('shopping_list', {}).get(clean_category, [])
    
    # Create keyboard with items and action buttons
    keyboard = []
    
    # Add items
    for item in items:
        keyboard.append([InlineKeyboardButton(f'❌ {item}', callback_data=f'delete_item_{clean_category}_{item}')])
    
    # Add action buttons
    keyboard.append([InlineKeyboardButton('➕ Добавить', callback_data=f'add_item_{clean_category}'), InlineKeyboardButton('🗑 Очистить', callback_data=f'clear_category_{clean_category}')])
    keyboard.append([InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')])  # Use consistent text
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if items:
        items_text = '\n'.join([f'• {item}' for item in items])
        message = f'{clean_category}:\n{items_text}'
    else:
        message = f'{clean_category}:\nСписок пуст. Добавьте первый элемент!'
    
    await query.edit_message_text(
        f'📋 {message}\n\nВыберите действие:',
        reply_markup=reply_markup
    )
    
    # Save state for adding items
    user_states = load_user_states()
    user_states[user_id] = f'ADDING_ITEM_{clean_category}'
    save_user_states(user_states)

# Handle adding item to shopping list
async def handle_add_shopping_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or not user_states[user_id].startswith('ADDING_ITEM_'):
        return
    
    clean_category = user_states[user_id].replace('ADDING_ITEM_', '')
    item = update.message.text
    
    if user_id not in user_data:
        user_data[user_id] = {'shopping_list': {}}
    if 'shopping_list' not in user_data[user_id]:
        user_data[user_id]['shopping_list'] = {}
    if clean_category not in user_data[user_id]['shopping_list']:
        user_data[user_id]['shopping_list'][clean_category] = []
    
    user_data[user_id]['shopping_list'][clean_category].append(item)
    save_user_data(user_data)
    
    del user_states[user_id]
    save_user_states(user_states)
    
    # Send confirmation message
    keyboard = [
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f'✅ Товар "{item}" добавлен в категорию "{clean_category}"!\n\n'
        f'Вы можете добавить еще товары или перейти к другим категориям.',
        reply_markup=reply_markup
    )

# Handle delete shopping item
async def handle_delete_shopping_item(update: Update, context: ContextTypes.DEFAULT_TYPE, item_to_delete: str) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    for category, items in user_data.get(user_id, {}).get('shopping_list', {}).items():
        if item_to_delete in items:
            items.remove(item_to_delete)
            save_user_data(user_data)
            
            # Send confirmation message
            keyboard = [
                [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f'✅ Товар "{item_to_delete}" удален из категории "{category}"!\n\n'
                f'Вы можете продолжить работу со списком покупок.',
                reply_markup=reply_markup
            )
            return
    
    await update.message.reply_text('❌ Предмет не найден', reply_markup=main_menu())

# Handle clear shopping category
async def handle_clear_shopping_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or not user_states[user_id].startswith('ADDING_ITEM_'):
        return
    
    clean_category = user_states[user_id].replace('ADDING_ITEM_', '')
    user_data[user_id]['shopping_list'][clean_category] = []
    save_user_data(user_data)
    
    del user_states[user_id]
    save_user_states(user_states)
    
    # Send confirmation message
    keyboard = [
        [InlineKeyboardButton('🛒 Список покупок', callback_data='shopping_list_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f'✅ Категория "{clean_category}" очищена!\n\n'
        f'Вы можете добавить новые товары или перейти к другим категориям.',
        reply_markup=reply_markup
    )

# Handle deposit to piggy bank
async def handle_deposit_to_piggy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    # Get current piggy bank from state
    if user_id not in user_states or not user_states[user_id].startswith('CURRENT_PIGGY_'):
        await update.message.reply_text('❌ Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
    
    if piggy_name not in user_data.get(user_id, {}).get('piggy_banks', {}):
        await update.message.reply_text('❌ Ошибка: копилка не найдена')
        return
    
    user_states[user_id] = f'DEPOSITING_{piggy_name}'
    save_user_states(user_states)
    
    keyboard = [
        [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f'💰 Введите сумму для пополнения копилки "{piggy_name}":',
        reply_markup=reply_markup
    )

# Handle withdraw from piggy bank
async def handle_withdraw_from_piggy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    # Get current piggy bank from state
    if user_id not in user_states or not user_states[user_id].startswith('CURRENT_PIGGY_'):
        await update.message.reply_text('❌ Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
    
    if piggy_name not in user_data.get(user_id, {}).get('piggy_banks', {}):
        await update.message.reply_text('❌ Ошибка: копилка не найдена')
        return
    
    user_states[user_id] = f'WITHDRAWING_{piggy_name}'
    save_user_states(user_states)
    
    keyboard = [
        [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f'💸 Введите сумму для снятия из копилки "{piggy_name}":',
        reply_markup=reply_markup
    )

# Handle amount input
async def handle_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states:
        return
    
    try:
        amount = float(update.message.text)
        piggy_name = user_states[user_id].split('_')[1]
        
        if user_states[user_id].startswith('DEPOSITING_'):
            user_data[user_id]['piggy_banks'][piggy_name]['current'] += amount
        elif user_states[user_id].startswith('WITHDRAWING_'):
            user_data[user_id]['piggy_banks'][piggy_name]['current'] -= amount
        
        save_user_data(user_data)
        del user_states[user_id]
        save_user_states(user_states)
        
        await handle_piggy_bank_actions(update, context, piggy_name)
    except ValueError:
        await update.message.reply_text('⚠️ Пожалуйста, введите корректную сумму (число):')

# Handle edit piggy bank
async def handle_edit_piggy_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    if user_id not in user_states or not user_states[user_id].startswith('CURRENT_PIGGY_'):
        await update.message.reply_text('❌ Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
    
    if piggy_name not in user_data.get(user_id, {}).get('piggy_banks', {}):
        await update.message.reply_text('❌ Ошибка: копилка не найдена')
        return
    
    keyboard = [
        [InlineKeyboardButton('✏️ Изменить название', callback_data=f'edit_name_{piggy_name}'), InlineKeyboardButton('✏️ Изменить сумму', callback_data=f'edit_target_{piggy_name}')],
        [InlineKeyboardButton(' Bakanы', callback_data='piggy_bank_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f'Редактирование копилки "{piggy_name}"\n\nВыберите действие:',
        reply_markup=reply_markup
    )

# Handle edit piggy bank name
async def handle_edit_piggy_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    if user_id not in user_states or not user_states[user_id].startswith('CURRENT_PIGGY_'):
        await update.message.reply_text('❌ Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
    
    if piggy_name not in user_data.get(user_id, {}).get('piggy_banks', {}):
        await update.message.reply_text('❌ Ошибка: копилка не найдена')
        return
    
    user_states[user_id] = f'EDITING_PIGGY_NAME_{piggy_name}'
    save_user_states(user_states)
    
    await update.message.reply_text(
        f'📝 Введите новое название для копилки "{piggy_name}":',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
        ])
    )

# Handle edit piggy bank name input
async def handle_edit_piggy_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or not user_states[user_id].startswith('EDITING_PIGGY_NAME_'):
        return
    
    new_name = update.message.text
    old_name = user_states[user_id].replace('EDITING_PIGGY_NAME_', '')
    
    if user_id not in user_data or old_name not in user_data[user_id]['piggy_banks']:
        await update.message.reply_text('❌ Ошибка: копилка не найдена')
        return
    
    user_data[user_id]['piggy_banks'][new_name] = user_data[user_id]['piggy_banks'].pop(old_name)
    save_user_data(user_data)
    
    del user_states[user_id]
    save_user_states(user_states)
    
    await handle_piggy_bank_actions(update, context, new_name)

# Handle edit piggy bank target
async def handle_edit_piggy_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_states = load_user_states()
    user_data = load_user_data()
    
    if user_id not in user_states or not user_states[user_id].startswith('CURRENT_PIGGY_'):
        await update.message.reply_text('❌ Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_states[user_id].replace('CURRENT_PIGGY_', '')
    
    if piggy_name not in user_data.get(user_id, {}).get('piggy_banks', {}):
        await update.message.reply_text('❌ Ошибка: копилка не найдена')
        return
    
    user_states[user_id] = f'EDITING_PIGGY_TARGET_{piggy_name}'
    save_user_states(user_states)
    
    await update.message.reply_text(
        f'🎯 Введите новую целевую сумму для копилки "{piggy_name}":',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
        ])
    )

# Handle edit piggy bank target input
async def handle_edit_piggy_target_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user_states = load_user_states()
    
    if user_id not in user_states or not user_states[user_id].startswith('EDITING_PIGGY_TARGET_'):
        return
    
    try:
        new_target = float(update.message.text)
        piggy_name = user_states[user_id].replace('EDITING_PIGGY_TARGET_', '')
        
        if user_id not in user_data or piggy_name not in user_data[user_id]['piggy_banks']:
            await update.message.reply_text('❌ Ошибка: копилка не найдена')
            return
        
        user_data[user_id]['piggy_banks'][piggy_name]['target'] = new_target
        save_user_data(user_data)
        
        del user_states[user_id]
        save_user_states(user_states)
        
        await handle_piggy_bank_actions(update, context, piggy_name)
    except ValueError:
        await update.message.reply_text('⚠️ Пожалуйста, введите корректную сумму (число):')

# Handle delete piggy bank
async def handle_delete_piggy_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None:
        return
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        await update.message.reply_text('❌ Ошибка: не выбрана копилка')
        return
    
    piggy_name = user_data[user_id]['piggy_banks'].keys()
    
    if not piggy_name:
        await update.message.reply_text('❌ Ошибка: копилка не найдена')
        return
    
    del user_data[user_id]['piggy_banks']
    save_user_data(user_data)
    
    await update.message.reply_text('✅ Копилка удалена', reply_markup=main_menu())

# Handle callback queries for inline keyboards
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if update.effective_user is None:
            return
        user_id = str(update.effective_user.id)
        
        logger.info(f"User {user_id} clicked button with callback_data: {data}")
        
        # Handle different callback data
        if data == 'main_menu':
            await show_main_menu_callback(query, context)
        elif data == 'piggy_bank_menu':
            await handle_piggy_bank_menu_callback(query, context)
        elif data == 'shopping_list_menu':
            await handle_shopping_list_menu_callback(query, context)
        elif data == 'notes_menu':
            await handle_notes_menu_callback(query, context)
        elif data == 'settings_menu':
            await handle_settings_menu_callback(query, context)
        elif data == 'help_menu':
            await handle_help_menu_callback(query, context)
        elif data.startswith('piggy_bank_'):
            piggy_name = data.replace('piggy_bank_', '')
            await handle_piggy_bank_actions_callback(query, context, piggy_name)
        elif data.startswith('category_'):
            category = data.replace('category_', '')
            await handle_shopping_category_callback(query, context, category)
        elif data == 'create_piggy_bank':
            await handle_create_piggy_bank_callback(query, context)
        elif data.startswith('deposit_'):
            piggy_name = data.replace('deposit_', '')
            # Handle deposit logic
            user_states = load_user_states()
            user_states[user_id] = f'DEPOSITING_{piggy_name}'
            save_user_states(user_states)
                
            keyboard = [
                [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            await query.edit_message_text(
                f'💰 Введите сумму для пополнения копилки "{piggy_name}":',
                reply_markup=reply_markup
            )
        elif data.startswith('withdraw_'):
            piggy_name = data.replace('withdraw_', '')
            # Handle withdraw logic
            user_states = load_user_states()
            user_states[user_id] = f'WITHDRAWING_{piggy_name}'
            save_user_states(user_states)
                
            keyboard = [
                [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            await query.edit_message_text(
                f'💸 Введите сумму для снятия из копилки "{piggy_name}":',
                reply_markup=reply_markup
            )
        elif data.startswith('edit_name_'):
            piggy_name = data.replace('edit_name_', '')
            # Handle edit name logic
            user_states = load_user_states()
            user_states[user_id] = f'EDITING_PIGGY_NAME_{piggy_name}'
            save_user_states(user_states)
                
            keyboard = [
                [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            await query.edit_message_text(
                f'📝 Введите новое название для копилки "{piggy_name}":',
                reply_markup=reply_markup
            )
        elif data.startswith('edit_target_'):
            piggy_name = data.replace('edit_target_', '')
            # Handle edit target logic
            user_states = load_user_states()
            user_states[user_id] = f'EDITING_PIGGY_TARGET_{piggy_name}'
            save_user_states(user_states)
                
            keyboard = [
                [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            await query.edit_message_text(
                f'🎯 Введите новую целевую сумму для копилки "{piggy_name}":',
                reply_markup=reply_markup
            )
        elif data.startswith('edit_'):
            piggy_name = data.replace('edit_', '')
            # Handle edit logic
            user_states = load_user_states()
            user_states[user_id] = f'EDITING_PIGGY_NAME_{piggy_name}'
            save_user_states(user_states)
                
            keyboard = [
                [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            await query.edit_message_text(
                f'📝 Введите новое название для копилки "{piggy_name}":',
                reply_markup=reply_markup
            )
        elif data.startswith('delete_'):
            piggy_name = data.replace('delete_', '')
            # Handle delete logic
            user_data = load_user_data()
            if piggy_name in user_data.get(user_id, {}).get('piggy_banks', {}):
                del user_data[user_id]['piggy_banks'][piggy_name]
                save_user_data(user_data)
                    
                keyboard = [
                    [InlineKeyboardButton(' Bakanы', callback_data='piggy_bank_menu'), InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                    
                await query.edit_message_text(
                    f'✅ Копилка "{piggy_name}" успешно удалена',
                    reply_markup=reply_markup
                )
            else:
                await query.edit_message_text('❌ Ошибка: копилка не найдена')
        elif data.startswith('add_item_'):
            category = data.replace('add_item_', '')
            # Handle add item logic
            user_states = load_user_states()
            user_states[user_id] = f'ADDING_ITEM_{category}'
            save_user_states(user_states)
                
            keyboard = [
                [InlineKeyboardButton('🏠 Главная', callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            await query.edit_message_text(
                f'📝 Введите название товара для категории "{category}":\n\n'
                f'Например: "Молоко", "Хлеб", "Лекарства"',
                reply_markup=reply_markup
            )
        elif data.startswith('clear_category_'):
            category = data.replace('clear_category_', '')
            # Handle clear category logic
            user_data = load_user_data()
            if category in user_data.get(user_id, {}).get('shopping_list', {}):
                user_data[user_id]['shopping_list'][category] = []
                save_user_data(user_data)
                    
                # Show updated category
                await handle_shopping_category_callback(query, context, category)
        elif data.startswith('delete_item_'):
            # Handle delete item logic
            parts = data.split('_', 3)
            if len(parts) >= 4:
                category = parts[2]
                item_name = parts[3]
                # Remove item from category
                user_data = load_user_data()
                if category in user_data.get(user_id, {}).get('shopping_list', {}):
                    if item_name in user_data[user_id]['shopping_list'][category]:
                        user_data[user_id]['shopping_list'][category].remove(item_name)
                        save_user_data(user_data)
                            
                        # Show updated category
                        await handle_shopping_category_callback(query, context, category)
                    else:
                        await query.edit_message_text('❌ Ошибка: товар не найден')
                else:
                    await query.edit_message_text('❌ Ошибка: категория не найдена')
            else:
                await query.edit_message_text('❌ Ошибка: некорректные данные')
        elif data.startswith('note_'):
            note_id = data.replace('note_', '')
            await handle_note_actions_callback(query, context, note_id)
        elif data == 'create_note':
            await handle_create_note_callback(query, context)
        elif data.startswith('edit_note_'):
            note_id = data.replace('edit_note_', '')
            await handle_edit_note_callback(query, context, note_id)
        elif data.startswith('delete_note_'):
            note_id = data.replace('delete_note_', '')
            await handle_delete_note_callback(query, context, note_id)
        elif data.startswith('save_note_'):
            note_id = data.replace('save_note_', '')
            await handle_save_note_callback(query, context, note_id)
        else:
            logger.warning(f"Unknown callback_data: {data}")
            await query.edit_message_text("Неизвестная команда. Пожалуйста, попробуйте еще раз.")
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        try:
            await update.callback_query.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
        except:
            pass

def main():
    """Start the bot."""
    # Import config after cleaning up the file
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Telegram Bot Token - loaded from environment variables
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не установлен в .env файле!")
        return
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Run the bot until the user presses Ctrl-C
    logger.info("Starting bot...")
    application.run_polling()
    logger.info("Bot started successfully!")

if __name__ == "__main__":
    main()