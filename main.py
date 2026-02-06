import os
from flask import Flask, jsonify, render_template, request
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

def init_db():
    """สร้างตารางและข้อมูลตัวอย่างถ้ายังไม่มี"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # สร้างตาราง users ถ้ายังไม่มี
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตรวจสอบว่ามีข้อมูลหรือยัง
        cur.execute('SELECT COUNT(*) FROM users')
        count = cur.fetchone()[0]
        
        # ถ้ายังไม่มีข้อมูล ให้เพิ่มข้อมูลตัวอย่าง
        if count == 0:
            cur.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                ('สมชาย ใจดี', 'somchai@example.com')
            )
            cur.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                ('สมหญิง รักสนุก', 'somying@example.com')
            )
            print('✓ เพิ่มข้อมูลตัวอย่างเรียบร้อย')
        
        conn.commit()
        cur.close()
        conn.close()
        print('✓ ฐานข้อมูลพร้อมใช้งาน')
        return True
    except Exception as e:
        print(f'⚠ เกิดข้อผิดพลาดในการสร้างตาราง: {e}')
        return False

@app.route('/')
def home():
    """หน้าเว็บแสดงผลข้อมูล"""
    try:
        # ตรวจสอบและสร้างตารางถ้ายังไม่มี
        conn = get_db_connection()
        cur = conn.cursor()
        
        # ตรวจสอบว่าตาราง users มีหรือยัง
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            cur.close()
            conn.close()
            init_db()
            conn = get_db_connection()
        
        cur = conn.cursor(row_factory=dict_row)
        cur.execute('SELECT * FROM users ORDER BY id;')
        users = cur.fetchall()
        user_count = len(users)
        cur.close()
        conn.close()
        
        return render_template('index.html', 
                             users=users, 
                             user_count=user_count,
                             db_status='เชื่อมต่อ')
    except Exception as e:
        # ถ้าเกิดข้อผิดพลาด ลองสร้างตารางใหม่
        try:
            init_db()
        except:
            pass
        return render_template('index.html', 
                             users=[], 
                             user_count=0,
                             db_status='ขัดข้อง')

@app.route('/api')
def api_home():
    return jsonify({
        'message': 'สวัสดี! API ทำงานปกติ',
        'status': 'success'
    })

@app.route('/api/health')
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

@app.route('/api/users')
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
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
            (name, email)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'เพิ่มผู้ใช้สำเร็จ',
            'user_id': user_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/init-db')
def init_db_endpoint():
    """Endpoint สำหรับสร้างตารางด้วย API"""
    success = init_db()
    if success:
        return jsonify({
            'status': 'success',
            'message': 'สร้างตารางและข้อมูลเรียบร้อย'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'เกิดข้อผิดพลาดในการสร้างตาราง'
        }), 500

if __name__ == '__main__':
    # สร้างตารางอัตโนมัติเมื่อเริ่มรัน
    init_db()
    
    port = int(os.getenv('PORT', 8000))
    print(f'✓ เริ่มรัน Flask API ที่ port {port}')
    app.run(host='0.0.0.0', port=port)
