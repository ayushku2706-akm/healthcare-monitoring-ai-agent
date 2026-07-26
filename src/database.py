import sqlite3
import os

# Sirf ek hi path rakho
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "health_companion.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table 1: Vitals Logs (Analytics ke liye)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vitals_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT DEFAULT CURRENT_DATE,
            systolic_bp INTEGER,
            glucose INTEGER
        )
    ''')
    
    # Table 2: Medications (Scheduler ke liye)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_name TEXT NOT NULL,
            dosage TEXT,
            reminder_time TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Table 3: Health Metrics (Additional tracking ke liye)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metric_type TEXT NOT NULL,
            value REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

