#!/usr/bin/env python3
"""
Simple test script to verify bot functionality
"""

import os
import sys
import time
from config import TELEGRAM_BOT_TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with inline buttons when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("Тестовая кнопка 1", callback_data="test1")],
        [InlineKeyboardButton("Тестовая кнопка 2", callback_data="test2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Тест бота - проверка работы inline кнопок:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "test1":
        await query.edit_message_text(text="Вы нажали кнопку 1")
    elif query.data == "test2":
        await query.edit_message_text(text="Вы нажали кнопку 2")

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
"""
Simple test script to check if bot can start properly
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import telegram
        print("✅ python-telegram-bot imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-telegram-bot: {e}")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-dotenv: {e}")
        return False
    
    try:
        import cryptography
        print("✅ cryptography imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import cryptography: {e}")
        return False
    
    return True

def test_config():
    """Test if config can be loaded"""
    try:
        from config import TELEGRAM_BOT_TOKEN
        print("✅ Config imported successfully")
        
        if TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != "your_telegram_bot_token_here":
            print("✅ Telegram bot token is set")
            return True
        else:
            print("❌ Telegram bot token is not set or is default value")
            return False
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False

def test_security():
    """Test if security module works"""
    try:
        from security import encrypt_data, decrypt_data
        print("✅ Security module imported successfully")
        
        # Test encryption/decryption
        test_data = "test_api_key"
        encrypted = encrypt_data(test_data)
        decrypted = decrypt_data(encrypted)
        
        if decrypted == test_data:
            print("✅ Encryption/decryption working correctly")
            return True
        else:
            print("❌ Encryption/decryption not working correctly")
            return False
    except Exception as e:
        print(f"❌ Failed to test security module: {e}")
        return False

if __name__ == "__main__":
    print("Testing bot components...")
    print("=" * 40)
    
    all_passed = True
    
    all_passed &= test_imports()
    print()
    
    all_passed &= test_config()
    print()
    
    all_passed &= test_security()
    print()
    
    if all_passed:
        print("🎉 All tests passed! Bot should work correctly.")
    else:
        print("❌ Some tests failed. Please check the issues above.")