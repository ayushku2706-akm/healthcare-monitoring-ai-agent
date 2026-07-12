import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

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
# STREAMLIT UI SETUP & INITIALIZATION
# ==========================================
st.set_page_config(page_title="CareAI - Personal Health Companion", layout="wide")
st.title("🏥 CareAI: Healthcare Monitoring Agent")

# AUTOMATED BACKGROUND TICKER: Refreshes every 10 seconds to process alarms
st_autorefresh(interval=10000, key="datetimemonitor")

# Keep running application states alive
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = HealthAgent()
if "last_triggered_reminder" not in st.session_state:
    st.session_state.last_triggered_reminder = ""

# ==========================================
# LIVE ALARM REMINDER CHECKING PIPELINE
# ==========================================
current_time_str = datetime.now().strftime("%H:%M")

conn = db.get_db_connection()
active_meds = conn.execute("SELECT medication_name, dosage, reminder_time FROM medications WHERE is_active = 1").fetchall()
conn.close()

for med in active_meds:
    if med['reminder_time'] == current_time_str:
        reminder_key = f"{med['medication_name']}_{current_time_str}"
        if st.session_state.last_triggered_reminder != reminder_key:
            st.session_state.last_triggered_reminder = reminder_key
            st.toast(f"🚨 MEDICATION ALARM: Take {med['medication_name']} NOW!", icon="🔔")
            st.error(f"🚨 **LIVE REMINDER ALARM:** It is exactly {current_time_str}! Please take your scheduled dose of **{med['medication_name']}** ({med['dosage']}).")
            try:
                import winsound
                winsound.MessageBeep()
            except Exception:
                pass

# ==========================================
# INTERFACE LAYOUT: DASHBOARD & CHAT
# ==========================================
col_dash, col_chat = st.columns([1, 1.2])

# ==========================================
# LEFT COLUMN: PATIENT DATA MONITORING
# ==========================================
with col_dash:
    st.subheader("📊 Patient Tracking Dashboard")
    
    # Feature 1: Medication Scheduler Panel
    with st.expander("💊 Schedule New Medication", expanded=False):
        med_name = st.text_input("Medication Name", placeholder="e.g., Metformin")
        dosage = st.text_input("Dosage Description", placeholder="e.g., 500mg once daily")
        remind_time = st.time_input("Set Reminder Time")
        
        if st.button("Save Schedule"):
            if med_name and dosage:
                formatted_time = remind_time.strftime("%H:%M")
                conn = db.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO medications (medication_name, dosage, reminder_time, is_active) VALUES (?, ?, ?, 1)",
                    (med_name, dosage, formatted_time)
                )
                conn.commit()
                conn.close()
                st.success(f"✅ Registered tracking schedule for {med_name} at {formatted_time}!")
                st.rerun()
            else:
                st.error("Please fill out both fields.")

    # Fetch active items from SQLite
    conn = db.get_db_connection()
    meds = conn.execute("SELECT id, medication_name, dosage, reminder_time FROM medications WHERE is_active = 1").fetchall()
    conn.close()

    # View Current List
    st.markdown("### Active Tracked Prescriptions")
    if meds:
        for med in meds:
            st.info(f"👉 **{med['medication_name']}** ({med['dosage']}) — Scheduled Daily at: `{med['reminder_time']}`")
    else:
        st.caption("No active medication items scheduled for tracking yet.")

    # Feature 2: NEW! Update & Delete Management Panel
    if meds:
        st.markdown("---")
        with st.expander("⚙️ Manage Existing Reminders", expanded=True):
            # Create a selection map for the dropdown
            med_options = {f"{m['medication_name']} ({m['reminder_time']})": m for m in meds}
            selected_label = st.selectbox("Select a reminder to modify:", list(med_options.keys()))
            selected_med = med_options[selected_label]
            
            # Form fields showing current values
            update_dosage = st.text_input("Edit Dosage Description", value=selected_med['dosage'])
            
            # Parse existing time to display as default
            try:
                parsed_time = datetime.strptime(selected_med['reminder_time'], "%H:%M").time()
            except Exception:
                parsed_time = datetime.now().time()
            update_time = st.time_input("Edit Reminder Time", value=parsed_time)
            
            col_update, col_delete = st.columns(2)
            
            # Update Action
            with col_update:
                if st.button("🔄 Update Reminder", use_container_width=True):
                    conn = db.get_db_connection()
                    conn.execute(
                        "UPDATE medications SET dosage = ?, reminder_time = ? WHERE id = ?",
                        (update_dosage, update_time.strftime("%H:%M"), selected_med['id'])
                    )
                    conn.commit()
                    conn.close()
                    st.success("Updated successfully!")
                    st.rerun()
                    
            # Delete Action
            with col_delete:
                if st.button("🗑️ Delete Reminder", use_container_width=True, type="primary"):
                    conn = db.get_db_connection()
                    # Soft delete by setting is_active to 0
                    conn.execute("UPDATE medications SET is_active = 0 WHERE id = ?", (selected_med['id'],))
                    conn.commit()
                    conn.close()
                    st.warning(f"Removed tracker for {selected_med['medication_name']}.")
                    st.rerun()

# ==========================================
# RIGHT COLUMN: CONVERSATIONAL AI COMPANION
# ==========================================
with col_chat:
    st.subheader("💬 AI Health Companion Chat")
    
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(text)
            
    if user_query := st.chat_input("Ask a tracking question..."):
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing request context..."):
                ai_response = st.session_state.agent.respond(st.session_state.chat_history, user_query)
                st.write(ai_response)
                
        st.session_state.chat_history.append(("user", user_query))
        st.session_state.chat_history.append(("assistant", ai_response))