#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска Telegram бота
"""

import os
import sys
from telegram_bot import main

if __name__ == "__main__":
    # Проверяем наличие файла .env
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("📋 Создайте файл .env в корне проекта и добавьте:")
        print("TELEGRAM_BOT_TOKEN=ваш_токен_бота")
        print("\n📖 Инструкция по получению токена:")
        print("1. Найдите @BotFather в Telegram")
        print("2. Отправьте команду /newbot")
        print("3. Следуйте инструкциям")
        print("4. Скопируйте токен в файл .env")
        sys.exit(1)
    
    # Запускаем бота
    sys.exit(main())
