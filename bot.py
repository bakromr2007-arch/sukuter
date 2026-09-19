import os
import sys
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')

print('=' * 50)
print('BOT ISHGA TUSHMOQDA...')
print('=' * 50)
print(f'BOT_TOKEN: {"✓ Mavjud" if BOT_TOKEN else "✗ YOQ"}')
print(f'ADMIN_IDS: {ADMIN_IDS}')
print(f'WEB_APP_URL: {WEB_APP_URL}')
print('=' * 50)

if not BOT_TOKEN:
    print('\n❌ XATO: BOT_TOKEN topilmadi!')
    print('Environment Variables ni tekshiring!')
    sys.exit(1)

def is_admin(user_id):
    """Admin tekshirish"""
    user_id_str = str(user_id)
    admin_list = [a.strip() for a in ADMIN_IDS if a.strip()]
    return user_id_str in admin_list

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    try:
        user = update.effective_user
        user_id = user.id
        name = user.first_name

        logger.info(f'Start command from: {user_id} ({name})')

        # Admin klaviaturasi
        keyboard = [
            [KeyboardButton('📊 Statistika')],
            [KeyboardButton('🛴 Skuterlar'), KeyboardButton('👥 Mijozlar')],
            [KeyboardButton('💰 Tolovlar')]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        if is_admin(user_id):
            message = (
                f'🎉 Assalomu alaykum, {name}!\n\n'
                f'Siz admin sifatida kirgansiz.\n'
                f'Bot ishlayapti va tayyor! ✅\n\n'
                f'Telegram ID: {user_id}'
            )
        else:
            message = (
                f'👋 Assalomu alaykum, {name}!\n\n'
                f'Bot ishlayapti! ✅\n\n'
                f'Telegram ID: {user_id}\n'
                f'Administrator bilan boglaning.'
            )

        await update.message.reply_text(message, reply_markup=reply_markup)
        logger.info(f'Start response sent to {user_id}')

    except Exception as e:
        logger.error(f'Start command error: {e}', exc_info=True)
        await update.message.reply_text('Xatolik yuz berdi. Qaytadan urinib koring.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = (
        '📖 Yordam:\n\n'
        '/start - Botni ishga tushirish\n'
        '/help - Yordam\n'
        '/ping - Bot holatini tekshirish\n'
        '/id - Telegram ID ni olish\n\n'
        'Bot ishlayapti! ✅'
    )
    await update.message.reply_text(help_text)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ping command"""
    await update.message.reply_text('🏓 Pong! Bot ishlayapti ✅')
    logger.info(f'Ping from {update.effective_user.id}')

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user ID"""
    user_id = update.effective_user.id
    await update.message.reply_text(f'Sizning Telegram ID: `{user_id}`', parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    try:
        text = update.message.text
        user_id = update.effective_user.id

        logger.info(f'Text message from {user_id}: {text}')

        if text == '📊 Statistika':
            await update.message.reply_text(
                '📊 Statistika:\n\n'
                'Bot ishlayapti va tayyor!\n'
                'Barcha funksiyalar normal.'
            )
        elif text == '🛴 Skuterlar':
            await update.message.reply_text('Skuterlar bo\'limi.')
        elif text == '👥 Mijozlar':
            await update.message.reply_text('Mijozlar bo\'limi.')
        elif text == '💰 Tolovlar':
            await update.message.reply_text('Tolovlar bo\'limi.')
        else:
            await update.message.reply_text('Xabar qabul qilindi ✓')

    except Exception as e:
        logger.error(f'Text handler error: {e}', exc_info=True)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Error handler"""
    logger.error(f'Exception: {context.error}', exc_info=context.error)

def main():
    """Main function"""
    try:
        # Application yaratish
        app = Application.builder().token(BOT_TOKEN).build()

        # Handlers
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('help', help_command))
        app.add_handler(CommandHandler('ping', ping))
        app.add_handler(CommandHandler('id', get_id))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

        # Error handler
        app.add_error_handler(error_handler)

        # Bot ishga tushirish
        print('\n✅ BOT MUVAFFAQIYATLI ISHGA TUSHDI!')
        print('Polling boshlandi...\n')

        # Run polling
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

    except Exception as e:
        logger.error(f'Bot ishga tushmadi: {e}', exc_info=True)
        print(f'\n❌ XATO: {e}\n')
        sys.exit(1)

if __name__ == '__main__':
    main()
