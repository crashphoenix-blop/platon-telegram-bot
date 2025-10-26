#!/bin/bash

echo "🚀 Развертывание Telegram бота на Heroku"
echo "========================================"

# Проверяем, что мы в правильной директории
if [ ! -f "telegram_bot.py" ]; then
    echo "❌ Ошибка: файл telegram_bot.py не найден"
    echo "Запустите скрипт из папки с проектом"
    exit 1
fi

# Проверяем, установлен ли Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI не установлен"
    echo "Установите с https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Проверяем, установлен ли Git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен"
    echo "Установите с https://git-scm.com/"
    exit 1
fi

echo "✅ Проверки пройдены"

# Инициализируем Git если нужно
if [ ! -d ".git" ]; then
    echo "📁 Инициализируем Git репозиторий..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Проверяем, авторизованы ли в Heroku
echo "🔐 Проверяем авторизацию в Heroku..."
if ! heroku auth:whoami &> /dev/null; then
    echo "Войдите в Heroku:"
    heroku login
fi

# Создаем приложение Heroku
echo "🏗️ Создаем приложение Heroku..."
APP_NAME="platon-bot-$(date +%s)"
heroku create $APP_NAME

# Устанавливаем переменные окружения
echo "⚙️ Настраиваем переменные окружения..."
heroku config:set TELEGRAM_BOT_TOKEN=8391405901:AAHw7IdJxuY-7V5DPZxwwrxpm7DeMmR7Yrs

# Развертываем приложение
echo "🚀 Развертываем приложение..."
git push heroku main

# Запускаем воркер
echo "👷 Запускаем воркер..."
heroku ps:scale worker=1

echo ""
echo "✅ Развертывание завершено!"
echo "🌐 URL приложения: https://$APP_NAME.herokuapp.com"
echo "📊 Проверить статус: heroku ps -a $APP_NAME"
echo "📋 Посмотреть логи: heroku logs --tail -a $APP_NAME"
echo ""
echo "🤖 Ваш бот теперь работает 24/7!"
echo "Найдите его в Telegram и отправьте /start"
