import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Тестовая функция для проверки inline-кнопок
async def test_inline_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Создаем inline-клавиатуру
    keyboard = [
        [InlineKeyboardButton("Тестовая кнопка 1", callback_data='test1')],
        [InlineKeyboardButton("Тестовая кнопка 2", callback_data='test2')],
        [InlineKeyboardButton("Главная", callback_data='main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text('Тестовое меню:', reply_markup=reply_markup)

# Обработчик callback-запросов
async def test_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'test1':
        await query.edit_message_text(text="Вы нажали на кнопку 1")
    elif query.data == 'test2':
        await query.edit_message_text(text="Вы нажали на кнопку 2")
    elif query.data == 'main':
        await test_inline_menu(update, context)

def main():
    # Здесь должен быть ваш токен бота
    # application = Application.builder().token("YOUR_BOT_TOKEN").build()
    
    print("Тестовый файл для проверки inline-меню создан успешно!")
    print("Для тестирования inline-меню в основном боте, запустите bot.py")

if __name__ == '__main__':
    main()