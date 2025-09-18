#!/usr/bin/env python3
"""
Test script to verify bot startup and configuration
"""

import os
import sys
import traceback
from config import TELEGRAM_BOT_TOKEN

def test_bot_startup():
    """Test bot startup and configuration"""
    print("Тестирование запуска бота...")
    print("=" * 40)
    
    # Test 1: Check if .env file exists
    print("Тест 1: Проверка наличия файла .env")
    if os.path.exists('.env'):
        print("✅ Файл .env найден")
    else:
        print("❌ Файл .env не найден")
        return False
    
    # Test 2: Check if TELEGRAM_BOT_TOKEN is set
    print("\nТест 2: Проверка наличия токена бота")
    if TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != "your_telegram_bot_token_here" and TELEGRAM_BOT_TOKEN != "YOUR_ACTUAL_TELEGRAM_BOT_TOKEN_HERE":
        print("✅ TELEGRAM_BOT_TOKEN установлен")
        print(f"   Длина токена: {len(TELEGRAM_BOT_TOKEN)} символов")
    else:
        print("⚠️  TELEGRAM_BOT_TOKEN не установлен или установлен неправильно")
        print("   Пожалуйста, укажите действительный токен в файле .env")
        # We won't return False here to allow testing other components
    
    # Test 3: Try to import required modules
    print("\nТест 3: Проверка импорта необходимых модулей")
    try:
        import telegram
        print("✅ python-telegram-bot установлен")
    except ImportError as e:
        print(f"❌ Ошибка импорта python-telegram-bot: {e}")
        return False
    
    try:
        from telegram.ext import Application
        print("✅ telegram.ext.Application доступен")
    except ImportError as e:
        print(f"❌ Ошибка импорта telegram.ext.Application: {e}")
        return False
    
    # Test 4: Try to import bot modules
    print("\nТест 4: Проверка импорта модулей бота")
    try:
        from bot import start, handle_callback_query, handle_menu
        print("✅ Модули бота импортируются успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта модулей бота: {e}")
        traceback.print_exc()
        return False
    
    # Test 5: Check data files
    print("\nТест 5: Проверка файлов данных")
    try:
        from config import USER_DATA_FILE, USER_STATES_FILE
        print(f"   Файл данных пользователей: {USER_DATA_FILE}")
        print(f"   Файл состояний пользователей: {USER_STATES_FILE}")
        
        # Check if files can be created/written
        test_data = {"test": "data"}
        import json
        
        # Test user data file
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        if loaded_data == test_data:
            print("✅ Файл данных пользователей работает корректно")
        else:
            print("❌ Ошибка работы с файлом данных пользователей")
            return False
            
        # Test user states file
        with open(USER_STATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        with open(USER_STATES_FILE, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        if loaded_data == test_data:
            print("✅ Файл состояний пользователей работает корректно")
        else:
            print("❌ Ошибка работы с файлом состояний пользователей")
            return False
            
        # Clean up test files
        os.remove(USER_DATA_FILE)
        os.remove(USER_STATES_FILE)
    except Exception as e:
        print(f"❌ Ошибка работы с файлами данных: {e}")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 40)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != "your_telegram_bot_token_here" and TELEGRAM_BOT_TOKEN != "YOUR_ACTUAL_TELEGRAM_BOT_TOKEN_HERE":
        print("✅ Все тесты пройдены успешно!")
        print("Бот готов к запуску.")
    else:
        print("⚠️  Основные компоненты бота работают корректно.")
        print("   Для полного запуска укажите действительный токен в файле .env")
    return True

if __name__ == "__main__":
    success = test_bot_startup()
    if not success:
        sys.exit(1)