from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.info import router as info_router
from app.config import settings
from app.api.auth import router as auth_router
from app.api.document import router as documents_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(info_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(chat_router)