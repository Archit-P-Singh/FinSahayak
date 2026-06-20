from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
import os
import shutil
from PyPDF2 import PdfReader
from io import BytesIO

from app.db.database import get_db
from app.db.models import User, Conversation, Message, FinancialProfile, UploadedFile
from app.api.deps import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.graph import agent_graph
from app.core.llm import get_gemini_llm
from langchain_core.messages import HumanMessage

router = APIRouter(prefix="/conversations", tags=["chat"])

def get_or_create_profile(db: Session, conversation_id: int):
    profile = db.query(FinancialProfile).filter(FinancialProfile.conversation_id == conversation_id).first()
    if not profile:
        profile = FinancialProfile(conversation_id=conversation_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.post("/", response_model=dict)
def create_conversation(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conv = Conversation(user_id=current_user.id, title="New Conversation")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "title": conv.title}

@router.post("/{conversation_id}/chat", response_model=ChatResponse)
def chat_with_agent(
    conversation_id: int, 
    request: ChatRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id, 
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    # Save user message
    user_msg = Message(conversation_id=conversation.id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()
    
    # Fetch history
    history = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at).all()
    langchain_messages = []
    for msg in history:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        else:
            langchain_messages.append(AIMessage(content=msg.content))
            
    # Fetch profile
    db_profile = get_or_create_profile(db, conversation.id)
    profile_dict = {
        "age": db_profile.age,
        "occupation": db_profile.occupation,
        "income_type": db_profile.income_type,
        "income": db_profile.income,
        "expenses": db_profile.expenses,
        "debt": db_profile.debt,
        "goals": db_profile.goals,
        "risk_tolerance": db_profile.risk_tolerance,
        "special_circumstances": db_profile.special_circumstances
    }
    
    # Run Graph
    initial_state = {
        "messages": langchain_messages,
        "extracted_profile": profile_dict,
        "missing_info_flag": False
    }
    
    try:
        final_state = agent_graph.invoke(initial_state)
    except Exception as e:
        print(f"Error invoking graph: {e}")
        raise HTTPException(status_code=500, detail="Error generating response from AI")
        
    # Extract latest AI message
    latest_messages = final_state.get("messages", [])
    response_content = ""
    if latest_messages and isinstance(latest_messages[-1], AIMessage):
        raw_content = latest_messages[-1].content
        if isinstance(raw_content, list):
            texts = [p.get("text", "") for p in raw_content if isinstance(p, dict) and p.get("type") == "text"]
            response_content = "\n".join(texts) if texts else str(raw_content)
        else:
            response_content = str(raw_content)
        
    # Save AI message
    ai_msg = Message(conversation_id=conversation.id, role="assistant", content=response_content)
    db.add(ai_msg)
    
    # Update profile in DB if it changed
    updated_profile = final_state.get("extracted_profile", {})
    
    if hasattr(updated_profile, 'model_dump'):
        updated_profile = updated_profile.model_dump()
    
    if isinstance(updated_profile, dict):
        if updated_profile.get("age") is not None: db_profile.age = updated_profile["age"]
        if updated_profile.get("occupation") is not None: db_profile.occupation = updated_profile["occupation"]
        if updated_profile.get("income_type") is not None: db_profile.income_type = updated_profile["income_type"]
        if updated_profile.get("income") is not None: db_profile.income = updated_profile["income"]
        if updated_profile.get("expenses") is not None: db_profile.expenses = updated_profile["expenses"]
        if updated_profile.get("debt") is not None: db_profile.debt = updated_profile["debt"]
        if updated_profile.get("goals") is not None: db_profile.goals = updated_profile["goals"]
        if updated_profile.get("risk_tolerance") is not None: db_profile.risk_tolerance = updated_profile["risk_tolerance"]
        if updated_profile.get("special_circumstances") is not None: db_profile.special_circumstances = updated_profile["special_circumstances"]
    
    db.commit()
    
    final_report_content = final_state.get("final_report")
    if isinstance(final_report_content, list):
        texts = [p.get("text", "") for p in final_report_content if isinstance(p, dict) and p.get("type") == "text"]
        final_report_content = "\n".join(texts) if texts else str(final_report_content)
    elif final_report_content is not None:
        final_report_content = str(final_report_content)

    if final_report_content == response_content:
        final_report_content = None

    return ChatResponse(
        response=response_content,
        missing_info_flag=final_state.get("missing_info_flag", False),
        final_report=final_report_content
    )

@router.post("/{conversation_id}/upload")
async def upload_file(
    conversation_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id, 
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    content = await file.read()
    extracted_text = ""
    
    if file.filename.lower().endswith(".pdf"):
        try:
            reader = PdfReader(BytesIO(content))
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")
            
    elif file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        # Note: In a production app, we would pass the image data to Gemini for OCR
        # using the multi-modal capabilities of Gemini 1.5 flash.
        # For simplicity and robust testing in this CLI backend, we will just simulate it
        # or require the user to send text.
        # Actually, let's just make a simple text extraction call using Gemini!
        try:
            import base64
            encoded_image = base64.b64encode(content).decode("utf-8")
            image_message = HumanMessage(
                content=[
                    {"type": "text", "text": "Extract all the text from this image as accurately as possible."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                    },
                ]
            )
            llm = get_gemini_llm()
            res = llm.invoke([image_message])
            raw_content = res.content
            if isinstance(raw_content, list):
                texts = [p.get("text", "") for p in raw_content if isinstance(p, dict) and p.get("type") == "text"]
                extracted_text = "\n".join(texts) if texts else str(raw_content)
            else:
                extracted_text = str(raw_content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")
        
    # Save file record to DB
    uploaded_file = UploadedFile(
        user_id=current_user.id,
        conversation_id=conversation.id,
        filename=file.filename,
        file_type=file.content_type,
        extracted_text=extracted_text
    )
    db.add(uploaded_file)
    
    # Also save as a system/user message so the agent has context
    context_msg = f"User uploaded a document '{file.filename}'. Extracted content:\n\n{extracted_text}"
    db.add(Message(conversation_id=conversation.id, role="user", content=context_msg))
    
    db.commit()
    return {"message": "File uploaded and processed successfully", "filename": file.filename}
