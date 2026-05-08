import asyncio
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ТОКЕН БОТА (замените на свой)
TOKEN = "8098904643:AAEMCop_ZfEof8C34vhSIPNVrfZtaQRgJ0Q"

# КАНАЛ ДЛЯ ПРОВЕРКИ ПОДПИСКИ
CHANNEL_USERNAME = "@dadnakormit_23"

# Словарь для хранения ID пользователей, которые уже крутили (в реальном боте нужно сохранять в файл/БД)
spun_users = set()

# Призы
PRIZES = [
    "🥐 Круассан классический",
    "🍵 Чай",
    "☕ Кофе",
    "🥐 Слойка сладкая на выбор",
    "🥨 Слойка солёная на выбор",
    "🧃 Лимонад в ассортименте"
]

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Проверяет, подписан ли пользователь на канал"""
    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return chat_member.status in ['member', 'creator', 'administrator']
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Проверяем подписку
    is_subscribed = await check_subscription(user_id, context)
    
    if not is_subscribed:
        keyboard = [[InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/dadnakormit_23")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Привет, {user_name}! 👋\n\n"
            f"Чтобы участвовать в розыгрыше, нужно подписаться на наш канал:\n"
            f"👉 @dadnakormit_23\n\n"
            f"После подписки нажмите /start снова",
            reply_markup=reply_markup
        )
        return
    
    # Проверяем, крутил ли уже пользователь
    if user_id in spun_users:
        await update.message.reply_text(
            "❌ Вы уже крутили колесо фортуны!\n"
            "Приходите в нашу пекарню за своим призом 🥐"
        )
        return
    
    # Показываем колесо фортуны
    keyboard = [[InlineKeyboardButton("🎡 Крутить колесо!", callback_data="spin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{user_name}, готов испытать удачу? 🎲\n\n"
        f"Крути колесо и выигрывай один из призов:\n"
        f"• Круассан классический\n"
        f"• Чай\n"
        f"• Кофе\n"
        f"• Слойка сладкая\n"
        f"• Слойка солёная\n"
        f"• Лимонад\n\n"
        f"Нажми на кнопку ниже 👇",
        reply_markup=reply_markup
    )

async def spin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия на кнопку кручения"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Ещё раз проверяем подписку (на случай, если отписался)
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        await query.edit_message_text(
            "❌ Вы отписались от канала!\n"
            "Подпишитесь снова и нажмите /start"
        )
        return
    
    # Проверяем, не крутил ли уже
    if user_id in spun_users:
        await query.edit_message_text(
            "❌ Вы уже крутили колесо фортуны!\n"
            "Приходите в пекарню за своим призом!"
        )
        return
    
    # Добавляем пользователя в список крутивших
    spun_users.add(user_id)
    
    # Выбираем случайный приз
    prize = random.choice(PRIZES)
    
    # Сохраняем результат (в реальном боте нужно сохранять в файл)
    with open("winners.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | ID: {user_id} | {user_name} | Приз: {prize}\n")
    
    # Отправляем результат
    message = (
        f"🎉 ПОЗДРАВЛЯЮ! 🎉\n\n"
        f"Вы выиграли:\n"
        f"🏆 {prize} 🏆\n\n"
        f"📍 Как получить приз:\n"
        f"Приходите в нашу пекарню с этим сообщением!\n\n"
        f"🥐 Батя накормит\n"
        f"г. Краснодар, ул. Командорская ул., 1/3\n\n"
        f"Покажите это сообщение нашему баристе и заберите свой приз! ☕"
    )
    
    await query.edit_message_text(message)

async def check_prize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки выигрыша по ID"""
    await update.message.reply_text(
        "Для получения приза просто покажите наше сообщение с выигрышем в пекарне!"
    )

def main():
    # Создаём приложение
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(spin_callback, pattern="spin"))
    app.add_handler(CommandHandler("check", check_prize))
    
    print("Бот запущен! 🚀")
    
    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
