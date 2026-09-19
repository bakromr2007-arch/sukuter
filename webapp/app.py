from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
CORS(app)

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rentals.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

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
    conn = get_db()
    cur = conn.cursor()
    customer = cur.execute('SELECT * FROM customers WHERE telegram_id = ?', (telegram_id,)).fetchone()
    conn.close()

    if not customer:
        return 'Mijoz topilmadi', 404

    return render_template('customer_dashboard.html', customer_id=customer['id'], telegram_id=telegram_id)

@app.route('/api/stats')
def get_stats():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
