from app.agents.state import AgentState

def health_score_node(state: AgentState) -> dict:
    print("--- FINANCIAL HEALTH SCORE AGENT ---")
    
    profile = state.get("extracted_profile", {})
    
    if hasattr(profile, 'model_dump'):
        profile_dict = profile.model_dump()
    elif isinstance(profile, dict):
        profile_dict = profile
    else:
        profile_dict = {}

    score = 50
    income = profile_dict.get("income") or 0
    expenses = profile_dict.get("expenses") or 0
    debt = profile_dict.get("debt") or 0
    
    if income > 0:
        savings_rate = (income - expenses) / income
        if savings_rate > 0.2:
            score += 20
        elif savings_rate > 0.1:
            score += 10
            
    if debt == 0:
        score += 15
    elif income > 0 and debt / income < 0.3:
        score += 5
        
    score = min(max(score, 0), 100)
    return {"health_score": int(score)}
