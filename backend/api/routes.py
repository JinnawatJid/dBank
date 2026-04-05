from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db

router = APIRouter()

class AskRequest(BaseModel):
    query: str

class AskResponse(BaseModel):
    answer: str
    tools_used: list[str] = []

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    """
    Core endpoint to handle natural language questions.
    Currently returns a dummy response to satisfy Task 2.1 API Skeleton DoD.
    """
    # In a later task, we will integrate Google Generative AI and MCP tool orchestration here.
    return AskResponse(
        answer=f"You asked: '{request.query}'. I am a skeleton API, so I don't know the answer yet!",
        tools_used=[]
    )
