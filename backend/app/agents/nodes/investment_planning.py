from app.agents.state import AgentState
from app.core.llm import get_groq_llm
from langchain_core.prompts import ChatPromptTemplate

def investment_planning_node(state: AgentState) -> dict:
    print("--- INVESTMENT PLANNING AGENT ---")
    
    llm = get_groq_llm()
    profile = state.get("extracted_profile", {})
    
    system_prompt = """You are an expert investment advisor.
Given the user's financial profile:
{profile}

Provide a concise investment strategy and asset allocation suggestion based on their risk tolerance and goals.
Keep it actionable and avoid overly complex jargon."""
    
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt)])
    chain = prompt | llm
    
    try:
        response = chain.invoke({"profile": str(profile)})
        return {"investment_plan": response.content}
    except Exception as e:
        print(f"Error in investment planning: {e}")
        return {"investment_plan": "Error generating investment plan."}
