import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Ensure pathing reads environment variables smoothly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(dotenv_path=ENV_PATH)

class HealthAgent:
    def __init__(self):
        primary_model = "gemini-2.5-flash"
        fallback_model = "gemini-2.0-flash"
        
        # Pull API key securely
        api_key = os.getenv("GOOGLE_API_KEY")
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=primary_model,
                temperature=0.3,
                google_api_key=api_key
            )
        except Exception:
            self.llm = ChatGoogleGenerativeAI(
                model=fallback_model,
                temperature=0.3,
                google_api_key=api_key
            )
        
        self.system_prompt = SystemMessage(content=(
            "You are CareAI, an advanced clinical intelligence and personal health companion. "
            "Your capabilities include providing detailed educational insights on medical research, "
            "symptom breakdowns, fitness planning, and medication tracking. "
            "\n\n"
            "CRITICAL MEDICAL GUARDRAIL: You are an AI, not a licensed medical professional. For every single response "
            "covering symptoms, pathology, or drug information, you MUST provide comprehensive information clearly, "
            "but conclude with a mandatory, prominent, professional disclaimer advising the user to consult a physician."
        ))

    def respond(self, chat_history, user_message):
        """
        Processes conversation safely with robust error handling layers.
        """
        # Defensive Check: Verify if API key exists before making network request
        if not os.getenv("GOOGLE_API_KEY"):
            return (
                "❌ **Configuration Error Detected:** Your `.env` file does not contain a valid `GOOGLE_API_KEY`. "
                "Please make sure your API key is pasted correctly inside your environment file."
            )

        messages = [self.system_prompt]
        
        # Map history logs securely
        for role, text in chat_history:
            if role == "user":
                messages.append(HumanMessage(content=text))
            elif role == "assistant":
                messages.append(AIMessage(content=text))
                
        messages.append(HumanMessage(content=user_message))
        
        # CRITICAL LAYER: Catch API crashes gracefully instead of breaking the app
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            # Return the exact error to the UI chat stream instead of crashing out
            return (
                f"⚠️ **AI Companion Communication Failure:** Something went wrong while connecting to the Gemini API servers. "
                f"\n\n**Technical Details:** `{str(e)}`"
            )
        
    def analyze_medical_report(self, report_text: str) -> str:
        """
        Parses raw text from medical reports and structures clinical insights 
        in conversational Hinglish written in English script.
        """
        if not os.getenv("GOOGLE_API_KEY"):
            return "❌ **Configuration Error:** Google API Key missing."

        prompt = (
            f"You are an empathetic, expert clinical AI assistant. Analyze the following raw medical report text "
            f"and provide a highly professional, structured doctor-like analysis. "
            f"CRITICAL: The response must be written in conversational HINGLISH (Hindi + English) using the English alphabet (Latin script). "
            f"Do NOT use pure/heavy Hindi words like 'vyavasthit', 'pradaan', 'antargat', 'khaan-paan', 'parhez'. "
            f"Instead, use normal day-to-day spoken language like 'Report summary', 'Blood sugar thoda high hai', 'Diet control', 'Regular exercise'.\n\n"
            f"Please structure your response with these exact headings:\n"
            f"1. **📋 Patient Profile Summary** (Extract Name, Age, Gender, Report Date, Referring Doctor if present)\n"
            f"2. **📊 Lab Vitals Analysis (Key Findings)** (Highlight abnormal metrics like high Sugar, Cholesterol, or BP with their status and normal ranges)\n"
            f"3. **🎯 Risk Assessment (Health Risk Analysis)** (Explain what these high values mean for the patient's future health based on their age in simple Hinglish)\n"
            f"4. **🏃 Actionable Solutions & Recommendations (Prevention Plan)** (Give clear diet, exercise, and lifestyle advice to normalize their levels)\n\n"
            f"Report Text:\n{report_text}\n\n"
            f"At the very end, conclude with this exact bold warning in Hinglish:\n"
            f"'⚠️ **MANDATORY CLINICAL DISCLAIMER:** Yeh analysis AI-generated hai aur sirf educational purposes ke liye hai. "
            f"Yeh kisi professional doctor ki jagah nahi le sakta. Koi bhi lifestyle change ya medicine shuru karne se pehle "
            f"apne primary doctor ya qualified medical professional se consult zaroor karein.'"
        )

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"⚠️ **Failed to analyze report document:** {str(e)}"