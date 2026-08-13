import sqlite3

DB_NAME = "iyte_academic_v7.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Profil Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY DEFAULT 1,
            name TEXT,
            department TEXT,
            grade TEXT,
            current_gpa REAL,
            current_credits INTEGER DEFAULT 60
        )
    ''')
    
    # Eksik sütun kontrolü (Sütun yoksa otomatik ekler)
    cursor.execute("PRAGMA table_info(profile)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'current_credits' not in columns:
        cursor.execute("ALTER TABLE profile ADD COLUMN current_credits INTEGER DEFAULT 60")
    
    cursor.execute("SELECT COUNT(*) FROM profile WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO profile (id, name, department, grade, current_gpa, current_credits)
            VALUES (1, 'İYTE Öğrenci Paneli', 'Makine Mühendisliği', '3. Sınıf', 3.00, 60)
        ''')
    
    # 2. Dersler Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            credit INTEGER,
            ects INTEGER DEFAULT 3,
            semester INTEGER DEFAULT 5
        )
    ''')
    
    # 3. Sınavlar Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            title TEXT NOT NULL,
            event_type TEXT,
            event_date DATE NOT NULL,
            weight INTEGER NOT NULL,
            score REAL DEFAULT NULL,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    ''')
    
    # 4. Ders Notları Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            tag TEXT DEFAULT 'Genel',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("V7 Veri tabanı başarıyla güncellendi!")