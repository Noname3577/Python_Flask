import os
from flask import Flask, jsonify
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)

def get_db_connection():
    """สร้างการเชื่อมต่อกับฐานข้อมูล PostgreSQL"""
    conn = psycopg.connect(
        host=os.getenv('PGHOST', 'localhost'),
        dbname=os.getenv('PGDATABASE', 'testdb'),
        user=os.getenv('PGUSER', 'postgres'),
        password=os.getenv('PGPASSWORD', 'password'),
        port=os.getenv('PGPORT', '5432')
    )
    return conn

@app.route('/')
def home():
    return jsonify({
        'message': 'สวัสดี! API ทำงานปกติ',
        'status': 'success'
    })

@app.route('/health')
def health():
    """ตรวจสอบสถานะการเชื่อมต่อฐานข้อมูล"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'version': db_version
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@app.route('/users')
def get_users():
    """ดึงข้อมูลผู้ใช้จากฐานข้อมูล"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        cur.execute('SELECT * FROM users;')
        users = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': users
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
