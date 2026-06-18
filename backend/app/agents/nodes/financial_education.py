from app.agents.state import AgentState
from app.core.llm import get_gemini_llm
from langchain_core.prompts import ChatPromptTemplate

def financial_education_node(state: AgentState) -> dict:
    print("--- FINANCIAL EDUCATION AGENT ---")
    
    llm = get_gemini_llm()
    profile = state.get("extracted_profile", {})
    plan = state.get("financial_plan", "")
    
    system_prompt = """You are a financial educator.
Based on the user's profile and plan, provide one "Did you know?" fact or a brief educational tip explaining *why* a certain financial principle (like emergency funds or compounding) is important for them.
**SCAM/FRAUD MANDATE**: If the user has a low/variable income or mentions being scared of scams, your 'Did you know?' fact MUST be a strict warning against unregulated WhatsApp investment tips, 'get rich quick' schemes, or predatory high-interest loan apps.
Keep it to 2-3 sentences max.

Profile:
{profile}
"""
    prompt = ChatPromptTemplate.from_messages([("human", system_prompt)])
    chain = prompt | llm
    
    try:
        response = chain.invoke({"profile": str(profile)})
        return {"education_context": response.content}
    except Exception as e:
        return {"education_context": "Did you know? Compound interest is the eighth wonder of the world."}
