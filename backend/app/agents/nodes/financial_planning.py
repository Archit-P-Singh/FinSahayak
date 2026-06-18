from app.agents.state import AgentState
from app.core.llm import get_groq_llm
from langchain_core.prompts import ChatPromptTemplate

def financial_planning_node(state: AgentState) -> dict:
    print("--- FINANCIAL PLANNING AGENT ---")
    
    llm = get_groq_llm()
    profile = state.get("extracted_profile", {})
    
    system_prompt = """You are an expert financial planner.
Given the user's financial profile:
{profile}

Provide a concise budget suggestion and a general financial roadmap.
CRITICAL INSTRUCTION: Tailor your advice heavily based on the user's occupation, income type, and special circumstances.
- If their income is "variable" or "seasonal", DO NOT recommend standard rules like 50/30/20. Instead, focus on building buffer funds, managing irregular cash flow, and surviving lean months.
- **ASSET ALLOCATION MANDATE**: If their income is "variable" or "seasonal", strictly AVOID recommending high percentages of locked-in or illiquid investments (like PPF or FDs). Prioritize highly liquid emergency funds to prevent them from taking high-interest loans during lean months.
- If they have special circumstances (e.g. debt crisis, visual impairment), prioritize those in your advice.
Keep it practical and easy to understand."""
    
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt)])
    chain = prompt | llm
    
    try:
        response = chain.invoke({"profile": str(profile)})
        return {"financial_plan": response.content}
    except Exception as e:
        print(f"Error in planning: {e}")
        return {"financial_plan": "Error generating financial plan."}
