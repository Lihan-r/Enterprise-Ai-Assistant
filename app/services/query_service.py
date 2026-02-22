"""
query_service.py - RAG Query Orchestrator

This service coordinates the full RAG pipeline:
    1. Embed the user's question → query vector
    2. Retrieve the top-k most similar document chunks from pgvector
    3. Build a context string and call Gemini
    4. Log the query + answer to query_logs
    5. Return a structured response dict

In Spring Boot terms this is the @Service layer that calls the
@Repository (retrieval_service) and external API clients
(embedding_service, gemini_service).
"""

import json
import logging
import time
from sqlalchemy.orm import Session

from app.config import settings
from app.services.embedding_service import embedding_service
from app.services.retrieval_service import retrieval_service
from app.services.gemini_service import gemini_service
from app.models.query_log import QueryLog

logger = logging.getLogger(__name__)


class QueryService:
    def answer_question(
        self,
        question: str,
        db: Session,
        top_k: int = 5,
    ) -> dict:
        """
        Run the full RAG pipeline for a single question.

        Args:
            question: Validated user question (max 1000 chars enforced at API layer).
            db:       SQLAlchemy session (injected by FastAPI dependency).
            top_k:    Number of chunks to retrieve (validated [1, 20] at API layer).

        Returns:
            Dict matching QueryResponse schema:
                question, answer, sources (list of ChunkResult dicts), response_time_ms.
        """
        start_time = time.time()

        # Step 1: Embed the question
        query_vector = embedding_service.generate_embedding(question)

        # Step 2: Retrieve similar chunks from pgvector
        chunks = retrieval_service.find_similar_chunks(query_vector, db, top_k)

        # Step 3: Generate answer (or short-circuit if no documents exist)
        if not chunks:
            answer = (
                "I don't have enough information to answer that question. "
                "No relevant documents were found in the knowledge base."
            )
            logger.info("No chunks found for question; returning no-information response.")
        else:
            # Build context string with clear separators between chunks
            context_parts = []
            for i, chunk in enumerate(chunks, start=1):
                context_parts.append(
                    f"[Source {i} — document_id={chunk['document_id']}, "
                    f"chunk_index={chunk['chunk_index']}]\n{chunk['content']}"
                )
            context = "\n\n---\n\n".join(context_parts)

            max_chars = settings.gemini_max_context_chars
            if len(context) > max_chars:
                original_len = len(context)
                truncated = context[:max_chars]
                # Find the last sentence boundary within the limit
                last_boundary = max(
                    truncated.rfind("."),
                    truncated.rfind("!"),
                    truncated.rfind("?"),
                )
                if last_boundary > 0:
                    truncated = truncated[: last_boundary + 1]
                context = truncated
                logger.warning(
                    "Context truncated from %d to %d chars (max_context_chars=%d)",
                    original_len,
                    len(context),
                    max_chars,
                )

            answer = gemini_service.generate_with_context(question, context)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # Step 4: Persist to query_logs
        source_doc_ids = list({chunk["document_id"] for chunk in chunks})
        log_entry = QueryLog(
            question=question,
            answer=answer,
            source_documents=json.dumps(source_doc_ids),
            response_time=elapsed_ms / 1000.0,  # store as seconds
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        # Step 5: Return structured result
        return {
            "question": question,
            "answer": answer,
            "sources": chunks,
            "response_time_ms": elapsed_ms,
        }


query_service = QueryService()
