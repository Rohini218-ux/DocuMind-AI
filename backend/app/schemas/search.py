from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=10)


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    content: str
    similarity: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]