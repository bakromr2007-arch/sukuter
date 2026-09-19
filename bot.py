import os
import sys
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
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
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')  # Render URL + /webhook

print('=' * 60)
print('BOT ISHGA TUSHMOQDA (WEBHOOK MODE)...')
print('=' * 60)
print(f'BOT_TOKEN: {"✓ Mavjud" if BOT_TOKEN else "✗ YOQ"}')
print(f'ADMIN_IDS: {ADMIN_IDS}')
print(f'WEBHOOK_URL: {WEBHOOK_URL if WEBHOOK_URL else "POLLING MODE"}')
print('=' * 60)

if not BOT_TOKEN:
    print('\n❌ BOT_TOKEN topilmadi!')
    sys.exit(1)

def is_admin(user_id):
    user_id_str = str(user_id)
    return user_id_str in [a.strip() for a in ADMIN_IDS if a.strip()]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    try:
        user = update.effective_user
        user_id = user.id
        name = user.first_name

        print(f'[START] User: {user_id} ({name})')
        logger.info(f'Start from: {user_id}')

        keyboard = [
            [KeyboardButton('📊 Statistika')],
            [KeyboardButton('🛴 Skuterlar'), KeyboardButton('👥 Mijozlar')],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        if is_admin(user_id):
            text = (
                f'🎉 Assalomu alaykum, {name}!\n\n'
                f'Admin panel\n'
                f'Bot ishlayapti ✅\n\n'
                f'ID: {user_id}'
            )
        else:
            text = (
                f'👋 Salom, {name}!\n\n'
                f'Bot ishlayapti ✅\n'
                f'ID: {user_id}'
            )

        await update.message.reply_text(text, reply_markup=reply_markup)
        print(f'[START] Response sent to {user_id}')

    except Exception as e:
        print(f'[START] Error: {e}')
        logger.error(f'Start error: {e}', exc_info=True)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ping"""
    print(f'[PING] From: {update.effective_user.id}')
    await update.message.reply_text('🏓 Pong! Bot ishlayapti ✅')

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ID"""
    user_id = update.effective_user.id
    await update.message.reply_text(f'ID: {user_id}')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help"""
    await update.message.reply_text(
        '📖 Buyruqlar:\n\n'
        '/start - Boshlash\n'
        '/ping - Test\n'
        '/id - ID olish\n'
        '/help - Yordam'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Text handler"""
    try:
        text = update.message.text
        user_id = update.effective_user.id

        print(f'[TEXT] {user_id}: {text}')

        if text == '📊 Statistika':
            await update.message.reply_text('📊 Bot ishlayapti!')
        elif text == '🛴 Skuterlar':
            await update.message.reply_text('🛴 Skuterlar bolimi')
        elif text == '👥 Mijozlar':
            await update.message.reply_text('👥 Mijozlar bolimi')
        else:
            await update.message.reply_text('Qabul qilindi ✓')

    except Exception as e:
        print(f'[TEXT] Error: {e}')
        logger.error(f'Text error: {e}')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Error handler"""
    print(f'[ERROR] {context.error}')
    logger.error(f'Error: {context.error}', exc_info=context.error)

async def post_init(application: Application):
    """Post init - webhook setup"""
    if WEBHOOK_URL:
        await application.bot.delete_webhook()
        await application.bot.set_webhook(url=WEBHOOK_URL)
        print(f'\n✅ WEBHOOK SOZLANDI: {WEBHOOK_URL}\n')
    else:
        await application.bot.delete_webhook()
        print('\n✅ POLLING MODE\n')

def main():
    """Main"""
    try:
        print('\n[INIT] Application yaratilmoqda...')

        # Application
        app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

        # Handlers
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('ping', ping))
        app.add_handler(CommandHandler('id', get_id))
        app.add_handler(CommandHandler('help', help_cmd))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_error_handler(error_handler)

        print('[INIT] Handlers qoshildi')

        # Run
        if WEBHOOK_URL:
            # Webhook mode
            print(f'[RUN] WEBHOOK mode: {WEBHOOK_URL}')
            port = int(os.getenv('PORT', 8443))
            app.run_webhook(
                listen='0.0.0.0',
                port=port,
                url_path='webhook',
                webhook_url=WEBHOOK_URL
            )
        else:
            # Polling mode
            print('[RUN] POLLING mode')
            app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )

    except Exception as e:
        print(f'\n❌ XATO: {e}\n')
        logger.error(f'Main error: {e}', exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
