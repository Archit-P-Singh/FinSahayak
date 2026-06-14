from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
import app.db.models as models

from app.api import auth, chat, profile

# Create all tables in the database (for dev, in prod use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinSahayak AI API",
    description="Backend API for FinSahayak AI Multi-Agent System",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(profile.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to FinSahayak AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

