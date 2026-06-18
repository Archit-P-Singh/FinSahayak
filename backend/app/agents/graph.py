from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.profile_extraction import profile_extraction_node
from app.agents.nodes.missing_info import missing_info_node
from app.agents.nodes.financial_planning import financial_planning_node
from app.agents.nodes.investment_planning import investment_planning_node
from app.agents.nodes.government_schemes import government_schemes_node
from app.agents.nodes.financial_education import financial_education_node
from app.agents.nodes.health_score import health_score_node
from app.agents.nodes.report_generation import report_generation_node

def should_ask_question(state: AgentState) -> str:
    """
    Conditional edge routing: if missing info, end the graph (return question to user).
    Otherwise, proceed to financial planning.
    """
    if state.get("missing_info_flag"):
        return "end"
    return "continue"

def build_graph():
    # 1. Initialize StateGraph
    workflow = StateGraph(AgentState)
    
    # 2. Add Nodes
    workflow.add_node("profile_extraction", profile_extraction_node)
    workflow.add_node("missing_info", missing_info_node)
    workflow.add_node("financial_planning", financial_planning_node)
    workflow.add_node("investment_planning", investment_planning_node)
    workflow.add_node("government_schemes", government_schemes_node)
    workflow.add_node("financial_education", financial_education_node)
    workflow.add_node("health_score", health_score_node)
    workflow.add_node("report_generation", report_generation_node)
    
    # 3. Add Edges
    workflow.set_entry_point("profile_extraction")
    
    workflow.add_edge("profile_extraction", "missing_info")
    
    # Conditional logic
    workflow.add_conditional_edges(
        "missing_info",
        should_ask_question,
        {
            "end": END,
            "continue": "financial_planning"
        }
    )
    
    # Linear flow after planning
    workflow.add_edge("financial_planning", "investment_planning")
    workflow.add_edge("investment_planning", "government_schemes")
    workflow.add_edge("government_schemes", "financial_education")
    workflow.add_edge("financial_education", "health_score")
    workflow.add_edge("health_score", "report_generation")
    
    workflow.add_edge("report_generation", END)
    
    # 4. Compile the graph
    app = workflow.compile()
    return app

# Expose a compiled instance
agent_graph = build_graph()
