import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "careai_health.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table 1: Vitals Logs 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vitals_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT DEFAULT CURRENT_DATE,
            systolic_bp INTEGER,
            glucose INTEGER
        )
    ''')
    
    # Table 2: Medications 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_name TEXT NOT NULL,
            dosage TEXT,
            reminder_time TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Table 3: Health Metrics 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metric_type TEXT NOT NULL,
            value REAL NOT NULL
        )
    ''')

    # Table 4: Patient Reports & Lab Context (NEW - Fixes the missing report memory issue)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            report_type TEXT DEFAULT 'lab_report',
            report_data TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Helper Functions for AI Tools & App Integration
# ---------------------------------------------------------

def save_patient_report(patient_name: str, report_data: str, report_type: str = "lab_report") -> str:
    """Parsed PDF report ya context ko SQLite me save karta hai."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Patient name ko normalize karke save karte hain
        p_name = patient_name.strip().lower() if patient_name else "default_patient"
        
        cursor.execute(
            "INSERT INTO patient_reports (patient_name, report_type, report_data) VALUES (?, ?, ?)",
            (p_name, report_type, report_data)
        )
        conn.commit()
        conn.close()
        return f"Successfully saved {report_type} for patient '{patient_name}'."
    except Exception as e:
        return f"Database error while saving report: {str(e)}"

def get_latest_patient_report(patient_name: str = "") -> str:
    """Latest patient report SQLite DB se fetch karta hai."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        p_name = patient_name.strip().lower() if patient_name else ""
        
        if p_name:
            cursor.execute(
                "SELECT report_type, report_data, timestamp FROM patient_reports WHERE LOWER(patient_name) = ? ORDER BY timestamp DESC LIMIT 1",
                (p_name,)
            )
        else:
            # Agar koi specific naam na diya ho, toh sabse recent uploaded report uthayega
            cursor.execute(
                "SELECT patient_name, report_type, report_data, timestamp FROM patient_reports ORDER BY timestamp DESC LIMIT 1"
            )
            
        row = cursor.fetchone()
        conn.close()
        
        if row:
            if p_name:
                return f"Report Type: {row['report_type']}\nDate: {row['timestamp']}\n\nData:\n{row['report_data']}"
            else:
                return f"Patient: {row['patient_name']}\nReport Type: {row['report_type']}\nDate: {row['timestamp']}\n\nData:\n{row['report_data']}"
        
        return f"No medical report records found in the database."
    except Exception as e:
        return f"Database error while fetching report: {str(e)}"

# Auto-initialize DB on import
init_db()