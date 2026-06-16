from app.agents.state import AgentState, FinancialProfileState
from app.core.llm import get_gemini_llm
from langchain_core.prompts import ChatPromptTemplate

def profile_extraction_node(state: AgentState) -> dict:
    print("--- PROFILE EXTRACTION AGENT ---")
    
    llm = get_gemini_llm().with_structured_output(FinancialProfileState)
    messages = state.get("messages", [])
    current_profile = state.get("extracted_profile", {})
    
    system_prompt = """You are a financial profile extraction agent.
Your job is to read the conversation and extract financial information into a structured format.
If a piece of information is not mentioned, leave it as null/None.
Update the current profile with any new information found in the latest messages.

IMPORTANT INSTRUCTIONS:
- Pay close attention to extracting the user's `occupation` (e.g. gig worker, teacher, farmer).
- Extract `special_circumstances` if the user mentions any disabilities (e.g. visually impaired), debt crises, or specific life challenges.
- If the user states they have a variable, seasonal, or non-continuous income, set `income_type` to "variable" or "seasonal" and estimate their average monthly `income` as a float based on any numbers they provide. If they provide no numbers but explain their situation, set `income` to 0.0 so the system knows it has been addressed.

Current Profile:
{current_profile}
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}")
    ])
    
    chain = prompt | llm
    
    try:
        updated_profile = chain.invoke({
            "messages": messages,
            "current_profile": str(current_profile)
        })
        # If extraction returns None (e.g., failure), keep current
        if not updated_profile:
            updated_profile = current_profile
        return {"extracted_profile": updated_profile}
    except Exception as e:
        print(f"Error in extraction: {e}")
        return {"extracted_profile": current_profile}
