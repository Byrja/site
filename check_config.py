#!/usr/bin/env python3
"""
Script to check bot configuration
"""

import os
from config import TELEGRAM_BOT_TOKEN
from dotenv import load_dotenv

def check_config():
    print("Проверка конфигурации бота...")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("   Создайте файл .env на основе .env.example")
        return False
    
    # Check TELEGRAM_BOT_TOKEN
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token or token == 'your_telegram_bot_token_here':
        print("❌ TELEGRAM_BOT_TOKEN не установлен или установлен неправильно!")
        print("   Откройте файл .env и укажите правильный токен бота")
        return False
    else:
        print("✅ TELEGRAM_BOT_TOKEN установлен")
    
    # Check if token looks valid
    if len(token) < 30:
        print("⚠️  Токен бота кажется слишком коротким. Убедитесь, что он правильный.")
    
    print("\nПроверка завершена!")
    return True

if __name__ == "__main__":
    check_config()