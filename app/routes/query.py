"""
query.py - RAG Query Endpoints

Routes:
    POST /query/             — ask a question, get an AI answer with sources
    GET  /query/history      — paginated list of past queries
    GET  /query/{query_id}   — single query log by ID

Security notes:
- QueryRequest.question is capped at 1000 chars (prompt-injection + token-exhaustion guard).
- QueryRequest.top_k is bounded [1, 20] (DoS guard — prevents huge pgvector + Gemini calls).
- history limit is bounded [1, 100] (prevents full table dump).
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import limiter
from app.schemas.query import QueryRequest, QueryResponse, QueryHistoryItem
from app.services.query_service import query_service
from app.models.query_log import QueryLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
@limiter.limit(settings.rate_limit_query)
def ask_question(request: Request, body: QueryRequest, db: Session = Depends(get_db)):
    """
    Submit a question and receive an AI-generated answer grounded in
    uploaded documents.

    - **question**: 1–1000 characters.
    - **top_k**: number of document chunks to retrieve (1–20, default 5).

    Rate-limited to protect the expensive embedding + Gemini pipeline.
    """
    result = query_service.answer_question(
        question=body.question,
        db=db,
        top_k=body.top_k,
    )
    return result


@router.get("/history", response_model=list[QueryHistoryItem])
def get_query_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Return recent query log entries, newest first.

    - **limit**: 1–100 results (default 20).
    """
    entries = (
        db.query(QueryLog)
        .order_by(QueryLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return entries


@router.get("/{query_id}", response_model=QueryHistoryItem)
def get_query_by_id(query_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single query log entry by its ID.
    Returns 404 if not found.
    """
    entry = db.query(QueryLog).filter(QueryLog.id == query_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Query log {query_id} not found.")
    return entry
