# CareAI: Healthcare Monitoring AI Agent

CareAI is an advanced clinical intelligence and personal health companion designed to provide educational insights on medical research, symptom breakdowns, fitness planning, and medication tracking.

## Features
- **Clinical Intelligence:** Uses Gemini 1.5 Flash (with fallback to 2.0 Flash) for reliable medical data processing.
- **Robust AI Workflow:** Implements LangGraph state management for complex clinical analysis.
- **Enterprise-Grade API:** FastAPI-powered backend for seamless integration, featuring:
    - HIPAA-compliant logic structure.
    - Performance monitoring with latency tracking.
    - Automated Swagger documentation.
- **PDF Reporting:** Automatic generation of professional clinical reports.
- **Medical Guardrails:** Built-in safety disclaimers for all health-related queries.

## Tech Stack
- **AI/LLM:** Google Gemini (via LangChain)
- **Framework:** Streamlit (Frontend), FastAPI (Backend)
- **Workflow:** LangGraph
- **Deployment:** Render / Streamlit Community Cloud

## API Documentation
Once the application is running, you can access the interactive API documentation at:
`http://127.0.0.1:8000/docs`

## Setup Instructions
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your `.env` file with `GOOGLE_API_KEY`.
4. Run the API: `uvicorn src.main_api:app --reload`
5. Run the frontend: `streamlit run src/app.py`

---
*Disclaimer: CareAI is an AI-powered assistant and not a substitute for professional medical advice. Always consult with a licensed physician for diagnosis and treatment.*