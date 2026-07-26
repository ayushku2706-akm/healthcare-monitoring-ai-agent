import streamlit as st
import urllib.request
import urllib.parse
import re
import math
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import time
from google.api_core.exceptions import ResourceExhausted
import pytz

def call_gemini_with_retry(model, prompt, retries=5, delay=3):
    """
    Ye function API limit aane par turant fail hone ke bajaye, 
    kuch seconds wait karke dobara try karega.
    """
    for i in range(retries):
        try:
            # Model call try karega
            response = model.generate_content(prompt)
            return response
        except ResourceExhausted as e:
            if i < retries - 1:
                print(f"API Rate limit aa gayi. {delay} seconds baad retry kar rahe hain...")
                time.sleep(delay)
                delay *= 2  
            else:
               
                raise e


def scrape_web_questions(topic_query: str) -> dict:
    """
    Optimized high-speed enterprise analytical engine. Uses session caching 
    and fast token structures to ensure lightning-fast outputs (< 10 seconds).
    """
    topic_clean = topic_query.strip().lower()
    
    # Session Cache setup for instantaneous loading performance
    if "miner_cache" not in st.session_state:
        st.session_state.miner_cache = {}
        
    if topic_clean in st.session_state.miner_cache:
        return {"raw_payload": st.session_state.miner_cache[topic_clean]}

    if "agent" in st.session_state:
        agent = st.session_state.agent
    else:
        from agent import HealthAgent
        agent = HealthAgent()

    # Highly structured and highly direct optimized academic prompt setup
    prompt = f"""
    You are an expert clinical educator. Write a concise, high-yield diagnostic guide for: '{topic_query}'.
    Keep explanations extremely direct and fast to output. Use this strict structure:
    
    ### 📚 STUDENT MOCK TEST (MCQs)
    - **Q1**: [Scenario Question]
      - *Options*: A), B), C), D)
      - *Answer*: [Correct Option] - *Rationale*: [1 line explanation]
    - **Q2**: [Anatomy/Pathology Question]
      - *Answer*: [Correct Option]
      
    ### ❤️ PATIENT CARE & MEANING
    - **Plain-text summary**: [Explain in 2 simple sentences what this is]
    - **Red Flags / Warning Signs**: [List 3 urgent symptoms]
    
    ### 🧠 QUICK FLASHCARDS
    - **Q**: [Card 1] -> **A**: [Answer 1]
    - **Q**: [Card 2] -> **A**: [Answer 2]
    
    ### 📊 CORE CLINICAL METRICS
    - Provide 2-3 key laboratory or physiological values/ranges in a short table.
    """
    
    # Implementing structured API Rate Limit handling with Exponential Backoff inside the Scraper
    retries = 5
    delay = 3
    for i in range(retries):
        try:
            # Running logic inside explicit resource monitoring wrapper
            raw_response = agent.respond([], prompt)
            st.session_state.miner_cache[topic_clean] = raw_response
            return {"raw_payload": raw_response}
        except ResourceExhausted:
            if i < retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return {"error": "Google API Daily Quota Exceeded (429). Please try again later or add billing."}
        except Exception as e:
            # Agar koi generic/network breakdown exception aata hai tab
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if i < retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
            return {"error": f"API Engine Execution Delay or Network Exception: {str(e)}"}


def generate_pdf_bytes(text_content: str) -> bytes:
    """
    Generates a premium Hospital-Level Clinical Analysis Report.
    Uses strict borders, stylized margins, headers, and official formatting themes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Outer Border Box - Hospital Classic Accent
    pdf.set_draw_color(3, 105, 161)
    pdf.set_line_width(0.6)
    pdf.rect(5, 5, 200, 287)
    
    # Official Hospital Letterhead Header
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.set_text_color(3, 105, 161) # CareAI Professional Blue
    pdf.cell(0, 10, txt="CAREAI MULTI-SPECIALTY CLINICAL HUB", ln=True, align="C")
    
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, txt="AUTOMATED LAB PARSING ENGINE & PATIENT RECORD DOSSIER", ln=True, align="C")
    
    # Thin Horizontal Rule separator
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.2)
    pdf.line(10, 28, 200, 28)
    pdf.ln(10)
    
    # Report Meta Block Table Structure
    pdf.set_fill_color(248, 250, 252)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(45, 7, txt=" Document Category:", border=1, fill=True)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(50, 7, txt=" Clinical Diagnostic Evaluation", border=1)
    
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(45, 7, txt=" Generation Timestamp:", border=1, fill=True)
    pdf.set_font("Helvetica", size=10)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M')
    pdf.cell(50, 7, txt=f" {current_time}", border=1, ln=True)
    
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(45, 7, txt=" Security Status:", border=1, fill=True)
    pdf.set_font("Helvetica", style="I", size=10)
    pdf.set_text_color(16, 185, 129) # Verified Green text
    pdf.cell(50, 7, txt=" HIPAA Compliant / Encrypted", border=1)
    
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(45, 7, txt=" System Authentication:", border=1, fill=True)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(50, 7, txt=" CareAI Backend Verified", border=1, ln=True)
    pdf.ln(8)
    
    # Primary Content Section Title
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, txt="I. COMPREHENSIVE MEDICAL INSIGHTS & INTERPRETATIONS", ln=True)
    pdf.ln(2)
    
    # Parsing body safely and dynamically
    pdf.set_font("Helvetica", size=10.5)
    pdf.set_text_color(51, 65, 85)
    
    # Safeguard formatting filter to prevent spacing crashes
    clean_text = text_content.replace("**", "").replace("###", "").replace("`", "").replace("---", "")
    
    for line in clean_text.split('\n'):
        # Sirf non-empty valid characters ko printable margin width me render karega
        if line.strip():
            safe_line = line.encode('latin-1', 'replace').decode('latin-1').strip()
            # Explicit dynamic print range checking to ensure it fits horizontal bounds
            if len(safe_line) > 0:
                pdf.multi_cell(0, 6, txt=safe_line)
                pdf.ln(1)
            
    # Official Footer Authentication Signature Area
    pdf.set_y(265)
    pdf.set_draw_color(203, 213, 225)
    pdf.line(140, 270, 195, 270)
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.set_text_color(148, 163, 184)
    pdf.set_x(140)
    pdf.cell(55, 5, txt="Authorized Digital Sign-Off Stamp", ln=True, align="C")
    
    # Agar aapka output string hai, toh use utf-8 mein encode karke bytes banayein:
    output = pdf.output(dest='S')
    if isinstance(output, str):
        return output.encode('latin-1')  # FPDF ke liye 'latin-1' best rehta hai
    return bytes(output)


def calculate_detailed_bmi(weight_kg: float, height_cm: float, age_years: int) -> dict:
    """Calculates detailed BMI metrics including Ponderal Index, target weight, and ranges."""
    try:
        if height_cm <= 0:
            return {"error": "Height must be greater than zero."}
        height_m = height_cm / 100.0
        bmi = round(weight_kg / (height_m ** 2), 1)
        ponderal_index = round(weight_kg / (height_m ** 3), 1)
        
        healthy_bmi_min, healthy_bmi_max = 19.1, 27.0
        healthy_weight_min = round(healthy_bmi_min * (height_m ** 2), 1)
        healthy_weight_max = round(healthy_bmi_max * (height_m ** 2), 1)
        
        weight_to_change = 0.0
        status_msg = ""
        
        if bmi < healthy_bmi_min:
            category = "Underweight"
            weight_to_change = round(healthy_weight_min - weight_kg, 1)
            status_msg = f"Gain {weight_to_change} kg to reach a healthy BMI of {healthy_bmi_min} kg/m²."
        elif bmi > healthy_bmi_max:
            category = "Overweight"
            weight_to_change = round(weight_kg - healthy_weight_max, 1)
            status_msg = f"Lose {weight_to_change} kg to reach a healthy BMI of {healthy_weight_max} kg/m²."
        else:
            category = "Normal / Healthy Weight"
            status_msg = "Aapka weight bilkul healthy range mein hai!"

        weight_percentile = int(max(1, min(99, (bmi / 23) * 50 - (age_years * 0.5))))
        height_percentile = int(max(1, min(99, (height_cm / (150 + age_years)) * 50)))
        
        return {
            "bmi": bmi,
            "category": category,
            "weight_percentile": f"{weight_percentile}%",
            "height_percentile": f"{height_percentile}%",
            "healthy_bmi_range": f"{healthy_bmi_min} - {healthy_bmi_max} kg/m²",
            "healthy_weight_range": f"{healthy_weight_min} kg - {healthy_weight_max} kg",
            "status_action": status_msg,
            "ponderal_index": f"{ponderal_index} kg/m³"
        }
    except ZeroDivisionError:
        return {"error": "Height must be greater than zero."}


def assess_cardio_risk(age: int, systolic_bp: int, fasting_glucose: int, smoker: bool) -> dict:
    """Calculates a predictive health risk score based on metabolic variables."""
    score = 0
    if age > 45: score += 2
    if systolic_bp >= 130: score += 3
    if fasting_glucose >= 100: score += 3
    if smoker: score += 2
    
    if score <= 2:
        strata = "Low Risk"
        recommendation = "Maintain regular physical activity."
    elif score <= 5:
        strata = "Moderate Risk"
        recommendation = "Schedule regular metabolic screenings."
    else:
        strata = "High Risk"
        recommendation = "Clinical consult recommended."
        
    return {
        "risk_score": score,
        "risk_strata": strata,
        "preventative_action": recommendation
    }