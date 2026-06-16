from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

def add_messages(left: list, right: list) -> list:
    """Append messages to the existing list."""
    return left + right

from pydantic import BaseModel, Field

class FinancialProfileState(BaseModel):
    age: Optional[int] = Field(default=None, description="Age of the user. Return null if not explicitly mentioned.")
    occupation: Optional[str] = Field(default=None, description="Occupation or job title (e.g. farmer, teacher, gig worker). Return null if not explicitly mentioned.")
    income_type: Optional[str] = Field(default=None, description="Type of income (e.g. fixed, variable, seasonal). Return null if not explicitly mentioned.")
    income: Optional[float] = Field(default=None, description="Average monthly income. Return null if not explicitly mentioned.")
    expenses: Optional[float] = Field(default=None, description="Monthly expenses. Return null if not explicitly mentioned.")
    debt: Optional[float] = Field(default=None, description="Total debt. Return null if not explicitly mentioned.")
    goals: Optional[str] = Field(default=None, description="Financial goals. Return null if not explicitly mentioned.")
    risk_tolerance: Optional[str] = Field(default=None, description="Risk tolerance (e.g. low, moderate, high). Return null if not explicitly mentioned.")
    special_circumstances: Optional[str] = Field(default=None, description="Any special circumstances or challenges (e.g. visually impaired, high interest loans, seasonal cash flow issues). Return null if not explicitly mentioned.")

class AgentState(TypedDict):
    # Chat history between user and assistant
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Financial profile extracted so far
    extracted_profile: FinancialProfileState
    
    # Flag to determine if we need to ask follow-up questions
    missing_info_flag: bool
    
    # Outputs from different agents
    financial_plan: str
    investment_plan: str
    schemes_info: str
    education_context: str
    health_score: int
    final_report: str
