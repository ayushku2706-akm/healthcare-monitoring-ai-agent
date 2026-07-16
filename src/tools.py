import pandas as pd
import numpy as np
import math

def calculate_detailed_bmi(weight_kg: float, height_cm: float, age_years: int) -> dict:
    """
    Calculates detailed BMI metrics including Ponderal Index, target weight, 
    healthy ranges, and custom percentile estimates based on age.
    """
    try:
        height_m = height_cm / 100.0
        bmi = round(weight_kg / (height_m ** 2), 1)
        
        # Ponderal Index Formula: kg / m^3
        ponderal_index = round(weight_kg / (height_m ** 3), 1)
        
        # Standard healthy BMI range
        healthy_bmi_min = 19.1
        healthy_bmi_max = 27.0
        
        # Calculate healthy weight range for this specific height
        healthy_weight_min = round(healthy_bmi_min * (height_m ** 2), 1)
        healthy_weight_max = round(healthy_bmi_max * (height_m ** 2), 1)
        
        # Determine Status and Weight Action Needed
        weight_to_change = 0.0
        status_msg = ""
        
        if bmi < healthy_bmi_min:
            category = "Underweight"
            weight_to_change = round(healthy_weight_min - weight_kg, 1)
            status_msg = f"Gain {weight_to_change} kg to reach a BMI of {healthy_bmi_min} kg/m²."
        elif bmi > healthy_bmi_max:
            category = "Overweight"
            weight_to_change = round(weight_kg - healthy_weight_max, 1)
            status_msg = f"Lose {weight_to_change} kg to reach a BMI of {healthy_bmi_max} kg/m²."
        else:
            category = "Normal / Healthy Weight"
            status_msg = "Aapka weight bilkul healthy range mein hai! Maintain physically active lifestyle."

        # Custom Percentile Logic (Simulated standard growth curve offsets based on age, height, and weight)
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


# Backwards compatibility wrapper for existing functions if any
def calculate_bmi_metrics(weight_kg: float, height_cm: float) -> dict:
    """Fallback standard calculator for legacy components."""
    try:
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            cat = "Underweight"
            risk = "Minimal (Risk of nutritional deficiency)"
        elif bmi < 25:
            cat = "Normal Weight"
            risk = "Very Low Risk Profile"
        elif bmi < 30:
            cat = "Overweight"
            risk = "Elevated Risk for Cardiovascular strain"
        else:
            cat = "Obese"
            risk = "High Risk for Type-2 Diabetes and Hypertension"
            
        return {
            "bmi": round(bmi, 2),
            "category": cat,
            "health_risk_profile": risk
        }
    except ZeroDivisionError:
        return {"error": "Height must be greater than zero."}


def assess_cardio_risk(age: int, systolic_bp: int, fasting_glucose: int, smoker: bool) -> dict:
    """Calculates a predictive health risk score based on metabolic variables."""
    score = 0
    # Risk Factor Aggregation
    if age > 45: score += 2
    if systolic_bp >= 130: score += 3  # Hypertension line
    if fasting_glucose >= 100: score += 3  # Pre-diabetes or diabetes line
    if smoker: score += 2
    
    # Map score to risk strata
    if score <= 2:
        strata = "Low Risk"
        recommendation = "Maintain regular physical activity and optimal standard dietary practices."
    elif score <= 5:
        strata = "Moderate Risk"
        recommendation = "Schedule regular metabolic screenings. Limit sodium and refined glycemic index foods."
    else:
        strata = "High Risk"
        recommendation = "Clinical consult recommended. Implement active cardiovascular and glucose tracking."
        
    return {
        "risk_score": score,
        "risk_strata": strata,
        "preventative_action": recommendation
    }


def analyze_health_trends(csv_path: str) -> dict:
    """Uses Pandas to extract predictive pattern recognition insights from health logs."""
    try:
        df = pd.read_csv(csv_path)
        # Verify columns exist
        if "Glucose_Level" not in df.columns:
            return {"error": "Invalid log format. Missing metric column."}
            
        avg_glucose = df["Glucose_Level"].mean()
        max_glucose = df["Glucose_Level"].max()
        
        # Simple pattern recognition sequence
        spikes = len(df[df["Glucose_Level"] > 130])
        
        if avg_glucose > 125:
            condition_trend = "Consistent Hyperglycemic Pattern Detected"
        elif spikes >= 2:
            condition_trend = "Unstable Fluctuations Post-Prandial"
        else:
            condition_trend = "Stable Glycemic Control Maintained"
            
        return {
            "historical_average": round(avg_glucose, 2),
            "peak_recorded_value": int(max_glucose),
            "detected_trend_pattern": condition_trend,
            "total_anomalous_spikes": spikes
        }
    except Exception as e:
        return {"error": f"Failed to parse health records: {str(e)}"}