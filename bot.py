import os
import logging
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')

# Database
DATABASE = 'rentals.db'

def init_database():
    """Database yaratish"""
    conn = sqlite3.connect(DATABASE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scooters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model TEXT,
            plate_number TEXT,
            status TEXT DEFAULT 'available',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT,
            phone TEXT,
            address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scooter_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            payment_type TEXT NOT NULL,
            weekly_price REAL,
            monthly_price REAL,
            deposit REAL DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date DATE NOT NULL,
            note TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info(f'Database yaratildi: {DATABASE}')

def is_admin(user_id: int) -> bool:
    """Admin tekshirish"""
    return str(user_id) in [admin.strip() for admin in ADMIN_IDS if admin.strip()]

def get_admin_keyboard(user_id: int):
    """Admin klaviaturasi"""
    keyboard = [
        [KeyboardButton('🌐 Admin Panel', web_app=WebAppInfo(url=f'{WEB_APP_URL}/admin-login'))],
        ['➕ Skuter qoshish', '📋 Skuterlar'],
        ['👤 Mijoz qoshish', '👥 Mijozlar'],
        ['📊 Statistika', '💰 Tolovlar']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_customer_keyboard(user_id: int):
    """Mijoz klaviaturasi"""
    keyboard = [
        [KeyboardButton('🌐 Mening kabinetim', web_app=WebAppInfo(url=f'{WEB_APP_URL}/customer/{user_id}'))],
        ['📱 Mening arendalarim', '💳 Tolovlarim']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start buyrugi"""
    user = update.effective_user
    user_id = user.id
    name = user.first_name

    logger.info(f'Start buyrugi: {user_id} - {name}')

    if is_admin(user_id):
        await update.message.reply_text(
            f'🎉 Assalomu alaykum, {name}!\n\n'
            f'Skuter arenda botiga xush kelibsiz.\n'
            f'Siz admin sifatida kirgansiz.\n\n'
            f'🌐 Web App tugmasini bosib admin panelga kiring!',
            reply_markup=get_admin_keyboard(user_id)
        )
    else:
        # Mijoz tekshirish
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        customer = cursor.execute(
            'SELECT * FROM customers WHERE telegram_id = ?',
            (user_id,)
        ).fetchone()
        conn.close()

        if customer:
            await update.message.reply_text(
                f'👋 Assalomu alaykum, {name}!\n\n'
                f'🌐 Web App tugmasini bosing va barcha malumotlaringizni koring:\n'
                f'• Arendalaringiz\n'
                f'• Tolovlar tarixi\n'
                f'• Qarzlaringiz',
                reply_markup=get_customer_keyboard(user_id)
            )
        else:
            await update.message.reply_text(
                f'👋 Assalomu alaykum, {name}!\n\n'
                f'Sizning malumotlaringiz hali tizimga kiritilmagan.\n'
                f'Administrator bilan boglaning.'
            )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam buyrugi"""
    await update.message.reply_text(
        '📖 Yordam\n\n'
        '/start - Botni ishga tushirish\n'
        '/help - Yordam\n'
        '/ping - Bot holatini tekshirish\n'
        '/id - Sizning Telegram ID\n\n'
        '🌐 Web App tugmasini bosib toliq funksiyalardan foydalaning!'
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ping buyrugi"""
    await update.message.reply_text('🏓 Pong! Bot ishlayapti ✅')

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ID buyrugi"""
    user_id = update.effective_user.id
    await update.message.reply_text(f'Sizning Telegram ID: {user_id}')

async def statistika(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistika"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text('Bu buyruq faqat adminlar uchun.')
        return

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        total_scooters = cursor.execute('SELECT COUNT(*) FROM scooters').fetchone()[0]
        active_rentals = cursor.execute('SELECT COUNT(*) FROM rentals WHERE status = "active"').fetchone()[0]
        total_customers = cursor.execute('SELECT COUNT(*) FROM customers').fetchone()[0]

        conn.close()

        await update.message.reply_text(
            f'📊 Statistika:\n\n'
            f'🛴 Skuterlar: {total_scooters}\n'
            f'📊 Aktiv arenda: {active_rentals}\n'
            f'👥 Mijozlar: {total_customers}',
            reply_markup=get_admin_keyboard(user_id)
        )
    except Exception as e:
        logger.error(f'Statistika xatosi: {e}')
        await update.message.reply_text('Xatolik yuz berdi.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha xabarlar"""
    text = update.message.text
    user_id = update.effective_user.id

    if text == '📊 Statistika':
        await statistika(update, context)
    elif text == '📋 Skuterlar' or text == '👥 Mijozlar':
        await update.message.reply_text(
            '🌐 Toliq malumot uchun Web App tugmasini bosing!',
            reply_markup=get_admin_keyboard(user_id) if is_admin(user_id) else get_customer_keyboard(user_id)
        )
    else:
        await update.message.reply_text('Xabar qabul qilindi ✓')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xatolarni tutish"""
    logger.error(f'Update {update} caused error {context.error}')

def main():
    """Botni ishga tushirish"""
    # Environment tekshirish
    print('=================================')
    print('Bot ishga tushmoqda...')
    print(f'BOT_TOKEN: {"Mavjud ✓" if BOT_TOKEN else "YOQ ✗"}')
    print(f'ADMIN_IDS: {ADMIN_IDS}')
    print(f'WEB_APP_URL: {WEB_APP_URL}')
    print('=================================')

    if not BOT_TOKEN:
        print('❌ BOT_TOKEN kiritilmagan!')
        return

    # Database yaratish
    init_database()

    # Bot yaratish
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlerlar
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('ping', ping))
    application.add_handler(CommandHandler('id', get_id))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    application.add_error_handler(error_handler)

    # Botni ishga tushirish
    print('')
    print('✅ Bot muvaffaqiyatli ishga tushdi!')
    print(f'Vaqt: {datetime.now()}')
    print('=================================')
    print('')

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
