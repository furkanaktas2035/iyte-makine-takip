import sqlite3

DB_NAME = "iyte_academic_v7.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # SQLite foreign key kısıtlamalarını aktifleştir
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # -------------------------------------------------------------
    # 1. PROFIL TABLOSU SÜTUN KONTROLÜ & MIGRATION (HATA ÇÖZÜCÜ)
    # -------------------------------------------------------------
    cursor.execute("PRAGMA table_info(profile)")
    profile_cols = [c[1] for c in cursor.fetchall()]
    
    # Eğer profile tablosu daha önceden var ama user_id sütunu yoksa, tabloyu yeniden yapılandır
    if profile_cols and 'user_id' not in profile_cols:
        cursor.execute("DROP TABLE profile")
        conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            user_id TEXT PRIMARY KEY,
            name TEXT DEFAULT 'İYTE Öğrenci Paneli',
            department TEXT DEFAULT 'Makine Mühendisliği',
            grade TEXT DEFAULT '3. Sınıf',
            current_gpa REAL DEFAULT 3.00,
            current_credits INTEGER DEFAULT 60
        )
    ''')
    
    # -------------------------------------------------------------
    # 2. DERSLER TABLOSU
    # -------------------------------------------------------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            credit INTEGER DEFAULT 3,
            ects INTEGER DEFAULT 3,
            semester INTEGER DEFAULT 5,
            FOREIGN KEY(user_id) REFERENCES profile(user_id) ON DELETE CASCADE
        )
    ''')
    
    # -------------------------------------------------------------
    # 3. SINAVLAR TABLOSU
    # -------------------------------------------------------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            course_id INTEGER,
            title TEXT NOT NULL,
            event_type TEXT,
            event_date DATE NOT NULL,
            weight INTEGER NOT NULL,
            score REAL DEFAULT NULL,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    ''')
    
    # -------------------------------------------------------------
    # 4. DERS NOTLARI TABLOSU
    # -------------------------------------------------------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            course_id INTEGER,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            tag TEXT DEFAULT 'Genel',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    ''')
    
    # -------------------------------------------------------------
    # 5. MIGRATION (Eski Tablolarda user_id Yoksa Otomatik Ekler)
    # -------------------------------------------------------------
    tables_to_check = ['courses', 'exams', 'notes']
    for table in tables_to_check:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cursor.fetchall()]
        if cols and 'user_id' not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id TEXT DEFAULT 'default_user'")
            
    conn.commit()
    conn.close()

# -------------------------------------------------------------
# APP.PY TARAFINDAN ÇAĞRILAN FONKSİYONLAR
# -------------------------------------------------------------

def get_or_create_profile(user_id):
    """Kullanıcının profil verisini çeker, yoksa varsayılan profili oluşturur."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, department, grade, current_gpa, current_credits FROM profile WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute('''
            INSERT INTO profile (user_id, name, department, grade, current_gpa, current_credits)
            VALUES (?, 'İYTE Öğrenci Paneli', 'Makine Mühendisliği', '3. Sınıf', 3.00, 60)
        ''', (user_id,))
        conn.commit()
        conn.close()
        return ('İYTE Öğrenci Paneli', 'Makine Mühendisliği', '3. Sınıf', 3.00, 60)
    
    conn.close()
    return row

def update_profile(user_id, name, department, grade, current_gpa, current_credits):
    """Kullanıcının profil bilgilerini ve tamamlanmış GPA değerini günceller."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO profile (user_id, name, department, grade, current_gpa, current_credits)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            department = excluded.department,
            grade = excluded.grade,
            current_gpa = excluded.current_gpa,
            current_credits = excluded.current_credits
    ''', (user_id, name, department, grade, current_gpa, current_credits))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("V7 Veri tabanı başarıyla güncellendi!")
    