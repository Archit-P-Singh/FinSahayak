from app.agents.state import AgentState
from app.core.rag import get_vector_store
from app.core.llm import get_gemini_llm
from langchain_core.prompts import ChatPromptTemplate

def government_schemes_node(state: AgentState) -> dict:
    print("--- GOVERNMENT SCHEMES AGENT (RAG) ---")
    
    profile = state.get("extracted_profile", {})
    goals = profile.get('goals') if isinstance(profile, dict) else getattr(profile, 'goals', None)
    occupation = profile.get('occupation') if isinstance(profile, dict) else getattr(profile, 'occupation', None)
    circumstances = profile.get('special_circumstances') if isinstance(profile, dict) else getattr(profile, 'special_circumstances', None)
    
    query = f"Government schemes, tax benefits, and investments for occupation: {occupation}, goals: {goals}, special circumstances: {circumstances}"
    
    try:
        vector_store = get_vector_store()
        # Ensure collection has items before search, else it might error out
        try:
            docs = vector_store.similarity_search(query, k=3)
            context = "\n".join([d.page_content for d in docs])
        except Exception:
            context = ""
            
        if not context.strip():
            context = "No specific government schemes found in the knowledge base."
            
        llm = get_gemini_llm()
        system_prompt = """You are a financial advisor specializing in Indian government schemes.
Given the retrieved knowledge below, suggest any relevant schemes for the user based on their profile.
If nothing is highly relevant, mention general tax-saving schemes like PPF or ELSS.

Retrieved Knowledge:
{context}

User Profile:
{profile}
"""
        prompt = ChatPromptTemplate.from_messages([("human", system_prompt)])
        chain = prompt | llm
        
        response = chain.invoke({
            "context": context,
            "profile": str(profile)
        })
        return {"schemes_info": response.content}
        
    except Exception as e:
        print(f"Error in RAG: {e}")
        return {"schemes_info": "Could not retrieve specific government schemes at this time."}
