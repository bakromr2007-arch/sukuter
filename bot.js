require('dotenv').config();
const { Telegraf, session } = require('telegraf');
const cron = require('node-cron');
const {
  scooterQueries,
  customerQueries,
  rentalQueries,
  paymentQueries,
  scheduleQueries,
  db
} = require('./database');
const {
  formatDate,
  addDays,
  formatMoney,
  isAdmin,
  calculateDebt,
  getNextPaymentDate,
  calculateRemainingDays
} = require('./utils');
const {
  mainAdminKeyboard,
  getCustomerKeyboard,
  cancelKeyboard,
  paymentTypeKeyboard,
  buildScooterListKeyboard,
  buildRentalListKeyboard
} = require('./keyboards');

if (!process.env.BOT_TOKEN) {
  console.error('BOT_TOKEN kiritilmagan!');
  process.exit(1);
}

if (!process.env.ADMIN_IDS) {
  console.error('ADMIN_IDS kiritilmagan!');
  process.exit(1);
}

const bot = new Telegraf(process.env.BOT_TOKEN);
bot.use(session());

bot.start((ctx) => {
  const userId = ctx.from.id;
  const name = ctx.from.first_name;

  if (isAdmin(userId)) {
    ctx.reply(
      `Assalomu alaykum, ${name}!\n\nSkuter arenda botiga xush kelibsiz.\nSiz admin sifatida kirgansiz.`,
      mainAdminKeyboard
    );
  } else {
    const customer = customerQueries.getByTelegramId.get(userId);
    if (customer) {
      ctx.reply(
        `Assalomu alaykum, ${name}!\n\nWeb App orqali barcha malumotlaringizni koring.`,
        getCustomerKeyboard(userId)
      );
    } else {
      ctx.reply(`Assalomu alaykum, ${name}!\n\nAdministrator bilan boglaning.`);
    }
  }
});

bot.hears('➕ Skuter qoshish', (ctx) => {
  if (!isAdmin(ctx.from.id)) return;
  ctx.session = { action: 'add_scooter', step: 1 };
  ctx.reply('Skuter nomini kiriting:', cancelKeyboard);
});

bot.hears('👤 Mijoz qoshish', (ctx) => {
  if (!isAdmin(ctx.from.id)) return;
  ctx.session = { action: 'add_customer', step: 1 };
  ctx.reply('Mijoz ismini kiriting:', cancelKeyboard);
});

bot.hears('🚀 Arenda berish', (ctx) => {
  if (!isAdmin(ctx.from.id)) return;
  const available = scooterQueries.getAvailable.all('available');
  if (available.length === 0) {
    ctx.reply('Bosh skuter yoq.', mainAdminKeyboard);
    return;
  }
  ctx.session = { action: 'create_rental', step: 1, data: {} };
  ctx.reply('Skuterni tanlang:', buildScooterListKeyboard(available));
});

bot.hears('💰 Tolov qabul qilish', (ctx) => {
  if (!isAdmin(ctx.from.id)) return;
  const rentals = rentalQueries.getActive.all();
  if (rentals.length === 0) {
    ctx.reply('Aktiv arenda yoq.', mainAdminKeyboard);
    return;
  }
  ctx.session = { action: 'accept_payment', step: 1, data: {} };
  ctx.reply('Kimdan tolov qabul qilasiz?', buildRentalListKeyboard(rentals));
});

bot.hears('📈 Statistika', (ctx) => {
  if (!isAdmin(ctx.from.id)) return;
  const total = scooterQueries.getAll.all().length;
  const active = rentalQueries.getActive.all().length;
  const customers = customerQueries.getAll.all().length;
  ctx.reply(
    `📈 Statistika:\n\n🛴 Skuterlar: ${total}\n📊 Aktiv arenda: ${active}\n👥 Mijozlar: ${customers}`,
    mainAdminKeyboard
  );
});

bot.hears('❌ Bekor qilish', (ctx) => {
  ctx.session = null;
  if (isAdmin(ctx.from.id)) {
    ctx.reply('Bekor qilindi.', mainAdminKeyboard);
  } else {
    ctx.reply('Bekor qilindi.', getCustomerKeyboard(ctx.from.id));
  }
});

bot.on('text', (ctx) => {
  if (!ctx.session?.action) return;
  const text = ctx.message.text;

  if (ctx.session.action === 'add_scooter') {
    if (ctx.session.step === 1) {
      ctx.session.data = { name: text };
      ctx.session.step = 2;
      ctx.reply('Model (yoki - bosing):');
    } else if (ctx.session.step === 2) {
      ctx.session.data.model = text === '-' ? null : text;
      ctx.session.step = 3;
      ctx.reply('Raqam (yoki - bosing):');
    } else if (ctx.session.step === 3) {
      ctx.session.data.plate_number = text === '-' ? null : text;
      try {
        scooterQueries.add.run(
          ctx.session.data.name,
          ctx.session.data.model,
          ctx.session.data.plate_number
        );
        ctx.reply('Skuter qoshildi!', mainAdminKeyboard);
        ctx.session = null;
      } catch (e) {
        ctx.reply('Xatolik!', mainAdminKeyboard);
        ctx.session = null;
      }
    }
  } else if (ctx.session.action === 'add_customer') {
    if (ctx.session.step === 1) {
      ctx.session.data = { first_name: text };
      ctx.session.step = 2;
      ctx.reply('Familiya (yoki -):');
    } else if (ctx.session.step === 2) {
      ctx.session.data.last_name = text === '-' ? null : text;
      ctx.session.step = 3;
      ctx.reply('Telefon:');
    } else if (ctx.session.step === 3) {
      ctx.session.data.phone = text;
      ctx.session.step = 4;
      ctx.reply('Manzil (yoki -):');
    } else if (ctx.session.step === 4) {
      ctx.session.data.address = text === '-' ? null : text;
      ctx.session.step = 5;
      ctx.reply('Telegram ID:');
    } else if (ctx.session.step === 5) {
      const tid = parseInt(text);
      if (isNaN(tid)) {
        ctx.reply('Faqat raqam!');
        return;
      }
      try {
        customerQueries.add.run(
          tid,
          ctx.session.data.first_name,
          ctx.session.data.last_name,
          ctx.session.data.phone,
          ctx.session.data.address
        );
        ctx.reply('Mijoz qoshildi!', mainAdminKeyboard);
        ctx.session = null;
      } catch (e) {
        ctx.reply('Xatolik!', mainAdminKeyboard);
        ctx.session = null;
      }
    }
  }
});

cron.schedule('0 9 * * *', () => {
  console.log('Eslatmalar yuborilmoqda...');
});

bot.launch().then(() => {
  console.log('Bot ishlayapti!');
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
