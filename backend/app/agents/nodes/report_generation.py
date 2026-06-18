from app.agents.state import AgentState
from app.core.llm import get_gemini_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

def report_generation_node(state: AgentState) -> dict:
    print("--- REPORT GENERATION AGENT ---")
    
    llm = get_gemini_llm()
    
    report_data = f"""
Profile: {state.get('extracted_profile', {})}
Health Score: {state.get('health_score')}
Financial Plan: {state.get('financial_plan')}
Investment Plan: {state.get('investment_plan')}
Government Schemes: {state.get('schemes_info')}
Education Context: {state.get('education_context')}
"""
    
    user_query = "Provide a financial report."
    for msg in reversed(state.get("messages", [])):
        if getattr(msg, "type", "") == "human":
            user_query = getattr(msg, "content", str(msg))
            break
            
    system_prompt = """You are a professional financial advisor.
Synthesize the following information into a beautifully formatted Markdown report for the user.
Use headings, bullet points, and bold text for readability. Do not output anything outside of the report.

**CRITICAL INSTRUCTION 1 (LANGUAGE)**: Analyze the user's prompt. If they mention struggling to find information in a specific language, or state a preference for a language (e.g., Kannada, Marathi), you MUST output your entire final report in that specific language. Do not output in Hindi if they ask for Kannada.
**CRITICAL INSTRUCTION 2 (ACCESSIBILITY)**: Review the Profile in the data below. If the user's special circumstances mention a visual impairment or disability, AVOID complex Markdown tables and nested bullet points. Output a linear, conversational response optimized for screen readers.

User's Last Request:
{user_query}

Data:
{report_data}
"""
    
    prompt = ChatPromptTemplate.from_messages([("human", system_prompt)])
    chain = prompt | llm
    
    try:
        response = chain.invoke({"report_data": report_data, "user_query": user_query})
        return {
            "final_report": response.content,
            "messages": [AIMessage(content=response.content)]
        }
    except Exception as e:
        print(f"Error generating report: {e}")
        fallback_msg = "Error generating final report."
        return {
            "final_report": fallback_msg,
            "messages": [AIMessage(content=fallback_msg)]
        }
