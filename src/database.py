import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/health_store.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Table for Basic Health Metrics (Steps, Calories, Sleep)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metric_type TEXT NOT NULL,  -- 'steps', 'calories', 'heart_rate'
            value REAL NOT NULL
        )
    ''')
    
    # 2. Table for Medication Tracking & Schedules
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            reminder_time TEXT NOT NULL, -- e.g., '08:00', '21:00'
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database and tables initialized successfully!")

if __name__ == "__main__":
    init_db()