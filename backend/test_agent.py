import asyncio
from langchain_core.messages import HumanMessage
from app.agents.graph import agent_graph

def run_test_case(test_name: str, initial_messages: list, initial_profile: dict = None):
    print(f"\n{'='*50}")
    print(f"RUNNING TEST CASE: {test_name}")
    print(f"{'='*50}")
    
    if initial_profile is None:
        initial_profile = {}
        
    state = {
        "messages": initial_messages,
        "extracted_profile": initial_profile,
        "missing_info_flag": False
    }
    
    try:
        final_state = agent_graph.invoke(state)
        
        print("\n--- RESULTS ---")
        print(f"Missing Info Flag: {final_state.get('missing_info_flag')}")
        
        print("\n--- EXTRACTED PROFILE ---")
        profile = final_state.get("extracted_profile")
        if hasattr(profile, 'model_dump'):
            print(profile.model_dump())
        else:
            print(profile)
            
        print("\n--- AGENT RESPONSE ---")
        messages = final_state.get("messages", [])
        if messages:
            print(messages[-1].content)
        else:
            print("No response generated.")
            
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    # Test Case 1: Stable Income, all info provided
    msg1 = "I am 23 years old and work as a software engineer. I earn 80,000 per month. My rent is 20,000 and food is 10,000. I have a 2 lakh education loan. I want to save for a house."
    run_test_case("Stable Income & Full Info", [HumanMessage(content=msg1)])
    
    # Test Case 2: Missing Information (Age is missing)
    msg2 = "I earn 50,000 a month but spend almost all of it. I have 3 lakh credit card debt. I need help."
    run_test_case("Missing Info (Age)", [HumanMessage(content=msg2)])
    
    # Test Case 3: Unstable Income (Freelancer)
    msg3 = "I am 28 years old. I am a freelance designer so my income is unstable, usually between 20k to 90k a month. My expenses are around 30k. I want to build an emergency fund."
    run_test_case("Unstable Income", [HumanMessage(content=msg3)])
