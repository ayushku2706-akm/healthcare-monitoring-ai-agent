import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from fpdf import FPDF

load_dotenv()

# Ensure pathing reads environment variables smoothly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(dotenv_path=ENV_PATH)

class HealthAgent:
    def __init__(self):
        primary_model = "gemini-2.5-flash"
        fallback_model = "gemini-2.0-flash"
        
        # Pull API key securely
        api_key = (
            st.secrets.get("GOOGLE_API_KEY")
            if "GOOGLE_API_KEY" in st.secrets
            else os.getenv("GOOGLE_API_KEY")
        )

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
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

    def generate_pdf_report(self, text_content, filename="Clinical_Report.pdf"):
        # Unwanted symbols remove karein
        clean_text = text_content.replace("?", "").replace("--", "").replace("**", "")
        
        pdf = FPDF()
        pdf.add_page()
        
        for line in clean_text.split('\n'):
            if line.strip().startswith("#"):
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt=line.replace("#", "").strip(), ln=True)
            elif line.strip(): # Khali line ignore karne ke liye
                pdf.set_font("Arial", '', 12)
                pdf.multi_cell(0, 10, txt=line.strip())
        
        pdf.output(filename)
        return filename

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
        if not os.getenv("GOOGLE_API_KEY"):
            return "❌ Configuration Error: Google API Key missing."

        prompt = (
            f"You are a Clinical AI. Analyze the report and provide a clean, professional report.\n"
            f"STRICT FORMATTING RULES:\n"
            f"1. Do NOT use '?', '--', or any special symbols for headings or lists.\n"
            f"2. Use only Markdown for structure: Use # for main titles and ** for bold text.\n"
            f"3. Use standard bullet points (-) for lists.\n"
            f"4. Keep the Hinglish conversational but professional.\n\n"
            f"Structure:\n"
            f"# Patient Profile Summary\n(Name, Age, Gender, etc.)\n\n"
            f"# Lab Vitals Analysis\n(Results in clean bullet points)\n\n"
            f"# Risk Assessment\n(Analysis in paragraphs)\n\n"
            f"# Actionable Solutions\n(Recommendations in bullet points)\n\n"
            f"# Clinical Disclaimer\n(Add the mandatory disclaimer text)\n\n"
            f"REPORT DATA: {report_text}"
        )

        try:
            response = self.llm.invoke(prompt)
            # Cleanup unwanted symbols manually as a safety layer
            content = response.content
            content = content.replace("?", "").replace("--", "").replace("::", ":")
            return content
        except Exception as e:
            return f"⚠️ Failed to analyze report: {str(e)}"