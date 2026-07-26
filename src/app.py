import streamlit as st
import os
import pandas as pd
import time
import importlib
from datetime import datetime
from fpdf import FPDF
from dotenv import load_dotenv
import tools as health_tools
import database as db
from agent import HealthAgent
import matplotlib.pyplot as plt
import sqlite3 
import io 
import pytz


from streamlit_autorefresh import st_autorefresh
count = st_autorefresh(interval=30000, limit=None, key="reminder_refresh_counter")
# ENVIRONMENT & PATH CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(dotenv_path=ENV_PATH)


# Initialize DB safely on startup
db.init_db()


@st.cache_resource
def get_agent():
    return HealthAgent()


if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "agent" not in st.session_state: st.session_state.agent = get_agent()


def generate_clean_pdf(text_content):
    
    clean_text = text_content.replace("?", "").replace("--", "").replace("**", "")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Multiline support
    for line in clean_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S')

# INITIALIZE INTERFACE WITH CUSTOM PREMIUM THEME
st.set_page_config(
    page_title="CareAI - Pro Health Hub", 
    layout="wide",
    initial_sidebar_state="collapsed"
)



st.markdown("""
    <style>
        /* Global Dark Theme Refinement */
        .stApp { background-color: #0B0E14; }
        
        /* Glassmorphism Card Logic */
        .glass-card {
            background: rgba(17, 24, 39, 0.6);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 24px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        
        /* Typography */
        h1, h2, h3 { color: #F8FAFC !important; letter-spacing: -0.5px; }
        
        /* Custom Metric Cards */
        .metric-card {
            background: linear-gradient(145deg, #1e293b, #0f172a);
            padding: 20px;
            border-radius: 16px;
            border-left: 4px solid #38BDF8;
        }
        
        /* Button Polish */
        .stButton>button {
            background: #38BDF8 !important;
            color: #0B0E14 !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            border: none !important;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover {
            filter: brightness(1.2);
            transform: translateY(-2px);
        }
    </style>
""", unsafe_allow_html=True)

# UI Implementation Helper
def glass_container():
    return st.container() # Isko CSS class se link karne ke liye niche markdown use karein

st.title("🏥 CareAI: Pro Health Diagnostic Hub")
st.markdown("<p style='color:#94A3B8; font-size:15px; margin-top:-15px;'>Enterprise Clinical Analytics, Automated Medicine Reminders & Patient Care Companion</p>", unsafe_allow_html=True)
st.markdown("---")

# Initialize persistent memory storage objects safely
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "agent" not in st.session_state: st.session_state.agent = HealthAgent()
if "last_triggered_reminder" not in st.session_state: st.session_state.last_triggered_reminder = ""
if "latest_report_insights" not in st.session_state: st.session_state.latest_report_insights = ""
if "diet_fitness_plan" not in st.session_state: st.session_state.diet_fitness_plan = ""

# ==========================================
# MEDICINE ALARM POLLING ENGINE
# ==========================================
@st.fragment(run_every=10)
def medicine_alarm_polling_engine():
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_ist_time = datetime.now(ist_timezone)
    current_time_str = current_ist_time.strftime('%H:%M')
    
    with db.get_db_connection() as conn:
        active_meds = conn.execute("SELECT medication_name, dosage, reminder_time FROM medications WHERE is_active = 1").fetchall()
        

    for med in active_meds:
        if med['reminder_time'] == current_time_str:
            reminder_key = f"{med['medication_name']}_{current_time_str}"
            
            if st.session_state.last_triggered_reminder != reminder_key:
                st.session_state.last_triggered_reminder = reminder_key
                
                st.error(f"🚨 **LIVE REMINDER ALARM:** It is exactly {current_time_str}! Take your **{med['medication_name']}** ({med['dosage']}).")
                st.toast(f"🔔 MEDICATION ALARM: {med['medication_name']} NOW!", icon="🚨")
                
                st.components.v1.html(
                    """
                    <script>
                        function triggerMedicalAlarm() {
                            var AudioContext = window.AudioContext || window.webkitAudioContext;
                            if (!AudioContext) return;
                            var audioCtx = new AudioContext();
                            var pulses = [0.0, 0.2, 0.4]; 
                            var duration = 0.12; 
                            
                            pulses.forEach(function(delay) {
                                var osc1 = audioCtx.createOscillator();
                                var osc2 = audioCtx.createOscillator();
                                var gainNode = audioCtx.createGain();
                                
                                osc1.type = 'sine'; osc1.frequency.setValueAtTime(987.77, audioCtx.currentTime + delay); 
                                osc2.type = 'sine'; osc2.frequency.setValueAtTime(1318.51, audioCtx.currentTime + delay); 
                                
                                gainNode.gain.setValueAtTime(0, audioCtx.currentTime + delay);
                                gainNode.gain.linearRampToValueAtTime(0.4, audioCtx.currentTime + delay + 0.01);
                                gainNode.gain.setValueAtTime(0.4, audioCtx.currentTime + delay + duration - 0.02);
                                gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + delay + duration);
                                
                                osc1.connect(gainNode); osc2.connect(gainNode); gainNode.connect(audioCtx.destination);
                                osc1.start(audioCtx.currentTime + delay); osc2.start(audioCtx.currentTime + delay + duration);
                                osc1.stop(audioCtx.currentTime + delay + duration + 0.05); osc2.stop(audioCtx.currentTime + delay + duration + 0.05);
                            });
                        }
                        try { triggerMedicalAlarm(); } catch(e) { window.addEventListener('click', function() { triggerMedicalAlarm(); }, { once: true }); }
                    </script>
                    """,
                    height=0,
                )

medicine_alarm_polling_engine()

# TODAY'S PRESCRIPTION GRID DISPLAY
st.markdown("### 📋 Today's Smart Prescription Grid")
conn = db.get_db_connection()
active_med_cards = conn.execute("SELECT medication_name, dosage, reminder_time FROM medications WHERE is_active = 1").fetchall()
conn.close()

if active_med_cards:
    card_cols = st.columns(min(len(active_med_cards), 4))
    for idx, med_card in enumerate(active_med_cards):
        col_target = card_cols[idx % 4]
        with col_target:
            st.markdown(f"""
                <div class="med-card">
                    <span class="med-time">⏰ {med_card['reminder_time']}</span>
                    <div class="med-title">💊 {med_card['medication_name']}</div>
                    <div class="med-meta">Dosage: <b>{med_card['dosage']}</b></div>
                    <div style="margin-top:10px;"><span class="status-badge">🟢 Active Tracking</span></div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("💡 No active schedules found. Add new logs in the panels below to view tracking cards.")

st.markdown("---")

# CORE LAYOUT SPLIT
col_dash, col_chat = st.columns([1.1, 1])

with col_dash:
    st.markdown("<h3 style='color:#F1F5F9;'>📊 Diagnostics & Utility Control Center</h3>", unsafe_allow_html=True)
    
    tab_scheduler, tab_fitness, tab_predictive, tab_diet, tab_scraper, tab_analytics = st.tabs([
        "📅 Med Scheduler", 
        "🏃 Growth Percentile", 
        "🎯 Risk Lab & PDF",
        "🥗 Smart Diet Planner",
        "🩺 Medical Topic Miner",
        "📈 Visual Journey"
    ])
    
    # 1. MEDICATION SCHEDULER PANEL
    with tab_scheduler:
        with st.expander("➕ Register New Prescription Schedule", expanded=False):
            med_name = st.text_input("Medication Name")
            dosage = st.text_input("Dosage")
            remind_time = st.time_input("Reminder Time", key="sched_time")
            if st.button("Save Entry", key="save_entry_btn"):
                if med_name and dosage:
                    conn = db.get_db_connection()
                    conn.execute("INSERT INTO medications (medication_name, dosage, reminder_time, is_active) VALUES (?, ?, ?, 1)",
                                 (med_name, dosage, remind_time.strftime("%H:%M")))
                    conn.commit(); conn.close()
                    st.success("Prescription Registered Successfully!")
                    st.rerun()

        conn = db.get_db_connection()
        meds = conn.execute("SELECT id, medication_name, dosage, reminder_time FROM medications WHERE is_active = 1").fetchall()
        conn.close()
        
        if meds:
            st.markdown("### 🗓️ Current Active Schedule")
            for m in meds:
                st.write(f"💊 **{m['medication_name']}** | {m['dosage']} | ⏰ {m['reminder_time']}")

            st.markdown("---")
            with st.expander("⚙️ Advanced Schedule Manager", expanded=True):
                med_map = {f"🗑️ {m['medication_name']} [{m['reminder_time']}]": m['id'] for m in meds}
                selected_to_delete = st.multiselect("Choose which prescriptions to remove:", options=list(med_map.keys()))
                if st.button("Delete Selected Choices", type="primary", key="del_entries_btn"):
                    if selected_to_delete:
                        target_ids = [med_map[label] for label in selected_to_delete]
                        conn = db.get_db_connection()
                        conn.executemany("UPDATE medications SET is_active = 0 WHERE id = ?", [(id_val,) for id_val in target_ids])
                        conn.commit(); conn.close()
                        st.success("Successfully deleted items!")
                        st.rerun()

    # 2. BMI & GROWTH ANALYSIS PANEL
    with tab_fitness:
        st.markdown("### 🏃 Advanced BMI & Growth Percentile Calculator")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1: age_yrs = st.number_input("Patient Age (Years)", min_value=2, max_value=120, value=22, key="fit_age")
        with col_f2: w_kg = st.number_input("Weight (kg)", min_value=5.0, max_value=250.0, value=65.0, key="fit_weight")
        with col_f3: h_cm = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, key="fit_height")
            
        if st.button("Run Detailed BMI Analysis", type="primary", key="bmi_calc_btn"):
            bmi_results = health_tools.calculate_detailed_bmi(w_kg, h_cm, age_yrs)
            st.markdown("---")
            st.info(
                f"**BMI = {bmi_results['bmi']} kg/m²** ({bmi_results['category']})\n\n"
                f"**Weight percentile:** {bmi_results['weight_percentile']} | **Height percentile:** {bmi_results['height_percentile']}\n\n"
                f"**Healthy Weight Range:** {bmi_results['healthy_weight_range']}\n\n"
                f"👉 **Action Plan:** {bmi_results['status_action']}"
            )

    # 3. METABOLIC RISK LAB & HIGH-END PDF GENERATOR
    with tab_predictive:
        st.markdown("### Predictive Metabolic Risk Assessment")
        age = st.slider("Patient Age", 1, 100, 25)
        sbp = st.slider("Systolic Blood Pressure (mmHg)", 90, 200, 120)
        glucose = st.slider("Fasting Blood Glucose (mg/dL)", 60, 250, 95)
        smoker = st.checkbox("Active Tobacco Consumer")
        
        if st.button("Execute Risk Evaluation", key="risk_eval_btn"):
            risk = health_tools.assess_cardio_risk(age, sbp, glucose, smoker)
            st.subheader(f"Risk Stratum: {risk['risk_strata']}")

            if risk['risk_strata'] in ["High", "Very High"]:
                st.error("⚠️ CRITICAL ALERT: Your vitals suggest high risk. Please consult a doctor immediately.")

            st.info(f"**Clinical Directive:** {risk['preventative_action']}")

            conn = db.get_db_connection()
            conn.execute("INSERT INTO vitals_logs (systolic_bp, glucose) VALUES (?, ?)", (sbp, glucose))
            conn.commit()
            conn.close()

        st.markdown("---")
        st.markdown("### 📄 Lab Report Parser & PDF Results")
        uploaded_file = st.file_uploader("Upload Medical Report (PDF / TXT)", type=["pdf", "txt"])
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            if uploaded_file.name.endswith(".pdf"):
                import parsers
                raw_text = parsers.extract_text_from_pdf(file_bytes)
            else:
                raw_text = file_bytes.decode("utf-8", errors="ignore")
            
            if "ERROR_SCANNED_IMAGE" in raw_text:
                st.error("⚠️ Scanned Image Layout: Clean text document load kijiye.")
            else:
                st.success("File context loaded successfully!")
                if st.button("Analyze Report with CareAI", type="primary"):
                    st.session_state.latest_report_insights = st.session_state.agent.analyze_medical_report(str(raw_text))
                    st.rerun()

        if st.session_state.latest_report_insights:
            st.markdown("#### CareAI Generated Diagnostics View")
            st.info(st.session_state.latest_report_insights)
            
            # bytearray ko strict bytes me cast karein
            pdf_data = bytes(health_tools.generate_pdf_bytes(st.session_state.latest_report_insights))

            st.download_button(
                label="📥 Download Hospital-Level Diagnostic PDF Report",
                data=pdf_data,
                file_name="Clinical_Report.pdf",
                mime="application/pdf"
            )

    # 4. SMART DIET PLANNER PANEL
    with tab_diet:
        st.markdown("### 🥗 AI Personalized Diet & Wellness Planner")
        health_goal = st.selectbox("Apna Primary Fitness Goal Chunein:", ["Weight Loss Management", "Muscle Gain & Fitness", "Diabetes Sugar Control", "Heart Health & BP Control"])
        activity_level = st.selectbox("Current Daily Physical Activity Kitna Hai?", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        diet_pref = st.radio("Dietary Preference:", ["Vegetarian 🥦", "Non-Vegetarian 🍗", "Vegan 🌱"], horizontal=True)
        
        if st.button("Generate Custom Plan", type="primary"):
            with st.spinner("Generating your custom diet plan..."):
                try:
                    prompt = f"Create a {diet_pref} diet plan for {health_goal} with {activity_level} activity level."
                    
                    response = st.session_state.agent.invoke(prompt)
                    
                    if isinstance(response, dict):
                        output_text = response.get("output", str(response))
                    else:
                        output_text = str(response)
                        
                    if output_text:
                        st.success("Here is your AI Diet Plan:")
                        st.write(output_text)
                    else:
                        st.warning("No response generated. Please try again.")
                        
                except Exception as e:
                    st.error(f"Error generating plan: {str(e)}")

    # 5. FAST INTERACTIVE CLINICAL INSIGHT MINER PANEL
    with tab_scraper:
        st.markdown("### 🩺 Clinical Insight Miner Engine")
        st.caption("Kisi bhi medical topic ya disease condition ko search karein.")
        
        topic_input = st.text_input("Enter Medical Condition or Lab Test Query", placeholder="e.g., Hypertension Management", key="web_scratch_topic")
        
        if st.button("Generate Complete Health Sheet", type="primary", key="trigger_scraper_btn"):
            if not topic_input.strip():
                st.warning("Please enter a valid topic name.")
            else:
                with st.spinner("Processing rapid clinical analysis..."):
                    insights = health_tools.scrape_web_questions(topic_input)
                    
                    if "error" in insights:
                        st.error(insights["error"])
                    elif "raw_payload" in insights:
                        st.markdown(f"---")
                        st.subheader(f"🔎 Results for: {topic_input}")
                        # CSS flex layout ke liye container
                        st.markdown(f"""
                            <div style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 15px; border-left: 5px solid #38BDF8; color: #E2E8F0;">
                                {insights['raw_payload']}
                            </div>
                        """, unsafe_allow_html=True)

    # 6. PROGRESS GRAPH CHANNEL PANEL
    with tab_analytics:
        st.markdown("### 📈 Live Visual Health Journey Tracker")
        conn = db.get_db_connection()
        # Step 2: Data Fetching logic
        logs = conn.execute("SELECT log_date, systolic_bp, glucose FROM vitals_logs ORDER BY id ASC LIMIT 15").fetchall()
        conn.close()
    
        if logs:
            chart_data = pd.DataFrame(logs, columns=['Date', 'BP', 'Sugar'])
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5.5), sharex=True)
            fig.patch.set_facecolor('#0E1117') 
            
            ax1.set_facecolor('#1E2330')
            ax1.plot(chart_data['Date'], chart_data['BP'], color='#38BDF8', marker='o', label='BP')
            ax1.set_ylabel('BP (mmHg)', color='#FFFFFF')
            ax1.tick_params(colors='#FFFFFF')
            
            ax2.set_facecolor('#1E2330')
            ax2.plot(chart_data['Date'], chart_data['Sugar'], color='#F59E0B', marker='s', label='Sugar')
            ax2.set_ylabel('Sugar (mg/dL)', color='#FFFFFF')
            ax2.tick_params(colors='#FFFFFF')
            
            st.pyplot(fig)
        else:
            st.info("No logs found. Add vitals in Risk Lab to see the chart.")

        try:
            import matplotlib.pyplot as plt
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5.5), sharex=True)
            fig.patch.set_facecolor('#0E1117') 
            
            ax1.set_facecolor('#1E2330')
            ax1.plot(chart_data['Date'], chart_data['BP'], color='#38BDF8', marker='o', linewidth=2.5, label='Aapka BP')
            ax1.axhline(130, color='#EF4444', linestyle='--')
            ax1.set_ylabel('BP (mmHg)', color='#FFFFFF')
            ax1.tick_params(colors='#FFFFFF', labelsize=8)
            ax1.grid(True, color='#2D3748', alpha=0.5)
            
            ax2.set_facecolor('#1E2330')
            ax2.plot(chart_data['Date'], chart_data['Sugar'], color='#F59E0B', marker='s', linewidth=2.5, label='Aapka Sugar')
            ax2.axhline(110, color='#EF4444', linestyle='--')
            ax2.set_ylabel('Sugar (mg/dL)', color='#FFFFFF')
            ax2.tick_params(colors='#FFFFFF', labelsize=8)
            ax2.grid(True, color='#2D3748', alpha=0.5)
            
            fig.tight_layout()
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Matplotlib setup note: {str(e)}")

# ==========================================
# RIGHT COLUMN: AI CLINICAL ENGINE CHAT MODULE
# ==========================================
with col_chat:
    st.markdown("<h3 style='color:#F1F5F9;'>💬 Live Clinical AI Agent Chat</h3>", unsafe_allow_html=True)
    for role, text in st.session_state.chat_history:
        with st.chat_message(role): st.write(text)
            
    if user_query := st.chat_input("Query clinical definitions or insights..."):
        st.session_state.chat_history.append(("user", user_query)) # Pehle append karo
        
        with st.chat_message("user"): st.write(user_query)
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                # Sirf last 4 messages bhejo context ke liye
                context_history = st.session_state.chat_history[-4:]
                ai_response = st.session_state.agent.respond(context_history, user_query)
                st.write(ai_response)
        
        st.session_state.chat_history.append(("assistant", ai_response))
        st.rerun()