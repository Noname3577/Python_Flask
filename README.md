# Python API สำหรับ Railway

โปรเจค Flask API พร้อมเชื่อมต่อฐานข้อมูล PostgreSQL สำหรับ deploy บน Railway

## คุณสมบัติ

- Flask Web Framework
- เชื่อมต่อ PostgreSQL Database
- Health check endpoint
- พร้อม deploy บน Railway

## การติดตั้งและรันในเครื่อง

1. สร้าง virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # บน Windows: venv\Scripts\activate
```

2. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

3. ตั้งค่า environment variables:
```bash
export PGHOST=localhost
export PGDATABASE=your_database
export PGUSER=your_user
export PGPASSWORD=your_password
export PGPORT=5432
export PORT=8000
```

4. รันแอพพลิเคชัน:
```bash
python main.py
```

## Deploy บน Railway

1. สร้างโปรเจคใหม่บน Railway
2. เพิ่ม PostgreSQL database จาก Railway
3. เชื่อมต่อ GitHub repository หรืออัพโหลดโค้ด
4. Railway จะตั้งค่า environment variables อัตโนมัติ
5. Deploy จะเริ่มทำงานทันที

## API Endpoints

- `GET /` - หน้าแรก
- `GET /health` - ตรวจสอบสถานะฐานข้อมูล
- `GET /users` - ดึงข้อมูลผู้ใช้ (ต้องมีตาราง users ในฐานข้อมูล)

## สร้างตารางตัวอย่าง

เชื่อมต่อฐานข้อมูลและรันคำสั่ง SQL:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email) VALUES 
    ('สมชาย ใจดี', 'somchai@example.com'),
    ('สมหญิง รักสนุก', 'somying@example.com');
```
