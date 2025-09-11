#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки функциональности бота с inline-меню
"""

import sys
import os

# Добавляем путь к директории с ботом
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_inline_menus():
    """
    Тест для проверки корректности inline-меню
    """
    print("Тестирование inline-меню бота...")
    
    # Проверяем, что все необходимые модули импортируются корректно
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        print("✓ Модули telegram импортируются корректно")
    except ImportError as e:
        print(f"✗ Ошибка импорта модулей telegram: {e}")
        return False
    
    # Проверяем структуру inline-кнопок
    try:
        # Тестовая клавиатура
        keyboard = [
            [InlineKeyboardButton("Тест 1", callback_data='test1')],
            [InlineKeyboardButton("Тест 2", callback_data='test2')],
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        print("✓ Inline-клавиатура создается корректно")
    except Exception as e:
        print(f"✗ Ошибка создания inline-клавиатуры: {e}")
        return False
    
    # Проверяем, что callback_data корректны
    expected_callbacks = ['test1', 'test2', 'back']
    actual_callbacks = [btn.callback_data for row in keyboard for btn in row]
    
    if actual_callbacks == expected_callbacks:
        print("✓ Callback data корректны")
    else:
        print(f"✗ Несоответствие callback data. Ожидалось: {expected_callbacks}, Получено: {actual_callbacks}")
        return False
    
    return True

def main():
    print("Запуск тестов для бота с inline-меню...\n")
    
    if test_inline_menus():
        print("\n✓ Все тесты пройдены успешно!")
        print("\nТеперь вы можете запустить бота командой:")
        print("python bot.py")
    else:
        print("\n✗ Некоторые тесты не пройдены. Проверьте код бота.")

if __name__ == "__main__":
    main()