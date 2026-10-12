
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.utils.auth import get_current_user
from app.database.models import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import answer_document_question


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/ask", response_model=ChatResponse)
def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return answer_document_question(
        db=db,
        user_id=current_user.id,
        question=request.question,
        top_k=request.top_k,
    )
