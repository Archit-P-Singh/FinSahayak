from app.agents.state import AgentState
from app.core.llm import get_gemini_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

def missing_info_node(state: AgentState) -> dict:
    print("--- MISSING INFO AGENT ---")
    profile = state.get("extracted_profile", {})
    
    # Handle case where profile might be an object instead of dict if extracted directly
    if hasattr(profile, 'model_dump'):
        profile_dict = profile.model_dump()
    elif isinstance(profile, dict):
        profile_dict = profile
    else:
        profile_dict = {}
        
    missing_fields = []
    if profile_dict.get("age") is None: missing_fields.append("age")
    if profile_dict.get("income") is None: missing_fields.append("income")
    
    missing_info_flag = len(missing_fields) > 0
    
    if missing_info_flag:
        llm = get_gemini_llm()
        system_prompt = f"""You are a polite financial advisor.
The user has not provided the following critical information: {', '.join(missing_fields)}.
Ask a single, natural, and polite follow-up question to get this information. Do not ask for anything else."""
        
        prompt = ChatPromptTemplate.from_messages([("human", system_prompt)])
        chain = prompt | llm
        
        try:
            response = chain.invoke({})
            return {
                "missing_info_flag": True,
                "messages": [response]
            }
        except Exception as e:
            fallback = f"Could you please tell me your {', '.join(missing_fields)}?"
            return {
                "missing_info_flag": True,
                "messages": [AIMessage(content=fallback)]
            }
    
    return {"missing_info_flag": False}
