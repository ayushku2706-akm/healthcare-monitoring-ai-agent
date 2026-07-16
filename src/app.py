import streamlit as st
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# ENVIRONMENT & PATH CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(dotenv_path=ENV_PATH)

from agent import HealthAgent
import database as db
import tools as health_tools

db.init_db()

# INITIALIZE INTERFACE
st.set_page_config(page_title="CareAI - Personal Health Companion", layout="wide")
st.title("🏥 CareAI: Predictive Health Agent & Monitoring Engine")

# Initialize persistent memory storage objects safely
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = HealthAgent()
if "last_triggered_reminder" not in st.session_state:
    st.session_state.last_triggered_reminder = ""
if "latest_report_insights" not in st.session_state:
    st.session_state.latest_report_insights = ""

# ==========================================
# SILENT ALARM REMINDER PIPELINE (NO FORCED RE-RUNS)
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
            st.error(f"🚨 **LIVE REMINDER ALARM:** It is exactly {current_time_str}! Take your **{med['medication_name']}** ({med['dosage']}).")

# CORE LAYOUT SPLIT
col_dash, col_chat = st.columns([1.1, 1])

# ==========================================
# LEFT COLUMN: INTERACTIVE TOOLS & PROGRESSION TRACKING
# ==========================================
with col_dash:
    st.subheader("📊 Advanced Patient Health Tools")
    
    tab_scheduler, tab_fitness, tab_predictive, tab_analytics = st.tabs([
        "📅 Med Scheduler", 
        "🏃 Fitness & Nutrition", 
        "🎯 Risk Diagnostics & Logs",
        "📈 Journey Analytics"
    ])
    
    with tab_scheduler:
        with st.expander("💊 Register New Prescription Schedule", expanded=False):
            med_name = st.text_input("Medication Name")
            dosage = st.text_input("Dosage")
            remind_time = st.time_input("Reminder Time", key="sched_time")
            if st.button("Save Entry"):
                if med_name and dosage:
                    conn = db.get_db_connection()
                    conn.execute("INSERT INTO medications (medication_name, dosage, reminder_time, is_active) VALUES (?, ?, ?, 1)",
                                 (med_name, dosage, remind_time.strftime("%H:%M")))
                    conn.commit(); conn.close()
                    st.success("Prescription Registered Successfully!")
                    st.rerun()

        # Display active trackers
        conn = db.get_db_connection()
        meds = conn.execute("SELECT id, medication_name, dosage, reminder_time FROM medications WHERE is_active = 1").fetchall()
        conn.close()

        st.markdown("### Active Tracked Prescriptions")
        if meds:
            for m in meds:
                st.info(f"👉 **{m['medication_name']}** ({m['dosage']}) at `{m['reminder_time']}`")
        else:
            st.caption("No active medication items scheduled for tracking yet.")

        # Advanced Bulk Actions
        if meds:
            st.markdown("---")
            with st.expander("⚙️ Advanced Schedule Manager (Bulk Options)", expanded=True):
                med_map = {f"🗑️ {m['medication_name']} [{m['reminder_time']}]": m['id'] for m in meds}
                selected_to_delete = st.multiselect("Choose which prescriptions to remove:", options=list(med_map.keys()))
                
                if st.button("Delete Selected Choices", type="primary"):
                    if selected_to_delete:
                        target_ids = [med_map[label] for label in selected_to_delete]
                        conn = db.get_db_connection()
                        conn.executemany("UPDATE medications SET is_active = 0 WHERE id = ?", [(id_val,) for id_val in target_ids])
                        conn.commit(); conn.close()
                        st.success("Successfully deleted selected items!")
                        st.rerun()

    with tab_fitness:
        st.markdown("### 🏃 Advanced BMI & Growth Percentile Calculator")
        
        # User Inputs including Age
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            age_yrs = st.number_input("Patient Age (Years)", min_value=2, max_value=120, value=15, key="fit_age")
        with col_f2:
            w_kg = st.number_input("Weight (kg)", min_value=5.0, max_value=250.0, value=45.0, key="fit_weight")
        with col_f3:
            h_cm = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=160.0, key="fit_height")
            
        if st.button("Run Detailed BMI Analysis", type="primary"):
            # Call our newly created detailed calculations tool
            bmi_results = health_tools.calculate_detailed_bmi(w_kg, h_cm, age_yrs)
            
            # Print output exactly matching your desired layout
            st.markdown("---")
            st.markdown("#### 📊 **Analysis Report Results:**")
            
            # Bold Metric Output Layout
            st.info(
                f"**BMI = {bmi_results['bmi']} kg/m²** ({bmi_results['category']})\n\n"
                f"**Weight-for-age percentile:** {bmi_results['weight_percentile']}\n\n"
                f"**Height-for-age percentile:** {bmi_results['height_percentile']}\n\n"
                f"**Healthy BMI range:** {bmi_results['healthy_bmi_range']}\n\n"
                f"**Healthy weight for the height:** {bmi_results['healthy_weight_range']}\n\n"
                f"👉 **Action Plan:** {bmi_results['status_action']}\n\n"
                f"**Ponderal Index:** {bmi_results['ponderal_index']}"
            )


    with tab_predictive:
        st.markdown("### Predictive Metabolic Risk Assessment")
        age = st.slider("Patient Age", 1, 100, 25)
        sbp = st.slider("Systolic Blood Pressure (mmHg)", 90, 200, 120)
        glucose = st.slider("Fasting Blood Glucose (mg/dL)", 60, 250, 95)
        smoker = st.checkbox("Active Tobacco Consumer")
        
        if st.button("Execute Risk Evaluation"):
            risk = health_tools.assess_cardio_risk(age, sbp, glucose, smoker)
            st.subheader(f"Risk Stratum: {risk['risk_strata']}")
            st.info(f"**Clinical Prevention Directive:** {risk['preventative_action']}")
            
            # Save metrics into database automatically for dynamic charting
            conn = db.get_db_connection()
            conn.execute("INSERT INTO vitals_logs (systolic_bp, glucose) VALUES (?, ?)", (sbp, glucose))
            conn.commit()
            conn.close()
            st.toast("📊 Vitals successfully saved to database timeline logs!", icon="💾")

        st.markdown("---")
        st.markdown("### 📄 Automated Clinical Report Parser")
        
        uploaded_file = st.file_uploader("Upload Medical Report or Lab Sheet (PDF / TXT)", type=["pdf", "txt"], key="report_file_uploader")
        
        if uploaded_file is not None:
            with st.spinner("Reading clinical document structure..."):
                file_bytes = uploaded_file.read()
                
                # Check file type extension and parse raw string contents
                if uploaded_file.name.endswith(".pdf"):
                    import parsers
                    raw_text = parsers.extract_text_from_pdf(file_bytes)
                else:
                    raw_text = file_bytes.decode("utf-8", errors="ignore")
            
            # Handle empty content or non-OCR scanned images safely
            if "ERROR_SCANNED_IMAGE" in raw_text:
                st.error("⚠️ **Scanned Document Detected:** Yeh PDF ek scanned photo ya image lag rahi hai jisme readable digital text layer nahi hai. Please ek clear typed text PDF file ya `.txt` document upload kijiye.")
            else:
                st.success("File context successfully loaded into application memory!")
                
                # Action button to trigger the Gemini parsing pipeline safely passing the context variable
                if st.button("Analyze Report with CareAI", type="primary", key="trigger_analysis_btn"):
                    if raw_text.strip():
                        with st.spinner("Extracting parameters and running diagnostics..."):
                            # Explicit string context passing
                            report_insights = st.session_state.agent.analyze_medical_report(str(raw_text))
                            st.session_state.latest_report_insights = report_insights
                            st.rerun()
                    else:
                        st.error("⚠️ Failed to read data from document. Please ensure the document contains extractable text elements.")

        # Display results if present in session state
        if st.session_state.latest_report_insights:
            st.markdown("#### 🔬 CareAI Structured Extraction Results:")
            st.info(st.session_state.latest_report_insights)

            # GENERATE AND DOWNLOAD PDF REPORT
            st.markdown("---")
            st.markdown("### 📥 Export Clinical Diagnostics")
            try:
                import reports
                pdf_data = reports.generate_health_report_pdf(
                    patient_id="PT-9942",
                    bmi_val=24.2,
                    bmi_cat="Normal Balance",
                    risk_strata="Comprehensive Baseline Review",
                    clinical_insights=st.session_state.latest_report_insights
                )
                
                st.download_button(
                    label="📥 Download Official Clinical Report (PDF)",
                    data=pdf_data,
                    file_name=f"CareAI_Health_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Could not generate PDF export engine: {str(e)}")

    # DYNAMIC CHART INTEGRATION: Pulls data directly from vitals_logs table
    with tab_analytics:
        st.markdown("### 📈 Historical Vitals Tracking Dashboard")
        
        # Pull logs dynamically from the database
        conn = db.get_db_connection()
        logs = conn.execute("SELECT log_date, systolic_bp, glucose FROM vitals_logs ORDER BY id ASC LIMIT 15").fetchall()
        conn.close()
        
        if len(logs) > 0:
            chart_data = pd.DataFrame([{
                'Date': datetime.strptime(log['log_date'], "%Y-%m-%d").strftime("%d %b") if '-' in log['log_date'] else log['log_date'],
                'Systolic BP': log['systolic_bp'],
                'Glucose (mg/dL)': log['glucose']
            } for log in logs])
        else:
            # Fallback/Initial Baseline Mock Data if database log is empty
            chart_data = pd.DataFrame({
                'Date': ["01 Jul", "02 Jul", "03 Jul", "04 Jul", "05 Jul", "06 Jul"],
                'Systolic BP': [120, 122, 130, 128, 125, 121],
                'Glucose (mg/dL)': [95, 98, 110, 105, 101, 96]
            })
            st.info("💡 **Getting Started:** Currently displaying baseline standard trends. Log your vitals in the **'Risk Diagnostics & Logs'** tab to generate your own personalized trend curves!")

        try:
            import matplotlib.pyplot as plt
            
            fig, ax1 = plt.subplots(figsize=(7, 3.5))
            fig.patch.set_facecolor('#0E1117') 
            ax1.set_facecolor('#1E2330')
            
            color = '#2B6CB0' 
            ax1.set_xlabel('Timeline Logs', color='#FFFFFF', fontsize=9)
            ax1.set_ylabel('Systolic Blood Pressure (mmHg)', color=color, fontsize=9)
            ax1.plot(chart_data['Date'], chart_data['Systolic BP'], color=color, marker='o', linewidth=2, label='Systolic BP')
            ax1.tick_params(axis='y', labelcolor=color, colors='#FFFFFF')
            ax1.tick_params(axis='x', colors='#FFFFFF')
            ax1.grid(True, color='#2D3748', linestyle=':', alpha=0.5)
            
            ax2 = ax1.twinx()
            color = '#DD6B20' 
            ax2.set_ylabel('Fasting Glucose (mg/dL)', color=color, fontsize=9)
            ax2.plot(chart_data['Date'], chart_data['Glucose (mg/dL)'], color=color, marker='s', linewidth=2, linestyle='--', label='Glucose')
            ax2.tick_params(axis='y', labelcolor=color, colors='#FFFFFF')
            
            plt.title("Patient Longitudinal Health Progression Chart", color='#FFFFFF', fontsize=11, pad=10)
            fig.tight_layout()
            
            st.pyplot(fig)
            st.caption("Figure 1.0: Live synchronized timeline tracking daily blood pressure variants paired with blood sugar fluctuations.")
        except Exception as e:
            st.warning(f"Matplotlib visual render is still loading. Details: {str(e)}")

# ==========================================
# RIGHT COLUMN: AI COMPANION (STABLE STREAMING LAYOUT)
# ==========================================
with col_chat:
    st.subheader("💬 AI Health Companion Chat")
    
    # Render all existing historical dialogue sequences instantly
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(text)
            
    # Process active incoming user prompts
    if user_query := st.chat_input("Query clinical definitions or symptoms...", key="care_chat_input"):
        with st.chat_message("user"):
            st.write(user_query)
        
        with st.chat_message("assistant"):
            with st.spinner("Generating clinical guidance..."):
                ai_response = st.session_state.agent.respond(st.session_state.chat_history, user_query)
                st.write(ai_response)
                
        st.session_state.chat_history.append(("user", user_query))
        st.session_state.chat_history.append(("assistant", ai_response))
        st.rerun()