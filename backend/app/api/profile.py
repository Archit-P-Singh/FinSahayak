from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, FinancialProfile
from app.api.deps import get_current_user
from app.schemas.profile import FinancialProfileResponse
from app.api.chat import get_or_create_profile

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/{conversation_id}", response_model=FinancialProfileResponse)
def get_profile(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.db.models import Conversation
    from fastapi import HTTPException
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    profile = get_or_create_profile(db, conversation.id)
    return profile
