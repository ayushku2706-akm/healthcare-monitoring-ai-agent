import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Load environment variables
load_dotenv()

class HealthAgent:
    def __init__(self):
        # FIX: Updated endpoints to match Google's active models
        primary_model = "gemini-2.5-flash"
        fallback_model = "gemini-2.0-flash"
        
        try:
            print(f"Initializing primary model: {primary_model}")
            self.llm = ChatGoogleGenerativeAI(
                model=primary_model,
                temperature=0.3,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        except Exception as e:
            print(f"Primary model initialization failed, switching to fallback ({fallback_model}). Error: {e}")
            self.llm = ChatGoogleGenerativeAI(
                model=fallback_model,
                temperature=0.3,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        
        # Medical compliance disclaimer safety guardrail
        self.system_prompt = SystemMessage(content=(
            "You are an AI Personal Health Assistant. "
            "Provide helpful, accurate structural guidance on medication tracking, wellness analytics, and health logs. "
            "CRITICAL SAFETY RULE: You are not a doctor. Always include a short, professional medical disclaimer stating "
            "that your responses are for educational/tracking purposes only and the user must consult a doctor for clinical choices."
        ))

    def respond(self, chat_history, user_message):
        """
        Processes conversation history and maps it to LangChain message formats.
        """
        messages = [self.system_prompt]
        
        # Format existing history for LangChain
        for role, text in chat_history:
            if role == "user":
                messages.append(HumanMessage(content=text))
            elif role == "assistant":
                messages.append(AIMessage(content=text))
                
        # Append the new user query
        messages.append(HumanMessage(content=user_message))
        
        # Invoke the model
        response = self.llm.invoke(messages)
        return response.content