"""Pydantic schemas for API request/response validation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TextIngestRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Raw contract text to analyze")
    filename: Optional[str] = Field("contract.txt", description="Document filename identifier")


class SetApiKeyRequest(BaseModel):
    api_key: str = Field(..., min_length=1, description="Google Gemini API Key")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Question about the uploaded document")
    top_k: Optional[int] = Field(4, ge=1, le=10, description="Number of context chunks to retrieve")


class CitationItem(BaseModel):
    chunk_id: int
    pages: str
    start_page: int
    end_page: int
    section: Optional[str] = None
    score: float
    snippet: str


class DocumentMetadata(BaseModel):
    filename: str
    total_pages: int
    total_words: int
    total_chars: int
    estimated_tokens: int
    chunks_count: int


class ChatResponse(BaseModel):
    answer: str
    direct_quotes: List[str] = []
    actionable_takeaway: Optional[str] = None
    relevant_pages: List[int] = []
    citations: List[Dict[str, Any]] = []
    mode: str = "live_gemini"
