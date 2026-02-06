import os
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)
DATABASE = 'test.db'

def get_db_connection():
    """สร้างการเชื่อมต่อกับฐานข้อมูล SQLite"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """สร้างตารางและข้อมูลตัวอย่าง"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # เพิ่มข้อมูลตัวอย่างถ้ายังไม่มี
    try:
        conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                    ('สมชาย ใจดี', 'somchai@example.com'))
        conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                    ('สมหญิง รักสนุก', 'somying@example.com'))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # ข้อมูลมีอยู่แล้ว
    
    conn.close()

@app.route('/')
def home():
    return jsonify({
        'message': 'สวัสดี! API ทำงานปกติ',
        'status': 'success',
        'database': 'SQLite (สำหรับทดสอบ)'
    })

@app.route('/health')
def health():
    """ตรวจสอบสถานะการเชื่อมต่อฐานข้อมูล"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT sqlite_version();')
        db_version = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'type': 'SQLite',
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
        cur = conn.cursor()
        cur.execute('SELECT * FROM users;')
        users = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'count': len(users),
            'data': users
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # สร้างฐานข้อมูลและตารางก่อนรัน
    init_db()
    print('✓ ฐานข้อมูล SQLite พร้อมใช้งาน')
    
    port = int(os.getenv('PORT', 8000))
    print(f'✓ เริ่มรัน Flask API ที่ http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True)
