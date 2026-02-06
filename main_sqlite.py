import os
import sqlite3
from flask import Flask, jsonify, render_template, request

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
    """หน้าเว็บแสดงผลข้อมูล"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users ORDER BY id;')
        users = [dict(row) for row in cur.fetchall()]
        user_count = len(users)
        cur.close()
        conn.close()
        
        return render_template('index.html', 
                             users=users, 
                             user_count=user_count,
                             db_status='เชื่อมต่อ')
    except Exception as e:
        return render_template('index.html', 
                             users=[], 
                             user_count=0,
                             db_status='ขัดข้อง')

@app.route('/api')
def api_home():
    return jsonify({
        'message': 'สวัสดี! API ทำงานปกติ',
        'status': 'success',
        'database': 'SQLite (สำหรับทดสอบ)'
    })

@app.route('/api/health')
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

@app.route('/api/users')
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

@app.route('/api/users/add', methods=['POST'])
def add_user():
    """เพิ่มผู้ใช้ใหม่"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({
                'status': 'error',
                'message': 'กรุณากรอกชื่อและอีเมล'
            }), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        user_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'เพิ่มผู้ใช้สำเร็จ',
            'user_id': user_id
        })
    except sqlite3.IntegrityError:
        return jsonify({
            'status': 'error',
            'message': 'อีเมลนี้มีอยู่ในระบบแล้ว'
        }), 400
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
