from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.semantic_search_service import search_documents
from app.utils.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Semantic Search"])


@router.post("/semantic", response_model=SearchResponse)
def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        results = search_documents(
            db=db,
            user_id=current_user.id,
            query=request.query.strip(),
            top_k=request.top_k,
        )

        return {
            "query": request.query,
            "results": results,
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Search index is not available yet.",
        )