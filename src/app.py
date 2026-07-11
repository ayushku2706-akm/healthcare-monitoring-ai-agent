import streamlit as st
import os
import time
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

# ==========================================
# ENVIRONMENT & PATH CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(dotenv_path=ENV_PATH)

from agent import HealthAgent
import database as db

# Initialize SQLite database schemas safely
db.init_db()

# ==========================================
# BACKGROUND BACKGROUND REMINDER THREAD LOGIC
# ==========================================
if "reminders_checked" not in st.session_state:
    st.session_state.reminders_checked = {}

def check_reminders_loop():
    """Background loop running outside Streamlit context to monitor times."""
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M")
            conn = db.get_db_connection()
            meds = conn.execute("SELECT * FROM medications WHERE is_active = 1").fetchall()
            conn.close()
            
            for med in meds:
                # If current system time matches reminder time, flag it for a popup
                if med['reminder_time'] == current_time:
                    med_id = med['id']
                    # Ensure we don't alert multiple times within the same minute
                    if st.session_state.get(f"alert_triggered_{med_id}_{current_time}") is not True:
                        st.session_state[f"alert_triggered_{med_id}_{current_time}"] = True
                        st.session_state["active_reminder_popup"] = f"🔔 REMINDER: It is time to take your {med['medication_name']} ({med['dosage']})!"
                        # Force Streamlit to rerun and show the message instantly
                        st.rerun()
        except Exception:
            pass
        time.sleep(10)  # Check every 10 seconds

# Keep the background daemon loop running continuously across page reloads
if "reminder_thread_started" not in st.session_state:
    thread = Thread(target=check_reminders_loop, daemon=True)
    thread.start()
    st.session_state.reminder_thread_started = True

# ==========================================
# STREAMLIT UI SETUP & INITIALIZATION
# ==========================================
st.set_page_config(page_title="CareAI - Personal Health Companion", layout="wide")
st.title("🏥 CareAI: Healthcare Monitoring Agent")

# POPUP TRIGGER: If a background thread flags a reminder, flash a prominent message box
if "active_reminder_popup" in st.session_state and st.session_state.active_reminder_popup:
    st.toast(st.session_state.active_reminder_popup, icon="⚠️")
    st.error(st.session_state.active_reminder_popup)
    if st.button("Dismiss Reminder"):
        st.session_state.active_reminder_popup = None
        st.rerun()

# Keep running chat logs and agent engine alive
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = HealthAgent()

# Create Layout: Left Dashboard Column, Right Chat Agent Column
col_dash, col_chat = st.columns([1, 1.2])

# ==========================================
# LEFT COLUMN: PATIENT DATA MONITORING
# ==========================================
with col_dash:
    st.subheader("📊 Patient Tracking Dashboard")
    
    # Medication Scheduler Panel
    # Medication Scheduler Panel
    with st.expander("💊 Schedule New Medication", expanded=True):
        med_name = st.text_input("Medication Name", placeholder="e.g., Metformin")
        dosage = st.text_input("Dosage Description", placeholder="e.g., 500mg once daily")
        remind_time = st.time_input("Set Reminder Time")
        
        if st.button("Save Schedule"):
            if med_name and dosage:
                conn = db.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO medications (medication_name, dosage, reminder_time) VALUES (?, ?, ?)",
                    (med_name, dosage, remind_time.strftime("%H:%M"))
                )
                conn.commit()
                conn.close()
                st.success(f"✅ Registered tracking schedule for {med_name}!")
                st.rerun()
            else:
                st.error("Please fill out both the Medication Name and Dosage fields.")

    # Live SQLite Data Feed View
    st.markdown("### Active Tracked Prescriptions")
    conn = db.get_db_connection()
    meds = conn.execute("SELECT * FROM medications WHERE is_active = 1").fetchall()
    conn.close()
    
    if meds:
        for med in meds:
            st.info(f"👉 **{med['medication_name']}** ({med['dosage']}) — Scheduled Daily at: `{med['reminder_time']}`")
    else:
        st.caption("No active medication items scheduled for tracking yet.")

# ==========================================
# RIGHT COLUMN: CONVERSATIONAL AI COMPANION
# ==========================================
with col_chat:
    st.subheader("💬 AI Health Companion Chat")
    
    # Loop and print out running dialogue logs
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(text)
            
    # Chat Input Interface
    if user_query := st.chat_input("Ask a tracking question..."):
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing request context..."):
                ai_response = st.session_state.agent.respond(st.session_state.chat_history, user_query)
                st.write(ai_response)
                
        st.session_state.chat_history.append(("user", user_query))
        st.session_state.chat_history.append(("assistant", ai_response))