# 🚂 Развертывание на Railway (инструкция)

## Вариант 1: Через GitHub (рекомендуется)

### 1. Создайте репозиторий на GitHub
1. Зайдите на https://github.com/new
2. Название: `platon-telegram-bot`
3. НЕ ставьте галочку "Initialize this repository"
4. Нажмите "Create repository"

### 2. Отправьте код на GitHub
Вставьте эти команды в терминал:

```bash
git remote add origin https://github.com/ВАШ_USERNAME/platon-telegram-bot.git
git push -u origin main
```

### 3. Подключите к Railway
1. Зайдите на https://railway.app
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub"
4. Выберите ваш репозиторий `platon-telegram-bot`
5. Railway автоматически начнет развертывание

### 4. Добавьте переменную окружения
1. В проекте Railway откройте вкладку "Variables"
2. Нажмите "New Variable"
3. Name: `TELEGRAM_BOT_TOKEN`
4. Value: `8391405901:AAHw7IdJxuY-7V5DPZxwwrxpm7DeMmR7Yrs`
5. Сохраните

## Вариант 2: Прямое развертывание (без GitHub)

1. Зайдите на https://railway.app
2. Нажмите "New Project" → "Empty Project"
3. Добавьте сервис → "GitHub Repo" → выберите репозиторий
4. В разделе "Settings" → "Variables" добавьте:
   - `TELEGRAM_BOT_TOKEN` = `8391405901:AAHw7IdJxuY-7V5DPZxwwrxpm7DeMmR7Yrs`

## После развертывания

1. **Остановите локальный бот** (закройте терминал или нажмите Ctrl+C)
2. Найдите бота в Telegram
3. Отправьте `/start`
4. Бот теперь работает 24/7 на Railway! 🎉
