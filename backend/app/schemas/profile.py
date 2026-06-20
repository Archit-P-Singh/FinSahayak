from pydantic import BaseModel
from typing import Optional

class FinancialProfileResponse(BaseModel):
    age: Optional[int]
    occupation: Optional[str]
    income_type: Optional[str]
    income: Optional[float]
    expenses: Optional[float]
    debt: Optional[float]
    goals: Optional[str]
    risk_tolerance: Optional[str]
    special_circumstances: Optional[str]

    class Config:
        from_attributes = True
