#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот для обработки данных системы "Платон"
"""

import os
import logging
import tempfile
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from platon_processor import PlatonProcessor
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PlatonTelegramBot:
    """Telegram бот для обработки данных системы Платон"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.processor = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("process", self.process_command))
        self.application.add_handler(CommandHandler("summary", self.summary_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("files", self.files_command))
        
        # Обработка файлов
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        
        # Обработка callback запросов
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = """
🤖 *Добро пожаловать в бот для обработки данных системы Платон!*

Этот бот поможет вам:
• Загружать CSV файлы с данными системы Платон
• Автоматически обрабатывать данные
• Создавать Excel отчеты
• Получать сводную информацию

📋 *Доступные команды:*
/help - Справка по командам
/files - Показать загруженные файлы
/process - Обработать загруженные файлы
/summary - Показать сводку по данным
/clear - Очистить все данные

📁 *Как использовать:*
1. Загрузите CSV файл с данными системы Платон
2. Используйте команду /process для обработки
3. Получите Excel отчет и сводку

Начните с загрузки CSV файла!
        """
        
        keyboard = [
            [InlineKeyboardButton("📁 Загруженные файлы", callback_data="files")],
            [InlineKeyboardButton("📊 Обработать данные", callback_data="process")],
            [InlineKeyboardButton("📋 Показать сводку", callback_data="summary")],
            [InlineKeyboardButton("🧹 Очистить данные", callback_data="clear")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📚 *Справка по командам бота*

🔹 */start* - Главное меню и приветствие
🔹 */help* - Эта справка
🔹 */files* - Показать список загруженных файлов
🔹 */process* - Обработать загруженные CSV файлы
🔹 */summary* - Показать сводку по обработанным данным
🔹 */clear* - Очистить все загруженные данные

📁 *Работа с файлами:*
• Просто отправьте CSV файл боту
• Файл должен содержать данные системы Платон
• После загрузки используйте /process для обработки

📊 *Что делает бот:*
• Анализирует данные по транспортным средствам
• Считает расходы по дорогам и датам
• Создает Excel отчет с несколькими листами
• Показывает сводную статистику

❓ *Проблемы?*
Если что-то не работает, попробуйте:
1. Перезапустить бота командой /start
2. Проверить формат CSV файла
3. Убедиться, что файл содержит данные системы Платон
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /clear"""
        try:
            # Очищаем загруженные файлы
            if 'csv_files' in context.user_data:
                for file_path in context.user_data['csv_files']:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                context.user_data['csv_files'] = []
            
            # Очищаем список имен файлов
            if 'file_names' in context.user_data:
                context.user_data['file_names'] = []
            
            # Очищаем процессор
            if 'processor' in context.user_data:
                del context.user_data['processor']
            
            await update.message.reply_text(
                "🧹 Все данные очищены!\n\n"
                "Теперь вы можете загрузить новые CSV файлы."
            )
            
        except Exception as e:
            logger.error(f"Ошибка при очистке данных: {e}")
            await update.message.reply_text("❌ Ошибка при очистке данных")
    
    async def files_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /files - показывает список загруженных файлов"""
        if 'file_names' not in context.user_data or not context.user_data['file_names']:
            await update.message.reply_text(
                "📁 Нет загруженных файлов.\n\n"
                "Отправьте CSV файл с данными системы Платон."
            )
            return
        
        files_list = "📁 *Загруженные файлы:*\n\n"
        for i, filename in enumerate(context.user_data['file_names'], 1):
            files_list += f"{i}. `{filename}`\n"
        
        files_list += f"\n📊 Всего файлов: {len(context.user_data['file_names'])}\n"
        files_list += "🔄 Используйте /process для обработки данных"
        
        await update.message.reply_text(files_list, parse_mode='Markdown')
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик загрузки документов"""
        document = update.message.document
        
        # Проверяем, что это CSV файл
        if not document.file_name.lower().endswith('.csv'):
            await update.message.reply_text(
                "❌ Пожалуйста, загрузите CSV файл с данными системы Платон"
            )
            return
        
        try:
            # Инициализируем список файлов если его нет
            if 'csv_files' not in context.user_data:
                context.user_data['csv_files'] = []
                context.user_data['file_names'] = []
            
            # Проверяем на дублирование имен файлов
            if document.file_name in context.user_data['file_names']:
                warning_msg = (
                    f"⚠️ *Внимание! Обнаружено два файла с одинаковым названием:*\n"
                    f"`{document.file_name}`\n\n"
                    f"Возможно наложение данных! Рекомендуется использовать уникальные имена файлов."
                )
                await update.message.reply_text(warning_msg, parse_mode='Markdown')
            
            # Скачиваем файл
            file = await context.bot.get_file(document.file_id)
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as temp_file:
                await file.download_to_drive(temp_file.name)
                temp_file_path = temp_file.name
            
            # Добавляем файл в список (не заменяем, а добавляем)
            context.user_data['csv_files'].append(temp_file_path)
            context.user_data['file_names'].append(document.file_name)
            
            # Очищаем предыдущий процессор при загрузке нового файла
            if 'processor' in context.user_data:
                del context.user_data['processor']
            
            await update.message.reply_text(
                f"✅ Файл *{document.file_name}* успешно загружен!\n\n"
                f"📁 Загружено файлов: {len(context.user_data['csv_files'])}\n"
                f"🔄 Используйте /process для обработки данных",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке файла: {e}")
            await update.message.reply_text(
                "❌ Ошибка при загрузке файла. Попробуйте еще раз."
            )
    
    async def process_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /process"""
        if 'csv_files' not in context.user_data or not context.user_data['csv_files']:
            await update.message.reply_text(
                "❌ Сначала загрузите CSV файлы!\n\n"
                "Отправьте CSV файл с данными системы Платон, а затем используйте /process"
            )
            return
        
        try:
            # Показываем, что началась обработка
            processing_msg = await update.message.reply_text("🔄 Обрабатываю данные... Пожалуйста, подождите.")
            
            # Создаем процессор
            processor = PlatonProcessor()
            
            # Обрабатываем каждый файл
            for csv_file in context.user_data['csv_files']:
                if os.path.exists(csv_file):
                    processor.read_csv_file(csv_file)
            
            if not processor.data:
                await processing_msg.edit_text("❌ Не удалось загрузить данные из файлов")
                return
            
            # Обрабатываем данные
            processor.process_data()
            
            # Создаем Excel отчет
            output_file = f"отчет_платон_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            if processor.create_excel_report(output_file):
                # Отправляем Excel файл
                with open(output_file, 'rb') as file:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=file,
                        filename=output_file,
                        caption="📊 Excel отчет готов!"
                    )
                
                # Удаляем временный файл
                os.remove(output_file)
                
                # Сохраняем процессор в контексте для команды summary
                context.user_data['processor'] = processor
                
                # Очищаем загруженные файлы после создания отчета
                for csv_file in context.user_data['csv_files']:
                    if os.path.exists(csv_file):
                        os.remove(csv_file)
                context.user_data['csv_files'] = []
                context.user_data['file_names'] = []
                
                await processing_msg.edit_text(
                    "✅ Обработка завершена! Excel отчет отправлен.\n\n"
                    "📁 Загруженные файлы очищены. Можете загрузить новые файлы.\n"
                    "Используйте /summary для просмотра сводки данных."
                )
            else:
                await processing_msg.edit_text("❌ Ошибка при создании Excel отчета")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке данных: {e}")
            await update.message.reply_text(f"❌ Ошибка при обработке: {str(e)}")
    
    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /summary"""
        if 'processor' not in context.user_data:
            await update.message.reply_text(
                "❌ Сначала обработайте данные командой /process"
            )
            return
        
        try:
            processor = context.user_data['processor']
            summary = processor.summary
            
            summary_text = f"""
📊 *Сводка по обработанным данным*

📈 *Общая статистика:*
• Записей: {summary['total_records']:,}
• Общая сумма: {summary['total_amount']:,.2f} руб.
• Общее расстояние: {summary['total_distance']:,.2f} км
• Транспортных средств: {len(summary['vehicles'])}
• Дорог: {len(summary['roads'])}

🚛 *Топ-5 транспортных средств по расходам:*
"""
            
            # Сортируем ТС по расходам
            vehicle_costs = []
            for vehicle, records in summary['by_vehicle'].items():
                total_amount = sum(processor._parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
                vehicle_costs.append((vehicle, total_amount))
            
            vehicle_costs.sort(key=lambda x: x[1], reverse=True)
            
            for i, (vehicle, amount) in enumerate(vehicle_costs[:5], 1):
                summary_text += f"{i}. {vehicle}: {amount:,.2f} руб.\n"
            
            summary_text += f"\n🛣️ *Топ-5 дорог по расходам:*\n"
            
            # Сортируем дороги по расходам
            road_costs = []
            for road, records in summary['by_road'].items():
                total_amount = sum(processor._parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
                road_costs.append((road, total_amount))
            
            road_costs.sort(key=lambda x: x[1], reverse=True)
            
            for i, (road, amount) in enumerate(road_costs[:5], 1):
                summary_text += f"{i}. {road[:50]}{'...' if len(road) > 50 else ''}: {amount:,.2f} руб.\n"
            
            await update.message.reply_text(summary_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Ошибка при создании сводки: {e}")
            await update.message.reply_text(f"❌ Ошибка при создании сводки: {str(e)}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "files":
            await self.files_command(update, context)
        elif query.data == "process":
            await self.process_command(update, context)
        elif query.data == "summary":
            await self.summary_command(update, context)
        elif query.data == "clear":
            await self.clear_command(update, context)
        elif query.data == "help":
            await self.help_command(update, context)
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск Telegram бота...")
        self.application.run_polling()

def main():
    """Основная функция"""
    # Получаем токен из переменных окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Ошибка: не найден токен бота!")
        print("Создайте файл .env и добавьте в него:")
        print("TELEGRAM_BOT_TOKEN=ваш_токен_бота")
        return 1
    
    # Создаем и запускаем бота
    bot = PlatonTelegramBot(token)
    bot.run()

if __name__ == "__main__":
    main()
