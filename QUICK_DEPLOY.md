# ⚡ Быстрое развертывание бота (5 минут)

## 🎯 Самый простой способ - Heroku

### 1. Подготовка (2 минуты)
```bash
# Установите Heroku CLI
# Windows: https://devcenter.heroku.com/articles/heroku-cli
# Mac: brew install heroku/brew/heroku
# Linux: https://devcenter.heroku.com/articles/heroku-cli

# Войдите в Heroku
heroku login
```

### 2. Автоматическое развертывание (1 минута)
```bash
# Запустите скрипт развертывания
./deploy.sh
```

### 3. Готово! (0 минут)
- Бот работает 24/7
- Найдите его в Telegram
- Отправьте `/start`

---

## 🔧 Ручное развертывание

Если скрипт не работает:

```bash
# 1. Инициализируйте Git
git init
git add .
git commit -m "Initial commit"

# 2. Создайте приложение
heroku create ваш-бот-платон

# 3. Установите токен
heroku config:set TELEGRAM_BOT_TOKEN=8391405901:AAHw7IdJxuY-7V5DPZxwwrxpm7DeMmR7Yrs

# 4. Разверните
git push heroku main

# 5. Запустите воркер
heroku ps:scale worker=1
```

---

## 📱 Проверка работы

1. Найдите бота в Telegram по username
2. Отправьте `/start`
3. Загрузите CSV файл
4. Используйте `/process`

---

## 🆘 Если что-то не работает

```bash
# Посмотреть логи
heroku logs --tail

# Проверить статус
heroku ps

# Перезапустить
heroku restart
```

---

## 💡 Альтернативы

- **Railway**: railway.app (еще проще)
- **Render**: render.com (бесплатно)
- **VPS**: DigitalOcean, Vultr (от $5/мес)
