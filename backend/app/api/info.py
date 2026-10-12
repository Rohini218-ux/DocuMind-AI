from fastapi import APIRouter

router = APIRouter()


@router.get("/info")
def get_info():
    return {
        "name": "DocuMind AI",
        "version": "1.0.0",
        "description": "AI-powered document question answering platform"
    }