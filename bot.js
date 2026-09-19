require('dotenv').config();
const { Telegraf, session } = require('telegraf');

// Environment variables tekshirish
console.log('=================================');
console.log('Bot ishga tushmoqda...');
console.log('BOT_TOKEN:', process.env.BOT_TOKEN ? 'Mavjud ✓' : 'YOQ ✗');
console.log('ADMIN_IDS:', process.env.ADMIN_IDS ? process.env.ADMIN_IDS : 'YOQ ✗');
console.log('WEB_APP_URL:', process.env.WEB_APP_URL ? process.env.WEB_APP_URL : 'YOQ ✗');
console.log('=================================');

if (!process.env.BOT_TOKEN) {
  console.error('❌ BOT_TOKEN kiritilmagan!');
  process.exit(1);
}

if (!process.env.ADMIN_IDS) {
  console.error('❌ ADMIN_IDS kiritilmagan!');
  process.exit(1);
}

const bot = new Telegraf(process.env.BOT_TOKEN);

// Session middleware
bot.use(session());

// Admin tekshirish funksiyasi
function isAdmin(userId) {
  const adminIds = process.env.ADMIN_IDS.split(',').map(id => parseInt(id.trim()));
  return adminIds.includes(userId);
}

// Start command
bot.start((ctx) => {
  console.log('Start buyrugi olindi:', ctx.from.id, ctx.from.first_name);

  const userId = ctx.from.id;
  const name = ctx.from.first_name;

  if (isAdmin(userId)) {
    console.log('Admin login:', userId);
    ctx.reply(
      `🎉 Assalomu alaykum, ${name}!\n\n` +
      `Siz admin sifatida tizimga kirgansiz.\n\n` +
      `Bot ishlayapti va tayyor! ✅`,
      {
        reply_markup: {
          keyboard: [
            ['📊 Statistika', '👥 Mijozlar'],
            ['🛴 Skuterlar', '💰 Tolovlar']
          ],
          resize_keyboard: true
        }
      }
    );
  } else {
    console.log('Oddiy foydalanuvchi:', userId);
    ctx.reply(
      `👋 Assalomu alaykum, ${name}!\n\n` +
      `Bot ishlayapti! ✅\n\n` +
      `Admin bilan boglaning.`
    );
  }
});

// Help command
bot.help((ctx) => {
  ctx.reply('Bot ishlayapti! /start buyrug\'ini yuboring.');
});

// Test command
bot.command('test', (ctx) => {
  console.log('Test buyrugi:', ctx.from.id);
  ctx.reply('✅ Bot ishlayapti! Barcha funksiyalar normal.');
});

// Ping command
bot.command('ping', (ctx) => {
  ctx.reply('🏓 Pong! Bot aktiv.');
});

// ID command
bot.command('id', (ctx) => {
  ctx.reply(`Sizning Telegram ID: ${ctx.from.id}`);
});

// Statistika
bot.hears('📊 Statistika', (ctx) => {
  if (!isAdmin(ctx.from.id)) {
    ctx.reply('Bu buyruq faqat adminlar uchun.');
    return;
  }
  ctx.reply('📊 Statistika:\n\nBot ishlayapti va tayyor!');
});

// Barcha text xabarlar uchun
bot.on('text', (ctx) => {
  console.log('Text olindi:', ctx.from.id, ctx.message.text);

  // Agar buyruq bo'lmasa
  if (!ctx.message.text.startsWith('/')) {
    ctx.reply('Xabar qabul qilindi ✓\n\nBot ishlayapti!');
  }
});

// Error handling
bot.catch((err, ctx) => {
  console.error('❌ Bot xatolik:', err);
  console.error('Context:', ctx.update);
});

// Bot launch
bot.launch()
  .then(() => {
    console.log('');
    console.log('=================================');
    console.log('✅ Bot muvaffaqiyatli ishga tushdi!');
    console.log('Vaqt:', new Date().toLocaleString());
    console.log('Bot username:', bot.botInfo?.username || 'unknown');
    console.log('=================================');
    console.log('');
  })
  .catch((err) => {
    console.error('❌ Bot ishga tushmadi:', err);
    process.exit(1);
  });

// Graceful shutdown
process.once('SIGINT', () => {
  console.log('Bot toxtatilmoqda (SIGINT)...');
  bot.stop('SIGINT');
});

process.once('SIGTERM', () => {
  console.log('Bot toxtatilmoqda (SIGTERM)...');
  bot.stop('SIGTERM');
});

// Process error handlers
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});
