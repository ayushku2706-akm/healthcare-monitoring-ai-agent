import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from fpdf import FPDF


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENV_PATH = os.path.join(
    BASE_DIR,
    "..",
    ".env"
)

# Load project .env
load_dotenv(dotenv_path=ENV_PATH)

# Also try current working directory
load_dotenv()


# ============================================================
# HEALTH AI AGENT
# ============================================================

class HealthAgent:

    def __init__(self):

        # ----------------------------------------------------
        # GEMINI MODELS
        # ----------------------------------------------------

        # Stable Gemini 2.5 models
        self.primary_model = "gemini-2.5-flash"
        self.fallback_model = "gemini-2.5-pro"

        # ----------------------------------------------------
        # API KEY
        # ----------------------------------------------------

        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if not api_key:

            raise ValueError(
                "GOOGLE_API_KEY / GEMINI_API_KEY "
                "not found in environment variables."
            )

        # ----------------------------------------------------
        # PRIMARY MODEL
        # ----------------------------------------------------

        self.llm = ChatGoogleGenerativeAI(
            model=self.primary_model,
            temperature=0.3,
            google_api_key=api_key,
            max_retries=2
        )

        # ----------------------------------------------------
        # FALLBACK MODEL
        # ----------------------------------------------------

        self.fallback_llm = ChatGoogleGenerativeAI(
            model=self.fallback_model,
            temperature=0.3,
            google_api_key=api_key,
            max_retries=2
        )

        # ====================================================
        # SYSTEM PROMPT
        # ====================================================

        self.system_prompt = SystemMessage(
            content=(
                "You are CareAI, an advanced clinical intelligence "
                "and personal health companion.\n\n"

                "Your capabilities include:\n"
                "- General health education\n"
                "- Symptom explanations\n"
                "- Fitness and wellness planning\n"
                "- Nutrition guidance\n"
                "- Medication education\n"
                "- Medical report interpretation\n"
                "- Preventive health information\n\n"

                "IMPORTANT MEDICAL SAFETY RULE:\n"
                "You are an AI assistant and not a licensed physician. "
                "Do not claim to diagnose diseases or replace professional "
                "medical care.\n\n"

                "For symptoms, pathology, medication or serious health "
                "concerns, provide educational information and recommend "
                "consulting a qualified healthcare professional.\n\n"

                "For emergencies, clearly advise the user to seek "
                "urgent/emergency medical care."
            )
        )

    # ============================================================
    # GEMINI INVOCATION WITH FALLBACK
    # ============================================================

    def _invoke_with_fallback(self, messages_or_prompt):

        primary_error = None

        # --------------------------------------------------------
        # PRIMARY
        # --------------------------------------------------------

        try:

            response = self.llm.invoke(
                messages_or_prompt
            )

            return response

        except Exception as e:

            primary_error = e

        # --------------------------------------------------------
        # FALLBACK
        # --------------------------------------------------------

        try:

            response = self.fallback_llm.invoke(
                messages_or_prompt
            )

            return response

        except Exception as fallback_error:

            raise Exception(
                "Gemini API failed.\n\n"
                f"Primary model "
                f"({self.primary_model}) error:\n"
                f"{primary_error}\n\n"
                f"Fallback model "
                f"({self.fallback_model}) error:\n"
                f"{fallback_error}"
            )

    # ============================================================
    # PDF TEXT SANITIZATION
    # ============================================================

    def _sanitize_for_pdf(self, text: str) -> str:

        replacements = {
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'",
            "—": "-",
            "–": "-",
            "•": "-",
            "…": "..."
        }

        for original, replacement in replacements.items():

            text = text.replace(
                original,
                replacement
            )

        return (
            text
            .encode(
                "latin-1",
                "ignore"
            )
            .decode("latin-1")
        )

    # ============================================================
    # GENERATE PDF
    # ============================================================

    def generate_pdf_report(
        self,
        text_content: str,
        filename: str = "Clinical_Report.pdf"
    ) -> str:

        clean_text = self._sanitize_for_pdf(
            text_content
        )

        pdf = FPDF()

        pdf.set_auto_page_break(
            auto=True,
            margin=15
        )

        pdf.add_page()

        for line in clean_text.split("\n"):

            line_str = line.strip()

            if not line_str:

                pdf.ln(4)

                continue

            # ------------------------------------------------
            # HEADINGS
            # ------------------------------------------------

            if line_str.startswith("#"):

                pdf.set_font(
                    "Arial",
                    "B",
                    14
                )

                clean_heading = (
                    line_str
                    .lstrip("#")
                    .strip()
                )

                pdf.cell(
                    0,
                    10,
                    txt=clean_heading,
                    ln=True
                )

            # ------------------------------------------------
            # NORMAL TEXT
            # ------------------------------------------------

            else:

                pdf.set_font(
                    "Arial",
                    "",
                    11
                )

                formatted_line = (
                    line_str
                    .replace("**", "")
                )

                pdf.multi_cell(
                    0,
                    8,
                    txt=formatted_line
                )

        pdf.output(
            filename
        )

        return filename

    # ============================================================
    # CHAT RESPONSE
    # ============================================================

    def respond(
        self,
        chat_history: list,
        user_message: str
    ) -> str:

        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if not api_key:

            return (
                "❌ **Configuration Error**\n\n"
                "Google Gemini API key was not found. "
                "Please check your `.env` file."
            )

        # --------------------------------------------------------
        # BUILD MESSAGE HISTORY
        # --------------------------------------------------------

        messages = [
            self.system_prompt
        ]

        for role, text in chat_history:

            if role == "user":

                messages.append(
                    HumanMessage(
                        content=text
                    )
                )

            elif role == "assistant":

                messages.append(
                    AIMessage(
                        content=text
                    )
                )

        messages.append(
            HumanMessage(
                content=user_message
            )
        )

        # --------------------------------------------------------
        # CALL GEMINI
        # --------------------------------------------------------

        try:

            response = self._invoke_with_fallback(
                messages
            )

            content = response.content

            # Sometimes Gemini/LangChain may return
            # non-string structured content
            if isinstance(content, list):

                content = "\n".join(
                    str(item)
                    for item in content
                )

            return str(content)

        except Exception as e:

            return (
                "⚠️ **AI Companion Communication Failure**\n\n"
                "CareAI could not connect to the Gemini service.\n\n"
                f"**Technical Details:** `{str(e)}`"
            )

    # ============================================================
    # MEDICAL REPORT ANALYSIS
    # ============================================================

    def analyze_medical_report(
        self,
        report_text: str
    ) -> str:

        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if not api_key:

            return (
                "❌ Configuration Error: "
                "Google Gemini API key is missing."
            )

        prompt = f"""
You are CareAI, a clinical information assistant.

Analyze the following medical/laboratory report.

IMPORTANT:
- Do not claim to provide a definitive diagnosis.
- Explain abnormal values clearly.
- Separate normal and abnormal findings.
- Mention when professional medical evaluation is recommended.
- Do not invent values that are not present in the report.

STRICT FORMATTING:

# Patient Profile Summary

Provide available patient information.

# Lab Vitals Analysis

Use clean bullet points.

# Normal Findings

Mention reassuring findings.

# Abnormal or Important Findings

Explain potentially important results in simple language.

# Risk Assessment

Provide educational risk interpretation.

# Actionable Solutions

Provide practical next steps.

# Clinical Disclaimer

Clearly state that this is AI-generated educational information
and does not replace evaluation by a qualified healthcare professional.

REPORT DATA:

{report_text}
"""

        try:

            response = self._invoke_with_fallback(
                prompt
            )

            content = response.content

            if isinstance(content, list):

                content = "\n".join(
                    str(item)
                    for item in content
                )

            content = str(content)

            content = (
                content
                .replace("--", "-")
                .replace("::", ":")
            )

            return content

        except Exception as e:

            return (
                "⚠️ **Medical Report Analysis Failed**\n\n"
                f"`{str(e)}`"
            )