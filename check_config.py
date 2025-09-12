#!/usr/bin/env python3
"""
Script to check bot configuration and diagnose issues
"""

import os
import sys
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

def diagnose_issues():
    """Diagnose common issues with the bot"""
    print("\nДиагностика проблем...")
    print("=" * 40)
    
    # Check dependencies
    try:
        import telegram
        print("✅ python-telegram-bot установлен")
    except ImportError:
        print("❌ python-telegram-bot не установлен")
        print("   Установите его командой: pip install python-telegram-bot")
        return False
    
    # Check config
    try:
        from config import TELEGRAM_BOT_TOKEN
        if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
            print("❌ TELEGRAM_BOT_TOKEN не установлен в config.py")
            return False
        else:
            print("✅ TELEGRAM_BOT_TOKEN доступен в config.py")
    except Exception as e:
        print(f"❌ Ошибка при импорте config.py: {e}")
        return False
    
    # Check if bot is running
    try:
        import psutil
        bot_running = False
        bot_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'bot.py' in ' '.join(proc.info['cmdline']):
                    bot_processes.append(proc.info)
                    bot_running = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if bot_running:
            print("✅ Бот запущен")
            for proc in bot_processes:
                print(f"   - PID: {proc['pid']}")
        else:
            print("⚠️  Бот не запущен")
    except ImportError:
        print("⚠️  psutil не установлен, невозможно проверить запущенные процессы")
    
    print("\nДиагностика завершена!")
    return True

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--diagnose':
        diagnose_issues()
    else:
        check_config()

if __name__ == "__main__":
    main()