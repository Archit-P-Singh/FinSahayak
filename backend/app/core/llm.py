import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

def get_gemini_llm(model="gemini-3.1-flash-lite", temperature=0.7):
    """
    Returns a Gemini LLM instance. 
    Using gemini-3.1-flash-lite as the default lightweight model.
    """
    if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
        # Return a dummy object if no key for local dev without errors
        print("WARNING: GEMINI_API_KEY not set. LLM calls will fail.")
        
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=gemini_api_key
    )

def get_groq_llm(model="qwen/qwen3-32b", temperature=0.7):
    """
    Returns a Groq LLM instance.
    Using qwen/qwen3-32b (Qwen 32B equivalent on Groq).
    """
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        print("WARNING: GROQ_API_KEY not set. LLM calls will fail.")
        
    return ChatGroq(
        model=model,
        temperature=temperature,
        groq_api_key=groq_api_key
    )
