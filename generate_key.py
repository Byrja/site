#!/usr/bin/env python3
"""
Script to generate a secure encryption key for production use
"""

from security import generate_secure_key

if __name__ == "__main__":
    print("Генерация безопасного ключа шифрования...")
    key = generate_secure_key()
    print(f"Сгенерированный ключ: {key}")
    print("\nДобавьте эту строку в ваш .env файл:")
    print(f"ENCRYPTION_KEY={key}")
    print("\nВАЖНО: Сохраните этот ключ в безопасном месте!")
    print("Если вы его потеряете, все зашифрованные данные станут недоступны.")