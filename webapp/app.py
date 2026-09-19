from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
CORS(app)

# Database fayli to'g'ridan-to'g'ri shu papkada
DATABASE = os.path.join(os.path.dirname(__file__), 'rentals.db')

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
            next_payment_date DATE,
            note TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payment_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_id INTEGER NOT NULL,
            due_date DATE NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            paid_amount REAL DEFAULT 0,
            paid_date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f'Database yaratildi: {DATABASE}')

# Database'ni ishga tushirishda yaratish
init_database()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    try:
        conn = get_db()
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({'status': 'ok', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json()
        password = data.get('password')
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')

        if password == admin_pass:
            session['is_admin'] = True
            return jsonify({'success': True})
        return jsonify({'error': 'Notogri parol'}), 401

    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return 'Unauthorized', 401
    return render_template('admin_dashboard.html')

@app.route('/customer/<int:telegram_id>')
def customer_dashboard(telegram_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        customer = cur.execute('SELECT * FROM customers WHERE telegram_id = ?', (telegram_id,)).fetchone()
        conn.close()

        if not customer:
            return 'Mijoz topilmadi', 404

        return render_template('customer_dashboard.html', customer_id=customer['id'], telegram_id=telegram_id)
    except Exception as e:
        return f'Xatolik: {str(e)}', 500

@app.route('/api/stats')
def get_stats():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db()
        cur = conn.cursor()

        total_scooters = cur.execute('SELECT COUNT(*) as count FROM scooters').fetchone()['count']
        active_rentals = cur.execute('SELECT COUNT(*) as count FROM rentals WHERE status = "active"').fetchone()['count']
        total_customers = cur.execute('SELECT COUNT(*) as count FROM customers').fetchone()['count']

        conn.close()

        return jsonify({
            'total_scooters': total_scooters,
            'active_rentals': active_rentals,
            'total_customers': total_customers,
            'overdue_count': 0,
            'total_debt': 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scooters')
def get_scooters():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db()
        cur = conn.cursor()
        scooters = cur.execute('SELECT * FROM scooters ORDER BY created_at DESC').fetchall()
        conn.close()
        return jsonify([dict(s) for s in scooters])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers')
def get_customers():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db()
        cur = conn.cursor()
        customers = cur.execute('SELECT * FROM customers ORDER BY created_at DESC').fetchall()
        conn.close()
        return jsonify([dict(c) for c in customers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rentals')
def get_rentals():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db()
        cur = conn.cursor()
        rentals = cur.execute('''
            SELECT r.*, s.name as scooter_name, s.model as scooter_model, s.plate_number,
                   c.first_name, c.last_name, c.phone, c.telegram_id
            FROM rentals r
            JOIN scooters s ON r.scooter_id = s.id
            JOIN customers c ON r.customer_id = c.id
            WHERE r.status = 'active'
            ORDER BY r.start_date DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rentals])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'Flask app ishga tushmoqda...')
    print(f'Database: {DATABASE}')
    print(f'Port: {port}')
    app.run(host='0.0.0.0', port=port)
