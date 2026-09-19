const Database = require('better-sqlite3');
const path = require('path');

const db = new Database(path.join(__dirname, 'rentals.db'));

db.exec(`
  CREATE TABLE IF NOT EXISTS scooters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    model TEXT,
    plate_number TEXT,
    status TEXT DEFAULT 'available',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT,
    phone TEXT,
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scooter_id) REFERENCES scooters(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
  );

  CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    payment_date DATE NOT NULL,
    next_payment_date DATE,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rental_id) REFERENCES rentals(id)
  );

  CREATE TABLE IF NOT EXISTS payment_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_id INTEGER NOT NULL,
    due_date DATE NOT NULL,
    amount REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    paid_amount REAL DEFAULT 0,
    paid_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rental_id) REFERENCES rentals(id)
  );
`);

const scooterQueries = {
  add: db.prepare('INSERT INTO scooters (name, model, plate_number) VALUES (?, ?, ?)'),
  getAll: db.prepare('SELECT * FROM scooters ORDER BY created_at DESC'),
  getAvailable: db.prepare('SELECT * FROM scooters WHERE status = ? ORDER BY name'),
  getById: db.prepare('SELECT * FROM scooters WHERE id = ?'),
  updateStatus: db.prepare('UPDATE scooters SET status = ? WHERE id = ?'),
  delete: db.prepare('DELETE FROM scooters WHERE id = ?')
};

const customerQueries = {
  add: db.prepare('INSERT INTO customers (telegram_id, first_name, last_name, phone, address) VALUES (?, ?, ?, ?, ?)'),
  getAll: db.prepare('SELECT * FROM customers ORDER BY created_at DESC'),
  getById: db.prepare('SELECT * FROM customers WHERE id = ?'),
  getByTelegramId: db.prepare('SELECT * FROM customers WHERE telegram_id = ?'),
  update: db.prepare('UPDATE customers SET first_name = ?, last_name = ?, phone = ?, address = ? WHERE id = ?')
};

const rentalQueries = {
  add: db.prepare('INSERT INTO rentals (scooter_id, customer_id, start_date, payment_type, weekly_price, monthly_price, deposit) VALUES (?, ?, ?, ?, ?, ?, ?)'),
  getActive: db.prepare(`
    SELECT r.*, s.name as scooter_name, s.model as scooter_model, s.plate_number,
           c.first_name, c.last_name, c.phone, c.telegram_id
    FROM rentals r
    JOIN scooters s ON r.scooter_id = s.id
    JOIN customers c ON r.customer_id = c.id
    WHERE r.status = 'active'
    ORDER BY r.start_date DESC
  `),
  getById: db.prepare(`
    SELECT r.*, s.name as scooter_name, s.model as scooter_model, s.plate_number,
           c.first_name, c.last_name, c.phone, c.telegram_id
    FROM rentals r
    JOIN scooters s ON r.scooter_id = s.id
    JOIN customers c ON r.customer_id = c.id
    WHERE r.id = ?
  `),
  getByCustomerId: db.prepare(`
    SELECT r.*, s.name as scooter_name, s.model as scooter_model, s.plate_number
    FROM rentals r
    JOIN scooters s ON r.scooter_id = s.id
    WHERE r.customer_id = ? AND r.status = 'active'
  `),
  close: db.prepare('UPDATE rentals SET status = ? WHERE id = ?')
};

const paymentQueries = {
  add: db.prepare('INSERT INTO payments (rental_id, amount, payment_date, next_payment_date, note) VALUES (?, ?, ?, ?, ?)'),
  getByRentalId: db.prepare('SELECT * FROM payments WHERE rental_id = ? ORDER BY payment_date DESC'),
  getTotalPaid: db.prepare('SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE rental_id = ?')
};

const scheduleQueries = {
  add: db.prepare('INSERT INTO payment_schedule (rental_id, due_date, amount) VALUES (?, ?, ?)'),
  getByRentalId: db.prepare('SELECT * FROM payment_schedule WHERE rental_id = ? ORDER BY due_date'),
  getPending: db.prepare(`
    SELECT ps.*, r.scooter_id, r.customer_id, s.name as scooter_name,
           c.first_name, c.last_name, c.telegram_id
    FROM payment_schedule ps
    JOIN rentals r ON ps.rental_id = r.id
    JOIN scooters s ON r.scooter_id = s.id
    JOIN customers c ON r.customer_id = c.id
    WHERE ps.status = 'pending' AND r.status = 'active'
    ORDER BY ps.due_date
  `),
  getOverdue: db.prepare(`
    SELECT ps.*, r.scooter_id, r.customer_id, s.name as scooter_name,
           c.first_name, c.last_name, c.telegram_id
    FROM payment_schedule ps
    JOIN rentals r ON ps.rental_id = r.id
    JOIN scooters s ON r.scooter_id = s.id
    JOIN customers c ON r.customer_id = c.id
    WHERE ps.status = 'pending' AND ps.due_date < date('now') AND r.status = 'active'
    ORDER BY ps.due_date
  `),
  markPaid: db.prepare('UPDATE payment_schedule SET status = ?, paid_amount = ?, paid_date = ? WHERE id = ?')
};

module.exports = {
  db,
  scooterQueries,
  customerQueries,
  rentalQueries,
  paymentQueries,
  scheduleQueries
};
