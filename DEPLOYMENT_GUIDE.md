# 🚀 Руководство по развертыванию бота на сервере

## Вариант 1: Heroku (рекомендуется - бесплатно)

### Шаг 1: Подготовка
1. Создайте аккаунт на [Heroku](https://heroku.com)
2. Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Установите [Git](https://git-scm.com/)

### Шаг 2: Настройка проекта
1. Откройте терминал в папке с проектом
2. Инициализируйте Git репозиторий:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

### Шаг 3: Создание приложения на Heroku
1. Войдите в Heroku:
   ```bash
   heroku login
   ```

2. Создайте приложение:
   ```bash
   heroku create ваш-бот-платон
   ```

3. Установите переменные окружения:
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=8391405901:AAHw7IdJxuY-7V5DPZxwwrxpm7DeMmR7Yrs
   ```

4. Разверните приложение:
   ```bash
   git push heroku main
   ```

5. Запустите воркер:
   ```bash
   heroku ps:scale worker=1
   ```

### Шаг 4: Проверка
- Бот должен работать 24/7
- Проверьте логи: `heroku logs --tail`

---

## Вариант 2: Railway (альтернатива)

### Шаг 1: Подготовка
1. Создайте аккаунт на [Railway](https://railway.app)
2. Подключите GitHub репозиторий

### Шаг 2: Настройка
1. Создайте новый проект
2. Подключите ваш репозиторий
3. Добавьте переменную окружения:
   - `TELEGRAM_BOT_TOKEN` = `8391405901:AAHw7IdJxuY-7V5DPZxwwrxpm7DeMmR7Yrs`

### Шаг 3: Развертывание
1. Railway автоматически развернет приложение
2. Бот будет работать постоянно

---

## Вариант 3: Render (простой)

### Шаг 1: Подготовка
1. Создайте аккаунт на [Render](https://render.com)
2. Подключите GitHub

### Шаг 2: Создание сервиса
1. Выберите "New Web Service"
2. Подключите репозиторий
3. Настройки:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python telegram_bot.py`
   - Environment Variables: `TELEGRAM_BOT_TOKEN=8391405901:AAHw7IdJxuY-7V5DPZxwwrxpm7DeMmR7Yrs`

---

## 🔧 Локальная разработка

Для тестирования на своем компьютере:

1. Создайте файл `.env`:
   ```
   TELEGRAM_BOT_TOKEN=8391405901:AAHw7IdJxuY-7V5DPZxwwrxpm7DeMmR7Yrs
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Запустите бота:
   ```bash
   python telegram_bot.py
   ```

---

## 📋 Структура файлов для развертывания

```
ваш-проект/
├── telegram_bot.py      # Основной файл бота
├── platon_processor.py  # Обработчик данных
├── requirements.txt     # Зависимости Python
├── Procfile            # Конфигурация для Heroku
├── runtime.txt         # Версия Python
└── .env                # Переменные окружения (локально)
```

---

## ⚠️ Важные замечания

1. **Безопасность**: Никогда не публикуйте токен бота в открытом коде
2. **Логи**: Регулярно проверяйте логи на наличие ошибок
3. **Обновления**: Для обновления бота просто загрузите новый код
4. **Мониторинг**: Настройте уведомления о сбоях

---

## 🆘 Решение проблем

### Бот не отвечает
- Проверьте логи: `heroku logs --tail`
- Убедитесь, что воркер запущен: `heroku ps:scale worker=1`

### Ошибки при развертывании
- Проверьте, что все файлы добавлены в Git
- Убедитесь, что токен бота установлен правильно

### Проблемы с зависимостями
- Проверьте файл `requirements.txt`
- Убедитесь, что версии совместимы
