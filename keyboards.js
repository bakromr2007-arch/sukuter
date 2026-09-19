const { Markup } = require('telegraf');

const WEB_APP_URL = process.env.WEB_APP_URL || 'http://localhost:5000';

const mainAdminKeyboard = Markup.keyboard([
  [Markup.button.webApp('🌐 Admin Panel', `${WEB_APP_URL}/admin-login`)],
  ['➕ Skuter qoshish', '📋 Skuterlar royxati'],
  ['👤 Mijoz qoshish', '👥 Mijozlar royxati'],
  ['🚀 Arenda berish', '📊 Aktiv arendalar'],
  ['💰 Tolov qabul qilish', '📈 Statistika']
]).resize();

function getCustomerKeyboard(telegramId) {
  return Markup.keyboard([
    [Markup.button.webApp('🌐 Mening kabinetim', `${WEB_APP_URL}/customer/${telegramId}`)],
    ['📱 Mening arendalarim', '💳 Tolovlarim']
  ]).resize();
}

const cancelKeyboard = Markup.keyboard([['❌ Bekor qilish']]).resize();

const paymentTypeKeyboard = Markup.keyboard([
  ['📅 Haftalik', '📆 Oylik'],
  ['❌ Bekor qilish']
]).resize();

function buildScooterListKeyboard(scooters) {
  const buttons = scooters.map(s => [`${s.name} - ${s.status === 'available' ? '✅' : '❌'}`]);
  buttons.push(['🔙 Orqaga']);
  return Markup.keyboard(buttons).resize();
}

function buildRentalListKeyboard(rentals) {
  const buttons = rentals.map(r => [`🛴 ${r.scooter_name} - ${r.first_name}`]);
  buttons.push(['🔙 Orqaga']);
  return Markup.keyboard(buttons).resize();
}

module.exports = {
  mainAdminKeyboard,
  getCustomerKeyboard,
  cancelKeyboard,
  paymentTypeKeyboard,
  buildScooterListKeyboard,
  buildRentalListKeyboard
};
