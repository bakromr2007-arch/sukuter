function formatDate(date) {
  if (typeof date === 'string') {
    date = new Date(date);
  }
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
}

function addDays(date, days) {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function getDaysDifference(date1, date2) {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  const diffTime = d2 - d1;
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

function formatMoney(amount) {
  return new Intl.NumberFormat('uz-UZ').format(amount) + ' som';
}

function isAdmin(userId) {
  const adminIds = process.env.ADMIN_IDS.split(',').map(id => parseInt(id));
  return adminIds.includes(userId);
}

function calculateDebt(rental, payments, schedules) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let totalDue = 0;
  let totalPaid = 0;

  for (const schedule of schedules) {
    const dueDate = new Date(schedule.due_date);
    if (dueDate <= today) {
      totalDue += schedule.amount;
      totalPaid += schedule.paid_amount || 0;
    }
  }

  return totalDue - totalPaid;
}

function getNextPaymentDate(rental) {
  const { scheduleQueries } = require('./database');
  const schedules = scheduleQueries.getByRentalId.all(rental.id);
  const pending = schedules.filter(s => s.status === 'pending');

  if (pending.length === 0) return null;
  return pending[0].due_date;
}

function calculateRemainingDays(nextPaymentDate) {
  if (!nextPaymentDate) return 0;

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(nextPaymentDate);
  due.setHours(0, 0, 0, 0);

  const diff = due - today;
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

module.exports = {
  formatDate,
  addDays,
  getDaysDifference,
  formatMoney,
  isAdmin,
  calculateDebt,
  getNextPaymentDate,
  calculateRemainingDays
};
