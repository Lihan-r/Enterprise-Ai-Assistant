"""
query.py - Pydantic DTOs for the RAG Query Pipeline

These are the request/response shapes for the /query/ endpoints.
Pydantic validates and coerces values automatically — analogous to
@RequestBody + @Valid + BindingResult in Spring MVC.

Validation notes:
- question is capped at 1000 chars to prevent token exhaustion and
  shrink the prompt-injection attack surface.
- top_k is bounded [1, 20] to prevent a single request from dumping
  thousands of DB rows into a Gemini prompt (DoS mitigation).
- history limit is bounded [1, 100] in the route layer (see routes/query.py).
"""

from datetime import datetime
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    # max_length=1000 shrinks prompt-injection surface and prevents token exhaustion.
    # NOTE: prompt injection cannot be fully prevented; the LLM prompt itself
    # includes a "Answer based ONLY on the provided context" guard as a soft mitigation.
    question: str = Field(..., min_length=1, max_length=1000)

    # ge=1, le=20 prevents a client from requesting 100k rows (DoS mitigation).
    top_k: int = Field(default=5, ge=1, le=20)


class ChunkResult(BaseModel):
    content: str
    document_id: int
    chunk_index: int
    similarity_score: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[ChunkResult]
    response_time_ms: float


class QueryHistoryItem(BaseModel):
    id: int
    question: str
    answer: str | None
    created_at: datetime
